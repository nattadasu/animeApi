"""Data models for anime entries"""

from dataclasses import asdict, dataclass
from typing import Any, Dict, Optional

import pandas as pd


@dataclass
class AnimeEntry:
    """Dataclass for anime entry from TSV"""

    title: Optional[str] = None
    anidb: Optional[int] = None
    anilist: Optional[int] = None
    animenewsnetwork: Optional[int] = None
    animeplanet: Optional[str] = None
    anisearch: Optional[int] = None
    annict: Optional[int] = None
    imdb: Optional[str] = None
    kaize: Optional[str] = None
    kaize_id: Optional[int] = None
    kitsu: Optional[int] = None
    letterboxd_lid: Optional[str] = None
    letterboxd_slug: Optional[str] = None
    letterboxd_uid: Optional[int] = None
    livechart: Optional[int] = None
    myanimelist: Optional[int] = None
    nautiljon: Optional[str] = None
    nautiljon_id: Optional[int] = None
    notify: Optional[str] = None
    otakotaku: Optional[int] = None
    shikimori: Optional[int] = None
    shoboi: Optional[int] = None
    silveryasha: Optional[int] = None
    simkl: Optional[int] = None
    themoviedb: Optional[int] = None
    themoviedb_season_id: Optional[int] = None
    themoviedb_type: Optional[str] = None
    thetvdb: Optional[int] = None
    thetvdb_season_id: Optional[int] = None
    trakt: Optional[int] = None
    trakt_may_invalid: Optional[bool] = None
    trakt_season: Optional[int] = None
    trakt_season_id: Optional[int] = None
    trakt_slug: Optional[str] = None
    trakt_type: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


def row_to_entry(row: pd.Series) -> AnimeEntry:
    """
    Convert pandas Series row to AnimeEntry dataclass

    :param row: Pandas Series representing a row
    :return: AnimeEntry instance
    """

    def safe_convert(val, target_type):
        """Safely convert value, returning None for NaN/empty"""
        if pd.isna(val) or val == "":
            return None
        if target_type == bool:
            return bool(val)
        if target_type == int:
            try:
                return int(val)
            except (ValueError, TypeError):
                return None
        return val

    return AnimeEntry(
        title=safe_convert(row.get("title"), str),
        anidb=safe_convert(row.get("anidb"), int),
        anilist=safe_convert(row.get("anilist"), int),
        animenewsnetwork=safe_convert(row.get("animenewsnetwork"), int),
        animeplanet=safe_convert(row.get("animeplanet"), str),
        anisearch=safe_convert(row.get("anisearch"), int),
        annict=safe_convert(row.get("annict"), int),
        imdb=safe_convert(row.get("imdb"), str),
        kaize=safe_convert(row.get("kaize"), str),
        kaize_id=safe_convert(row.get("kaize_id"), int),
        kitsu=safe_convert(row.get("kitsu"), int),
        letterboxd_lid=safe_convert(row.get("letterboxd_lid"), str),
        letterboxd_slug=safe_convert(row.get("letterboxd_slug"), str),
        letterboxd_uid=safe_convert(row.get("letterboxd_uid"), int),
        livechart=safe_convert(row.get("livechart"), int),
        myanimelist=safe_convert(row.get("myanimelist"), int),
        nautiljon=safe_convert(row.get("nautiljon"), str),
        nautiljon_id=safe_convert(row.get("nautiljon_id"), int),
        notify=safe_convert(row.get("notify"), str),
        otakotaku=safe_convert(row.get("otakotaku"), int),
        shikimori=safe_convert(row.get("shikimori"), int),
        shoboi=safe_convert(row.get("shoboi"), int),
        silveryasha=safe_convert(row.get("silveryasha"), int),
        simkl=safe_convert(row.get("simkl"), int),
        themoviedb=safe_convert(row.get("themoviedb"), int),
        themoviedb_season_id=safe_convert(row.get("themoviedb_season_id"), int),
        themoviedb_type=safe_convert(row.get("themoviedb_type"), str),
        thetvdb=safe_convert(row.get("thetvdb"), int),
        thetvdb_season_id=safe_convert(row.get("thetvdb_season_id"), int),
        trakt=safe_convert(row.get("trakt"), int),
        trakt_may_invalid=safe_convert(row.get("trakt_may_invalid"), bool),
        trakt_season=safe_convert(row.get("trakt_season"), int),
        trakt_season_id=safe_convert(row.get("trakt_season_id"), int),
        trakt_slug=safe_convert(row.get("trakt_slug"), str),
        trakt_type=safe_convert(row.get("trakt_type"), str),
    )
