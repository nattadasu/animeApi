# SPDX-License-Identifier: MIT

import json
from typing import Any, Literal, Union

import cloudscraper # type: ignore
from prettyprint import Platform, PrettyPrint, Status
from requests import Response

pprint = PrettyPrint()


class Downloader:
    """Download json file"""

    def __init__(
        self,
        url: str,
        file_name: str,
        file_type: Literal["json", "txt"] = "json",
        platform: Platform = Platform.SYSTEM,
    ) -> None:
        """
        Initialize the Downloader class

        :param url: The url to download the json file
        :type url: str
        :param file_name: The name of the file
        :type file_name: str
        :param file_type: The type of the file, defaults to "json"
        :type file_type: Literal["json", "txt"], optional
        :param platform: The platform to print the message, defaults to Platform.SYSTEM
        :type platform: Platform, optional
        """
        self.url = url
        self.file_name = file_name
        self.file_type = file_type
        self.platform = platform
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

    def _get(self) -> Union[Response, None]:
        """
        Get the response from the url

        :return: The response from the url
        :rtype: Union[Response, None]
        """
        if not self.scrape:
            pprint.print(self.platform, Status.ERR, "Failed to create cloudscraper")
            return None
        response = self.scrape.get(self.url, timeout=None)
        try:
            # raise ConnectionError("Force use local file")
            if response.status_code != 200:
                raise ConnectionError(
                    f"{response.status_code}",
                    f"{response.reason}",
                )
            return response
        except ConnectionError as err:
            pprint.print(self.platform, Status.ERR, f"Error: {err}")
            return None

    def dumper(self) -> Any:
        """
        Dump the data to process

        :return: The data to process
        :rtype: Any
        """
        response = self._get()
        if response:
            content = response.json() if self.file_type == "json" else response.text
            if self.file_type == "json":
                with open(
                    f"database/raw/{self.file_name}.json", "w", encoding="utf-8"
                ) as file:
                    json.dump(content, file)
            else:
                with open(
                    f"database/raw/{self.file_name}.txt", "w", encoding="utf-8"
                ) as file:
                    file.write(content)
            pprint.print(
                self.platform,
                Status.PASS,
                f"Successfully download {self.file_name}.{self.file_type}",
            )
            return content
        else:
            pprint.print(
                self.platform,
                Status.ERR,
                "Failed to dump data, loading from local file",
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
                    f"database/raw/{self.file_name}.txt", "r", encoding="utf-8"
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
