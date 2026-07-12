import time
from typing import Any

import requests

from processor.commons.logger import log


def http_get(
    url: str,
    headers: dict[str, str] | None = None,
    timeout: float = 10.0,
    max_retries: int = 3,
    backoff: float = 2.0,
    is_xml: bool = False,
) -> Any | None:
    """
    Performs an HTTP GET request with retry logic, exponential backoff, and logging.

    Args:
        url: The URL to fetch.
        headers: Optional HTTP headers to include in the request.
        timeout: Request timeout in seconds.
        max_retries: Maximum number of request attempts.
        backoff: Multiplier for exponential backoff sleep duration.
        is_xml: If True, returns raw bytes content (e.g. for XML parsing).
                If False, returns parsed JSON object (dict/list).

    Returns:
        The response content (parsed JSON or raw bytes) or None if the request failed.
    """
    request_headers = {"User-Agent": "Mozilla/5.0"}
    if headers:
        request_headers.update(headers)

    for attempt in range(1, max_retries + 1):
        try:
            resp = requests.get(url, headers=request_headers, timeout=timeout)
            resp.raise_for_status()
            if is_xml:
                return resp.content
            return resp.json()
        except Exception as e:
            log.warning(f"Attempt {attempt}/{max_retries} failed for {url}: {e}")
            if attempt < max_retries:
                time.sleep(backoff * attempt)
            else:
                log.error(f"Failed to fetch {url} after {max_retries} attempts.")
                raise e
    return None
