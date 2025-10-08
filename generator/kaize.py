# SPDX-License-Identifier: MIT

import json
import math
import re
import time
from typing import Any, Literal, Optional, Union

import requests as req
from alive_progress import alive_bar  # type: ignore
from bs4 import BeautifulSoup, Tag
from fake_useragent import FakeUserAgent  # type: ignore
from prettyprint import Platform, PrettyPrint, Status

pprint = PrettyPrint()
fua = FakeUserAgent(browsers=["firefox", "chrome", "edge", "safari"])
rand_fua: str = f"{fua.random}"  # type: ignore


class Kaize:
    """Kaize anime data scraper"""

    def __init__(
        self,
        session: Optional[str] = None,
        xsrf_token: Optional[str] = None,
        user_agent: Optional[str] = None,
        email: Optional[str] = None,
        password: Optional[str] = None,
    ) -> None:
        """
        Initialize the Kaize class

        :param session: The session, defaults to None
        :type session: Optional[str], optional
        :param xsrf_token: The XSRF token, defaults to None
        :type xsrf_token: Optional[str], optional
        :param user_agent: The user agent, defaults to None
        :type user_agent: Optional[str], optional
        :param email: The email, defaults to None
        :type email: Optional[str], optional
        :param password: The password, defaults to None
        :type password: Optional[str], optional
        """
        self.base_url = "https://kaize.io"
        self.session = req.Session()
        self.xsrf_token = xsrf_token
        self.csrf_token: Optional[str] = None
        self.user_agent = user_agent or rand_fua
        self.email = email
        self.password = password
        self.cookie_jar: dict[str, str] = {}
        self.session.headers.update({
            "User-Agent": self.user_agent,
        })
        pprint.print(
            Platform.KAIZE,
            Status.READY,
            "Kaize anime data scraper ready to use",
        )

    def get_csrf_tokens(self) -> None:
        """
        Get the CSRF tokens from the login page
        """
        login_url: str = f"{self.base_url}/login"
        response: req.Response = self.session.get(login_url)
        if 'XSRF-TOKEN' in response.cookies:
            self.xsrf_token = response.cookies['XSRF-TOKEN']
            self.cookie_jar['XSRF-TOKEN'] = self.xsrf_token
        soup: BeautifulSoup = BeautifulSoup(response.text, 'html.parser')
        csrf_meta: Optional[Tag] = soup.find('meta', {'name': 'csrf-token'})
        if csrf_meta:
            self.csrf_token = csrf_meta.get('content')
    
    def update_cookies(self, response: req.Response) -> None:
        """
        Update cookies from response
        
        :param response: The response object
        :type response: req.Response
        """
        for cookie_name in ['XSRF-TOKEN', 'kaize_session', 'remember_web']:
            if cookie_name in response.cookies:
                self.cookie_jar[cookie_name] = response.cookies[cookie_name]
    
    def login(self, email: str, password: str) -> bool:
        """
        Login to Kaize
        
        :param email: Email address
        :type email: str
        :param password: Password
        :type password: str
        :return: True if login successful, False otherwise
        :rtype: bool
        """
        login_url: str = f"{self.base_url}/login"
        login_data: dict[str, str] = {
            '_token': str(self.csrf_token),
            'email': email,
            'password': password,
            'remember': 'on'
        }
        response: req.Response = self.session.post(
            login_url, data=login_data, allow_redirects=False
        )
        if response.status_code == 302:
            pprint.print(Platform.KAIZE, Status.PASS, "Login successful")
            self.update_cookies(response)
            return True
        else:
            pprint.print(Platform.KAIZE, Status.ERR, f"Login failed with status code: {response.status_code}")
            return False
    
    def _session_set(self) -> None:
        """
        Set the session and XSRF token

        :raises ValueError: Email or password not provided
        :raises ValueError: XSRF token not found
        :raises ConnectionError: Unable to connect to kaize.io
        """
        if not self.email or not self.password:
            raise ValueError("Email or password not provided")
        
        # Get CSRF tokens
        self.get_csrf_tokens()
        
        # Login
        if not self.login(self.email, self.password):
            raise ConnectionError("Unable to login to kaize.io")

    def _get(self, url: str) -> Union[req.Response, None]:
        """
        Get the response from the url

        :param url: The url to get the response
        :type url: str
        :return: The response
        :rtype: Union[req.Response, None]
        """
        try:
            response = self.session.get(url, timeout=15)
            if response.status_code == 200:
                self.update_cookies(response)
                return response
            return None
        except Exception as err:
            pprint.print(Platform.KAIZE, Status.ERR, f"Error: {err}")
            return None

    def _post(
        self,
        url: str,
        data: Union[dict[str, Any], str],
        header: Union[dict[str, Any], None] = None,
    ) -> Union[req.Response, None]:
        """
        Do POST request to the url

        :param url: The url to do the POST request
        :type url: str
        :param data: The data to POST
        :type data: Union[dict[str, Any], str]
        :param header: The header, defaults to None
        :type header: Union[dict[str, Any], None], optional
        :return: The response
        :rtype: Union[req.Response, None]
        """
        headers = header if header else {}
        try:
            response = self.session.post(url, headers=headers, data=data, timeout=15)
            if response.status_code == 200 or response.status_code == 302:
                self.update_cookies(response)
                return response
            return None
        except Exception as err:
            pprint.print(Platform.KAIZE, Status.ERR, f"Error: {err}")
            return None

    def pages(self, media: Literal["anime", "manga"] = "anime") -> int:
        """
        Get the total pages

        :param media: The media, defaults to 'anime'
        :type media: Literal['anime', 'manga'], optional
        :raises ConnectionError: Unable to connect to kaize.io
        :return: The total pages
        :rtype: int
        """
        kzp = 0
        pgHundreds = True
        pgTens = True
        pgOnes = True
        kzpg = 0
        while pgHundreds is True:
            pprint.print(
                Platform.KAIZE,
                Status.INFO,
                f"Checking in hundreds, page {kzp}",
                clean_line=True,
                end="",
            )
            pg_check = self._get(f"{self.base_url}/{media}/top?page={kzp}")
            if not pg_check:
                pprint.print(
                    Platform.KAIZE, Status.ERR, "Unable to connect to kaize.io"
                )
                break
            soup = BeautifulSoup(pg_check.text, "html.parser")
            try:
                kzDat = soup.find_all("div", {"class": "anime-list-element"})
                if kzDat[0].find("div", {"class": "rank"}).text:
                    kzp += 100
                    time.sleep(1.2)
            except IndexError:
                kzpg = kzp - 100
                pgHundreds = False

        kzp = kzpg + 10
        while pgTens is True:
            pprint.print(
                Platform.KAIZE,
                Status.INFO,
                f"Checking in tens, page {kzp}",
                clean_line=True,
                end="",
            )
            pg_check = self._get(f"{self.base_url}/{media}/top?page={kzp}")
            if not pg_check:
                pprint.print(
                    Platform.KAIZE, Status.ERR, "Unable to connect to kaize.io"
                )
                break
            soup = BeautifulSoup(pg_check.text, "html.parser")
            try:
                kzDat = soup.find_all("div", {"class": "anime-list-element"})
                if kzDat[0].find("div", {"class": "rank"}).text:
                    kzp += 10
                    time.sleep(1.2)
            except IndexError:
                kzpg = kzp - 10
                pgTens = False

        kzp = kzpg + 1
        while pgOnes is True:
            pprint.print(
                Platform.KAIZE,
                Status.INFO,
                f"Checking in ones, page {kzp}",
                clean_line=True,
                end="",
            )
            pg_check = self._get(f"{self.base_url}/{media}/top?page={kzp}")
            if not pg_check:
                pprint.print(
                    Platform.KAIZE, Status.ERR, "Unable to connect to kaize.io"
                )
                break
            soup = BeautifulSoup(pg_check.text, "html.parser")
            try:
                kzDat = soup.find_all("div", {"class": "anime-list-element"})
                if kzDat[0].find("div", {"class": "rank"}).text:
                    kzp += 1
                    time.sleep(1.2)
            except IndexError:
                kzpg = kzp - 1
                pgOnes = False

        pprint.print(
            Platform.KAIZE,
            Status.PASS,
            f"Done checking, total pages: {kzpg}",
        )
        return kzpg

    def _get_data_index(
        self, page: int, media: Literal["anime", "manga"] = "anime"
    ) -> list[dict[str, Any]]:
        """
        Get the data from the index

        :param page: The page
        :type page: int
        :param media: The media, defaults to 'anime'
        :type media: Literal['anime', 'manga'], optional
        :raises ConnectionError: Unable to connect to kaize.io
        :return: The data
        :rtype: list[dict[str, Any]]
        """
        response = self._get(f"{self.base_url}/{media}/top?page={page}")
        if not response:
            raise ConnectionError("Unable to connect to kaize.io")
        soup = BeautifulSoup(response.text, "html.parser")
        kz_dat = soup.find_all("div", {"class": "anime-list-element"})
        result: list[dict[str, Any]] = []
        for kz in kz_dat:
            title: str = kz.find("a", {"class": "name"}).text
            link = kz.find("a", {"class": "name"}).get("href")
            slug: str = link.split("/")[-1]
            # background-image: url(https://kaize.io/images/animes_images/2022/anime_image_6289_14_22_44.jpg)
            media_id = kz.find("div", {"class": "cover"}).get("style")
            media_id = re.search(r"/anime_image_(\d+)", media_id)
            if media_id:
                media_id = media_id.group(1)
            else:
                media_id = 0
            result.append(
                {
                    "title": title,
                    "slug": slug,
                    "kaize": int(media_id),
                }
            )
        return result

    def get_anime(self) -> list[dict[str, Any]]:
        """
        Get complete anime data

        :raises ConnectionError: Unable to connect to kaize.io
        :return: The anime data
        :rtype: list[dict[str, Any]]
        """
        anime_data: list[dict[str, Any]] = []
        file_path = "database/raw/kaize.json"
        try:
            # raise ConnectionError("Force use local file")
            self._session_set()
            pages = self.pages()
            with alive_bar(pages, title="Getting data", spinner=None) as bar:  # type: ignore
                for page in range(1, pages + 1):
                    anime_data.extend(self._get_data_index(page))
                    bar()
            with open(file_path, "w", encoding="utf-8") as file:
                anime_data.sort(key=lambda x: x["title"])  # type: ignore
                json.dump(anime_data, file)
            pprint.print(
                Platform.KAIZE,
                Status.PASS,
                f"Done getting data, total data: {len(anime_data)},",
                f"or around {str(math.ceil(len(anime_data) / 50))} pages,",
                "expected pages:",
                str(pages),
            )
        except ConnectionError:
            pprint.print(
                Platform.KAIZE,
                Status.WARN,
                "Unable to connect to kaize.io, loading from local file",
            )
            with open(file_path, "r", encoding="utf-8") as file:
                anime_data = json.load(file)
        anime_data.sort(key=lambda x: x["title"])  # type: ignore
        return anime_data

    @staticmethod
    def convert_list_to_dict(data: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
        """
        Convert list of dict to dict

        :param data: The data
        :type data: list[dict[str, Any]]
        :return: The dict
        :rtype: dict[str, dict[str, Any]]
        """
        result: dict[str, dict[str, Any]] = {}
        for item in data:
            result[item["slug"]] = item
        return result
