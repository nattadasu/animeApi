import json
from typing import Union, Any

from fake_useragent import FakeUserAgent  # type: ignore
from bs4 import BeautifulSoup, Tag
import requests as req
from alive_progress import alive_bar  # type: ignore

from prettyprint import PrettyPrint, Platform, Status

pprint = PrettyPrint()
fua = FakeUserAgent(browsers=["firefox", "chrome", "edge", "safari"])
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
            'referer': 'https://otakotaku.com/anime/view/1',
            'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Microsoft Edge";v="92"',
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
        try:
            response = req.get(url, headers=self.headers, timeout=15)
            if response.status_code == 200:
                return response
            return None
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
            pprint.print(Platform.OTAKOTAKU, Status.ERR, "Failed to get latest anime")
            return 0
        link = link.find("a")
        if not isinstance(link, Tag):
            pprint.print(Platform.OTAKOTAKU, Status.ERR, "Failed to get latest anime")
            return 0
        href = link.get("href")
        if not href:
            pprint.print(Platform.OTAKOTAKU, Status.ERR, "Failed to get latest anime")
            return 0
        if isinstance(href, list):
            href = href[0]
        anime_id = href.rstrip("/").split("/")[-2]
        pprint.print(Platform.OTAKOTAKU, Status.PASS, f"Latest anime id: {anime_id}")
        return int(anime_id)

    def _get_data_index(self, anime_id: int) -> Union[dict[str, Any], None]:
        response = self._get(f"https://otakotaku.com/api/anime/view/{anime_id}")
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
        result = {
            'otakotaku': int(data['id_anime']),
            'title': data['judul_anime'],
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
        try:
            latest_id = self.get_latest_anime()
            if not latest_id:
                raise ConnectionError("Failed to connect to otakotaku.com")
            with alive_bar(latest_id, title="Getting data", spinner=None) as bar:  # type: ignore
                for anime_id in range(1, latest_id + 1):
                    data_index = self._get_data_index(anime_id)
                    if not data_index:
                        pprint.print(
                            Platform.OTAKOTAKU,
                            Status.ERR,
                            f"Failed to get data index for anime id: {anime_id},"
                            " data may be empty or invalid",
                        )
                        continue
                    anime_list.append(data_index)
                    bar()
            with open(file_path, "w", encoding="utf-8") as file:
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
        return anime_list

    @staticmethod
    def convert_list_to_dict(data: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
        """Convert list to dict"""
        result: dict[str, dict[str, Any]] = {}
        for item in data:
            result[str(item['otakotaku'])] = item
        return result
