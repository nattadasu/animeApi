# SPDX-License-Identifier: AGPL-3.0-only AND MIT

import json
from typing import Any

from alive_progress import alive_bar  # type: ignore
from const import pprint
from downloader import Downloader
from prettyprint import Platform, Status


def get_anime_offline_database() -> dict[str, Any]:
    """
    Get info from manami-project/anime-offline-database

    :return: AOD data
    :rtype: dict[str, Any]
    """
    ddump = Downloader(
        url="https://raw.githubusercontent.com/manami-project/anime-offline-database/master/anime-offline-database-minified.json",
        file_name="aod",
        file_type="json",
        platform=Platform.ANIMEOFFLINEDATABASE,
    )
    content: dict[str, Any] = ddump.dumper()
    pprint.print(
        Platform.ANIMEOFFLINEDATABASE,
        Status.PASS,
        "anime-offline-database data retrieved successfully",
    )
    return content


def get_arm() -> list[dict[str, Any]]:
    """
    Get info from kawaiioverflow/arm

    :return: ARM data
    :rtype: list[dict[str, Any]]
    """
    ddump = Downloader(
        url="https://raw.githubusercontent.com/kawaiioverflow/arm/master/arm.json",
        file_name="arm",
        file_type="json",
        platform=Platform.ARM,
    )
    data: list[dict[str, Any]] = ddump.dumper()
    pprint.print(
        Platform.ARM,
        Status.PASS,
        "ARM data retrieved successfully",
    )
    return data


def get_anitrakt() -> list[dict[str, Any]]:
    """
    Get info from ryuuganime/aniTrakt-IndexParser

    :return: AniTrakt data; merged TV and movie data
    :rtype: list[dict[str, Any]]
    """
    base_url = "https://raw.githubusercontent.com/rensetsu/db.trakt.anitrakt/main/db/"
    ddump_tv = Downloader(
        url=f"{base_url}tv.json",
        file_name="anitrakt_tv",
        file_type="json",
        platform=Platform.ANITRAKT,
    )
    data_tv: list[dict[str, Any]] = ddump_tv.dumper()

    ddump_movie = Downloader(
        url=f"{base_url}movies.json",
        file_name="anitrakt_movie",
        file_type="json",
        platform=Platform.ANITRAKT,
    )
    data_movie: list[dict[str, Any]] = ddump_movie.dumper()
    with alive_bar(
        len(data_movie), title="Fixing AniTrakt data for movie", spinner=None
    ) as bar:  # type: ignore
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
    """
    Get info from Silveryasha. However due to Cloudflare protection, we need to
    manually download the data and save it to database/raw/silveryasha.json
    instead of using Downloader class, until we can find a way to bypass it.

    :return: Silveryasha data
    :rtype: list[dict[str, Any]]
    """
    ddump = Downloader(
        url="https://raw.githubusercontent.com/rensetsu/db.rensetsu.public-dump/main/Silveryasha/silveryasha_raw.json",
        file_name="silveryasha",
        file_type="json",
        platform=Platform.SILVERYASHA,
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
    """
    Get info from Fribb's Animelists for IMDb and TMDB IDs

    :return: Fribb's Animelists data
    :rtype: list[dict[str, Any]]
    """
    ddump = Downloader(
        url="https://raw.githubusercontent.com/Fribb/anime-lists/master/anime-lists-reduced.json",
        file_name="fribb_animelists",
        file_type="json",
        platform=Platform.FRIBB,
    )
    data: list[dict[str, Any]] = ddump.dumper()
    pprint.print(
        Platform.FRIBB,
        Status.PASS,
        "Fribb's Animelists data retrieved successfully",
    )
    return data


def simplify_aod_data(aod: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Convert AOD data to a format that is easier to work with

    :param aod: AOD data
    :type aod: dict[str, Any]
    :return: Simplified AOD data
    :rtype: list[dict[str, Any]]
    """
    data: list[dict[str, Any]] = []
    items: list[dict[str, Any]] = aod["data"]
    with alive_bar(len(items), title="Simplifying AOD data", spinner=None) as bar:  # type: ignore
        for item in items:
            adb_id: int | None = None
            al_id: int | None = None
            ap_slug: str | None = None
            as_id: int | None = None
            kt_id: int | None = None
            lc_id: int | None = None
            mal_id: int | None = None
            ntf_b64: str | None = None
            smk_id: int | None = None
            for sauce in item["sources"]:
                if sauce.startswith("https://anidb.net/anime/"):
                    adb_id = int(sauce.split("/")[-1])
                elif sauce.startswith("https://anilist.co/anime/"):
                    al_id = int(sauce.split("/")[-1])
                elif sauce.startswith("https://anime-planet.com/anime/"):
                    ap_slug = sauce.split("/")[-1]
                elif sauce.startswith("https://anisearch.com/anime/"):
                    as_id = int(sauce.split("/")[-1])
                elif sauce.startswith("https://kitsu.io/anime/") or sauce.startswith(
                    "https://kitsu.app/anime/"
                ):
                    kt_id = int(sauce.split("/")[-1])
                elif sauce.startswith("https://livechart.me/anime/"):
                    lc_id = int(sauce.split("/")[-1])
                elif sauce.startswith("https://myanimelist.net/anime/"):
                    mal_id = int(sauce.split("/")[-1])
                elif sauce.startswith("https://notify.moe/anime/"):
                    ntf_b64 = sauce.split("/")[-1]
                elif sauce.startswith("https://simkl.com/anime/"):
                    smk_id = int(sauce.split("/")[-1])
            data.append(
                {
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
                    "simkl": smk_id,
                }
            )
            bar()
    pprint.print(
        Platform.ANIMEOFFLINEDATABASE,
        Status.PASS,
        "AOD data simplified successfully, total data:",
        f"{len(data)}",
    )
    return data


def simplify_silveryasha_data() -> list[dict[str, Any]]:
    """
    Simplify data from silveryasha

    :return: Simplified Silveryasha data
    :rtype: list[dict[str, Any]]
    """
    final: list[dict[str, Any]] = []
    data = get_silveryasha()
    with alive_bar(
        len(data), title="Simplifying Silveryasha data", spinner=None
    ) as bar:  # type: ignore
        for item in data:
            final.append(
                {
                    "title": item["title"],
                    "alternative_titles": item["title_alt"],
                    "silveryasha": item["id"],
                    "myanimelist": item["mal_id"],
                }
            )
            bar()
    return final
