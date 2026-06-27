# SPDX-License-Identifier: MIT

import csv
import json
import pickle
import re
from datetime import datetime, timezone
from pathlib import Path
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
    if not data:
        return

    header = list(data[0].keys())
    with open(f"{file_path}.tsv", "w", encoding="utf-8", newline="") as file_:
        writer = csv.writer(file_, delimiter="\t", lineterminator="\n")
        writer.writerow(header)
        with alive_bar(len(data), title="Saving data to TSV", spinner=None) as bar:  # type: ignore
            for item in data:
                # Ensure values are written in the same order as header and format consistently
                row = []
                for key in header:
                    val = item.get(key)
                    if val is True:
                        row.append("True")
                    elif val is False:
                        row.append("False")
                    elif val is None:
                        row.append("")
                    else:
                        row.append(val)
                writer.writerow(row)
                bar()
    return None


def save_dataframe_to_pickle(df: pd.DataFrame, file_path: str) -> None:
    """
    Save DataFrame to pickle for fast loading

    :param df: DataFrame to save
    :type df: pd.DataFrame
    :param file_path: file path (without extension)
    :type file_path: str
    :return: None
    :rtype: None
    """
    pprint.print(
        Platform.SYSTEM,
        Status.INFO,
        "Save data to pickle for fast API loading",
    )
    try:
        with open(f"{file_path}.pkl", "wb") as file_:
            pickle.dump(df, file_, protocol=pickle.HIGHEST_PROTOCOL)
        file_size = Path(f"{file_path}.pkl").stat().st_size / 1024 / 1024
        pprint.print(
            Platform.SYSTEM,
            Status.PASS,
            f"Pickle saved: {file_size:.1f}MB",
        )
    except (OSError, pickle.PicklingError) as e:
        pprint.print(
            Platform.SYSTEM,
            Status.FAIL,
            f"Failed to save pickle: {e}",
        )
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

    # Load TSV and convert to DataFrame for pickle
    df = load_tsv_for_counting()
    save_dataframe_to_pickle(df, "database/animeapi")

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
    Handles both NaN/None (from keep_default_na=True) and empty strings.

    :param df: DataFrame to count from
    :type df: pd.DataFrame
    :param column: Column name to count
    :type column: str
    :return: Count of non-empty entries
    :rtype: int
    """
    # Check for both Not NaN and Not Empty String
    # (Just .notna() covers NaN/None, but explicit empty strings might exist)
    return int((df[column].notna() & (df[column] != "")).sum())


def load_tsv_for_counting() -> pd.DataFrame:
    """
    Load TSV data for counting platform entries

    :return: DataFrame with TSV data
    :rtype: pd.DataFrame
    """
    tsv_dtypes = {
        "title": str,
        "anidb": "Int64",
        "anilist": "Int64",
        "animenewsnetwork": "Int64",
        "animeplanet": str,
        "anisearch": "Int64",
        "annict": "Int64",
        "hikka": str,
        "imdb": str,
        "kaize": str,
        "kaize_id": "Int64",
        "kitsu": "Int64",
        "letterboxd_lid": str,
        "letterboxd_slug": str,
        "letterboxd_uid": "Int64",
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
        "trakt_may_invalid": "boolean",
        "trakt_season": "Int64",
        "trakt_season_id": "Int64",
        "trakt_slug": str,
        "trakt_type": str,
    }

    try:
        # Read TSV with specific data types
        df = pd.read_csv(  # type: ignore
            "database/animeapi.tsv",
            sep="\t",
            dtype=tsv_dtypes,
            keep_default_na=True,
        )
    except ValueError as e:
        pprint.print(Platform.SYSTEM, Status.ERR, f"TSV Load Error: {e}")
        pprint.print(Platform.SYSTEM, Status.INFO, "Diagnosing invalid values...")

        # Diagnostic: Read as string to find the culprit
        try:
            debug_df = pd.read_csv(  # type: ignore
                "database/animeapi.tsv",
                sep="\t",
                dtype=str,
                keep_default_na=False,
            )

            for col, dtype in tsv_dtypes.items():
                if dtype == "Int64":
                    # Try converting to numeric
                    numeric_series = pd.to_numeric(debug_df[col], errors="coerce")
                    # Find where original was not empty but numeric is NaN
                    mask = (debug_df[col] != "") & (numeric_series.isna())
                    if mask.any():
                        bad_rows = debug_df[mask]
                        for idx, row in bad_rows.iterrows():
                            pprint.print(
                                Platform.SYSTEM,
                                Status.FAIL,
                                f"Type Mismatch in Row {idx} (Line ~{idx + 2}):",
                                f"Column '{col}' expected Int64 but got '{row[col]}'",
                            )
                            pprint.print(
                                Platform.SYSTEM,
                                Status.FAIL,
                                f"Entry Context (Title): {row.get('title', 'Unknown')}",
                            )
                            # Print full row for debug
                            print(f"Full Row Data: {row.to_dict()}")
                            raise e
        except Exception as diag_err:
            print(f"Diagnostic failed: {diag_err}")

        # Re-raise original error
        raise e

    return df


def get_sample_data_from_tsv(
    df: pd.DataFrame, platform: str, platform_id: Any
) -> dict[str, Any]:
    """
    Get sample data from TSV for a specific platform and ID

    :param df: DataFrame with TSV data
    :type df: pd.DataFrame
    :param platform: Platform name
    :type platform: str
    :param platform_id: Platform ID to lookup
    :type platform_id: Any
    :return: Dictionary representation of the row
    :rtype: dict[str, Any]
    """
    # Support both numeric types (since some columns are Int64) and string values
    try:
        val_as_int = int(platform_id)
        mask = (df[platform] == val_as_int) | (df[platform] == str(platform_id))
    except ValueError:
        mask = df[platform] == str(platform_id)

    if not mask.any():
        return {}

    row = df[mask].iloc[0]  # type: ignore
    # Convert row to dict and handle type conversions
    result: dict[str, Any] = row.to_dict()  # type: ignore
    # Convert string values to appropriate types
    for key, value in result.items():  # type: ignore
        if pd.isna(value) or value == "":  # type: ignore
            result[key] = None
        elif value == "True":
            result[key] = True
        elif value == "False":
            result[key] = False
        elif isinstance(value, bool):
            # Keep booleans as-is
            result[key] = value
        elif isinstance(value, str) and value.isdigit():
            # Convert numeric strings to integers
            result[key] = int(value)
        elif isinstance(value, str) and value.lstrip("-").isdigit():
            # Handle negative numbers
            result[key] = int(value)

    return result  # type: ignore


def get_trakt_sample_from_tsv(
    df: pd.DataFrame, trakt_id: int, season: int
) -> dict[str, Any]:
    """
    Get sample data from TSV for a specific Trakt show and season

    :param df: DataFrame with TSV data
    :type df: pd.DataFrame
    :param trakt_id: Trakt ID
    :type trakt_id: int
    :param season: Season number
    :type season: int
    :return: Dictionary representation of the row
    :rtype: dict[str, Any]
    """
    # Support both numeric types (since some columns are Int64) and string values
    mask = (
        ((df["trakt"] == int(trakt_id)) | (df["trakt"] == str(trakt_id)))
        & ((df["trakt_season"] == int(season)) | (df["trakt_season"] == str(season)))
    )
    if not mask.any():
        return {}

    row = df[mask].iloc[0]  # type: ignore
    result: dict[str, Any] = row.to_dict()  # type: ignore
    # Convert string values to appropriate types
    for key, value in result.items():
        if pd.isna(value) or value == "":  # type: ignore
            result[key] = None
        elif value == "True":
            result[key] = True
        elif value == "False":
            result[key] = False
        elif isinstance(value, bool):
            # Keep booleans as-is
            result[key] = value
        elif isinstance(value, str) and value.isdigit():
            # Convert numeric strings to integers
            result[key] = int(value)
        elif isinstance(value, str) and value.lstrip("-").isdigit():
            # Handle negative numbers
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
        ("hikka", "Hikka"),
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
    counts: dict[str, int] = {}
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
    table_rows: list[str] = []
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

    # Update status.json with correct counts
    pprint.print(
        Platform.SYSTEM,
        Status.INFO,
        "Updating status.json with platform counts",
    )
    with open("api/status.json", "w", encoding="utf-8") as file:
        json.dump(attr, file)

    pprint.print(
        Platform.SYSTEM,
        Status.PASS,
        "Counters updated in README.md",
    )
    return attr
