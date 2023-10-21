"""
SPDX-License-Identifier: MIT

A module for handling HTTP requests
"""

import cloudscraper  # type: ignore
from fake_useragent import FakeUserAgent  # type: ignore
from requests import Response
from urllib.parse import urlencode
from typing import Any
from json import load, dump
from alive_progress import alive_bar  # type: ignore

from animeapi_backend.config.const import PPRINT, START_TIME
from animeapi_backend.config.variables import is_debug, is_verbose
from animeapi_backend.prettyprint import Platform, PrettyPrint, Status
from animeapi_backend.utils.process import proc_stop


USER_AGENT = str(FakeUserAgent(browsers=["chrome", "firefox"], os=[
                 "windows"]).random)  # type: ignore


class HTTPRequest:
    """HTTP request class"""

    def __init__(self,
                 user_agent: str = USER_AGENT,
                 headers: dict[str, Any] | None = None,
                 timeout: int | None = None,
                 platform: Platform = Platform.SYSTEM) -> None:
        """
        Initialize the HTTPRequest class

        :param user_agent: The user agent, defaults to USER_AGENT (chrome, firefox; windows) set in controller/httprequest.py
        :type user_agent: str, optional
        :param headers: The headers, defaults to None
        :type headers: dict[str, Any], optional
        :param timeout: The timeout, defaults to None
        :type timeout: int, optional
        :param platform: The platform to print the message, defaults to Platform.SYSTEM
        :type platform: Platform, optional
        """
        if headers is not None:
            self.headers: dict[str, Any] = headers
        # check if the user agent is set in the headers, if not apply the user agent
        # to the headers
        if headers is None:
            self.headers = {"User-Agent": user_agent}
        elif "User-Agent" not in headers or headers["User-Agent"] in ["", None]:
            self.headers["User-Agent"] = user_agent
        self.timeout = timeout
        self.platform = platform
        self.scrape = cloudscraper.create_scraper(  # type: ignore
            browser={"browser": "chrome",
                     "platform": "windows",
                     "mobile": False})
        if is_verbose:
            PPRINT.print(self.platform,
                         Status.NOTICE,
                         "HTTP request initialized")

    def get(self,
            url: str,
            param_query: dict[str, str | int] | None = None) -> Response:
        """
        Get the response from the url

        :param url: The url to get the response
        :type url: str
        :param param_query: The query params, defaults to None
        :type param_query: dict[str, str | int], optional
        :return: The response from the url
        :rtype: Response
        """
        if param_query is not None:
            url = f"{url}?{urlencode(param_query)}"
        if is_verbose:
            PPRINT.print(self.platform,
                         Status.NOTICE,
                         f"Getting response from {url}")
        print_str = PrettyPrint(False, False).string(
            self.platform,
            Status.INFO,
            "GET content",
            end=None)
        with alive_bar(100, title=print_str, spinner="dots_waves2") as bar:  # type: ignore
            response = self.scrape.get(url,
                                       headers=self.headers,
                                       timeout=self.timeout,
                                       stream=True)
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    bar()
        if is_debug:
            PPRINT.print(self.platform,
                         Status.NOTICE,
                         f"Response from {url} is {response}")
        return response

    def post(self,
             url: str,
             content_type: str = "application/json",
             data: dict[str, Any] | str | None = None) -> Response:
        """
        Post the data to the url

        :param url: The url to post the data
        :type url: str
        :param content_type: The content type, defaults to "application/json"
        :type content_type: str, optional
        :param data: The data to post, defaults to None
        :type data: dict[str, Any] | str, optional
        :return: The response from the url
        :rtype: Response
        """
        if is_verbose:
            PPRINT.print(self.platform,
                         Status.NOTICE,
                         f"Posting data to {url}")

        elif "Content-Type" not in self.headers or self.headers["Content-Type"] in ["", None]:
            self.headers["Content-Type"] = content_type
        elif self.headers["Content-Type"] != content_type:
            PPRINT.print(self.platform,
                         Status.NOTICE,
                         f"Content-Type changed from {self.headers['Content-Type']} to {content_type}! This may cause an error!")
            self.headers["Content-Type"] = content_type

        response = self.scrape.post(url,
                                    headers=self.headers,
                                    data=data,
                                    timeout=self.timeout)

        if is_debug:
            PPRINT.print(self.platform,
                         Status.NOTICE,
                         f"Response from {url} is {response}")

        return response

    @staticmethod
    def _local_load(file_name: str,
                    file_type: str) -> str | dict[str, Any]:  # type: ignore
        """
        Load the local data

        :param file_name: The name of the file
        :type file_name: str
        :param file_type: The type of the file
        :type file_type: str
        :return: The local data
        :rtype: str | dict[str, Any]
        """
        try:
            if file_type == "json":
                with open(f"database/raw/{file_name}.{file_type}", "r") as file:
                    return load(file)
            else:
                with open(f"database/raw/{file_name}.{file_type}", "r") as file:
                    return file.read()
        except FileNotFoundError:
            proc_stop(start_time=START_TIME,
                      status=Status.ERR,
                      message=f"File {file_name}.{file_type} not found!",
                      exit_code=1,
                      show_traceback=True)

    def download(self,
                 file_name: str,
                 file_type: str,
                 url: str,
                 param_query: dict[str, str | int] | None = None) -> str | dict[str, Any]:  # type: ignore
        """
        Download the data to process for better practice rather manually set
        the logic in the generator

        :param file_name: The name of the file
        :type file_name: str
        :param file_type: The type of the file
        :type file_type: str
        :param url: The url to download the data
        :type url: str
        :param param_query: The query params, defaults to None
        :type param_query: dict[str, str | int], optional
        """
        if is_verbose:
            PPRINT.print(self.platform,
                         Status.NOTICE,
                         f"Downloading {file_name}.{file_type} from {url}")

        response = self.get(url=url,
                            param_query=param_query)

        if response:
            content = response.json() if file_type == "json" else response.text
            if file_type == "json":
                with open(f"database/raw/{file_name}.{file_type}",
                          "w",
                          encoding="utf-8") as file:
                    dump(content, file)
            else:
                with open(f"database/raw/{file_name}.{file_type}",
                          "w",
                          encoding="utf-8") as file:
                    file.write(content)
            PPRINT.print(self.platform,
                         Status.PASS,
                         f"Successfully download {file_name}.{file_type}")
            return content
        else:
            PPRINT.print(self.platform,
                         Status.ERR,
                         f"Failed to download {file_name}.{file_type}, trying to load from local file")
            content = self._local_load(file_name=file_name,
                                       file_type=file_type)
            PPRINT.print(self.platform,
                         Status.PASS,
                         f"Successfully load {file_name}.{file_type} from local file")
            return content
