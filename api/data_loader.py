"""Data loading and caching module for TSV data"""

from functools import lru_cache
from typing import Any, Dict, Optional, Union

import pandas as pd

try:
    from .models import AnimeEntry, row_to_entry
except ImportError:
    from models import AnimeEntry, row_to_entry

# Global cache for TSV data
_tsv_cache: Optional[pd.DataFrame] = None
_tsv_indices: Dict[str, Dict[Any, int]] = {}


@lru_cache(maxsize=1)
def load_tsv_data() -> pd.DataFrame:
    """Load and cache TSV data with pandas for fast lookups"""
    global _tsv_cache, _tsv_indices

    if _tsv_cache is not None:
        return _tsv_cache

    # Read TSV with pandas - much faster than JSON
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
            "trakt_may_invalid": str,  # Read as string, convert to bool later
            "trakt_season": "Int64",
            "trakt_season_id": "Int64",
            "trakt_slug": str,
            "trakt_type": str,
        },
        keep_default_na=False,
        na_values=[""],
    )

    # Convert trakt_may_invalid to boolean
    df["trakt_may_invalid"] = df["trakt_may_invalid"].replace(
        {
            "True": True,
            "False": False,
            "1": True,
            "0": False,
            1: True,
            0: False,
            "": None,
        }
    )

    # Build indices for fast lookup by platform ID
    for col in df.columns:
        if col != "title":
            # Create a dictionary mapping platform_id -> row_index for non-null values
            mask = df[col].notna()
            _tsv_indices[col] = {
                val: idx for idx, val in zip(df[mask].index, df[mask][col])
            }

    _tsv_cache = df
    return df


def lookup_by_platform_id(
    platform: str, platform_id: Union[int, str]
) -> Optional[AnimeEntry]:
    """
    Fast lookup of anime entry by platform and ID using TSV data

    :param platform: Platform name
    :type platform: str
    :param platform_id: Platform ID
    :type platform_id: Union[int, str]
    :return: AnimeEntry or None
    :rtype: Optional[AnimeEntry]
    """
    df = load_tsv_data()

    # Handle special cases for composite IDs
    if platform in ["trakt", "themoviedb", "thetvdb"]:
        return lookup_composite_platform(platform, platform_id, df)

    # Handle letterboxd with priority: letterboxd_slug -> letterboxd_lid -> letterboxd_uid
    if platform == "letterboxd":
        return lookup_letterboxd(platform_id, df)

    # Convert platform_id to appropriate type
    if platform in _tsv_indices:
        # Try to find exact match
        try:
            if platform in [
                "imdb",
                "animeplanet",
                "kaize",
                "letterboxd_lid",
                "letterboxd_slug",
                "nautiljon",
                "notify",
                "trakt_slug",
                "themoviedb_type",
                "trakt_type",
            ]:
                lookup_id = str(platform_id)
            else:
                lookup_id = int(platform_id)

            if lookup_id in _tsv_indices[platform]:
                row_idx = _tsv_indices[platform][lookup_id]
                row = df.iloc[row_idx]
                return row_to_entry(row)
        except (ValueError, KeyError):
            pass

    return None


def lookup_letterboxd(
    platform_id: Union[int, str], df: pd.DataFrame
) -> Optional[AnimeEntry]:
    """
    Handle letterboxd lookups with priority: letterboxd_slug -> letterboxd_lid -> letterboxd_uid

    :param platform_id: Platform ID
    :param df: DataFrame
    :return: AnimeEntry or None
    """
    lookup_id = str(platform_id)

    # Priority order: letterboxd_slug -> letterboxd_lid -> letterboxd_uid
    for field in ["letterboxd_slug", "letterboxd_lid", "letterboxd_uid"]:
        if field in _tsv_indices and lookup_id in _tsv_indices[field]:
            row_idx = _tsv_indices[field][lookup_id]
            row = df.iloc[row_idx]
            return row_to_entry(row)

    return None


def lookup_composite_platform(
    platform: str, platform_id: str, df: pd.DataFrame
) -> Optional[AnimeEntry]:
    """
    Handle composite platform IDs (trakt, themoviedb, thetvdb)

    :param platform: Platform name
    :param platform_id: Platform ID (may include type/season info)
    :param df: DataFrame
    :return: AnimeEntry or None
    """
    if platform == "trakt":
        # Format: shows/123 or movies/456 or shows/123/seasons/2
        # Also supports: shows/slug-name or movies/slug-name
        parts = str(platform_id).split("/")
        if len(parts) >= 2:
            media_type = parts[0]
            media_id_or_slug = parts[1]
            season_num = None
            if len(parts) >= 4 and parts[2] == "seasons":
                try:
                    season_num = int(parts[3])
                except ValueError:
                    season_num = None

            # Try numeric ID first
            try:
                media_id = int(media_id_or_slug)
                mask = (df["trakt"] == media_id) & (df["trakt_type"] == media_type)
                if season_num is not None:
                    mask = mask & (df["trakt_season"] == season_num)

                matches = df[mask]
                if not matches.empty:
                    return row_to_entry(matches.iloc[0])
            except ValueError:
                # Not a numeric ID, try slug lookup
                if (
                    "trakt_slug" in _tsv_indices
                    and media_id_or_slug in _tsv_indices["trakt_slug"]
                ):
                    row_idx = _tsv_indices["trakt_slug"][media_id_or_slug]
                    row = df.iloc[row_idx]
                    # Verify media_type and season match
                    if row.get("trakt_type") == media_type and (
                        season_num is None or row.get("trakt_season") == season_num
                    ):
                        return row_to_entry(row)

    elif platform == "themoviedb":
        # Format: movie/123 or tv/456 or tv/456/season/2
        parts = str(platform_id).split("/")
        if len(parts) >= 2:
            media_type = parts[0]
            try:
                media_id = int(parts[1])
                season_num = None
                if len(parts) >= 4 and parts[2] == "season":
                    season_num = int(parts[3])

                mask = (df["themoviedb"] == media_id) & (
                    df["themoviedb_type"] == media_type
                )
                if season_num is not None:
                    mask = mask & (df["trakt_season"] == season_num)

                matches = df[mask]
                if not matches.empty:
                    return row_to_entry(matches.iloc[0])
            except (ValueError, IndexError):
                pass

    elif platform == "thetvdb":
        # Format: series/123 or series/123/seasons/2
        parts = str(platform_id).split("/")
        if len(parts) >= 2 and parts[0] == "series":
            try:
                series_id = int(parts[1])
                season_num = None
                if len(parts) >= 4 and parts[2] == "seasons":
                    season_num = int(parts[3])

                mask = df["thetvdb"] == series_id
                if season_num is not None:
                    mask = mask & (df["trakt_season"] == season_num)

                matches = df[mask]
                if not matches.empty:
                    return row_to_entry(matches.iloc[0])
            except (ValueError, IndexError):
                pass

    return None
