"""
SPDX-License-Identifier: MIT

Pretty print for the proccess
"""

from datetime import datetime
from enum import Enum


class Platform(Enum):
    """Platform color to be used for pretty printing."""

    ALLCINEMA = 0xEC0A0A
    ANIDB = 0x2A2F46
    ANILIST = 0x2F80ED
    ANIMEPLANET = 0xE75448
    ANISEARCH = 0xFDA37C
    ANIMENEWSNETWORK = 0x2D50A7
    ANNICT = 0xF65B73
    FRIBB = 0x212121
    HIKKA = 0xA284E3
    IMDB = 0xF5C518
    KAIZE = 0x692FC2
    KITSU = 0xF85235
    LETTERBOXD = 0x00D735
    LIVECHART = 0x67A427
    MYANIMELIST = 0x2F51A3
    NAUTILJON = 0x3C5891
    NOTIFY = 0xDEA99E
    OTAKOTAKU = 0xBE2222
    SHIKIMORI = 0x2E2E2E
    SHOBOI = 0xE3F0FD
    SILVERYASHA = 0x0172BB
    SIMKL = 0x0B0F10
    SYOBOI = 0xE3F0FD
    TMDB = 0x09B4E2
    TVDB = 0x6CD491
    TVTIME = 0xFBD737
    SYSTEM = 0x000000
    ARM = 0x222222
    ANIMEOFFLINEDATABASE = 0x101010
    ANITRAKT = 0xED1C24
    GECKYZZ = 0x4CAF50


class Status(Enum):
    """
    Status color to be used for pretty printing.

    Supported status:
        - Pass
        - Fail
        - Err
        - Warn
        - Info
        - Debug
        - Notice
        - Log
        - Ready
        - Assert
    """

    # Use Hex color codes instead of ANSI color codes
    PASS = 0x2ECC71
    FAIL = 0xE74C3C
    ERR = 0xFF0000
    WARN = 0xFFA500
    INFO = 0x3498DB
    DEBUG = 0xBFBFBF
    LOG = 0x1A1A1A
    READY = 0x228B22
    NOTICE = 0x1E90FF
    ASSERT = 0x808080
    BUILD = 0x4B0082


def translate_hex_to_rgb(hex_: int) -> tuple[int, int, int]:
    """Translate hex to rgb"""
    return ((hex_ >> 16) & 0xFF, (hex_ >> 8) & 0xFF, hex_ & 0xFF)


def calculate_contrast_ratio(r: int, g: int, b: int) -> float:
    """
    Calculate WCAG contrast ratio between RGB color and white text.
    Uses relative luminance formula.

    :param r: Red component (0-255)
    :param g: Green component (0-255)
    :param b: Blue component (0-255)
    :return: Contrast ratio (higher = more contrast)
    """
    # Normalize to 0-1
    r_norm = r / 255.0
    g_norm = g / 255.0
    b_norm = b / 255.0

    # Calculate relative luminance
    def adjust_channel(c: float) -> float:
        if c <= 0.03928:
            return c / 12.92
        return ((c + 0.055) / 1.055) ** 2.4

    r_lum = adjust_channel(r_norm)
    g_lum = adjust_channel(g_norm)
    b_lum = adjust_channel(b_norm)

    luminance = 0.2126 * r_lum + 0.7152 * g_lum + 0.0722 * b_lum

    # White has luminance of 1.0, black has 0.0
    white_luminance = 1.0
    black_luminance = 0.0

    # Contrast ratio = (L1 + 0.05) / (L2 + 0.05), where L1 > L2
    contrast_white = (white_luminance + 0.05) / (luminance + 0.05)
    contrast_black = (luminance + 0.05) / (black_luminance + 0.05)

    return contrast_white if contrast_white > contrast_black else contrast_black


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
        Format the date and time with contrast-aware text color.

        :return: The formatted date
        :rtype: str
        """
        # Use RGB color for date/time background (blue: 52, 152, 219)
        # Same as Status.INFO color for consistency
        bg_color = "48;2;52;152;219"  # INFO blue
        text_color = "38;2;255;255;255"  # White text (good contrast)

        date = (
            f"\033[{bg_color};{text_color}m {self._get_date()} \033[0m "
            if self.show_date
            else ""
        )
        time = (
            f"\033[{bg_color};{text_color}m {self._get_time()} \033[0m "
            if self.show_time
            else ""
        )
        return f"{date}{time}"

    def _format_to_hex(self, enums: Platform | Status) -> str:
        """
        Format the text block to hex with contrast-aware text color.
        Uses white text by default, switches to black if contrast is poor.

        :param enums: The enum to be formatted
        :type enums: Platform | Status
        :return: The formatted text block
        :rtype: str
        """
        col = translate_hex_to_rgb(enums.value)
        sp = "  "
        if isinstance(enums, Platform):
            sp = " "

        # Calculate contrast and choose text color
        contrast = calculate_contrast_ratio(col[0], col[1], col[2])
        # Use white (255,255,255) if contrast is good (>4.5), otherwise black (0,0,0)
        text_color = "38;2;255;255;255" if contrast > 4.5 else "38;2;0;0;0"

        return f"\033[48;2;{col[0]};{col[1]};{col[2]};{text_color}m{sp}{enums.name}{sp}\033[0m"

    def print(
        self,
        platform: Platform,
        status: Status,
        *args: str,
        clean_line: bool = False,
        end: str = "\n",
        sep: str = " ",
    ) -> None:
        """
        Print the data

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
        print(
            f"{anullen}{cr_}{self._format_date()}{self._format_to_hex(platform)} {self._format_to_hex(status)} {message}",
            end=end,
        )


__all__ = ["PrettyPrint", "Platform", "Status"]
