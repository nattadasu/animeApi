# SPDX-License-Identifier: AGPL-3.0-only AND MIT

import csv
import json
import re
from datetime import datetime, timezone
from typing import Any

import pandas as pd
import requests
from alive_progress import alive_bar  # type: ignore
from const import pprint
from prettyprint import Platform, Status


def populate_contributors(attr: dict[str, Any]) -> dict[str, Any]:
    """
    Read total contributors from GitHub API

    :param attr: attribution dict
    :type attr: dict[str, Any]
    :return: attribution dict that has been updated
    :rtype: dict[str, Any]
    """
    response = requests.get(
        "https://api.github.com/repos/nattadasu/animeApi/contributors?per_page=100",
        headers={
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "nattadasu/animeApi",
        },
    )
    if response.status_code == 200:
        # clear the list first
        attr["contributors"] = []
        attr["contributors"] = [contributor["login"] for contributor in response.json()]
    return attr


def save_to_file(
    data: list[dict[str, Any]], platform: str, attr: dict[str, Any]
) -> None:
    """
    Save data to file

    :param data: data to save
    :type data: list[dict[str, Any]]
    :param platform: platform name
    :type platform: str
    :param attr: attribution dict
    :type attr: dict[str, Any]
    :return: None
    :rtype: None
    """
    items: list[dict[str, Any]] = []
    with alive_bar(len(data), title="Removing None values", spinner=None) as bar:  # type: ignore
        for item in data:
            # Special handling for letterboxd and thetvdb
            if platform == "letterboxd":
                pkey = item.get("letterboxd_slug", None)
            else:
                pkey = item.get(f"{platform}", None)

            if pkey is not None:
                items.append(item)
            bar()
    # with open(f"database/{platform}.json", "w", encoding="utf-8") as file:
    #     json.dump(items, file)
    # save object-formatted data to file
    obj_data: dict[str, dict[str, Any]] = {}
    with alive_bar(
        len(items), title="Converting data to object format", spinner=None
    ) as bar:  # type: ignore
        for item in items:
            if platform not in ["trakt", "themoviedb", "thetvdb", "letterboxd"]:
                obj_data[item[f"{platform}"]] = item
            elif platform == "letterboxd":
                # Use letterboxd_slug for lookup
                if item.get("letterboxd_slug"):
                    obj_data[item["letterboxd_slug"]] = item
            elif platform == "thetvdb":
                # Use thetvdb for lookup
                thetvdb_id = item.get("thetvdb")
                trakt_season = item.get("trakt_season")
                tvdb_sid = item.get("thetvdb_season_id")
                if thetvdb_id:
                    # Base entry: series/entry_id
                    base_key = f"series/{thetvdb_id}"
                    if trakt_season is None or trakt_season == 1:
                        obj_data[base_key] = item
                    # Season entry: series/entry_id/seasons/season_number
                    if trakt_season is not None:
                        season_key = f"{base_key}/seasons"
                        obj_data[f"{season_key}/{trakt_season}"] = item
                        obj_data[f"{season_key}/{tvdb_sid}"] = item
            elif platform == "trakt":
                if item["trakt_type"] in ["movie", "movies"]:
                    obj_data[f"{item['trakt_type']}/{item['trakt']}"] = item
                else:
                    trakt_season = item["trakt_season"]
                    if trakt_season:
                        obj_data[
                            f"{item['trakt_type']}/{item['trakt']}/seasons/{trakt_season}"
                        ] = item
                        if trakt_season == 1:
                            obj_data[f"{item['trakt_type']}/{item['trakt']}"] = item

            elif platform == "themoviedb":
                themoviedb_type = item.get("themoviedb_type", "movie")
                themoviedb_id = item.get("themoviedb")
                trakt_season = item.get("trakt_season")
                if themoviedb_id:
                    # Base entry: type/entry_id
                    base_key = f"{themoviedb_type}/{themoviedb_id}"
                    if trakt_season is None or trakt_season == 1:
                        obj_data[base_key] = item
                    # Season entry for TV: type/entry_id/season/season_number
                    if themoviedb_type == "tv":
                        season_key = f"{base_key}/season"
                        if trakt_season:
                            obj_data[f"{season_key}/{trakt_season}"] = item
                        if item["themoviedb_season_id"]:
                            obj_data[
                                f"{season_key}/{item['themoviedb_season_id']}"
                            ]: item
            bar()
    # with open(f"database/{platform}_object.json", "w", encoding="utf-8") as file:
    #     json.dump(obj_data, file)
    # update attr
    attr["counts"][f"{platform}"] = len(items)  # type: ignore
    return None


