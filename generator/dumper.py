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
    # NOTE: Platform-specific dumper removed (deprecated since Oct 22, 2025)
    # Users should use /animeapi.json or /animeapi.tsv instead

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
    Count non-empty entries in a DataFrame column.
    Since all columns are read as strings, count non-empty strings.

    :param df: DataFrame to count from
    :type df: pd.DataFrame
    :param column: Column name to count
    :type column: str
    :return: Count of non-empty entries
    :rtype: int
    """
    return int((df[column] != "").sum())


def load_tsv_for_counting() -> pd.DataFrame:
    """
    Load TSV data for counting platform entries

    :return: DataFrame with TSV data
    :rtype: pd.DataFrame
    """
    # Read all columns as strings to avoid pandas type inference errors
    # (some columns may have mixed types or special characters)
    df = pd.read_csv(
        "database/animeapi.tsv",
        sep="\t",
        dtype=str,  # All columns as strings
        keep_default_na=False,  # Don't convert empty strings to NaN
        na_values=[],  # Empty list means no values are treated as null
    )
    df["trakt_may_invalid"] = df["trakt_may_invalid"].replace(
        {"True": True, "False": False, "": None}
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
        elif isinstance(value, bool):
            # Keep booleans as-is (must check before int since bool is subclass of int)
            result[key] = value
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
        elif isinstance(value, bool):
            # Keep booleans as-is (must check before int since bool is subclass of int)
            result[key] = value
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
    now: datetime = datetime.fromtimestamp(attr["updated"]["timestamp"], timezone.utc)  # type: ignore
    readme = re.sub(
        r"<!-- updated -->(.|\n)*<!-- \/updated -->",
        f"<!-- updated -->\nLast updated: {now.strftime('%d %B %Y %H:%M:%S UTC')}\n<!-- /updated -->",
        readme,
    )
    readme = re.sub(
        r"<!-- updated-txt -->(.|\n)*<!-- \/updated-txt -->",
        f"<!-- updated-txt -->\n```txt\nUpdated on {now.strftime('%m/%d/%Y %H:%M:%S UTC')}\n```\n<!-- /updated-txt -->",
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
