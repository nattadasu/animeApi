"""Pretty print for the proccess"""
from enum import Enum
from datetime import datetime

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
    IMDB = 0xF5C518
    KAIZE = 0x692FC2
    KITSU = 0xF85235
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


class PrettyPrint:
    """Pretty print for the proccess"""

    def __init__(self, show_date: bool = True, show_time: bool = True) -> None:
        """Initialize the pretty print class"""
        self.show_date = show_date
        self.show_time = show_time
        self.previously_clear = False

    @staticmethod
    def _get_date() -> str:
        """Get the date"""
        # example: Jun 31
        return datetime.now().strftime("%b %d")

    @staticmethod
    def _get_time() -> str:
        """Get the time"""
        # example: 12:00:00 AM
        return datetime.now().strftime("%I:%M:%S %p")

    def _format_date(self) -> str:
        """Format the data"""
        date = f"\033[104m {self._get_date()} \033[0m " if self.show_date else ""
        time = f"\033[104m {self._get_time()} \033[0m " if self.show_time else ""
        return f"{date}{time}"

    def _format_to_hex(self, enums: Platform | Status) -> str:
        """Format the platform"""
        col = translate_hex_to_rgb(enums.value)
        sp = "  "
        if isinstance(enums, Platform):
            sp = " "
        return f"\033[48;2;{col[0]};{col[1]};{col[2]}m{sp}{enums.name}{sp}\033[0m"

    def print(
        self,
        platform: Platform,
        status: Status,
        *args: str,
        clean_line: bool = False,
        end: str = "\n",
        sep: str = " ",
    ) -> None:
        """Print the data"""
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
