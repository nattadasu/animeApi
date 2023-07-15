import json
import os
import re
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
        "kaize": 0,
        "kitsu": 0,
        "livechart": 0,
        "myanimelist": 0,
        "notify": 0,
        "otakotaku": 0,
        "shikimori": 0,
        "shoboi": 0,
        "silveryasha": 0,
        "trakt": 0,
        "total": 0,
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
    pprint.print(
        Platform.KAIZE,
        Status.READY,
        "Linking Kaize slug to MyAnimeList ID",
    )
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
    pprint.print(
        Platform.ANIMEOFFLINEDATABASE,
        Status.DEBUG,
        "Fixing missing items in processed AOD data to old AOD data",
    )
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
    with open("database/raw/kaize_linked.json", "w", encoding="utf-8") as file:
        json.dump(kz_fixed, file)
    return aod_list


def link_otakotaku_to_mal(
    otakotaku: list[dict[str, Any]],
    aod: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Link Otakotaku slug to MyAnimeList ID based similarity in title name over 85% in fuzzy search"""
    pprint.print(
        Platform.OTAKOTAKU,
        Status.READY,
        "Linking Otakotaku slug to MyAnimeList ID",
    )
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
                   title="Linking Otakotaku slug to MyAnimeList ID",
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
    pprint.print(
        Platform.ANIMEOFFLINEDATABASE,
        Status.DEBUG,
        "Fixing missing items in processed AOD data to old AOD data",
    )
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
        "Otakotaku slug linked to MyAnimeList ID, unlinked data will be saved to otakotaku_unlinked.json.",
        "Total linked data:",
        f"{len(ot_fixed)},",
        "total unlinked data:",
        f"{len(unlinked)}",
    )
    with open("database/raw/otakotaku_unlinked.json", "w", encoding="utf-8") as file:
        json.dump(unlinked, file)
    with open("database/raw/otakotaku_linked.json", "w", encoding="utf-8") as file:
        json.dump(ot_fixed, file)
    return aod_list


def link_silveryasha_to_mal(
    silveryasha: list[dict[str, Any]],
    aod: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Link Silveryasha slug to MyAnimeList ID based similarity in title name over 85% in fuzzy search"""
    pprint.print(
        Platform.SILVERYASHA,
        Status.READY,
        "Linking Silveryasha slug to MyAnimeList ID",
    )
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
                   title="Linking Silveryasha slug to MyAnimeList ID",
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
    pprint.print(
        Platform.ANIMEOFFLINEDATABASE,
        Status.DEBUG,
        "Fixing missing items in processed AOD data to old AOD data",
    )
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
        "Silveryasha slug linked to MyAnimeList ID, unlinked data will be saved to silveryasha_unlinked.json.",
        "Total linked data:",
        f"{len(sy_fixed)},",
        "total unlinked data:",
        f"{len(unlinked)}",
    )
    with open("database/raw/silveryasha_unlinked.json", "w", encoding="utf-8") as file:
        json.dump(unlinked, file)
    with open("database/raw/silveryasha_linked.json", "w", encoding="utf-8") as file:
        json.dump(sy_fixed, file)
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
                    })
                    linked += 1
                    break
            bar()
    pprint.print(
        Platform.ARM,
        Status.PASS,
        "ARM data combined with AOD data, unlinked data will be saved to arm_unlinked.json.",
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
        "AniTrakt data combined with AOD data, unlinked data will be saved to anitrakt_unlinked.json.",
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
            if platform != "trakt":
                obj_data[item[f"{platform}"]] = item
            else:
                if item["trakt_type"] == "movie":
                    obj_data[f"{item['trakt_type']}/{item['trakt']}"] = item
                else:
                    if item["trakt_season"] == 1:
                        obj_data[f"{item['trakt_type']}/{item['trakt']}"] = item
                    obj_data[f"{item['trakt_type']}/{item['trakt']}/seasons/{item['trakt_season']}"] = item
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
            case _:
                name = Platform.SYSTEM
        pprint.print(
            name,
            Status.INFO,
            f"Saving data to {plat}.json",
        )
        save_to_file(data, plat)
    return None


def update_attribution(data: list[dict[str, Any]]) -> None:
    """Update attribution"""
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


def update_markdown() -> None:
    """Update counters in README.md by looking <!-- counters --><!-- /counters -->"""
    pprint.print(
        Platform.SYSTEM,
        Status.INFO,
        "Updating counters in README.md",
    )
    with open("README.md", "r", encoding="utf-8") as file:
        readme = file.read()
    table = "| Platform | Count |\n| --- | --- |\n"
    tram = ""
    for key, value in attribution["counts"].items():  # type: ignore
        if key == "total":
            tram = f"| **Total** | {value} |\n"
        else:
            table += f"| `{key}` | **{value}** |\n"
    table += tram
    readme = re.sub(
        r"<!-- counters -->(.|\n)*<!-- \/counters -->",
        f"<!-- counters -->\n{table}<!-- /counters -->",
        readme,
    )
    # update updated timestamp
    now: int = attribution["updated"]["timestamp"]  # type: ignore
    readme = re.sub(
        r"<!-- updated -->(.|\n)*<!-- \/updated -->",
        f"<!-- updated -->\nLast updated: {datetime.fromtimestamp(now).strftime('%d %B %Y %H:%M:%S UTC')}\n<!-- /updated -->",
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


def main() -> None:
    """Main function"""
    try:
        start_time = time()
        pprint.print(Platform.SYSTEM, Status.READY, "Generator ready to use")
        aod = get_anime_offline_database()
        aod_arr = simplify_aod_data(aod)
        kz_ = Kaize(
            session=KAIZE_SESSION,
            email=KAIZE_EMAIL,
            password=KAIZE_PASSWORD,
            xsrf_token=KAIZE_XSRF_TOKEN)
        kza = kz_.get_anime()
        aod_arr = link_kaize_to_mal(kza, aod_arr)
        ot_ = OtakOtaku()
        ota = ot_.get_anime()
        aod_arr = link_otakotaku_to_mal(ota, aod_arr)
        sy_ = simplify_silveryasha_data()
        aod_arr = link_silveryasha_to_mal(sy_, aod_arr)
        arm = get_arm()
        aod_arr = combine_arm(arm, aod_arr)
        anitrakt = get_anitrakt()
        aod_arr = combine_anitrakt(anitrakt, aod_arr)
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
                    "trakt": item.get("trakt", None),
                    "trakt_type": item.get("trakt_type", None),
                    "trakt_season": item.get("trakt_season", None),
                }
                final_arr.append(data)
                bar()
        update_attribution(final_arr)
        with open("database/animeapi.json", "w", encoding="utf-8") as file:
            json.dump(final_arr, file)
        end_time = time()
        pprint.print(
            Platform.SYSTEM,
            Status.INFO,
            f"Generator finished in {end_time - start_time:.2f} seconds",
        )
        update_markdown()
        counts: dict[str, int] = attribution["counts"]  # type: ignore
        print(f"""Data parsed:
* aniDB: {counts["anidb"]}
* AniList: {counts["anilist"]}
* Anime-Planet: {counts["animeplanet"]}
* aniSearch: {counts["anisearch"]}
* Annict: {counts["annict"]}
* Kaize: {counts["kaize"]}
* Kitsu: {counts["kitsu"]}
* LiveChart.me: {counts["livechart"]}
* MyAnimeList: {counts["myanimelist"]}
* Notify.moe: {counts["notify"]}
* Otak-Otaku: {counts["otakotaku"]}
* Shikimori: {counts["shikimori"]}
* Shoboi: {counts["shoboi"]}
* Silveryasha: {counts["silveryasha"]}
* Trakt: {counts["trakt"]}
""")
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
