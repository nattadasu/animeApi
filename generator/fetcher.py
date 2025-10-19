# SPDX-License-Identifier: AGPL-3.0-only AND MIT

import json
from typing import Any

from alive_progress import alive_bar  # type: ignore
from aod_entry import AodEntry
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
        url="https://github.com/manami-project/anime-offline-database/releases/download/latest/anime-offline-database-minified.json",
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
    Get info from rensetsu/db.trakt.extended-anitrakt

    :return: Extended AniTrakt data; merged TV and movie data
    :rtype: list[dict[str, Any]]
    """
    base_url = (
        "https://raw.githubusercontent.com/rensetsu/db.trakt.extended-anitrakt/main/"
    )
    ddump_tv = Downloader(
        url=f"{base_url}tv_ex.json",
        file_name="anitrakt_tv",
        file_type="json",
        platform=Platform.ANITRAKT,
    )
    data_tv: list[dict[str, Any]] = ddump_tv.dumper()

    ddump_movie = Downloader(
        url=f"{base_url}movies_ex.json",
        file_name="anitrakt_movie",
        file_type="json",
        platform=Platform.ANITRAKT,
    )
    data_movie: list[dict[str, Any]] = ddump_movie.dumper()

    # Merge TV and movie data
    data = data_tv + data_movie
    with open("database/raw/anitrakt.json", "w", encoding="utf-8") as file:
        json.dump(data, file)
    pprint.print(
        Platform.ANITRAKT,
        Status.PASS,
        "Completely compiled Extended AniTrakt data",
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
    Convert AOD data to a format that is easier to work with.

    This function now uses AodEntry dataclass to smartly parse entries and
    handles duplicate titles by merging entries with no overlapping IDs.

    When multiple entries have the same title:
    - If they have NO overlapping IDs: They are the same anime from different
      sources and should be merged to create a complete entry.
    - If they have overlapping IDs: They represent different entries that
      somehow got the same title (shouldn't happen in AOD).

    :param aod: AOD data
    :type aod: dict[str, Any]
    :return: Simplified AOD data
    :rtype: list[dict[str, Any]]
    """
    data: list[dict[str, Any]] = []
    items: list[dict[str, Any]] = aod["data"]

    # Track entries by title to handle duplicates
    title_to_entries: dict[str, list[AodEntry]] = {}

    with alive_bar(
        len(items), title="Parsing AOD data with smart entry detection", spinner=None
    ) as bar:  # type: ignore
        for item in items:
            entry = AodEntry.from_aod_dict(item)
            title = entry.title

            if title not in title_to_entries:
                title_to_entries[title] = [entry]
            else:
                # Try to merge with existing entries that have the same title
                merged = False
                for i, existing_entry in enumerate(title_to_entries[title]):
                    if not entry.has_overlapping_ids(existing_entry):
                        # No overlapping IDs - these are different representations
                        # of the same anime. Merge them!
                        from aod_entry import merge_aod_entries_if_compatible

                        merged_entry = merge_aod_entries_if_compatible(
                            existing_entry, entry
                        )
                        if merged_entry:
                            # Replace the existing entry with the merged one
                            title_to_entries[title][i] = merged_entry
                            merged = True
                            break
                    # If has overlapping IDs, skip and check next entry

                if not merged:
                    # Could not merge with any existing entry, add as separate
                    title_to_entries[title].append(entry)
            bar()

    # Convert all entries to simplified dict format
    with alive_bar(
        sum(len(entries) for entries in title_to_entries.values()),
        title="Converting entries to simplified format",
        spinner=None,
    ) as bar:  # type: ignore
        for entries in title_to_entries.values():
            for entry in entries:
                data.append(entry.to_simplified_dict())
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
