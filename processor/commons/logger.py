import logging
from datetime import datetime
from enum import Enum

from rich.logging import RichHandler
from rich.progress import ProgressColumn
from rich.text import Text

FORMAT = "%(message)s"
handler = RichHandler(
    show_time=False,
    show_level=False,
    show_path=False,
    markup=True,
    rich_tracebacks=True,
)
handler.highlighter = None

logging.basicConfig(
    level="INFO",
    format=FORMAT,
    handlers=[handler],
)


class Status(Enum):
    INFO = ("INFO", "#3498DB", "white")
    WARNING = ("WARN", "#FFA500", "white")
    ERROR = ("ERROR", "#E74C3C", "white")
    CRITICAL = ("FATAL", "#FF0000", "white")
    DEBUG = ("DEBUG", "#BFBFBF", "black")

    def __init__(self, status_name: str, bg_color: str, fg_color: str):
        self.status_name = status_name
        self.bg_color = bg_color
        self.fg_color = fg_color

    @classmethod
    def from_levelname(cls, levelname: str) -> "Status":
        if levelname == "INFO":
            return cls.INFO
        if levelname == "WARNING":
            return cls.WARNING
        if levelname == "ERROR":
            return cls.ERROR
        if levelname == "CRITICAL":
            return cls.CRITICAL
        return cls.DEBUG

    def to_tag(self) -> str:
        return f"[on {self.bg_color} {self.fg_color}] {self.status_name:^5} [/]"


class Platform(Enum):
    ANIDB = ("ANIDB", "#2A2F46", "white")
    SHOKO = ("SHOKO", "#279ceb", "white")
    ANIDUMP = ("ANIDUMP", "#16161a", "white")
    DATABASE = ("DATABASE", "#4CAF50", "black")
    HTTP = ("HTTP", "#9C27B0", "white")
    ANILIST = ("ANILIST", "#3db4f2", "white")
    SYSTEM = ("SYSTEM", "#757575", "white")

    def __init__(self, platform_name: str, bg_color: str, fg_color: str):
        self.platform_name = platform_name
        self.bg_color = bg_color
        self.fg_color = fg_color

    @classmethod
    def from_pathname(cls, pathname: str) -> "Platform":
        if "shoko" in pathname:
            return cls.SHOKO
        if "anidb" in pathname:
            return cls.ANIDB
        if "anilist" in pathname:
            return cls.ANILIST
        if "anidump" in pathname:
            return cls.ANIDUMP
        if "manager.py" in pathname or "/db/" in pathname:
            return cls.DATABASE
        if "http.py" in pathname:
            return cls.HTTP
        return cls.SYSTEM

    def to_tag(self) -> str:
        return f"[on {self.bg_color} {self.fg_color}] {self.platform_name} [/]"


class PlatformFilter(logging.Filter):
    """A logging filter that prepends the timestamp, status, and platform detail (with colors) to the log message."""

    def filter(self, record: logging.LogRecord) -> bool:
        platform = Platform.from_pathname(record.pathname)
        status = Status.from_levelname(record.levelname)
        time_str = datetime.now().strftime("%X")
        time_tag = f"[on #3498DB white] {time_str} [/]"
        record.msg = f"{time_tag} {status.to_tag()} {platform.to_tag()} {record.msg}"
        return True


log = logging.getLogger("rich")
log.addFilter(PlatformFilter())


class TimeColumn(ProgressColumn):
    """A progress bar column that displays the current local time in the same format and style as the rich log handler."""

    def render(self, task) -> Text:
        time_str = datetime.now().strftime("%X")
        return Text.from_markup(f"[on #3498DB white] {time_str} [/]")
