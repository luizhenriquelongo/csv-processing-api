import glob
import threading
import traceback
from pathlib import Path
from typing import Any, Dict, Literal, Protocol, Set, Tuple

import pandas as pd
import polars as pl

import helpers
from background_tasks.exceptions import ProcessingError
from dtos import Task, TaskStatus
from dtos.types import ErrorsDict
from logger import get_logger

logger = get_logger(__file__)
pl.enable_string_cache(True)


class TaskDAO(Protocol):
    def get_task(self, task_id: str) -> Task:
        ...

    def update_task(self, task: Task) -> Task:
        ...


class CSVProcessor:
    """
    CSVProcessor class processes a CSV file by splitting it into multiple temporary files
    and generating a result file by executing queries on the temporary files.

    This class is meant to be used with the 'with' statement in order to clean tmp files and handle
    exceptions in the right way.

    Example:
        >>> with CSVProcessor(...) as processor:
        ...     processor.execute()
        >>> print('Temporary files and exceptions handled succesfully!')
    """

    def __init__(
        self,
        task_id: str,
        dao: TaskDAO,
        *,
        output_dir: Path | str,
        chunk_size: int | None = 2_000_000,
    ):
        self.dao = dao
        self.task = self.dao.get_task(task_id)
        self.output_dir = output_dir if isinstance(output_dir, Path) else Path(output_dir).resolve()
        self.chunk_size = chunk_size
        self.__lock = threading.Lock()
        self.__tmp_dir = self.output_dir / f"{self.task.id}"
        helpers.enforce_directory_creation(self.__tmp_dir)

    def execute(self):
        self.update_task(status=TaskStatus.IN_PROGRESS)

        self.validate_task()

        result_file_path = self.process_task()

        self.update_task(status=TaskStatus.COMPLETED, output_file_path=result_file_path)

    def validate_task(self):
        errors = {}
        if self.task.input_file_path is None:
            errors["input_file"] = ["Cannot process a csv without the input file."]

        elif not self.task.input_file_path.endswith(".csv"):
            errors["input_file"] = ["File format not supported."]

        if errors:
            raise ProcessingError(errors=errors)

    def process_task(self) -> Path:
        """
        Processes the task and generates the result file.

        Returns:
            Path: The path to the result file.
        """
        self.split_file_into_multiple_tmp_files_by_name()
        return self.process_and_generate_result_file()

    def split_file_into_multiple_tmp_files_by_name(self) -> None:
        """
        Splits the input file into multiple temporary files.

        This method reads the CSV file in chunks, converts it to a polars dataframe,
        partitions the dataframe by "Song", and creates a temporary file for each partition.

        Note:
            This code has a bottleneck which is the tmp file per song, if one of these files are
            larger than memory, the application may run out of memory while processing it in the next
            processing stage.
        """
        seen_groups: Set[str | Tuple[str, str]] = set()

        # Read csv in chunks using pandas
        for chunk in pd.read_csv(
            self.task.input_file_path, chunksize=self.chunk_size, dtype=self._get_dtypes(engine="pandas")
        ):
            # Convert the pandas dataframe into polars dataframe since polars is faster and handles memory usage better.
            dataframe = pl.from_pandas(chunk, schema_overrides=self._get_dtypes(engine="polars")).sort("Song")

            # Remove the pandas dataframe chunk from memory since we are not going to use it anymore.
            del chunk

            #

            # Partitioning the dataframe by "Song" and create a temporary csv file for each "Song".
            partitions = dataframe.partition_by("Song", as_dict=True, maintain_order=False)

            helpers.execute_in_thread_pool(
                fn=helpers.save_dataframe_to_group_file,
                args_list=[
                    (group, dataframe, self.__tmp_dir, seen_groups, self.__lock)
                    for group, dataframe in partitions.items()
                ],
            )

            # Avoid keeping things in memory
            del partitions

    def process_and_generate_result_file(self) -> Path:
        """
        Processes the temporary files and generates the result file.

        This method creates a query for each temporary file, executes the queries in parallel,
        and appends the query results to the result file.

        Returns:
            Path: The path to the result file.
        """
        queries = [
            pl.scan_csv(file, dtypes=self._get_dtypes(engine="polars"))
            .groupby("Song", "Date")
            .agg(pl.sum("Number of Plays"))
            for file in glob.glob(f"{self.__tmp_dir}/*.csv")
        ]

        output_file = helpers.make_output_file_path(output_dir=self.output_dir, file_name=self.task.id)
        with open(output_file, "a") as f:
            # Write the output csv headers
            f.write("Song,Date,Total Number of Plays for Date\n")

            helpers.execute_in_thread_pool(
                helpers.write_rows_to_an_opened_file,
                [(query.collect().write_csv(file=None, has_header=False), f, self.__lock) for query in queries],
            )

        return output_file

    def update_task(
        self,
        status: TaskStatus | None = None,
        output_file_path: Path | str | None = None,
        errors: ErrorsDict | None = None,
    ) -> None:
        """
        Updates the task with the provided parameters.

        Args:
            status (TaskStatus | None, optional): The status of the task. Defaults to None.
            output_file_path (Path | str | None, optional): The path to the output file. Defaults to None.
            errors (ErrorsDict | None, optional): The dictionary containing error messages. Defaults to None.
        """
        task_has_changes = status is not None or output_file_path is not None or errors is not None
        if task_has_changes:
            if status:
                self.task.status = status

            if output_file_path:
                output_file_path = str(output_file_path) if isinstance(output_file_path, Path) else output_file_path
                self.task.output_file_path = output_file_path

            if errors:
                if self.task.errors is None:
                    self.task.errors = errors
                else:
                    self.task.errors.update(errors)

            self.task = self.dao.update_task(self.task)

    @staticmethod
    def _get_dtypes(*, engine: Literal["pandas", "polars"]) -> Dict[str, Any] | None:
        """
        Returns the data types dictionary based on the engine.

        Args:
            engine (Literal["pandas", "polars"]): The data processing engine.

        Returns:
            Dict[str, Any] | None: The dictionary of column names and their data types.
        """
        df_columns = ("Song", "Date", "Number of Plays")
        pandas_dtypes = ("category", "category", "uint32")
        polars_dtypes = (pl.Categorical, pl.Categorical, pl.UInt32)

        if engine == "pandas":
            return dict(zip(df_columns, pandas_dtypes))

        if engine == "polars":
            return dict(zip(df_columns, polars_dtypes))

        logger.warning(
            "No 'engine' argument while calling '_get_dtypes()', returning None.\n"
            "Setting 'dtypes' to None while reading DataFrames may lead to unecessary memory usage or even errors."
        )
        return None

    def __enter__(self):
        return self

    def __exit__(self, exc, exc_val, exc_tb):
        if exc is not None:
            if isinstance(exc, ProcessingError):
                errors = exc.errors

            else:
                logger.error(f"{exc_val}. For more information, check the DEBUG level log.")
                logger.debug(traceback.format_exc())
                errors = {"error": "Something went wrong while processing the csv file."}

            self.update_task(status=TaskStatus.FAILED, errors=errors)

        helpers.remove_tmp_dir_and_files(self.__tmp_dir)
        return True
