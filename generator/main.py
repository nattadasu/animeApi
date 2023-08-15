import csv
import json
import os
import re
import subprocess
import sys
import traceback
from datetime import datetime, timezone
from time import time
from typing import Any, Union

import requests as req
from alive_progress import alive_bar  # type: ignore
from datadump import DataDump
from fuzzywuzzy import fuzz  # type: ignore
from kaize import Kaize
from otakotaku import OtakOtaku
from prettyprint import Platform, PrettyPrint, Status
from slugify import slugify

KAIZE_XSRF_TOKEN = os.getenv("KAIZE_XSRF_TOKEN")
KAIZE_SESSION = os.getenv("KAIZE_SESSION")
KAIZE_EMAIL = os.getenv("KAIZE_EMAIL")
KAIZE_PASSWORD = os.getenv("KAIZE_PASSWORD")

if (KAIZE_XSRF_TOKEN is None) and (KAIZE_SESSION is None) and (KAIZE_EMAIL is None) and (KAIZE_PASSWORD is None):
    raise Exception('Kaize login info does not available in environment variables')

pprint = PrettyPrint()

attribution = {
    "mainrepo": "https://github.com/nattadasu/animeApi/tree/v3",
    "updated": {
        "timestamp": 0,
        "iso": ""
    },
    "contributors": [
        ""
    ],
    "sources": [
        "manami-project/anime-offline-database",
        "kawaiioverflow/arm",
        "ryuuganime/aniTrakt-IndexParser",
        "https://db.silveryasha.web.id",
        "https://kaize.io",
        "https://otakotaku.com",
    ],
    "license": "AGPL-3.0",
    "website": "https://animeapi.my.id",
    "counts": {
        "anidb": 0,
        "anilist": 0,
        "animeplanet": 0,
        "anisearch": 0,
        "annict": 0,
        "imdb": 0,
        "kaize": 0,
        "kitsu": 0,
        "livechart": 0,
        "myanimelist": 0,
        "notify": 0,
        "otakotaku": 0,
        "shikimori": 0,
        "shoboi": 0,
        "silveryasha": 0,
        "themoviedb": 0,
        "trakt": 0,
        "total": 0,
    },
    "endpoints": {
        "$comment": "The endpoints are stated in Python regex format",
        "anidb": r"/anidb/(?P<media_id>\d+)",
        "anilist": r"/anilist/(?P<media_id>\d+)",
        "animeapi_tsv": r"/anime(a|A)pi.tsv",
        "animeplanet": r"/animeplanet/(?P<media_id>[\w\-]+)",
        "anisearch": r"/anisearch/(?P<media_id>\d+)",
        "annict": r"/annict/(?P<media_id>\d+)",
        "heartbeat": r"/(heartbeat|ping)",
        "imdb": r"/imdb/(?P<media_id>tt[\d]+)",
        "kaize": r"/kaize/(?P<media_id>[\w\-]+)",
        "kitsu": r"/kitsu/(?P<media_id>\d+)",
        "livechart": r"/livechart/(?P<media_id>\d+)",
        "myanimelist": r"/myanimelist/(?P<media_id>\d+)",
        "notify": r"/notify/(?P<media_id>[\w\-_]+)",
        "otakotaku": r"/otakotaku/(?P<media_id>\d+)",
        "repo": r"/",
        "schema": r"/schema(?:.json)?",
        "shikimori": r"/shikimori/(?P<media_id>\d+)",
        "shoboi": r"/shoboi/(?P<media_id>\d+)",
        "silveryasha": r"/silveryasha/(?P<media_id>\d+)",
        "status": r"/status",
        "syobocal": r"/syobocal/(?P<media_id>\d+)",
        "themoviedb": r"/themoviedb/movie/(?P<media_id>\d+)",
        "trakt": r"/trakt/(?P<media_type>show|movie)(s)?/(?P<media_id>\d+)(?:/season(s)?/(?P<season_id>\d+))?",
        "updated": r"/updated",
    }
}


def get_anime_offline_database() -> dict[str, Any]:
    """Get info from manami-project/anime-offline-database"""
    pprint.print(
        Platform.ANIMEOFFLINEDATABASE,
        Status.READY,
        "anime-offline-database ready to use",
    )
    ddump = DataDump(
        url="https://raw.githubusercontent.com/manami-project/anime-offline-database/master/anime-offline-database-minified.json",
        file_name="aod",
        file_type="json",
    )
    content: dict[str, Any] = ddump.dumper()
    pprint.print(
        Platform.ANIMEOFFLINEDATABASE,
        Status.PASS,
        "anime-offline-database data retrieved successfully",
    )
    return content


def get_arm() -> list[dict[str, Any]]:
    pprint.print(
        Platform.ARM,
        Status.READY,
        "ARM ready to use",
    )
    ddump = DataDump(
        url="https://raw.githubusercontent.com/kawaiioverflow/arm/master/arm.json",
        file_name="arm",
        file_type="json",
    )
    data: list[dict[str, Any]] = ddump.dumper()
    pprint.print(
        Platform.ARM,
        Status.PASS,
        "ARM data retrieved successfully",
    )
    return data


def get_anitrakt() -> list[dict[str, Any]]:
    pprint.print(
        Platform.ANITRAKT,
        Status.READY,
        "AniTrakt ready to use",
    )
    base_url = "https://raw.githubusercontent.com/ryuuganime/aniTrakt-IndexParser/main/db/"
    ddump_tv = DataDump(
        url=f"{base_url}tv.json",
        file_name="anitrakt_tv",
        file_type="json",
    )
    data_tv: list[dict[str, Any]] = ddump_tv.dumper()
    pprint.print(
        Platform.ANITRAKT,
        Status.PASS,
        "AniTrakt data for TV retrieved successfully",
    )

    ddump_movie = DataDump(
        url=f"{base_url}movies.json",
        file_name="anitrakt_movie",
        file_type="json",
    )
    data_movie: list[dict[str, Any]] = ddump_movie.dumper()
    pprint.print(
        Platform.ANITRAKT,
        Status.PASS,
        "AniTrakt data for Movie retrieved successfully",
    )
    with alive_bar(len(data_movie),
                   title="Fixing AniTrakt data for movie",
                   spinner=None) as bar:  # type: ignore
        for index, item in enumerate(data_movie):
            item["season"] = None
            data_movie[index] = item
            bar()  # type: ignore
    data = data_tv + data_movie
    with open("database/raw/anitrakt.json", "w", encoding="utf-8") as file:
        json.dump(data, file)
    pprint.print(
        Platform.ANITRAKT,
        Status.PASS,
        "Completely compiled AniTrakt data",
    )
    return data


