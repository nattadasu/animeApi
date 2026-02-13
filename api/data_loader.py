"""Data loading and caching module for TSV data"""

import os
import pickle
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Optional, Union

# Lazy import pandas - only when needed
pd = None

try:
    from .models import AnimeEntry, row_to_entry
except ImportError:
    from models import AnimeEntry, row_to_entry

# Global cache for TSV data
_tsv_cache: Optional[Any] = None
_tsv_indices: Dict[str, Dict[Any, int]] = {}


@lru_cache(maxsize=1)
def load_tsv_data() -> Any:
    """Load and cache TSV data with pandas for fast lookups"""
    global _tsv_cache, _tsv_indices, pd

    if _tsv_cache is not None:
        return _tsv_cache

    # Try to load from pickle cache first (pre-built by generator for fast cold starts)
    pickle_path = Path("database/animeapi.pkl")
    if pickle_path.exists():
        try:
            with open(pickle_path, "rb") as f:
                _tsv_cache = pickle.load(f)
            # Still need to build indices even from pickle
            df = _tsv_cache
            for col in df.columns:
                if col != "title":
                    mask = df[col].notna()
                    _tsv_indices[col] = {
                        val: idx for idx, val in zip(df[mask].index, df[mask][col])
                    }
            return _tsv_cache
        except (pickle.UnpicklingError, EOFError, OSError):
            # Pickle cache corrupted, fall through to TSV parsing
            pass

    # Lazy import pandas only when needed
    import pandas as pd_module
    pd = pd_module

    # Read TSV with pandas - much faster than JSON
    df = pd.read_csv(  # type: ignore
        "database/animeapi.tsv",
        sep="\t",
        dtype=str,
        keep_default_na=False,
        na_values=[""],
        low_memory=False,
    )

    # Convert to appropriate dtypes
    int_cols = [
        "anidb",
        "anilist",
        "animenewsnetwork",
        "anisearch",
        "annict",
        "kaize_id",
        "kitsu",
        "letterboxd_uid",
        "livechart",
        "myanimelist",
        "nautiljon_id",
        "otakotaku",
        "shikimori",
        "shoboi",
        "silveryasha",
        "simkl",
        "themoviedb",
        "themoviedb_season_id",
        "thetvdb",
        "thetvdb_season_id",
        "trakt",
        "trakt_season",
        "trakt_season_id",
    ]
    for col in int_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Convert trakt_may_invalid to boolean
    df["trakt_may_invalid"] = df["trakt_may_invalid"].replace(  # type: ignore
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
                "animeplanet",
                "hikka",
                "imdb",
                "kaize",
                "letterboxd_lid",
                "letterboxd_slug",
                "myanimelist",
                "nautiljon",
                "notify",
                "themoviedb_type",
                "trakt_slug",
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
    platform_id: Union[int, str], df: Any
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
    platform: str, platform_id: Union[int, str], df: Any
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
            if len(parts) >= 4 and (parts[2] == "season" or parts[2] == "seasons"):
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
                if len(parts) >= 4 and (parts[2] == "season" or parts[2] == "seasons"):
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
                if len(parts) >= 4 and (parts[2] == "season" or parts[2] == "seasons"):
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
