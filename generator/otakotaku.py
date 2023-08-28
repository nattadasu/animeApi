import json
import os
from datetime import datetime
from typing import Any, Union

import requests as req
from alive_progress import alive_bar  # type: ignore
from bs4 import BeautifulSoup, Tag
from const import GITHUB_DISPATCH
from fake_useragent import FakeUserAgent  # type: ignore
from prettyprint import Platform, PrettyPrint, Status

pprint = PrettyPrint()
fua = FakeUserAgent(browsers=["chrome"])
rand_fua: str = f"{fua.random}"  # type: ignore


class OtakOtaku:
    """OtakOtaku anime data scraper"""

    def __init__(self) -> None:
        self.headers = {
            'authority': 'otakotaku.com',
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'cookie': 'lang=id',
            'dnt': '1',
            'referer': 'https://otakotaku.com/anime/view/1/yahari-ore-no-seishun-love-comedy-wa-machigatteiru',
            'sec-ch-ua': '"Chromium";v="116", " Not)A;Brand";v="24", "Microsoft Edge";v="116"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'sec-gpc': '1',
            'user-agent': rand_fua,
            'x-requested-with': 'XMLHttpRequest',
            'Content-Encoding': 'gzip'
        }
        pprint.print(
            Platform.OTAKOTAKU,
            Status.READY,
            "OtakOtaku anime data scraper ready to use",
        )

    def _get(self, url: str) -> Union[req.Response, None]:
        """Get the response from the url"""
        response = req.get(url, headers=self.headers, timeout=15)
        try:
            response.raise_for_status()
            return response
        except Exception as err:
            pprint.print(Platform.OTAKOTAKU, Status.ERR, f"Error: {err}")
            return None

    def get_latest_anime(self) -> int:
        """Get latest anime from the website"""
        url = "https://otakotaku.com/anime/feed"
        response = self._get(url)
        if not response:
            raise ConnectionError("Failed to connect to otakotaku.com")
        soup = BeautifulSoup(response.text, "html.parser")
        link = soup.find("div", class_='anime-img')
        if not isinstance(link, Tag):
            pprint.print(Platform.OTAKOTAKU, Status.ERR,
                         "Failed to get latest anime")
            return 0
        link = link.find("a")
        if not isinstance(link, Tag):
            pprint.print(Platform.OTAKOTAKU, Status.ERR,
                         "Failed to get latest anime")
            return 0
        href = link.get("href")
        if not href:
            pprint.print(Platform.OTAKOTAKU, Status.ERR,
                         "Failed to get latest anime")
            return 0
        if isinstance(href, list):
            href = href[0]
        anime_id = href.rstrip("/").split("/")[-2]
        pprint.print(Platform.OTAKOTAKU, Status.PASS,
                     f"Latest anime id: {anime_id}")
        return int(anime_id)

    def _get_data_index(self, anime_id: int) -> Union[dict[str, Any], None]:
        response = self._get(
            f"https://otakotaku.com/api/anime/view/{anime_id}")
        if not response:
            raise ConnectionError("Failed to connect to otakotaku.com")
        json: dict[str, Any] = response.json()
        if not json:
            return None
        data: dict[str, Any] = json['data']
        mal: Union[str, int, None] = data.get('mal_id_anime', None)
        if mal:
            mal = int(mal)
        apla = data.get('ap_id_anime', None)
        if apla:
            apla = int(apla)
        anidb = data.get('anidb_id_anime', None)
        if anidb:
            anidb = int(anidb)
        ann = data.get('ann_id_anime', None)
        if ann:
            ann = int(ann)
        title = data['judul_anime']
        title = title.replace("&quot;", '"')
        result = {
            'otakotaku': int(data['id_anime']),
            'title': title,
            'myanimelist': mal,
            'animeplanet': apla,
            'anidb': anidb,
            'animenewsnetwork': ann,
        }
        return result

    def get_anime(self) -> list[dict[str, Any]]:
        """Get complete anime data"""
        file_path = "database/raw/otakotaku.json"
        anime_list: list[dict[str, Any]] = []
        latest_file_path = "database/raw/_latest_otakotaku.txt"
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as file:
                anime_list = json.load(file)
        try:
            # raise ConnectionError("Failed to connect to otakotaku.com")
            latest_id = self.get_latest_anime()
            if not latest_id:
                raise ConnectionError("Failed to connect to otakotaku.com")
            if not datetime.now().day in [1, 15] and len(anime_list) > 0 and not GITHUB_DISPATCH:
                with open(latest_file_path, "r", encoding="utf-8") as file:
                    latest = int(file.read().strip())
                if latest == latest_id:
                    pprint.print(
                        Platform.OTAKOTAKU,
                        Status.PASS,
                        "Data is up to date, loading from local file",
                    )
                    return anime_list
                latest = latest + 1
                loop = latest_id - latest + 1
            else:
                anime_list = []  # remove possible duplicate
                latest = 1
                loop = latest_id
            with alive_bar(loop, title="Getting data", spinner=None) as bar:  # type: ignore
                for anime_id in range(latest, latest_id + 1):
                    data_index = self._get_data_index(anime_id)
                    if not data_index:
                        pprint.print(
                            Platform.OTAKOTAKU,
                            Status.ERR,
                            f"Failed to get data index for anime id: {anime_id},"
                            " data may be empty or invalid",
                        )
                        bar()
                        continue
                    anime_list.append(data_index)
                    bar()
            with open(latest_file_path, "w", encoding="utf-8") as file:
                file.write(str(latest_id))
            with open(file_path, "w", encoding="utf-8") as file:
                anime_list.sort(key=lambda x: x['title'])  # type: ignore
                json.dump(anime_list, file)
            pprint.print(
                Platform.OTAKOTAKU,
                Status.PASS,
                f"Total anime data: {len(anime_list)}"
            )
        except ConnectionError:
            pprint.print(
                Platform.OTAKOTAKU,
                Status.WARN,
                "Failed to get data, loading from local file",
            )
            with open(file_path, "r", encoding="utf-8") as file:
                anime_list = json.load(file)
        anime_list.sort(key=lambda x: x['title'])  # type: ignore
        return anime_list

    @staticmethod
    def convert_list_to_dict(data: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
        """Convert list to dict"""
        result: dict[str, dict[str, Any]] = {}
        for item in data:
            result[str(item['otakotaku'])] = item
        return result