def get_silveryasha() -> list[dict[str, Any]]:
    pprint.print(
        Platform.SILVERYASHA,
        Status.READY,
        "Silveryasha ready to use",
    )
    ddump = DataDump(
        url="https://db.silveryasha.web.id/ajax/anime/dtanime",
        file_name="silveryasha",
        file_type="json",
    )
    data_: dict[str, Any] = ddump.dumper()
    data: list[dict[str, Any]] = data_["data"]
    pprint.print(
        Platform.SILVERYASHA,
        Status.PASS,
        "Silveryasha data retrieved successfully",
    )
    return data


def get_fribb_animelists() -> list[dict[str, Any]]:
    pprint.print(
        Platform.FRIBB,
        Status.READY,
        "Fribb Animelists ready to use",
    )
    ddump = DataDump(
        url="https://raw.githubusercontent.com/Fribb/anime-lists/master/anime-lists-reduced.json",
        file_name="fribb_animelists",
        file_type="json",
    )
    data: list[dict[str, Any]] = ddump.dumper()
    pprint.print(
        Platform.FRIBB,
        Status.PASS,
        "Fribb's Animelists data retrieved successfully",
    )
    return data


def populate_contributors() -> None:
    """Read total contributors from GitHub API"""
    response = req.get(
        "https://api.github.com/repos/nattadasu/animeApi/contributors?per_page=100",
        headers={
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "nattadasu/animeApi",
        },
    )
    if response.status_code == 200:
        # clear the list first
        attribution["contributors"] = []
        attribution["contributors"] = [
            contributor["login"] for contributor in response.json()
        ]
    return None


def simplify_aod_data(aod: dict[str, Any]) -> list[dict[str, Any]]:
    """Convert AOD data to a format that is easier to work with"""
    data: list[dict[str, Any]] = []
    items: list[dict[str, Any]] = aod["data"]
    with alive_bar(len(items),
                   title="Simplifying AOD data",
                   spinner=None) as bar:  # type: ignore
        for item in items:
            adb_id: int | None = None
            al_id: int | None = None
            ap_slug: str | None = None
            as_id: int | None = None
            kt_id: int | None = None
            lc_id: int | None = None
            mal_id: int | None = None
            ntf_b64: str | None = None
            for sauce in item["sources"]:
                if sauce.startswith("https://anidb.net/anime/"):
                    adb_id = int(sauce.split("/")[-1])
                elif sauce.startswith("https://anilist.co/anime/"):
                    al_id = int(sauce.split("/")[-1])
                elif sauce.startswith("https://anime-planet.com/anime/"):
                    ap_slug = sauce.split("/")[-1]
                elif sauce.startswith("https://anisearch.com/anime/"):
                    as_id = int(sauce.split("/")[-1])
                elif sauce.startswith("https://kitsu.io/anime/"):
                    kt_id = int(sauce.split("/")[-1])
                elif sauce.startswith("https://livechart.me/anime/"):
                    lc_id = int(sauce.split("/")[-1])
                elif sauce.startswith("https://myanimelist.net/anime/"):
                    mal_id = int(sauce.split("/")[-1])
                elif sauce.startswith("https://notify.moe/anime/"):
                    ntf_b64 = sauce.split("/")[-1]
            data.append({
                "title": item["title"],
                "anidb": adb_id,
                "anilist": al_id,
                "animeplanet": ap_slug,
                "anisearch": as_id,
                "kitsu": kt_id,
                "livechart": lc_id,
                "myanimelist": mal_id,
                "notify": ntf_b64,
                "shikimori": mal_id,
            })
            bar()
    pprint.print(
        Platform.ANIMEOFFLINEDATABASE,
        Status.PASS,
        "AOD data simplified successfully, total data:",
        f"{len(data)}",
    )
    return data


def simplify_silveryasha_data() -> list[dict[str, Any]]:
    """Simplify data from silveryasha"""
    final: list[dict[str, Any]] = []
    data = get_silveryasha()
    with alive_bar(len(data),
                   title="Simplifying Silveryasha data",
                   spinner=None) as bar:  # type: ignore
        for item in data:
            final.append({
                "title": item["title"],
                "alternative_titles": item["title_alt"],
                "silveryasha": item["id"],
                "myanimelist": item["mal_id"],
            })
            bar()
    return final


