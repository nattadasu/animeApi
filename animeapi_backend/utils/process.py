import sys
from time import time

from animeapi_backend.utils.clock import convert_float_to_time
from animeapi_backend.config.const import PPRINT
from animeapi_backend.prettyprint import Platform, Status

def proc_stop(start_time: float,
              status: Status,
              message: str | None = None,
              exit_code: int = 0,
              show_traceback: bool = False) -> None:
    """
    Show message and exit from program

    :param start_time: start time
    :type start_time: float
    :param status: status
    :type status: Status
    :param message: message, defaults to None
    :type message: str, optional
    :param exit_code: exit code, defaults to 0
    :type exit_code: int, optional
    :param show_traceback: show traceback, defaults to False
    :type show_traceback: bool, optional
    :return: None
    :rtype: None
    """
    end_time = time()
    subtract_time = end_time - start_time
    context = convert_float_to_time(subtract_time)
    print()
    PPRINT.print(Platform.SYSTEM,
                 Status.INFO,
                 f"Generator finished in {context}")
    if message:
        PPRINT.print(Platform.SYSTEM, status, message)
    if show_traceback:
        import traceback
        traceback.print_exc()
    sys.exit(exit_code)
