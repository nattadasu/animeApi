# SPDX-License-Identifier: MIT

import hashlib
import json
from typing import Any, Literal, Union

import cloudscraper  # type: ignore
import zstandard as zstd
from alive_progress import alive_bar
from prettyprint import Platform, PrettyPrint, Status
from requests import Response

pprint = PrettyPrint()


class Downloader:
    """Download json file"""

    def __init__(
        self,
        url: str,
        file_name: str,
        file_type: Literal["json", "txt", "zst", "tsv"] = "json",
        platform: Platform = Platform.SYSTEM,
        ignore_headers: bool = False,
    ) -> None:
        """
        Initialize the Downloader class

        :param url: The url to download the json file
        :type url: str
        :param file_name: The name of the file
        :type file_name: str
        :param file_type: The type of the file, defaults to "json"
        :type file_type: Literal["json", "txt", "zst", "tsv"], optional
        :param platform: The platform to print the message, defaults to Platform.SYSTEM
        :type platform: Platform, optional
        :param ignore_headers: Whether to ignore remote headers and force download if available, defaults to False
        :type ignore_headers: bool, optional
        """
        self.url = url
        self.file_name = file_name
        self.file_type = file_type
        self.platform = platform
        self.ignore_headers = ignore_headers
        self.scrape: cloudscraper.CloudScraper = cloudscraper.create_scraper(  # type: ignore
            browser={
                "browser": "chrome",
                "platform": "windows",
                "mobile": False,
            }
        )
        pprint.print(
            self.platform,
            Status.NOTICE,
            f"Prepare to download {self.file_name}.{self.file_type}",
        )

    def _format_size(self, size_bytes: int) -> str:
        """
        Format bytes to human-readable size with power of 2 units (MiB, GiB)

        :param size_bytes: Size in bytes
        :type size_bytes: int
        :return: Formatted string with units
        :rtype: str
        """
        for unit in ["B", "KiB", "MiB", "GiB", "TiB"]:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} PiB"

    def _get_stored_metadata(self) -> dict | None:
        """
        Load metadata from TSV file (.downloader.tsv).

        :return: Metadata dict or None if not found
        """
        try:
            with open("database/raw/.downloader.tsv", "r") as f:
                for line in f:
                    parts = line.strip().split("\t")
                    if parts and parts[0] == self.file_name:
                        return {
                            "etag": parts[1] if len(parts) > 1 and parts[1] else None,
                            "last-modified": parts[2]
                            if len(parts) > 2 and parts[2]
                            else None,
                            "content-length": parts[3]
                            if len(parts) > 3 and parts[3]
                            else None,
                            "hash": parts[4] if len(parts) > 4 and parts[4] else None,
                        }
            return None
        except FileNotFoundError:
            return None

    def _save_metadata(self, metadata: dict) -> None:
        """
        Save metadata to TSV file (.downloader.tsv).

        :param metadata: Metadata dict with ETag, Last-Modified, Content-Length, hash
        """
        try:
            # Read existing entries
            rows = {}
            try:
                with open("database/raw/.downloader.tsv", "r") as f:
                    next(f)  # Skip header
                    for line in f:
                        parts = line.strip().split("\t")
                        if parts and parts[0] != "filename":  # Skip if header
                            rows[parts[0]] = parts
            except FileNotFoundError:
                pass

            # Update/add this file's metadata
            rows[self.file_name] = [
                self.file_name,
                metadata.get("etag") or "",
                metadata.get("last-modified") or "",
                metadata.get("content-length") or "",
                metadata.get("hash") or "",
            ]

            # Write back all rows
            with open("database/raw/.downloader.tsv", "w") as f:
                f.write("filename\tetag\tlast-modified\tcontent-length\thash\n")
                for row in rows.values():
                    f.write("\t".join(row) + "\n")
        except Exception:
            pass  # Non-critical, silently ignore

    def _get_stored_etag(self) -> str | None:
        """
        Load previously stored ETag if available.

        :return: ETag string or None if not found
        """
        try:
            with open(f"database/raw/{self.file_name}.etag", "r") as f:
                return f.read().strip()
        except FileNotFoundError:
            return None

    def _save_etag(self, etag: str) -> None:
        """
        Save ETag to file for future comparisons.

        :param etag: ETag to save
        """
        try:
            with open(f"database/raw/{self.file_name}.etag", "w") as f:
                f.write(etag)
        except Exception:
            pass  # Non-critical, silently ignore

    def _check_remote_unchanged(self) -> bool:
        """
        Check if remote file is unchanged using ETag, Last-Modified, or Content-Length.
        Uses HTTP HEAD request (cheap, no download).
        Falls back to hash comparison if headers unavailable.

        :return: True if unchanged (should use cache), False if changed
        """
        if self.ignore_headers:
            return False
        try:
            # Use HEAD request to avoid downloading
            head_response = self.scrape.head(self.url, timeout=10)

            if head_response.status_code == 404:
                return False  # File doesn't exist, need to try download

            metadata = {
                "etag": head_response.headers.get("etag"),
                "last-modified": head_response.headers.get("last-modified"),
                "content-length": head_response.headers.get("content-length"),
            }

            stored = self._get_stored_metadata()

            # Check ETag (preferred, most reliable)
            # if metadata["etag"] and stored and stored.get("etag") == metadata["etag"]:
            #     pprint.print(
            #         self.platform,
            #         Status.NOTICE,
            #         f"Remote file unchanged (ETag match), using cached {self.file_name}.{self.file_type}",
            #     )
            #     return True

            # Check Last-Modified if no ETag
            if (
                metadata["last-modified"]
                and stored
                and stored.get("last-modified") == metadata["last-modified"]
            ):
                pprint.print(
                    self.platform,
                    Status.NOTICE,
                    f"Remote file unchanged (Last-Modified match), using cached {self.file_name}.{self.file_type}",
                )
                return True

            # Fallback for GitHub releases: check Content-Length + Last-Modified combo
            # (releases often update without changing size, so this is unreliable but better than nothing)
            if (
                metadata["content-length"]
                and stored
                and stored.get("content-length") == metadata["content-length"]
                and metadata["last-modified"]
                and stored.get("last-modified") == metadata["last-modified"]
            ):
                pprint.print(
                    self.platform,
                    Status.NOTICE,
                    f"Remote file unchanged (Content-Length + Last-Modified match), using cached {self.file_name}.{self.file_type}",
                )
                return True

            # Store new metadata for next time
            self._save_metadata(metadata)
            return False
        except Exception:
            # On any error, attempt download (fallback to hash check after)
            return False

    def _get(self) -> Union[Response, None]:
        """
        Get the response from the url with progress bar

        :return: The response from the url
        :rtype: Union[Response, None]
        """
        if not self.scrape:
            pprint.print(self.platform, Status.ERR, "Failed to create cloudscraper")
            return None

        try:
            # Stream the download to show progress
            response = self.scrape.get(self.url, timeout=None, stream=True)

            # raise ConnectionError("Force use local file")
            if response.status_code != 200:
                raise ConnectionError(
                    f"{response.status_code}",
                    f"{response.reason}",
                )

            # Get total file size
            total_size = int(response.headers.get("content-length", 0))

            if total_size > 0:
                block_size = 8192  # 8 KiB for smoother progress
                downloaded = 0
                chunks = []

                with alive_bar(
                    total_size,
                    title=f"Downloading {self.file_name}.{self.file_type}",
                    spinner=None,
                    unit="B",
                    scale="IEC",
                ) as bar:  # type: ignore
                    for chunk in response.iter_content(chunk_size=block_size):
                        if chunk:
                            chunks.append(chunk)
                            downloaded += len(chunk)
                            bar(len(chunk))  # type: ignore

                # Combine all chunks
                response._content = b"".join(chunks)
            else:
                # No content-length header, download without progress
                response._content = response.content

            # If zst file, save compressed bytes BEFORE decompression for hashing
            compressed_content = None
            if self.file_type == "zst":
                compressed_content = response._content
                pprint.print(
                    self.platform,
                    Status.NOTICE,
                    f"Decompressing {self.file_name}.zst",
                )
                dctx = zstd.ZstdDecompressor()
                # Use stream_reader for files without determinable content size
                decompressed = dctx.decompress(
                    response._content, max_output_size=2**31 - 1
                )
                response._content = decompressed
                pprint.print(
                    self.platform,
                    Status.PASS,
                    f"Successfully decompressed {self.file_name}.zst",
                )

            # Attach compressed bytes to response for later hashing
            response._compressed_content = compressed_content

            return response
        except ConnectionError as err:
            pprint.print(self.platform, Status.ERR, f"Error: {err}")
            return None

    def _compute_hash(self, data: str | bytes) -> str:
        """
        Compute SHA256 hash of data.

        :param data: Data to hash (str or bytes)
        :return: Hex digest of SHA256 hash
        """
        if isinstance(data, str):
            data = data.encode("utf-8")
        return hashlib.sha256(data).hexdigest()

    def _get_stored_hash(self) -> str | None:
        """
        Load previously stored hash if available.

        :return: Hash string or None if not found
        """
        try:
            with open(f"database/raw/{self.file_name}.hash", "r") as f:
                return f.read().strip()
        except FileNotFoundError:
            return None

    def _save_hash(self, data_hash: str) -> None:
        """
        Save hash to file for future comparisons.

        :param data_hash: Hash to save
        """
        try:
            with open(f"database/raw/{self.file_name}.hash", "w") as f:
                f.write(data_hash)
        except Exception:
            pass  # Non-critical, silently ignore

    def dumper(self) -> Any:
        """
        Dump the data to process with efficient caching.
        Checks remote file first (ETag/Last-Modified) before downloading.
        Falls back to hash-based verification if available.

        :return: The data to process
        :rtype: Any
        """
        # First, check if remote file is unchanged (cheap HEAD request)
        if not self.ignore_headers and self._check_remote_unchanged():
            try:
                if self.file_type == "json":
                    with open(
                        f"database/raw/{self.file_name}.json", "r", encoding="utf-8"
                    ) as f:
                        return json.load(f)
                else:
                    with open(
                        f"database/raw/{self.file_name}.{self.file_type}",
                        "r",
                        encoding="utf-8",
                    ) as f:
                        return f.read()
            except FileNotFoundError:
                pass  # Fall through to download

        # If remote check didn't skip, proceed with download
        response = self._get()
        if response:
            # For zst files, hash the raw compressed bytes BEFORE decompression
            if self.file_type == "zst":
                # Hash raw compressed bytes from _get()
                raw_hash_data = response._compressed_content
                pprint.print(
                    self.platform,
                    Status.NOTICE,
                    f"Computing local hash for {self.file_name}.{self.file_type} (raw compressed bytes)",
                )
                current_hash = self._compute_hash(raw_hash_data)
                stored_hash = self._get_stored_hash()

                if current_hash == stored_hash:
                    pprint.print(
                        self.platform,
                        Status.NOTICE,
                        f"ZST data unchanged (compressed hash match), using cached {self.file_name}.{self.file_type}",
                    )
                    # Already decompressed by _get(), just parse
                    content = json.loads(response._content.decode("utf-8"))
                    return content

                if stored_hash:
                    pprint.print(
                        self.platform,
                        Status.NOTICE,
                        f"ZST hash mismatch: stored={stored_hash[:8]}... vs current={current_hash[:8]}..., updating",
                    )

                # Already decompressed by _get()
                content = json.loads(response._content.decode("utf-8"))
                file_extension = "json"
                final_hash = current_hash
            else:
                content = response.json() if self.file_type == "json" else response.text
                file_extension = self.file_type
                # Compute hash based on content type
                raw_data = (
                    json.dumps(content, separators=(",", ":"))
                    if file_extension == "json"
                    else content
                )

                pprint.print(
                    self.platform,
                    Status.NOTICE,
                    f"Computing local hash for {self.file_name}.{self.file_type} (fallback verification)",
                )
                current_hash = self._compute_hash(raw_data)
                stored_hash = self._get_stored_hash()

                # Skip download if unchanged
                if current_hash == stored_hash:
                    pprint.print(
                        self.platform,
                        Status.NOTICE,
                        f"Data unchanged (local hash match), using cached {self.file_name}.{self.file_type}",
                    )
                    return content

                if stored_hash:
                    pprint.print(
                        self.platform,
                        Status.NOTICE,
                        f"Hash mismatch: stored={stored_hash[:8]}... vs current={current_hash[:8]}..., updating cache",
                    )

                final_hash = current_hash

            # Data changed, save it
            if file_extension == "json":
                with open(
                    f"database/raw/{self.file_name}.json", "w", encoding="utf-8"
                ) as file:
                    json.dump(content, file)
            else:
                with open(
                    f"database/raw/{self.file_name}.{file_extension}",
                    "w",
                    encoding="utf-8",
                ) as file:
                    file.write(content)

            # Save metadata from response headers
            metadata = {
                "etag": response.headers.get("etag"),
                "last-modified": response.headers.get("last-modified"),
                "content-length": response.headers.get("content-length"),
                "hash": final_hash,
            }
            self._save_metadata(metadata)
            pprint.print(
                self.platform,
                Status.PASS,
                f"Successfully downloaded {self.file_name}.{self.file_type}",
            )
            return content
        else:
            pprint.print(
                self.platform,
                Status.ERR,
                "Failed to download data, loading from local cache",
            )
            return self.loader()

    def loader(self) -> Any:
        """
        Load the data from a file

        :return: The data to process
        :rtype: Any
        """
        try:
            if self.file_type == "json":
                with open(
                    f"database/raw/{self.file_name}.json", "r", encoding="utf-8"
                ) as file:
                    return json.load(file)
            else:
                with open(
                    f"database/raw/{self.file_name}.{self.file_type}",
                    "r",
                    encoding="utf-8",
                ) as file:
                    return file.read()
        # file not found
        except FileNotFoundError:
            pprint.print(
                self.platform,
                Status.ERR,
                "Failed to load data, please download the data first, or check your internet connection",
            )
            raise SystemExit