def link_kaize_to_mal(
    kaize: list[dict[str, Any]],
    aod: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Link Kaize slug to MyAnimeList ID based similarity in title name over 85% in fuzzy search"""
    # add dummy data to aod
    for item in aod:
        item.update({
            "kaize": None,
            "kaize_id": None,
        })
    unlinked: list[dict[str, Any]] = []
    kz_fixed: list[dict[str, Any]] = []
    kz_dict: dict[str, Any] = {}
    aod_dict: dict[str, Any] = {}
    with alive_bar(len(aod),
                   title="Translating AOD list to a dict with custom slug",
                   spinner=None) as bar:  # type: ignore
        for item in aod:
            aod_slug = slugify(item["title"]).replace("-", "")
            aod_dict[aod_slug] = item
            bar()
    with alive_bar(len(kaize),
                   title="Translating Kaize list to a dict with custom slug",
                   spinner=None) as bar:  # type: ignore
        for item in kaize:
            kz_slug = slugify(item["slug"]).replace("-", "")
            kz_dict[kz_slug] = item
            bar()
    with alive_bar(len(kz_dict),
                   title="Linking Kaize slug to MyAnimeList ID",
                   spinner=None) as bar:  # type: ignore
        for kz_slug, kz_item in kz_dict.items():
            if kz_slug in aod_dict:
                aod_item: Union[dict[str, Any],
                                None] = aod_dict.get(kz_slug, None)
                if aod_item:
                    # add more data from kaize
                    kz_item.update({
                        "myanimelist": aod_item["myanimelist"],
                    })
                    kz_fixed.append(kz_item)
                    aod_item.update({
                        "kaize": kz_item["slug"],
                        "kaize_id": None if kz_item["kaize"] == 0 else kz_item["kaize"],
                    })
                else:
                    unlinked.append(kz_item)
            else:
                unlinked.append(kz_item)
            bar()
    # on unlinked, fuzzy search the title name
    with alive_bar(len(unlinked),
                   title="Fuzzy searching unlinked data",
                   spinner=None) as bar:  # type: ignore
        for item in unlinked:
            title = item["title"]
            for aod_item in aod:
                aod_title = aod_item["title"]
                ratio = fuzz.ratio(title, aod_title)  # type: ignore
                if ratio >= 85:
                    kz_dat = {
                        "anidb": aod_item["anidb"],
                        "anilist": aod_item["anilist"],
                        "animeplanet": aod_item["animeplanet"],
                        "anisearch": aod_item["anisearch"],
                        "kitsu": aod_item["kitsu"],
                        "myanimelist": aod_item["myanimelist"],
                        "notify": aod_item["notify"],
                        "shikimori": aod_item["shikimori"],
                    }
                    item.update(kz_dat)
                    kz_fixed.append(item)
                    aod_item.update({
                        "kaize": item["slug"],
                        "kaize_id": None if item["kaize"] == 0 else item["kaize"],
                    })
                    # in unlinked, remove the item with the same id
                    unlinked.remove(item)
                    break
            bar()
    # load manual link data
    with open("database/raw/kaize_manual.json", "r", encoding="utf-8") as file:
        manual_link: dict[str, dict[str, str | int | None]] = json.load(file)
    with alive_bar(len(manual_link),
                   title="Linking manually linked data",
                   spinner=None) as bar:  # type: ignore
        for title, kz_item in manual_link.items():
            for aod_item in aod:
                aod_title = aod_item["title"]
                if title == aod_title:
                    kz_dat = {
                        "kaize": kz_item["kaize"],
                        "kaize_id": None if kz_item["kaize"] == 0 else kz_item["kaize"],
                    }
                    aod_item.update(kz_dat)
                    kz_fixed.append(aod_item)
                    # in unlinked, remove the item with the same id
                    for item in unlinked:
                        if item["kaize"] == kz_item["kaize"]:
                            unlinked.remove(item)
                            break
                    break
            bar()
    # remove if unlinked data is already linked
    with alive_bar(len(kz_fixed),
                   title="Removing linked data from unlinked data",
                   spinner=None) as bar:  # type: ignore
        for item in kz_fixed:
            if item in unlinked:
                unlinked.remove(item)
            bar()
    aod_list: list[dict[str, Any]] = []
    with alive_bar(len(aod_dict),
                   title="Translating AOD dict to a list",
                   spinner=None) as bar:  # type: ignore
        for _, value in aod_dict.items():
            # check if kaize_id or kaize key not exists, then set it to None
            if "kaize" not in value:
                value["kaize"] = None
            if "kaize_id" not in value:
                value["kaize_id"] = None
            aod_list.append(value)
            bar()
    merged: list[dict[str, Any]] = []
    merged.extend(aod)

    # add missing items from old AOD data
    with alive_bar(len(aod_list),
                   title="Adding missing items from old AOD data",
                   spinner=None) as bar:  # type: ignore
        for item in aod_list:
            if item not in aod:
                merged.append(item)
            bar()

    aod_list = merged

    pprint.print(
        Platform.KAIZE,
        Status.PASS,
        "Kaize slug linked to MyAnimeList ID, unlinked data will be saved to kaize_unlinked.json.",
        "Total linked data:",
        f"{len(kz_fixed)},",
        "total unlinked data:",
        f"{len(unlinked)}",
    )
    with open("database/raw/kaize_unlinked.json", "w", encoding="utf-8") as file:
        json.dump(unlinked, file)
    return aod_list


def link_otakotaku_to_mal(
    otakotaku: list[dict[str, Any]],
    aod: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Link Otak Otaku ID to MyAnimeList ID based similarity in title name over 85% in fuzzy search"""
    unlinked: list[dict[str, Any]] = []
    ot_fixed: list[dict[str, Any]] = []
    ot_dict: dict[str, Any] = {}
    aod_dict: dict[str, Any] = {}
    with alive_bar(len(aod),
                   title="Translating AOD list to a dict with MAL ID",
                   spinner=None) as bar:  # type: ignore
        for item in aod:
            if item["myanimelist"]:
                aod_dict[f"{item['myanimelist']}"] = item
            else:
                aod_dict[item["title"]] = item
            bar()
    with alive_bar(len(otakotaku),
                   title="Translating Otakotaku list to a dict with MAL ID",
                   spinner=None) as bar:  # type: ignore
        for item in otakotaku:
            mal_id = item["myanimelist"]
            if mal_id:
                ot_dict[f"{mal_id}"] = {
                    "title": item["title"],
                    "otakotaku": item["otakotaku"],
                    "animeplanet": item["animeplanet"],
                    "anidb": item["anidb"],
                    "animenewsnetwork": item["animenewsnetwork"],
                }
            else:
                ot_dict[item["title"]] = {
                    "title": item["title"],
                    "otakotaku": item["otakotaku"],
                    "animeplanet": item["animeplanet"],
                    "anidb": item["anidb"],
                    "animenewsnetwork": item["animenewsnetwork"],
                }
            bar()
    with alive_bar(len(ot_dict),
                   title="Linking Otak Otaku ID to MyAnimeList ID",
                   spinner=None) as bar:  # type: ignore
        for mal_id, ot_item in ot_dict.items():
            if mal_id in aod_dict:
                aod_item: Union[dict[str, Any], None] = aod_dict.get(
                    f"{mal_id}", None)
                if aod_item:
                    # add more data from otakotaku
                    ot_dat = {
                        "otakotaku": ot_item["otakotaku"],
                    }
                    aod_item.update(ot_dat)
                    ot_fixed.append(aod_item)
                else:
                    unlinked.append(ot_item)
            else:
                unlinked.append(ot_item)
            bar()
    # on unlinked, fuzzy search the title name
    with alive_bar(len(unlinked),
                   title="Fuzzy searching unlinked data",
                   spinner=None) as bar:  # type: ignore
        for item in unlinked:
            title = item["title"]
            for aod_item in aod:
                aod_title = aod_item["title"]
                ratio = fuzz.ratio(title, aod_title)  # type: ignore
                if ratio >= 85:
                    ot_dat = {
                        "otakotaku": item["otakotaku"],
                    }
                    aod_item.update(ot_dat)
                    ot_fixed.append(aod_item)
                    # in unlinked, remove the item with the same id
                    for item in unlinked:
                        if item["otakotaku"] == ot_dat["otakotaku"]:
                            unlinked.remove(item)
                    break
            bar()
    # load manual link data
    with open("database/raw/otakotaku_manual.json", "r", encoding="utf-8") as file:
        manual_link: dict[str, int] = json.load(file)
    with alive_bar(len(manual_link),
                   title="Linking manually linked data",
                   spinner=None) as bar:  # type: ignore
        for title, oo_id in manual_link.items():
            for aod_item in aod:
                aod_title = aod_item["title"]
                if title == aod_title:
                    oo_dat = {
                        "otakotaku": oo_id,
                    }
                    aod_item.update(oo_dat)
                    ot_fixed.append(aod_item)
                    # in unlinked, remove the item with the same id
                    for item in unlinked:
                        if item["otakotaku"] == oo_id:
                            unlinked.remove(item)
                    break
            bar()
    # remove if unlinked data is already linked
    with alive_bar(len(ot_fixed),
                   title="Removing linked data from unlinked data",
                   spinner=None) as bar:  # type: ignore
        for item in ot_fixed:
            if item in unlinked:
                unlinked.remove(item)
            bar()
    aod_list: list[dict[str, Any]] = []
    with alive_bar(len(aod_dict),
                   title="Translating AOD dict to a list",
                   spinner=None) as bar:  # type: ignore
        for _, value in aod_dict.items():
            if "otakotaku" not in value:
                value["otakotaku"] = None
            aod_list.append(value)
            bar()
    merged: list[dict[str, Any]] = []
    merged.extend(aod)

    # add missing items from old AOD data
    with alive_bar(len(aod_list),
                   title="Adding missing items from old AOD data",
                   spinner=None) as bar:  # type: ignore
        for item in aod_list:
            if item not in aod:
                merged.append(item)
            bar()

    aod_list = merged
    pprint.print(
        Platform.OTAKOTAKU,
        Status.PASS,
        "Otak Otaku entries linked to MyAnimeList ID, unlinked data will be saved to otakotaku_unlinked.json.",
        "Total linked data:",
        f"{len(ot_fixed)},",
        "total unlinked data:",
        f"{len(unlinked)}",
    )
    with open("database/raw/otakotaku_unlinked.json", "w", encoding="utf-8") as file:
        json.dump(unlinked, file)
    return aod_list


def link_silveryasha_to_mal(
    silveryasha: list[dict[str, Any]],
    aod: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Link Silveryasha ID to MyAnimeList ID based similarity in title name over 85% in fuzzy search"""
    unlinked: list[dict[str, Any]] = []
    sy_fixed: list[dict[str, Any]] = []
    sy_dict: dict[str, Any] = {}
    aod_dict: dict[str, Any] = {}
    with alive_bar(len(aod),
                   title="Translating AOD list to a dict with MAL ID",
                   spinner=None) as bar:  # type: ignore
        for item in aod:
            if item["myanimelist"]:
                aod_dict[f"{item['myanimelist']}"] = item
            else:
                aod_dict[item["title"]] = item
            bar()
    with alive_bar(len(silveryasha),
                   title="Translating Silveryasha list to a dict with MAL ID",
                   spinner=None) as bar:  # type: ignore
        for item in silveryasha:
            mal_id = item["myanimelist"]
            if mal_id:
                sy_dict[f"{mal_id}"] = {
                    "title": item["title"],
                    "silveryasha": item["silveryasha"],
                }
            else:
                sy_dict[item["title"]] = {
                    "title": item["title"],
                    "silveryasha": item["silveryasha"],
                }
            bar()
    with alive_bar(len(sy_dict),
                   title="Linking Silveryasha ID to MyAnimeList ID",
                   spinner=None) as bar:  # type: ignore
        for mal_id, sy_item in sy_dict.items():
            if mal_id in aod_dict:
                aod_item: Union[dict[str, Any], None] = aod_dict.get(
                    f"{mal_id}", None)
                if aod_item:
                    # add more data from silveryasha
                    sy_dat = {
                        "silveryasha": sy_item["silveryasha"],
                    }
                    aod_item.update(sy_dat)
                    sy_fixed.append(aod_item)
                else:
                    unlinked.append(sy_item)
            else:
                unlinked.append(sy_item)
            bar()
    # on unlinked, fuzzy search the title name
    with alive_bar(len(unlinked),
                   title="Fuzzy searching unlinked data",
                   spinner=None) as bar:  # type: ignore
        for item in unlinked:
            title = item["title"]
            for aod_item in aod:
                aod_title = aod_item["title"]
                ratio = fuzz.ratio(title, aod_title)  # type: ignore
                if ratio >= 85:
                    sy_dat = {
                        "silveryasha": item["silveryasha"],
                    }
                    aod_item.update(sy_dat)
                    sy_fixed.append(aod_item)
                    # in unlinked, remove the item with the same id
                    for item in unlinked:
                        if item["silveryasha"] == sy_id:
                            unlinked.remove(item)
                            break
                    break
            bar()
    # load manual link data
    with open("database/raw/silveryasha_manual.json", "r", encoding="utf-8") as file:
        manual_link: dict[str, int] = json.load(file)
    with alive_bar(len(manual_link),
                   title="Linking manually linked data",
                   spinner=None) as bar:  # type: ignore
        for title, sy_id in manual_link.items():
            for aod_item in aod:
                aod_title = aod_item["title"]
                if title == aod_title:
                    sy_dat = {
                        "silveryasha": sy_id,
                    }
                    aod_item.update(sy_dat)
                    sy_fixed.append(aod_item)
                    # in unlinked, remove the item with the same id
                    for item in unlinked:
                        if item["silveryasha"] == sy_id:
                            unlinked.remove(item)
                    break
            bar()
    # remove if unlinked data is already linked
    with alive_bar(len(sy_fixed),
                   title="Removing linked data from unlinked data",
                   spinner=None) as bar:  # type: ignore
        for item in sy_fixed:
            if item in unlinked:
                unlinked.remove(item)
            bar()
    aod_list: list[dict[str, Any]] = []
    with alive_bar(len(aod_dict),
                   title="Translating AOD dict to a list",
                   spinner=None) as bar:  # type: ignore
        for _, value in aod_dict.items():
            if "silveryasha" not in value:
                value["silveryasha"] = None
            aod_list.append(value)
            bar()
    merged: list[dict[str, Any]] = []
    merged.extend(aod)

    # add missing items from old AOD data
    with alive_bar(len(aod_list),
                   title="Adding missing items from old AOD data",
                   spinner=None) as bar:  # type: ignore
        for item in aod_list:
            if item not in aod:
                merged.append(item)
            bar()

    aod_list = merged
    pprint.print(
        Platform.SILVERYASHA,
        Status.PASS,
        "Silveryasha entry linked to MyAnimeList ID, unlinked data will be saved to silveryasha_unlinked.json.",
        "Total linked data:",
        f"{len(sy_fixed)},",
        "total unlinked data:",
        f"{len(unlinked)}",
    )
    with open("database/raw/silveryasha_unlinked.json", "w", encoding="utf-8") as file:
        json.dump(unlinked, file)
    return aod_list


def combine_arm(
    arm: list[dict[str, Any]],
    aod: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Combine ARM data with AOD data"""
    linked = 0
    with alive_bar(len(aod),
                   title="Combining ARM data with AOD data",
                   spinner=None) as bar:  # type: ignore
        for item in aod:
            myanimelist = item['myanimelist']
            anilist = item['anilist']
            # Skip if both myanimelist and anilist are null
            if myanimelist is None and anilist is None:
                item.update({
                    'shoboi': None,
                    'annict': None,
                })
                bar()
                continue

            # Check if mal_id and anilist_id exist in arm_data
            for arm_item in arm:
                mal_id = arm_item.get('mal_id', None)
                anilist_id = arm_item.get('anilist_id', None)
                syoboi = arm_item.get('syobocal_tid', None)
                annict = arm_item.get('annict_id', None)
                if myanimelist is not None and mal_id == myanimelist:
                    # Combine the data from arm_item with the item in aod_data
                    item.update({
                        'shoboi': syoboi,
                        'annict': annict,
                        'anilist': anilist if anilist is not None else anilist_id,
                    })

                    linked += 1
                    break
                elif anilist is not None and anilist_id == anilist:
                    # Combine the data from arm_item with the item in aod_data
                    item.update({
                        'shoboi': syoboi,
                        'annict': annict,
                        'myanimelist': myanimelist if myanimelist is not None else mal_id,
                        'shikimori': myanimelist if myanimelist is not None else mal_id,
                    })
                    linked += 1
                    break
            bar()
    pprint.print(
        Platform.ARM,
        Status.PASS,
        "ARM data combined with AOD data.",
        "Total linked data:",
        f"{linked},",
        "AOD data:",
        f"{len(aod)}",
    )
    return aod


def combine_anitrakt(
    anitrakt: list[dict[str, Any]],
    aod: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Combine AniTrakt data with AOD data"""
    linked = 0
    with alive_bar(len(aod),
                   title="Combining AniTrakt data with AOD data",
                   spinner=None) as bar:  # type: ignore
        for item in aod:
            matched = False
            myanimelist = item['myanimelist']
            # Skip if both myanimelist and anilist are null
            if myanimelist is None:
                item.update({
                    'trakt': None,
                    'trakt_type': None,
                    'trakt_season': None,
                })
                bar()
                continue

            # Check if mal_id and anilist_id exist in anitrakt_data
            for anitrakt_item in anitrakt:
                mal_id = anitrakt_item.get('mal_id', None)
                trakt = anitrakt_item.get('trakt_id', None)
                media_type = anitrakt_item.get('type', None)
                media_season = anitrakt_item.get('season', None)
                if myanimelist is not None and mal_id == myanimelist:
                    # Combine the data from anitrakt_item with the item in aod_data
                    item.update({
                        'trakt': trakt,
                        'trakt_type': media_type,
                        'trakt_season': media_season,
                    })
                    linked += 1
                    matched = True
                    break

            if not matched:
                item.update({
                    'trakt': None,
                    'trakt_type': None,
                    'trakt_season': None,
                })
            bar()
    pprint.print(
        Platform.ANITRAKT,
        Status.PASS,
        "AniTrakt data combined with AOD data.",
        "Total linked data:",
        f"{linked},",
        "AOD data:",
        f"{len(aod)}",
    )
    return aod


def combine_fribb(
    fribb: list[dict[str, Any]],
    aod: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Combine Fribb's Animelists data with AOD data to obtain IMDb and TMDB IDs via AniDB"""
    linked = 0
    with alive_bar(len(aod),
                   title="Combining Fribb's Animelists data with AOD data",
                   spinner=None) as bar:  # type: ignore
        for item in aod:
            matched = False
            anidb = item['anidb']
            # Skip if anidb is null
            if anidb is None:
                item.update({
                    'imdb': None,
                    'themoviedb': None,
                })
                bar()
                continue

            # Check if anidb_id exist in fribb_data
            for fbi in fribb:
                anidb_id = fbi.get('anidb_id', None)
                imdb = fbi.get('imdb_id', None)
                tmdb: str | int | None = fbi.get('themoviedb_id', None)
                if anidb is not None and anidb_id == anidb:
                    # Combine the data from fribb_item with the item in aod_data
                    data_fbi = {}
                    data_fbi['imdb'] = imdb
                    if isinstance(tmdb, str):
                        tmdbl = tmdb.split(",")
                        tmdb = int(tmdbl[0])
                    data_fbi['themoviedb'] = tmdb
                    item.update(data_fbi)
                    linked += 1
                    matched = True
                    break

            if not matched:
                item.update({
                    'imdb': None,
                    'themoviedb': None,
                })
            bar()
    pprint.print(
        Platform.FRIBB,
        Status.PASS,
        "Fribb's Animelists data combined with AOD data.",
        "Total linked data:",
        f"{linked},",
        "AOD data:",
        f"{len(aod)}",
    )
    return aod

def save_to_file(data: list[dict[str, Any]], platform: str) -> None:
    """Save data to file"""
    items: list[dict[str, Any]] = []
    with alive_bar(len(data),
                   title="Removing None values",
                   spinner=None) as bar:  # type: ignore
        for item in data:
            # if platform key in item not None, then add it to items
            pkey = item.get(f"{platform}", None)
            if pkey is not None:
                items.append(item)
            bar()
    with open(f"database/{platform}.json", "w", encoding="utf-8") as file:
        json.dump(items, file)
    # save object-formatted data to file
    obj_data: dict[str, dict[str, Any]] = {}
    with alive_bar(len(items),
                   title="Converting data to object format",
                   spinner=None) as bar:  # type: ignore
        for item in items:
            if platform not in ["trakt", "themoviedb"]:
                obj_data[item[f"{platform}"]] = item
            elif platform == "trakt":
                if item["trakt_type"] in ["movie", "movies"]:
                    obj_data[f"{item['trakt_type']}/{item['trakt']}"] = item
                else:
                    if item["trakt_season"] == 1:
                        obj_data[f"{item['trakt_type']}/{item['trakt']}"] = item
                    obj_data[f"{item['trakt_type']}/{item['trakt']}/seasons/{item['trakt_season']}"] = item
            # elif platform == "themoviedb":
            #     if item["themoviedb_type"] == "movie":
            #         obj_data[f"{item['themoviedb_type']}/{item['themoviedb']}"] = item
            #     else:
            #         if item["themoviedb_season"] == 1:
            #             obj_data[f"{item['themoviedb_type']}/{item['themoviedb']}"] = item
            #         obj_data[f"{item['themoviedb_type']}/{item['themoviedb']}/season/{item['themoviedb_season']}"] = item
            elif platform == "themoviedb":
                obj_data[f"movie/{item['themoviedb']}"] = item
            bar()
    with open(f"database/{platform}_object.json", "w", encoding="utf-8") as file:
        json.dump(obj_data, file)
    # update attribution
    attribution["counts"][f"{platform}"] = len(items)  # type: ignore
    return None


def save_platform_loop(data: list[dict[str, Any]]) -> None:
    """Loop through platforms and save data to file"""
    platforms = [
        "anidb",
        "anilist",
        "animeplanet",
        "anisearch",
        "annict",
        "imdb",
        "kaize",
        "kitsu",
        "livechart",
        "myanimelist",
        "notify",
        "otakotaku",
        "shikimori",
        "shoboi",
        "silveryasha",
        "trakt",
        "themoviedb",
    ]
    # sort key in data
    pprint.print(
        Platform.SYSTEM,
        Status.INFO,
        "Sorting data by title",
    )
    data = sorted(data, key=lambda k: k["title"])
    for plat in platforms:
        match plat:
            case "anidb":
                name = Platform.ANIDB
            case "anilist":
                name = Platform.ANILIST
            case "animeplanet":
                name = Platform.ANIMEPLANET
            case "anisearch":
                name = Platform.ANISEARCH
            case "annict":
                name = Platform.ANNICT
            case "imdb":
                name = Platform.IMDB
            case "kaize":
                name = Platform.KAIZE
            case "kitsu":
                name = Platform.KITSU
            case "livechart":
                name = Platform.LIVECHART
            case "myanimelist":
                name = Platform.MYANIMELIST
            case "notify":
                name = Platform.NOTIFY
            case "otakotaku":
                name = Platform.OTAKOTAKU
            case "shikimori":
                name = Platform.SHIKIMORI
            case "shoboi":
                name = Platform.SHOBOI
            case "silveryasha":
                name = Platform.SILVERYASHA
            case "trakt":
                name = Platform.ANITRAKT
            case "themoviedb":
                name = Platform.TMDB
            case _:
                name = Platform.SYSTEM
        pprint.print(
            name,
            Status.INFO,
            f"Saving data to {plat}.json",
        )
        save_to_file(data, plat)
    return None


def save_list_to_tsv(data: list[dict[str, Any]], file_path: str) -> None:
    """Save list to TSV"""
    with open(f"{file_path}.tsv", "w", encoding="utf-8", newline="") as file_:
        writer = csv.writer(file_, delimiter="\t", lineterminator="\n")
        writer.writerow(data[0].keys())
        with alive_bar(len(data),
                       title="Saving data to TSV",
                       spinner=None) as bar:  # type: ignore
            for item in data:
                writer.writerow(item.values())
                bar()
    return None


def update_attribution(data: list[dict[str, Any]]) -> None:
    """Update attribution"""
    pprint.print(
        Platform.SYSTEM,
        Status.INFO,
        "Save data to JSON",
    )
    with open("database/animeapi.json", "w", encoding="utf-8") as file_:
        json.dump(data, file_)
    pprint.print(
        Platform.SYSTEM,
        Status.INFO,
        "Save data to TSV",
    )
    save_list_to_tsv(data, "database/animeapi")

    pprint.print(
        Platform.SYSTEM,
        Status.INFO,
        "Updating attribution",
    )
    now = datetime.now(tz=timezone.utc)
    attribution["updated"]["iso"] = now.isoformat()  # type: ignore
    attribution["updated"]["timestamp"] = int(now.timestamp())  # type: ignore
    populate_contributors()

    total_data = len(data)
    save_platform_loop(data)

    attribution["counts"]["total"] = total_data  # type: ignore
    with open("api/status.json", "w", encoding="utf-8") as file:
        json.dump(attribution, file)
    pprint.print(
        Platform.SYSTEM,
        Status.PASS,
        "Attribution updated",
    )
    return None

def add_spaces(data: int, spaces_max: int = 9) -> str:
    """Add spaces to data"""
    spaces = spaces_max - len(f"{data}")
    return f"{' ' * spaces}{data}"

def update_markdown() -> None:
    """Update counters in README.md by looking <!-- counters --><!-- /counters -->"""
    pprint.print(
        Platform.SYSTEM,
        Status.INFO,
        "Updating counters in README.md",
    )
    with open("README.md", "r", encoding="utf-8") as file:
        readme = file.read()
    counts: dict[str, int] = attribution["counts"]  # type: ignore
    adb = add_spaces(counts["anidb"])
    anl = add_spaces(counts["anilist"])
    apl = add_spaces(counts["animeplanet"])
    ase = add_spaces(counts["anisearch"])
    anc = add_spaces(counts["annict"])
    idb = add_spaces(counts["imdb"])
    kze = add_spaces(counts["kaize"])
    kts = add_spaces(counts["kitsu"])
    lvc = add_spaces(counts["livechart"])
    mal = add_spaces(counts["myanimelist"])
    ntf = add_spaces(counts["notify"])
    ook = add_spaces(counts["otakotaku"])
    shk = add_spaces(counts["shikimori"])
    shb = add_spaces(counts["shoboi"])
    sys = add_spaces(counts["silveryasha"])
    tmd = add_spaces(counts["themoviedb"])
    trk = add_spaces(counts["trakt"])
    ttl = counts["total"]
    table = f"""| Platform           |            ID |     Count |
| :----------------- | ------------: | --------: |
| aniDB              |       `anidb` | {adb} |
| AniList            |     `anilist` | {anl} |
| Anime-Planet       | `animeplanet` | {apl} |
| aniSearch          |   `anisearch` | {ase} |
| Annict             |      `annict` | {anc} |
| IMDb               |        `imdb` | {idb} |
| Kaize              |       `kaize` | {kze} |
| Kitsu              |       `kitsu` | {kts} |
| LiveChart          |   `livechart` | {lvc} |
| MyAnimeList        | `myanimelist` | {mal} |
| Notify.moe         |      `notify` | {ntf} |
| Otak Otaku         |   `otakotaku` | {ook} |
| Shikimori          |   `shikimori` | {shk} |
| Shoboi/Syobocal    |      `shoboi` | {shb} |
| Silver Yasha       | `silveryasha` | {sys} |
| The Movie Database |  `themoviedb` | {tmd} |
| Trakt              |       `trakt` | {trk} |
|                    |               |           |
|                    |     **Total** | **{ttl}** |
"""
    readme = re.sub(
        r"<!-- counters -->(.|\n)*<!-- \/counters -->",
        f"<!-- counters -->\n{table}<!-- /counters -->",
        readme,
    )

    pprint.print(
        Platform.SYSTEM,
        Status.INFO,
        "Updating status example in README.md",
    )
    status = json.dumps(attribution, indent=2, ensure_ascii=False).replace('\\', '\\\\')
    readme = re.sub(
        r"<!-- status -->(.|\n)*<!-- \/status -->",
        f"<!-- status -->\n```json\n{status}\n```\n<!-- /status -->",
        readme,
    )

    pprint.print(
        Platform.SYSTEM,
        Status.INFO,
        "Updating updated timestamp in README.md",
    )
    # update updated timestamp
    now: int = attribution["updated"]["timestamp"]  # type: ignore
    readme = re.sub(
        r"<!-- updated -->(.|\n)*<!-- \/updated -->",
        f"<!-- updated -->\nLast updated: {datetime.fromtimestamp(now).strftime('%d %B %Y %H:%M:%S UTC')}\n<!-- /updated -->",
        readme,
    )
    formatted_time = datetime.utcfromtimestamp(now).strftime("%m/%d/%Y %H:%M:%S UTC")
    readme = re.sub(
        r"<!-- updated-txt -->(.|\n)*<!-- \/updated-txt -->",
        f"<!-- updated-txt -->\n```json\nUpdated on {formatted_time}\n```\n<!-- /updated-txt -->",
        readme,
    )

    pprint.print(
        Platform.SYSTEM,
        Status.INFO,
        "Updating JSON Schema in README.md",
    )
    with open("api/schema.json", "r", encoding="utf-8") as file:
        jschema = json.dumps(
            json.load(file),
            indent=2,
            ensure_ascii=False)
        jschema = jschema.replace("\\", "\\\\")
    readme = re.sub(
        r"<!-- jsonschema -->(.|\n)*<!-- \/jsonschema -->",
        f"<!-- jsonschema -->\n```json\n{jschema}\n```\n<!-- /jsonschema -->",
        readme
    )

    pprint.print(
        Platform.SYSTEM,
        Status.INFO,
        "Updating sample data in README.md, using MyAnimeList ID 1",
    )
    with open("database/myanimelist_object.json", "r", encoding="utf-8") as file:
        sample = json.load(file)
        sample = sample["1"]
        readme = re.sub(
            r"<!-- sample -->(.|\n)*<!-- \/sample -->",
            f"<!-- sample -->\n```json\n{json.dumps(sample, indent=2)}\n```\n<!-- /sample -->",
            readme,
        )

    pprint.print(
        Platform.SYSTEM,
        Status.INFO,
        "Updating sample data in README.md, using Trakt ID 152334, season 3",
    )
    with open("database/trakt_object.json", "r", encoding="utf-8") as file:
        sampler = json.load(file)
        readme = re.sub(
            r"<!-- trakt152334 -->(.|\n)*<!-- \/trakt152334 -->",
            f"<!-- trakt152334 -->\n```json\n{json.dumps(sampler['shows/152334/seasons/3'], indent=2)}\n```\n<!-- /trakt152334 -->",
            readme,
        )
    with open("README.md", "w", encoding="utf-8") as file:
        file.write(readme)
    pprint.print(
        Platform.SYSTEM,
        Status.PASS,
        "Counters updated in README.md",
    )
    return None


def check_git_any_changes() -> bool:
    """Check if there's any changes in git"""
    try:
        subprocess.check_output(["git", "diff", "--quiet"])
        pprint.print(
            Platform.SYSTEM,
            Status.INFO,
            "Git has no changes, skipping data update",
        )
        return False
    except subprocess.CalledProcessError:
        pprint.print(
            Platform.SYSTEM,
            Status.INFO,
            "Git has changes, updating data",
        )
        return True


def main() -> None:
    """Main function"""
    try:
        start_time = time()
        pprint.print(Platform.SYSTEM, Status.READY, "Generator ready to use")
        aod = get_anime_offline_database()
        aod_arr = simplify_aod_data(aod)
        kza = Kaize(
            session=KAIZE_SESSION,
            email=KAIZE_EMAIL,
            password=KAIZE_PASSWORD,
            xsrf_token=KAIZE_XSRF_TOKEN).get_anime()
        ota = OtakOtaku().get_anime()
        sy_ = simplify_silveryasha_data()
        arm = get_arm()
        anitrakt = get_anitrakt()
        fribb = get_fribb_animelists()
        git_changes = check_git_any_changes()
        if git_changes is True:
            pprint.print(Platform.SYSTEM, Status.INFO, "Generating data")
            pprint.print(Platform.KAIZE, Status.BUILD, "Linking Kaize slug to MyAnimeList ID")
            aod_arr = link_kaize_to_mal(kza, aod_arr)
            pprint.print(Platform.OTAKOTAKU, Status.BUILD, "Linking Otak Otaku ID to MyAnimeList ID")
            aod_arr = link_otakotaku_to_mal(ota, aod_arr)
            pprint.print(Platform.SILVERYASHA, Status.BUILD, "Linking Silveryasha ID to MyAnimeList ID")
            aod_arr = link_silveryasha_to_mal(sy_, aod_arr)
            pprint.print(Platform.ARM, Status.BUILD, "Combining ARM data with AOD data")
            aod_arr = combine_arm(arm, aod_arr)
            pprint.print(Platform.ANITRAKT, Status.BUILD, "Combining AniTrakt data with AOD data")
            aod_arr = combine_anitrakt(anitrakt, aod_arr)
            pprint.print(Platform.FRIBB, Status.BUILD, "Combining Fribb's Animelists data with AOD data")
            aod_arr = combine_fribb(fribb, aod_arr)
            final_arr: list[dict[str, Any]] = []
            with alive_bar(len(aod_arr),
                           title="Fixing missing keys",
                           spinner=None) as bar:  # type: ignore
                for item in aod_arr:
                    data = {
                        "title": item.get("title", None),
                        "anidb": item.get("anidb", None),
                        "anilist": item.get("anilist", None),
                        "animeplanet": item.get("animeplanet", None),
                        "anisearch": item.get("anisearch", None),
                        "annict": item.get("annict", None),
                        "imdb": item.get("imdb", None),
                        "kaize": item.get("kaize", None),
                        "kaize_id": item.get("kaize_id", None),
                        "kitsu": item.get("kitsu", None),
                        "livechart": item.get("livechart", None),
                        "myanimelist": item.get("myanimelist", None),
                        "notify": item.get("notify", None),
                        "otakotaku": item.get("otakotaku", None),
                        "shikimori": item.get("shikimori", None),
                        "shoboi": item.get("shoboi", None),
                        "silveryasha": item.get("silveryasha", None),
                        "themoviedb": item.get("themoviedb", None),
                        # "themoviedb_type": item.get("themoviedb_type", None),
                        # "themoviedb_season": item.get("themoviedb_season", None),
                        "trakt": item.get("trakt", None),
                        "trakt_type": item.get("trakt_type", None),
                        "trakt_season": item.get("trakt_season", None),
                    }
                    final_arr.append(data)
                    bar()
            with open("database/animeapi.json", "w", encoding="utf-8") as file:
                json.dump(final_arr, file)
        else:
            # get data from animeapi.json
            with open("database/animeapi.json", "r", encoding="utf-8") as file:
                final_arr = json.load(file)
        update_attribution(final_arr)
        update_markdown()
        counts: dict[str, int] = attribution["counts"]  # type: ignore
        print(f"""Data parsed:
* aniDB: {counts["anidb"]}
* AniList: {counts["anilist"]}
* Anime-Planet: {counts["animeplanet"]}
* aniSearch: {counts["anisearch"]}
* Annict: {counts["annict"]}
* IMDb: {counts["imdb"]}
* Kaize: {counts["kaize"]}
* Kitsu: {counts["kitsu"]}
* LiveChart.me: {counts["livechart"]}
* MyAnimeList: {counts["myanimelist"]}
* Notify.moe: {counts["notify"]}
* Otak-Otaku: {counts["otakotaku"]}
* Shikimori: {counts["shikimori"]}
* Shoboi: {counts["shoboi"]}
* Silveryasha: {counts["silveryasha"]}
* The Movie DB: {counts["themoviedb"]}
* Trakt: {counts["trakt"]}
""")
        end_time = time()
        pprint.print(
            Platform.SYSTEM,
            Status.INFO,
            f"Generator finished in {end_time - start_time:.2f} seconds",
        )
    except KeyboardInterrupt:
        print()
        pprint.print(Platform.SYSTEM, Status.ERR, "Stopped by user")
    except Exception as err:
        print()
        pprint.print(Platform.SYSTEM, Status.ERR, f"Error: {err}")
        traceback.print_exc()
        sys.exit(1)
    finally:
        pprint.print(Platform.SYSTEM, Status.INFO, "Exiting...")
        sys.exit(0)
