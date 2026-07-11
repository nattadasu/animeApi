from pathlib import Path

import requests
from rich.progress import (
    BarColumn,
    DownloadColumn,
    Progress,
    TextColumn,
    TimeRemainingColumn,
    TransferSpeedColumn,
)


def download_file(url: str, dest_path: Path) -> Path:
    """
    Downloads a file from a URL to a destination path showing a rich progress bar.

    Args:
        url: The URL of the file to download.
        dest_path: The local destination file path.

    Returns:
        The destination Path object.
    """
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    # Send head request or stream requests to get content length
    response = requests.get(url, stream=True)
    response.raise_for_status()

    total_size = int(response.headers.get("content-length", 0))
    chunk_size = 1024 * 16  # 16KB chunks

    progress = Progress(
        TextColumn("[bold blue]{task.description}"),
        BarColumn(bar_width=40),
        "[progress.percentage]{task.percentage:>3.1f}%",
        "•",
        DownloadColumn(binary_units=True),
        "•",
        TransferSpeedColumn(binary_units=True),
        "•",
        TimeRemainingColumn(),
    )

    with progress:
        task_id = progress.add_task(f"Downloading {dest_path.name}", total=total_size)
        with open(dest_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
                    progress.update(task_id, advance=len(chunk))

    return dest_path
