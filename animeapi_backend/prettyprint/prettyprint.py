"""
SPDX-License-Identifier: MIT

A module for pretty printing the program's proccess
"""

from datetime import datetime

from prettyprint.enums import Platform, Status
from prettyprint.color_utils import translate_hex_to_rgb


class PrettyPrint:
    """Pretty print for the proccess"""

    def __init__(self, show_date: bool = True, show_time: bool = True) -> None:
        """
        Initialize the pretty print class

        :param show_date: Show the date, defaults to True
        :type show_date: bool, optional
        :param show_time: Show the time, defaults to True
        :type show_time: bool, optional
        """
        self.show_date = show_date
        self.show_time = show_time
        self.previously_clear = False

    @staticmethod
    def _get_date() -> str:
        """
        Get the date

        :return: The date
        :rtype: str
        """
        # example: Jun 31
        return datetime.now().strftime("%b %d")

    @staticmethod
    def _get_time() -> str:
        """
        Get the time

        :return: The time
        :rtype: str
        """
        # example: 12:00:00 AM
        return datetime.now().strftime("%I:%M:%S %p")

    def _format_date(self) -> str:
        """
        Format the data

        :return: The formatted date
        :rtype: str
        """
        date = f"\033[104m {self._get_date()} \033[0m " if self.show_date else ""
        time = f"\033[104m {self._get_time()} \033[0m " if self.show_time else ""
        return f"{date}{time}"

    def _format_to_hex(self, enums: Platform | Status) -> str:
        """
        Format the text block to hex
        
        :param enums: The enum to be formatted
        :type enums: Platform | Status
        :return: The formatted text block
        :rtype: str
        """
        col = translate_hex_to_rgb(enums.value)
        sp = "  "
        if isinstance(enums, Platform):
            sp = " "
        return f"\033[48;2;{col[0]};{col[1]};{col[2]}m{sp}{enums.name}{sp}\033[0m"

    def string(self,
               platform: Platform,
               status: Status,
               *args: str,
               clean_line: bool = False,
               end: str = "\n",
               sep: str = " ",) -> str:
        """
        Format the string

        :param platform: The platform to be used
        :type platform: Platform
        :param status: The status to be used
        :type status: Status
        :param args: The arguments to be printed
        :type args: str
        :param clean_line: Clean the line, defaults to False
        :type clean_line: bool, optional
        :param end: The end character, defaults to "\\n"
        :type end: str, optional
        :param sep: The separator, defaults to " "
        :type sep: str, optional
        :raises ValueError: clean_line and end cannot be used together
        :return: The formatted string
        :rtype: str
        """
        if clean_line and end == "\n":
            raise ValueError("clean_line and end cannot be used together")
        anullen = ""
        if clean_line:
            anullen = "\033[2K\r"
            self.previously_clear = True
        elif self.previously_clear:
            anullen = "\n"
            self.previously_clear = False
        cr_ = "\r" if end == "" else ""
        message = sep.join(args)
        return f"{anullen}{cr_}{self._format_date()}{self._format_to_hex(platform)} {self._format_to_hex(status)} {message}"

    def print(self,
              platform: Platform,
              status: Status,
              *args: str,
              clean_line: bool = False,
              end: str = "\n",
              sep: str = " ") -> None:
        """
        Print the formatted string

        :param platform: The platform to be used
        :type platform: Platform
        :param status: The status to be used
        :type status: Status
        :param args: The arguments to be printed
        :type args: str
        :param clean_line: Clean the line, defaults to False
        :type clean_line: bool, optional
        :param end: The end character, defaults to "\\n"
        :type end: str, optional
        :param sep: The separator, defaults to " "
        :type sep: str, optional
        """
        print(self.string(platform,
                          status,
                          *args,
                          clean_line=clean_line,
                          end=end,
                          sep=sep),
              end=end)
