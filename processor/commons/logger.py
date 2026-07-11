import logging

from rich.logging import RichHandler

FORMAT = "%(message)s"
logging.basicConfig(
    level="INFO",
    format=FORMAT,
    datefmt="[%X]",
    handlers=[
        RichHandler(
            markup=True, highlighter=None, rich_tracebacks=True, show_path=False
        )
    ],
)

log = logging.getLogger("rich")
