import shutil
import threading
from pathlib import Path
from typing import Literal, TextIO, Tuple

from polars import DataFrame

import helpers.strings as string_helper


def write_rows_to_an_opened_file(rows: str, file: TextIO, lock: threading.Lock) -> None:
    """
    Write the given rows to the specified file object while ensuring thread safety using the provided lock.

    Args:
        rows (str): The rows to be written to the file.
        file (TextIO): The file object to write to.
        lock (threading.Lock): The lock object to ensure thread safety.

    Returns:
        None
    """
    with lock:
        file.write(rows)


def write_dataframe_to_file(
    dataframe: DataFrame,
    file: Path | str | TextIO,
    lock: threading.Lock,
    has_header: bool = False,
    batch_size: int = 100_000,
) -> None:
    """
    Write a pandas DataFrame to a file.

    Args:
        dataframe (DataFrame): The DataFrame to write to the file.
        file (Union[Path, str, TextIO]): The file to write to. It can be a file path (str or pathlib.Path) or a
            file object (io.TextIO).
        lock (threading.Lock): The lock object to ensure thread safety when writing to the file.
        has_header (bool, optional): Whether the file has a header row. Defaults to False.
        batch_size (int, optional): The number of rows to write at a time. Defaults to 100,000.

    Returns:
        None

    Raises:
        TypeError: If the file parameter is not a str, pathlib.Path, or io.TextIO object.

    Example:
        >>> write_dataframe_to_file(df, 'output.csv', has_header=True, lock=lock)

    """
    if not isinstance(file, (Path, str, TextIO)):
        raise TypeError("'file' must be of a str, pathlib.Path, or io.TextIO")

    rows = dataframe.write_csv(file=None, has_header=has_header, batch_size=batch_size)
    if isinstance(file, TextIO):
        write_rows_to_an_opened_file(rows, file, lock)

    else:
        with open(file, "a") as f:
            write_rows_to_an_opened_file(rows, f, lock)


def save_dataframe_to_group_file(
    group: str | Tuple[str, str],
    dataframe: DataFrame,
    base_path: Path,
    seen_groups: set,
    lock: threading.Lock,
) -> None:
    """
    Save a DataFrame to a group file based on the specified group. The group can be a string or a tuple of strings.

    Args:
        group (str | Tuple[str, str]): The group identifier.
        dataframe (DataFrame): The DataFrame to be saved.
        base_path (Path): The base path where the group files will be saved.
        seen_groups (set): A set to keep track of seen groups to determine if a header should be added.
        lock (threading.Lock): The lock object to ensure thread safety when writing to the file.

    Returns:
        None
    """
    if isinstance(group, tuple):
        group = "".join(group)

    file_name = string_helper.remove_non_alphanumeric_chars(group)
    has_header = group not in seen_groups
    write_dataframe_to_file(dataframe, file=base_path / f"{file_name}.csv", has_header=has_header, lock=lock)

    seen_groups.add(group)


def make_output_file_path(
    base_dir: Path | str, output_dir: str, file_name: str, file_format: Literal["csv"] = "csv"
) -> Path:
    """
    Create the full path to the output file based on the provided base directory, output directory, file name,
    and file format.

    Args:
        base_dir (Path | str): The base directory for the output file. It can be a Path object or a string.
        output_dir (str): The directory where the output file will be saved.
        file_name (str): The name of the output file.
        file_format (Literal["csv"], optional): The file format. Defaults to "csv".

    Returns:
        Path: The full path to the output file.

    Example:
        >>> file_path = make_output_file_path(base_dir='/usr/app/ ', output_dir='static/outputs', file_name='some_file')
        >>> print(file_path)
        'usr/app/static/outputs/some_file.csv'
    """
    if not isinstance(base_dir, Path):
        base_dir = Path(base_dir).resolve()

    base_file_path = base_dir / output_dir
    # Make sure to create the whole directory path if the does not exist
    base_file_path.mkdir(parents=True, exist_ok=True)

    return base_file_path / f"{file_name}.{file_format}"


def remove_tmp_dir_and_files(directory: Path | str) -> None:
    """
    Remove the temporary directory and all files within it.

    Args:
        directory (Path | str): The directory to be removed.

    Returns:
        None
    """
    shutil.rmtree(directory)


def enforce_directory_creation(directory: Path) -> None:
    """
    Create the specified directory if it does not already exist.

    Args:
        directory (Path): The directory to be created.

    Returns:
        None
    """
    directory.mkdir(parents=True, exist_ok=True)