def save_platform_loop(
    data: list[dict[str, Any]], attr: dict[str, Any]
) -> dict[str, Any]:
    """
    Loop through platforms and save data to file

    :param data: data to save
    :type data: list[dict[str, Any]]
    :param attr: attribution dict
    :type attr: dict[str, Any]
    :return: attribution dict that has been updated
    :rtype: dict[str, Any]
    """
    platforms = [
        "anidb",
        "anilist",
        "animenewsnetwork",
        "animeplanet",
        "anisearch",
        "annict",
        "imdb",
        "kaize",
        "kitsu",
        "letterboxd",
        "livechart",
        "myanimelist",
        "nautiljon",
        "notify",
        "otakotaku",
        "shikimori",
        "shoboi",
        "silveryasha",
        "simkl",
        "themoviedb",
        "thetvdb",
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
            case "animenewsnetwork":
                name = Platform.ANIMENEWSNETWORK
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
            case "letterboxd":
                name = Platform.LETTERBOXD
            case "livechart":
                name = Platform.LIVECHART
            case "myanimelist":
                name = Platform.MYANIMELIST
            case "nautiljon":
                name = Platform.NAUTILJON
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
            case "simkl":
                name = Platform.SIMKL
            case "themoviedb":
                name = Platform.TMDB
            case "thetvdb":
                name = Platform.TVDB
            case "trakt":
                name = Platform.ANITRAKT
            case _:
                name = Platform.SYSTEM
        pprint.print(
            name,
            Status.INFO,
            f"Saving data to {plat}.json",
        )
        save_to_file(data, plat, attr)
    return attr


def save_list_to_tsv(data: list[dict[str, Any]], file_path: str) -> None:
    """
    Save list to TSV

    :param data: data to save
    :type data: list[dict[str, Any]]
    :param file_path: file path
    :type file_path: str
    :return: None
    :rtype: None
    """
    with open(f"{file_path}.tsv", "w", encoding="utf-8", newline="") as file_:
        writer = csv.writer(file_, delimiter="\t", lineterminator="\n")
        writer.writerow(data[0].keys())
        with alive_bar(len(data), title="Saving data to TSV", spinner=None) as bar:  # type: ignore
            for item in data:
                writer.writerow(item.values())
                bar()
    return None


def update_attribution(
    data: list[dict[str, Any]], attr: dict[str, Any]
) -> dict[str, Any]:
    """
    Update attr

    :param data: data to save
    :type data: list[dict[str, Any]]
    :param attr: attribution dict
    :type attr: dict[str, Any]
    :return: attribution dict that has been updated
    :rtype: dict[str, Any]
    """
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
        "Updating attr",
    )
    now = datetime.now(tz=timezone.utc)
    attr["updated"]["iso"] = now.isoformat()  # type: ignore
    attr["updated"]["timestamp"] = int(now.timestamp())  # type: ignore
    attr = populate_contributors(attr)

    total_data = len(data)
    attr = save_platform_loop(data, attr)

    attr["counts"]["total"] = total_data  # type: ignore
    with open("api/status.json", "w", encoding="utf-8") as file:
        json.dump(attr, file)
    pprint.print(
        Platform.SYSTEM,
        Status.PASS,
        "Attribution updated",
    )
    return attr


def add_spaces(data: int, spaces_max: int = 9) -> str:
    """
    Add spaces to data

    :param data: data to add spaces
    :type data: int
    :param spaces_max: maximum spaces, defaults to 9
    :type spaces_max: int, optional
    :return: data with spaces
    :rtype: str
    """
    spaces = spaces_max - len(f"{data}")
    return f"{' ' * spaces}{data}"


def count_non_null_entries(df: pd.DataFrame, column: str) -> int:
    """
    Count non-null entries in a DataFrame column

    :param df: DataFrame to count from
    :type df: pd.DataFrame
    :param column: Column name to count
    :type column: str
    :return: Count of non-null entries
    :rtype: int
    """
    return int(df[column].notna().sum())


