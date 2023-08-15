import json
import requests as req
from typing import Any, Union, Literal

from fake_useragent import FakeUserAgent  # type: ignore

from prettyprint import PrettyPrint, Platform, Status


pprint = PrettyPrint()
fua = FakeUserAgent(browsers=["firefox", "chrome", "edge", "safari"])
rand_fua: str = f"{fua.random}"  # type: ignore


class DataDump:
    """Dump data to json file"""

    def __init__(self, url: str, file_name: str, file_type: Literal["json", "txt"] = "json") -> None:
        """Initialize the DataDump class"""
        self.url = url
        self.file_name = file_name
        self.file_type = file_type

    def _get(self) -> Union[req.Response, None]:
        """Get the response from the url"""
        headers = {
            "User-Agent": rand_fua,
        }
        try:
            # raise ConnectionError("Force use local file")
            response = req.get(self.url, headers=headers, timeout=None)
            if response.status_code == 200:
                return response
            return None
        except Exception as err:
            pprint.print(Platform.SYSTEM, Status.ERR, f"Error: {err}")
            return None

    def dumper(self) -> Any:
        """Dump the data to json file"""
        response = self._get()
        if response:
            content = response.json() if self.file_type == "json" else response.text
            if self.file_type == "json":
                with open(f"database/raw/{self.file_name}.json", "w", encoding="utf-8") as file:
                    json.dump(content, file)
            else:
                with open(f"database/raw/{self.file_name}.txt", "w", encoding="utf-8") as file:
                    file.write(content)
            return content
        else:
            pprint.print(
                Platform.SYSTEM,
                Status.ERR,
                "Failed to dump data, loading from local file",
            )
            return self.loader()

    def loader(self) -> Any:
        """Load the data from json file"""
        try:
            if self.file_type == "json":
                with open(f"database/raw/{self.file_name}.json", "r", encoding="utf-8") as file:
                    return json.load(file)
            else:
                with open(f"database/raw/{self.file_name}.txt", "r", encoding="utf-8") as file:
                    return file.read()
        # file not found
        except FileNotFoundError:
            pprint.print(
                Platform.SYSTEM,
                Status.ERR,
                "Failed to load data, please download the data first, or check your internet connection",
            )
            raise SystemExit
