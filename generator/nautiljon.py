import json
import math
import random
import re
from datetime import datetime
from time import sleep

import cloudscraper  # type: ignore
from alive_progress import alive_bar  # type: ignore
from bs4 import BeautifulSoup, Tag
from const import GITHUB_DISPATCH
from prettyprint import Platform, PrettyPrint, Status
from requests import Response, HTTPError

pprint = PrettyPrint()


def extract_table_data(html_content: str) -> list[dict[str, str | int | None]]:
    soup = BeautifulSoup(html_content, 'html.parser')
    table = soup.find('table', class_='search')
    if not isinstance(table, Tag):
        return []

    data_list: list[dict[str, str | int | None]] = []

    if table:
        # find tbody
        tbody: Tag = table.find('tbody')  # type: ignore
        # find all rows
        rows = tbody.find_all('tr')

        for row in rows:
            columns: list[Tag] = row.find_all('td')

            if len(columns) >= 4:
                title = columns[1].find('a',
                    class_='eTitre').get_text().strip()  # type: ignore
                francais = columns[1].find('span', class_="infos_small")
                try:
                    if francais:
                        francais = francais.get_text().strip()
                        francais = francais.removeprefix("(").removesuffix(")")
                    else:
                        francais = title
                except Exception:
                    francais = title
                slug = columns[0].find('a')['href']  # type: ignore
                # remove animes/ and .html
                slug = slug.split('/')[-1]  # type: ignore
                slug = re.sub(".html$", "", slug)
                # img src="/imagesmin/anime/00/68/offside_tv_12086.webp?1692218537
                # search for anime id in img src, before .webp and after last _
                try:
                    img_src = columns[0].find('img')['src']  # type: ignore
                    entry_id_match = re.search(r'_(\d+)\.webp', img_src)
                    
                    if entry_id_match:
                        entry_id = int(entry_id_match.group(1))  # type: ignore
                    else:
                        entry_id = None
                except KeyError:
                    entry_id = None
                format_value = columns[2].get_text().strip()
                status = columns[3].get_text().strip()

                data_list.append({
                    'title': f"{title}",
                    'francais': f"{francais}",
                    'slug': f"{slug}",
                    'entry_id': entry_id,
                    'format': format_value,
                    'status': status
                })

    return data_list


class Nautiljon:
    """Nautiljon class"""

    def __init__(self, scraper_: cloudscraper.CloudScraper | None = None) -> None:
        """Initialize the Nautiljon class"""
        if scraper_ is None:
            self.scraper = cloudscraper.create_scraper()  # type: ignore
        else:
            self.scraper = scraper_
        self.base_url = 'https://www.nautiljon.com'
        self.search_url = f"{self.base_url}/animes/"
        pprint.print(Platform.NAUTILJON, Status.READY,
                     "Nautiljon anime data scraper ready to use")

    def _get(self, url: str) -> Response:
        """Get the content of the url"""
        resp = self.scraper.get(url)
        if resp.status_code != 200:
            resp.raise_for_status()
        return resp

    def get_animes(self) -> list[dict[str, str | int | None]]:
        """Get the animes"""
        anime_data: list[dict[str, str | int | None]] = []
        file_path = "database/raw/nautiljon.json"
        try:
            # raise ConnectionError("Force use local file")
            if datetime.now().day not in [2, 16] and not GITHUB_DISPATCH:
                raise ConnectionError("Scraper is not allowed to run today")
            pprint.print(Platform.NAUTILJON, Status.INFO,
                         "Getting animes from Nautiljon")
            page = self._get(self.search_url)
            # get the last page number
            soup = BeautifulSoup(page.content, 'html.parser')
            # get dbt= from the last page
            last_page = soup.find('p', class_='menupage').find_all(  # type: ignore
                'a')[-1]['href'].split('=')[-1]  # type: ignore
            last_page = round(int(f"{last_page}") / 15)
            pprint.print(Platform.NAUTILJON, Status.NOTICE,
                         f"Last page: {last_page}")
            # loop through the other pages, by incrementing the page number * 15
            with alive_bar(
                last_page,
                title="Getting animes from Nautiljon",
                spinner=None) as bar:  # type: ignore
                scraped = extract_table_data(page.text)
                # append the first page
                anime_data.extend(scraped)
                bar()
                for page_number in range(15, last_page * 15, 15):
                    # random sleep between 0.1 and 1.5 seconds
                    sleep(random.uniform(0.1, 1.5))
                    page = self._get(f"{self.search_url}?dbt={page_number}")
                    scrape = extract_table_data(page.text)
                    # if scrape has less than 15 items and not in the last page
                    if len(scrape) < 15 and page_number < last_page * 15:
                        pg = (page_number//15)+1
                        pprint.print(Platform.NAUTILJON, Status.WARN,
                                     f"Page {pg} has less than 15 animes,"
                                     f"only {len(scrape)} animes scraped")
                    anime_data.extend(scrape)
                    bar()
            with open(file_path, 'w', encoding='utf-8') as file:
                # sort by title
                anime_data.sort(key=lambda x: x['title'])  # type: ignore
                json.dump(anime_data, file)
            pprint.print(
                Platform.NAUTILJON,
                Status.PASS,
                "Done getting animes from Nautiljon,",
                f"total animes: {len(anime_data)},",
                f"or around {math.ceil(len(anime_data) / 15)} pages.",
                f"Expected pages: {last_page}",
            )
        except ConnectionError as err:
            pprint.print(Platform.NAUTILJON, Status.ERR,
                         f"Error: {err}")
            pprint.print(Platform.NAUTILJON, Status.ERR,
                         "Connection error, using local file")
            with open(file_path, 'r', encoding='utf-8') as f:
                anime_data = json.load(f)
        except HTTPError as http:
            pprint.print(Platform.NAUTILJON, Status.ERR,
                         "Connection error, using local file."
                         f"HTTPError: {http.response}")
            with open(file_path, 'r', encoding='utf-8') as f:
                anime_data = json.load(f)
        anime_data.sort(key=lambda x: x['title'])  # type: ignore
        return anime_data
