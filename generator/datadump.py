import json
import requests as req
from typing import Any, Union

from fake_useragent import FakeUserAgent  # type: ignore

from prettyprint import PrettyPrint, Platform, Status


pprint = PrettyPrint()
fua = FakeUserAgent(browsers=["firefox", "chrome", "edge", "safari"])
rand_fua: str = f"{fua.random}"  # type: ignore


class DataDump:
    """Dump data to json file"""

    def __init__(self, url: str, file_name: str, file_type: str = "json") -> None:
        """Initialize the DataDump class"""
        self.url = url
        self.file_name = file_name
        self.file_type = file_type
        pprint.print(
            Platform.SYSTEM,
            Status.READY,
            "DataDump ready to use",
        )

    def _get(self) -> Union[req.Response, None]:
        """Get the response from the url"""
        headers = {
            "User-Agent": rand_fua,
        }
        try:
            response = req.get(self.url, headers=headers, timeout=15)
            if response.status_code == 200:
                return response
            return None
        except Exception as err:
            pprint.print(Platform.SYSTEM, Status.ERR, f"Error: {err}")
            return None

    def dumper(self) -> None:
        """Dump the data to json file"""
        response = self._get()
        if response:
            if self.file_type == "json":
                with open(f"database/raw/{self.file_name}.json", "w", encoding="utf-8") as file:
                    json.dump(response.json(), file, indent=4)
            else:
                with open(f"database/raw/{self.file_name}.txt", "w", encoding="utf-8") as file:
                    file.write(response.text)
            pprint.print(
                Platform.SYSTEM,
                Status.PASS,
                f"Data dumped to {self.file_name}.{self.file_type}",
            )

    def loader(self) -> Any:
        """Load the data from json file"""
        if self.file_type == "json":
            with open(f"database/raw/{self.file_name}.json", "r", encoding="utf-8") as file:
                return json.load(file)
        else:
            with open(f"database/raw/{self.file_name}.txt", "r", encoding="utf-8") as file:
                return file.read()