def load_tsv_for_counting() -> pd.DataFrame:
    """
    Load TSV data for counting platform entries

    :return: DataFrame with TSV data
    :rtype: pd.DataFrame
    """
    df = pd.read_csv(
        "database/animeapi.tsv",
        sep="\t",
        dtype={
            "title": str,
            "anidb": "Int64",
            "anilist": "Int64",
            "animenewsnetwork": "Int64",
            "animeplanet": str,
            "anisearch": "Int64",
            "annict": "Int64",
            "imdb": str,
            "kaize": str,
            "kaize_id": "Int64",
            "kitsu": "Int64",
            "letterboxd_lid": str,
            "letterboxd_slug": str,
            "letterboxd_uid": str,
            "livechart": "Int64",
            "myanimelist": "Int64",
            "nautiljon": str,
            "nautiljon_id": "Int64",
            "notify": str,
            "otakotaku": "Int64",
            "shikimori": "Int64",
            "shoboi": "Int64",
            "silveryasha": "Int64",
            "simkl": "Int64",
            "themoviedb": "Int64",
            "themoviedb_season_id": "Int64",
            "themoviedb_type": str,
            "thetvdb": "Int64",
            "thetvdb_season_id": "Int64",
            "trakt": "Int64",
            "trakt_may_invalid": str,
            "trakt_season": "Int64",
            "trakt_season_id": "Int64",
            "trakt_slug": str,
            "trakt_type": str,
        },
        keep_default_na=False,
        na_values=[""],
    )
    return df


def get_sample_data_from_tsv(df: pd.DataFrame, platform: str, platform_id: Any) -> dict:
    """
    Get sample data from TSV for a specific platform and ID

    :param df: DataFrame with TSV data
    :type df: pd.DataFrame
    :param platform: Platform name
    :type platform: str
    :param platform_id: Platform ID to lookup
    :type platform_id: Any
    :return: Dictionary representation of the row
    :rtype: dict
    """
    mask = df[platform] == platform_id
    if not mask.any():
        return {}

    row = df[mask].iloc[0]
    # Convert row to dict and handle NaN values
    result = row.to_dict()
    # Replace NaN with None for JSON serialization
    for key, value in result.items():
        if pd.isna(value):
            result[key] = None
        elif isinstance(value, (pd.Int64Dtype, int)) and not pd.isna(value):
            result[key] = int(value)

    return result


def get_trakt_sample_from_tsv(df: pd.DataFrame, trakt_id: int, season: int) -> dict:
    """
    Get sample data from TSV for a specific Trakt show and season

    :param df: DataFrame with TSV data
    :type df: pd.DataFrame
    :param trakt_id: Trakt ID
    :type trakt_id: int
    :param season: Season number
    :type season: int
    :return: Dictionary representation of the row
    :rtype: dict
    """
    mask = (df["trakt"] == trakt_id) & (df["trakt_season"] == season)
    if not mask.any():
        return {}

    row = df[mask].iloc[0]
    result = row.to_dict()
    # Replace NaN with None for JSON serialization
    for key, value in result.items():
        if pd.isna(value):
            result[key] = None
        elif isinstance(value, (pd.Int64Dtype, int)) and not pd.isna(value):
            result[key] = int(value)

    return result


