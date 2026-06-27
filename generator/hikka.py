# SPDX-License-Identifier: MIT

import json
from datetime import datetime
from time import sleep
from typing import Any

import requests
from alive_progress import alive_bar  # type: ignore
from const import GITHUB_DISPATCH
from prettyprint import Platform, PrettyPrint, Status
from requests import HTTPError, Response

pprint = PrettyPrint()


class Hikka:
    """Hikka.io anime data fetcher"""

    def __init__(self) -> None:
        """Initialize the Hikka fetcher"""
        self.base_url = "https://api.hikka.io"
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:147.0) Gecko/20100101 Firefox/147.0",
                "Accept": "*/*",
                "Accept-Language": "en",
                "Content-Type": "application/json",
                "Origin": "https://hikka.io",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-site",
            }
        )
        pprint.print(
            Platform.HIKKA,
            Status.READY,
            "Hikka anime data fetcher ready to use",
        )

    def _post(self, url: str, data: dict[str, Any]) -> Response:
        """
        POST request to the URL

        :param url: The url to post to
        :type url: str
        :param data: The JSON data to post
        :type data: dict
        :return: The response
        :rtype: Response
        """
        resp = self.session.post(url, json=data)
        if resp.status_code != 200:
            resp.raise_for_status()
        return resp

    def get_animes(self) -> list[dict[str, Any]]:
        """
        Get anime data from Hikka API using POST requests.
        First queries with size=1 to get total count, then iterates with size=100.

        :return: List of anime data
        :rtype: list[dict[str, Any]]
        """
        anime_data: list[dict[str, Any]] = []
        file_path = "database/raw/hikka.json"

        try:
            if datetime.now().day not in [3, 17] and not GITHUB_DISPATCH:
                raise ConnectionError("Fetcher is not allowed to run today")

            pprint.print(
                Platform.HIKKA, Status.INFO, "Getting total anime count from Hikka API"
            )

            # First request: get total count with size=1
            payload: dict[str, Any] = {
                "media_type": [],
                "status": [],
                "season": [],
                "rating": [],
                "years": [],
                "genres": [],
                "studios": [],
                "only_translated": False,
                "sort": ["score:desc"],
            }

            page_size = 100  # Maximum allowed by Hikka API
            response = self._post(f"{self.base_url}/anime?page=1&size=1", payload)
            data = response.json()
            pagination = data.get("pagination", {})

            total_anime = pagination.get("total", 0)
            # Do NOT use pagination["pages"] here — that value was computed
            # with size=1, so it equals total_anime (one page per entry).
            # Re-derive the correct page count from the actual fetch size.
            total_pages = (total_anime + page_size - 1) // page_size

            pprint.print(
                Platform.HIKKA,
                Status.INFO,
                f"Found {total_anime} anime across {total_pages} pages (page size: {page_size})",
            )

            page = 1

            with alive_bar(
                total_anime, title="Getting anime from Hikka API", spinner=None
            ) as bar:  # type: ignore
                while page <= total_pages:
                    try:
                        sleep(0.5)  # Rate limiting between requests

                        url = f"{self.base_url}/anime?page={page}&size={page_size}"
                        response = self._post(url, payload)
                        data = response.json()

                        items = data.get("list", [])

                        if not items:
                            break

                        for item in items:
                            # Only include if we have both slug and mal_id for matching
                            slug = item.get("slug")
                            mal_id = item.get("mal_id")

                            if slug and mal_id:
                                anime_data.append(
                                    {
                                        "slug": slug,
                                        "mal_id": mal_id,
                                        "title_ja": item.get("title_ja"),
                                        "title_en": item.get("title_en"),
                                        "title_ua": item.get("title_ua"),
                                    }
                                )

                        bar(len(items))
                        page += 1

                    except HTTPError as e:
                        if e.response.status_code == 404:
                            break
                        raise

            # Sort by title for consistency
            anime_data.sort(key=lambda x: x.get("title_en", "") or "")

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(anime_data, f)

            pprint.print(
                Platform.HIKKA,
                Status.PASS,
                "Done getting anime from Hikka API,",
                f"total linked: {len(anime_data)},",
                f"API total: {total_anime}",
            )

        except ConnectionError as err:
            pprint.print(Platform.HIKKA, Status.ERR, f"Error: {err}")
            pprint.print(
                Platform.HIKKA, Status.ERR, "Connection error, using local file"
            )
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    anime_data = json.load(f)
            except FileNotFoundError:
                pprint.print(
                    Platform.HIKKA, Status.ERR, "Local file not found, skipping Hikka"
                )

        except HTTPError as http:
            pprint.print(
                Platform.HIKKA,
                Status.ERR,
                f"HTTP Error: {http.response.status_code}, using local file",
            )
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    anime_data = json.load(f)
            except FileNotFoundError:
                pprint.print(
                    Platform.HIKKA, Status.ERR, "Local file not found, skipping Hikka"
                )

        anime_data.sort(key=lambda x: x.get("title_en", "") or "")
        return anime_data
