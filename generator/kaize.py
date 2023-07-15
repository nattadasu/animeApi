import json
import math
import re
import time
from typing import Union, Optional, Any, Literal

from alive_progress import alive_bar  # type: ignore
from fake_useragent import FakeUserAgent  # type: ignore
from bs4 import BeautifulSoup, Tag
import requests as req

from prettyprint import PrettyPrint, Platform, Status

pprint = PrettyPrint()
fua = FakeUserAgent(browsers=["firefox", "chrome", "edge", "safari"])
rand_fua: str = f"{fua.random}"  # type: ignore

class Kaize:
    """Kaize anime data scraper"""

    def __init__(
        self,
        xsrf_token: Optional[str] = None,
        user_agent: Optional[str] = None,
        email: Optional[str] = None,
        password: Optional[str] = None
    ) -> None:
        """Initialize the Kaize class"""
        self.base_url = "https://kaize.io"
        self.xsrf_token = xsrf_token
        self.user_agent = user_agent or rand_fua
        self.email = email
        self.password = password
        pprint.print(
            Platform.KAIZE,
            Status.READY,
            "Kaize anime data scraper ready to use",
        )

    def _get(self, url: str) -> Union[req.Response, None]:
        """Get the response from the url"""
        headers = {
            "User-Agent": self.user_agent,
        }
        if self.xsrf_token:
            headers["X-XSRF-TOKEN"] = self.xsrf_token
        try:
            response = req.get(url, headers=headers, timeout=15)
            if response.status_code == 200:
                return response
            return None
        except Exception as err:
            pprint.print(Platform.KAIZE, Status.ERR, f"Error: {err}")
            return None

    def _post(
        self,
        url: str,
        data: Union[dict[str, Any], str],
        header: Union[dict[str, Any], None] = None
    ) -> Union[req.Response, None]:
        """Do POST request to the url"""
        headers = {
            "User-Agent": self.user_agent,
        }
        if self.xsrf_token:
            headers["X-XSRF-TOKEN"] = self.xsrf_token
        if header:
            headers.update(header)
        try:
            response = req.post(url, headers=headers, data=data, timeout=15)
            if response.status_code == 200 or response.status_code == 302:
                return response
            return None
        except Exception as err:
            pprint.print(Platform.KAIZE, Status.ERR, f"Error: {err}")
            return None

    def _get_xsrf_token(self) -> str:
        """Get the xsrf token"""
        if not self.email or not self.password:
            raise ValueError("Email or password not provided")
        base_url = f"{self.base_url}/login"
        response = self._get(base_url)
        if not response:
            raise ConnectionError("Unable to connect to kaize.io")
        soup = BeautifulSoup(response.text, "html.parser")
        xsrf_token = soup.find("meta", attrs={"name": "csrf-token"})
        if not isinstance(xsrf_token, Tag):
            raise ValueError("XSRF token not found")
        token = xsrf_token.get("content", None)
        if not token:
            raise ValueError("XSRF token not found")
        # post login
        header_login = {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Cookie": response.headers["Set-Cookie"].split(",")[0].split(";")[0]
        }
        data_raw: list[str] = [
            f"_token={token}",
            f"email={self.email}",
            f"password={self.password}",
        ]
        data: str = "&".join(data_raw)
        response = self._post(f"{base_url}", data, header_login)
        if not response:
            raise ConnectionError("Unable to connect to kaize.io")
        # set cookie
        cookie = (
            response.headers["Set-Cookie"].split(",")[0].split(";")[0] +
            "; " +
            response.headers["Set-Cookie"].split(",")[2].split(";")[0]
        )
        return cookie

    def pages(self, media: Literal['anime', 'manga'] = 'anime') -> int:
        """Get the total pages"""
        if not self.xsrf_token:
            self.xsrf_token = self._get_xsrf_token()
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
                    Platform.KAIZE, Status.ERR, "Unable to connect to kaize.io")
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
                    Platform.KAIZE, Status.ERR, "Unable to connect to kaize.io")
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
                    Platform.KAIZE, Status.ERR, "Unable to connect to kaize.io")
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

    def _get_data_index(self, page: int, media: Literal['anime', 'manga'] = 'anime') -> list[dict[str, Any]]:
        """Get the data from the index"""
        response = self._get(f"{self.base_url}/{media}/top?page={page}")
        if not response:
            raise ConnectionError("Unable to connect to kaize.io")
        soup = BeautifulSoup(response.text, "html.parser")
        kz_dat = soup.find_all("div", {"class": "anime-list-element"})
        result: list[dict[str, Any]] = []
        for kz in kz_dat:
            rank: str = kz.find("div", {"class": "rank"}).text
            rank = rank.replace("#", "")
            rank = rank.replace("\n", "")
            rank = rank.replace("\t", "")
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
            result.append({
                "rank": int(rank),
                "title": title,
                "slug": slug,
                "kaize": int(media_id),
            })
        return result

    def get_anime(self) -> list[dict[str, Any]]:
        """Get complete anime data"""
        anime_data: list[dict[str, Any]] = []
        file_path = "database/raw/kaize.json"
        try:
            pages = self.pages()
            with alive_bar(pages, title="Getting data", spinner=None) as bar:  # type: ignore
                for page in range(1, pages + 1):
                    anime_data.extend(self._get_data_index(page))
                    bar()
            with open(file_path, "w", encoding="utf-8") as file:
                json.dump(anime_data, file)
            pprint.print(
                Platform.KAIZE,
                Status.PASS,
                f"Done getting data, total data: {len(anime_data)},",
                f"or around {str(math.ceil(len(anime_data) / 50))} pages,",
                "expected pages:", str(pages)
            )
        except ConnectionError:
            pprint.print(
                Platform.KAIZE,
                Status.WARN,
                "Unable to connect to kaize.io, loading from local file",
            )
            with open(file_path, "r", encoding="utf-8") as file:
                anime_data = json.load(file)
        return anime_data

    @staticmethod
    def convert_list_to_dict(data: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
        """Convert list of dict to dict"""
        result: dict[str, dict[str, Any]] = {}
        for item in data:
            result[item["slug"]] = item
        return result