def update_markdown(
    attr: dict[str, dict[str, int | str] | str | int | list[str]],
) -> dict[str, Any]:
    """
    Update counters in README.md by looking <!-- counters --><!-- /counters -->
    Uses TSV data instead of JSON objects for counting and samples.

    :param attr: attribution
    :type attr: dict[str, dict[str, int | str] | str | int | list[str]]
    :return: attribution
    :rtype: dict[str, Any]
    """
    pprint.print(
        Platform.SYSTEM,
        Status.INFO,
        "Updating counters in README.md",
    )

    # Load TSV data
    df = load_tsv_for_counting()

    # Platform mapping: key = column name, value = (display name, count key)
    # This allows us to dynamically build the counts and table
    platform_mapping = [
        ("anidb", "aniDB"),
        ("anilist", "AniList"),
        ("animenewsnetwork", "Anime News Network"),
        ("animeplanet", "Anime-Planet"),
        ("anisearch", "aniSearch"),
        ("annict", "Annict"),
        ("imdb", "IMDb"),
        ("kaize", "Kaize"),
        ("kitsu", "Kitsu"),
        ("letterboxd_slug", "Letterboxd"),  # Use letterboxd_slug as the column
        ("livechart", "LiveChart"),
        ("myanimelist", "MyAnimeList"),
        ("nautiljon", "Nautiljon"),
        ("notify", "Notify.moe"),
        ("otakotaku", "Otak Otaku"),
        ("shikimori", "Shikimori"),
        ("shoboi", "Shoboi/Syobocal"),
        ("silveryasha", "Silver Yasha"),
        ("simkl", "SIMKL"),
        ("themoviedb", "The Movie Database"),
        ("thetvdb", "The TVDB"),
        ("trakt", "Trakt"),
    ]

    # Build counts dictionary dynamically
    counts = {}
    for column, display_name in platform_mapping:
        # Convert display name to count key format
        # Remove special chars and convert to lowercase for key
        if column == "letterboxd_slug":
            count_key = "letterboxd"
        else:
            count_key = column
        counts[count_key] = count_non_null_entries(df, column)

    counts["total"] = len(df)

    # Update attr with counts
    attr["counts"] = counts  # type: ignore

    with open("README.md", "r", encoding="utf-8") as file:
        readme = file.read()

    # Build table dynamically
    table_header = """| Platform           |     Count |
| :----------------- | --------: |
"""
    table_rows = []
    for column, display_name in platform_mapping:
        # Get the count key
        if column == "letterboxd_slug":
            count_key = "letterboxd"
        else:
            count_key = column

        count_value = counts[count_key]
        formatted_count = add_spaces(count_value)
        table_rows.append(f"| {display_name:<18} | {formatted_count} |")

    # Add separator and total
    table_rows.append("|                    |           |")
    table_rows.append(f"| **Total**          | **{counts['total']}** |")

    table = table_header + "\n".join(table_rows) + "\n"

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
    status = json.dumps(attr, indent=2, ensure_ascii=False).replace("\\", "\\\\")
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
    now: int = attr["updated"]["timestamp"]  # type: ignore
    formatted = datetime.fromtimestamp(now, timezone.utc).strftime('%d %B %Y %H:%M:%S UTC')
    readme = re.sub(
        r"<!-- updated -->(.|\n)*<!-- \/updated -->",
        f"<!-- updated -->\nLast updated: {formatted}\n<!-- /updated -->",
        readme,
    )
    readme = re.sub(
        r"<!-- updated-txt -->(.|\n)*<!-- \/updated-txt -->",
        f"<!-- updated-txt -->\n```txt\nUpdated on {formatted}\n```\n<!-- /updated-txt -->",
        readme,
    )

    pprint.print(
        Platform.SYSTEM,
        Status.INFO,
        "Updating JSON Schema in README.md",
    )
    with open("api/schema.json", "r", encoding="utf-8") as file:
        jschema = json.dumps(json.load(file), indent=2, ensure_ascii=False)
        jschema = jschema.replace("\\", "\\\\")
    readme = re.sub(
        r"<!-- jsonschema -->(.|\n)*<!-- \/jsonschema -->",
        f"<!-- jsonschema -->\n```json\n{jschema}\n```\n<!-- /jsonschema -->",
        readme,
    )

    pprint.print(
        Platform.SYSTEM,
        Status.INFO,
        "Updating sample data in README.md, using MyAnimeList ID 1",
    )
    # Get sample from TSV instead of JSON file
    sample = get_sample_data_from_tsv(df, "myanimelist", 1)
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
    # Get Trakt sample from TSV instead of JSON file
    trakt_sample = get_trakt_sample_from_tsv(df, 152334, 3)
    readme = re.sub(
        r"<!-- trakt152334 -->(.|\n)*<!-- \/trakt152334 -->",
        f"<!-- trakt152334 -->\n```json\n{json.dumps(trakt_sample, indent=2)}\n```\n<!-- /trakt152334 -->",
        readme,
    )

    with open("README.md", "w", encoding="utf-8") as file:
        file.write(readme)

    pprint.print(
        Platform.SYSTEM,
        Status.PASS,
        "Counters updated in README.md",
    )
    return attr
