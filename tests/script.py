"""
Use this module to create large csv files to be processed by the application.

The output file will live in /tests/static/
"""

import time
from functools import wraps

import polars as pl


def log_elapsed_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        elapsed_time = time.time() - start_time
        elapsed_time_formatted = f"{elapsed_time:.3f}"
        print(f"Elapsed time for {func.__name__}: {elapsed_time_formatted} seconds")
        return result

    return wrapper


def shorten_number(number):
    units = ["", "k", "M", "B", "T"]

    num_digits = len(str(number))
    unit_index = (num_digits - 1) // 3

    shortened_value = number / 10 ** (unit_index * 3)

    shortened_value = f"{shortened_value:.0f}{units[unit_index]}"
    return shortened_value.replace(".", "_")


@log_elapsed_time
def create_larger_csv_file(n: int = 1000):
    """A file with 100M (n=1000) lines will have around 3.38Gb"""

    base_sample_file = "static/100k_sample.csv"
    final_sample_file = f"static/{shorten_number(100_000 * n)}_sample.csv"
    dtypes = {"Song": pl.Categorical, "Date": pl.Categorical, "Number of Plays": pl.UInt32}
    df = pl.scan_csv(base_sample_file, dtypes=dtypes, infer_schema_length=0)

    # Keep in mind that the sample file have 100k rows, so the final file will have 100_000 * n rows.
    df = pl.concat([df] * n)

    df.collect(streaming=True).write_csv(final_sample_file, has_header=True, batch_size=100_000)


if __name__ == "__main__":
    create_larger_csv_file()
