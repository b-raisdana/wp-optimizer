import datetime
import functools
import time
import traceback
from datetime import datetime
from enum import Enum




class LogSeverity(Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"

def log(log_message: str, severity: LogSeverity = LogSeverity.INFO, stack_trace: bool = True) -> None:
    """
    Log a message with an optional severity level and stack trace.

    Args:
        log_message (str): The message to be logged.
        severity (LogSeverity, optional): The severity level of the log message. Defaults to LogSeverity.WARNING.
        stack_trace (bool, optional): Whether to include a stack trace in the log message. Defaults to True.

    Returns:
        None
    """
    print(f'{severity.value}@{datetime.now().strftime("%m-%d.%H:%M:%S")}#{log_message}')
    if stack_trace:
        stack = traceback.extract_stack(limit=2 + 1)[:-1]  # Remove the last item
        traceback.print_list(stack)


def measure_time(func):
    @functools.wraps(func)
    def _measure_time(*args, **kwargs):
        """
        Measure the execution time of a function and log the start and end times.

        Args:
            *args: Positional arguments to be passed to the wrapped function.
            **kwargs: Keyword arguments to be passed to the wrapped function.

        Returns:
            result: The result of the wrapped function.
        """
        start_time = time.time()
        function_parameters = (", ".join(
            [
                'list...' if isinstance(arg, list)
                else str(arg)
                for arg in args
            ] +
            [
                f'{k}:list...' if isinstance(kwargs[k], list)
                else f'{k}:{kwargs[k]}'
                for k in kwargs.keys()
            ]))
        log(f"{func.__name__}({function_parameters}) started", stack_trace=False)
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        log(f"{func.__name__}({function_parameters}) executed in {execution_time:.3f} seconds", stack_trace=False)
        return result

    return _measure_time
