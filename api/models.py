"""Data models for anime entries"""

from dataclasses import asdict, dataclass
from typing import Any

import pandas as pd


@dataclass
class AnimeEntry:
    """Dataclass for anime entry from TSV"""

    title: str | None = None
    anidb: int | None = None
    anilist: int | None = None
    animenewsnetwork: int | None = None
    animeplanet: str | None = None
    anisearch: int | None = None
    annict: int | None = None
    hikka: str | None = None
    imdb: str | None = None
    kaize: str | None = None
    kaize_id: int | None = None
    kitsu: int | None = None
    letterboxd_lid: str | None = None
    letterboxd_slug: str | None = None
    letterboxd_uid: int | None = None
    livechart: int | None = None
    myanimelist: int | None = None
    nautiljon: str | None = None
    nautiljon_id: int | None = None
    notify: str | None = None
    otakotaku: int | None = None
    shikimori: int | None = None
    shoboi: int | None = None
    silveryasha: int | None = None
    simkl: int | None = None
    themoviedb: int | None = None
    themoviedb_season_id: int | None = None
    themoviedb_type: str | None = None
    thetvdb: int | None = None
    thetvdb_season_id: int | None = None
    trakt: int | None = None
    trakt_may_invalid: bool | None = None
    trakt_season: int | None = None
    trakt_season_id: int | None = None
    trakt_slug: str | None = None
    trakt_type: str | None = None

    def to_dict(self) -> dict[str, Any]:
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
        if target_type is bool:
            if isinstance(val, bool):
                return val
            if isinstance(val, int):
                return bool(val)
            if isinstance(val, str):
                lowered = val.strip().lower()
                if lowered in {"true", "1"}:
                    return True
                if lowered in {"false", "0"}:
                    return False
            return None
        if target_type is int:
            try:
                int_val = int(val)
                if int_val == 0:
                    return None
                return int_val
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
        hikka=safe_convert(row.get("hikka"), str),
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
