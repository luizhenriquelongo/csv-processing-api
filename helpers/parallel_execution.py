import concurrent.futures
from typing import Callable, List, Tuple


def execute_in_thread_pool(fn: Callable, args_list: List[Tuple]) -> None:
    """
    Executes the given function in a thread pool with the provided arguments list.

    Args:
        fn (Callable): The function to be executed in the thread pool.
        args_list (List[Tuple]): The list of argument tuples to be passed to the function.

    Raises:
        Exception: If any of the futures in the thread pool raises an exception.

    Returns:
        None: This function does not return anything.

    Example:
        >>> def sum_numbers(x, y):
        ...     return x + y
        >>> execute_in_thread_pool(sum_numbers, [(2, 3), (4, 5), (6, 7)])
    """
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(fn, *args) for args in args_list]
        concurrent.futures.wait(futures, return_when=concurrent.futures.FIRST_EXCEPTION)

        for future in futures:
            if future.exception() is not None:
                raise future.exception()
