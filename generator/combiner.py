# SPDX-License-Identifier: AGPL-3.0-only AND MIT

from typing import Any

from alive_progress import alive_bar  # type: ignore
from const import pprint
from prettyprint import Platform, Status


def combine_arm(
    arm: list[dict[str, Any]], aod: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """
    Combine ARM data with AOD data

    :param arm: ARM data
    :type arm: list[dict[str, Any]]
    :param aod: AOD data
    :type aod: list[dict[str, Any]]
    :return: AOD data
    :rtype: list[dict[str, Any]]
    """
    linked = 0
    with alive_bar(
        len(aod), title="Combining ARM data with AOD data", spinner=None
    ) as bar:  # type: ignore
        for item in aod:
            myanimelist = item["myanimelist"]
            anilist = item["anilist"]
            # Skip if both myanimelist and anilist are null
            if myanimelist is None and anilist is None:
                item.update(
                    {
                        "shoboi": None,
                        "annict": None,
                    }
                )
                bar()
                continue

            # Check if mal_id and anilist_id exist in arm_data
            for arm_item in arm:
                mal_id = arm_item.get("mal_id", None)
                anilist_id = arm_item.get("anilist_id", None)
                syoboi = arm_item.get("syobocal_tid", None)
                annict = arm_item.get("annict_id", None)
                if myanimelist is not None and mal_id == myanimelist:
                    # Combine the data from arm_item with the item in aod_data
                    item.update(
                        {
                            "shoboi": syoboi,
                            "annict": annict,
                            "anilist": anilist if anilist is not None else anilist_id,
                        }
                    )

                    linked += 1
                    break
                elif anilist is not None and anilist_id == anilist:
                    # Combine the data from arm_item with the item in aod_data
                    item.update(
                        {
                            "shoboi": syoboi,
                            "annict": annict,
                            "myanimelist": myanimelist
                            if myanimelist is not None
                            else mal_id,
                            "shikimori": myanimelist
                            if myanimelist is not None
                            else mal_id,
                        }
                    )
                    linked += 1
                    break
            bar()
    pprint.print(
        Platform.ARM,
        Status.PASS,
        "ARM data combined with AOD data.",
        "Total linked data:",
        f"{linked},",
        "AOD data:",
        f"{len(aod)}",
        "ARM data:",
        f"{len(arm)}",
    )
    return aod


def combine_anitrakt(
    anitrakt: list[dict[str, Any]], aod: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """
    Combine Extended AniTrakt data with AOD data

    :param anitrakt: Extended AniTrakt data
    :type anitrakt: list[dict[str, Any]]
    :param aod: AOD data
    :type aod: list[dict[str, Any]]
    :return: AOD data with Trakt and related IDs
    :rtype: list[dict[str, Any]]
    """
    linked = 0
    with alive_bar(
        len(aod), title="Combining Extended AniTrakt data with AOD data", spinner=None
    ) as bar:  # type: ignore
        for item in aod:
            matched = False
            myanimelist = item["myanimelist"]
            # Skip if myanimelist is null
            if myanimelist is None:
                item.update(
                    {
                        "trakt": None,
                        "trakt_type": None,
                        "trakt_season": None,
                        "trakt_slug": None,
                        "trakt_may_invalid": None,
                        "trakt_season_id": None,
                        "thetvdb": None,
                        "thetvdb_season_id": None,
                        "themoviedb_type": None,
                        "themoviedb_season_id": None,
                        "letterboxd_slug": None,
                        "letterboxd_lid": None,
                        "letterboxd_uid": None,
                    }
                )
                bar()
                continue

            # Check if mal_id exists in anitrakt_data
            for anitrakt_item in anitrakt:
                mal_id = anitrakt_item.get("myanimelist", {}).get("id", None)
                if myanimelist is not None and mal_id == myanimelist:
                    trakt_info = anitrakt_item.get("trakt", {})
                    trakt_type = trakt_info.get("type", None)

                    # Extract common fields
                    trakt_id = trakt_info.get("id", None)
                    trakt_slug = trakt_info.get("slug", None)

                    # Initialize fields
                    trakt_season = None
                    trakt_may_invalid = None
                    trakt_season_id = None
                    thetvdb = None
                    thetvdb_season_id = None
                    themoviedb_type = None
                    themoviedb_season_id = None
                    letterboxd_slug = None
                    letterboxd_lid = None
                    letterboxd_uid = None

                    if trakt_type == "shows":
                        # TV show specific fields
                        is_split_cour = trakt_info.get("is_split_cour", False)
                        trakt_may_invalid = is_split_cour

                        season_info = trakt_info.get("season", None)
                        if season_info is not None and not is_split_cour:
                            trakt_season = season_info.get("number", None)
                            trakt_season_id = season_info.get("id", None)
                            season_externals = season_info.get("externals", {})
                            thetvdb_season_id = season_externals.get("tvdb", None)
                            themoviedb_season_id = season_externals.get("tmdb", None)

                        # Show-level externals
                        show_externals = anitrakt_item.get("externals", {})
                        thetvdb = show_externals.get("tvdb", None)
                        themoviedb = show_externals.get("tmdb", None)
                        imdb = show_externals.get("imdb", None)

                        # Overwrite themoviedb and imdb with Trakt data
                        if themoviedb is not None:
                            item["themoviedb"] = themoviedb
                        if imdb is not None:
                            item["imdb"] = imdb

                        themoviedb_type = "tv"

                    elif trakt_type == "movies":
                        # Movie specific fields - set trakt_may_invalid to False for movies
                        trakt_may_invalid = False

                        movie_externals = anitrakt_item.get("externals", {})
                        themoviedb = movie_externals.get("tmdb", None)
                        imdb = movie_externals.get("imdb", None)

                        # Overwrite themoviedb and imdb with Trakt data
                        if themoviedb is not None:
                            item["themoviedb"] = themoviedb
                        if imdb is not None:
                            item["imdb"] = imdb

                        themoviedb_type = "movie"

                        # Letterboxd data
                        letterboxd_info = movie_externals.get("letterboxd", {})
                        if letterboxd_info:
                            letterboxd_slug = letterboxd_info.get("slug", None)
                            letterboxd_lid = letterboxd_info.get("lid", None)
                            letterboxd_uid = letterboxd_info.get("uid", None)

                    # Combine the data
                    item.update(
                        {
                            "trakt": trakt_id,
                            "trakt_type": trakt_type,
                            "trakt_season": trakt_season,
                            "trakt_slug": trakt_slug,
                            "trakt_may_invalid": trakt_may_invalid,
                            "trakt_season_id": trakt_season_id,
                            "thetvdb": thetvdb,
                            "thetvdb_season_id": thetvdb_season_id,
                            "themoviedb_type": themoviedb_type,
                            "themoviedb_season_id": themoviedb_season_id,
                            "letterboxd_slug": letterboxd_slug,
                            "letterboxd_lid": letterboxd_lid,
                            "letterboxd_uid": letterboxd_uid,
                        }
                    )
                    linked += 1
                    matched = True
                    break

            if not matched:
                item.update(
                    {
                        "trakt": None,
                        "trakt_type": None,
                        "trakt_season": None,
                        "trakt_slug": None,
                        "trakt_may_invalid": None,
                        "trakt_season_id": None,
                        "thetvdb": None,
                        "thetvdb_season_id": None,
                        "themoviedb_type": None,
                        "themoviedb_season_id": None,
                        "letterboxd_slug": None,
                        "letterboxd_lid": None,
                        "letterboxd_uid": None,
                    }
                )
            bar()
    pprint.print(
        Platform.ANITRAKT,
        Status.PASS,
        "Extended AniTrakt data combined with AOD data.",
        "Total linked data:",
        f"{linked},",
        "AOD data:",
        f"{len(aod)}",
        "Extended AniTrakt data:",
        f"{len(anitrakt)}",
    )
    return aod


def combine_fribb(
    fribb: list[dict[str, Any]], aod: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """
    Combine Fribb's Animelists data with AOD data to obtain IMDb and TMDB IDs
    via AniDB

    :param fribb: Fribb's Animelists data
    :type fribb: list[dict[str, Any]]
    :param aod: AOD data
    :type aod: list[dict[str, Any]]
    :return: AOD data
    :rtype: list[dict[str, Any]]
    """
    linked = 0
    with alive_bar(
        len(aod), title="Combining Fribb's Animelists data with AOD data", spinner=None
    ) as bar:  # type: ignore
        for item in aod:
            matched = False
            anidb = item["anidb"]
            # Skip if anidb is null
            if anidb is None:
                item.update(
                    {
                        "imdb": None,
                        "themoviedb": None,
                    }
                )
                bar()
                continue

            # Check if anidb_id exist in fribb_data
            for fbi in fribb:
                anidb_id = fbi.get("anidb_id", None)
                imdb = fbi.get("imdb_id", None)
                tmdb: str | int | None = fbi.get("themoviedb_id", None)
                if anidb is not None and anidb_id == anidb:
                    # Combine the data from fribb_item with the item in aod_data
                    data_fbi: dict[str, Any] = {}
                    data_fbi["imdb"] = imdb
                    if isinstance(tmdb, str):
                        tmdbl = tmdb.split(",")
                        tmdb = int(tmdbl[0])
                    data_fbi["themoviedb"] = tmdb
                    item.update(data_fbi)
                    linked += 1
                    matched = True
                    break

            if not matched:
                item.update(
                    {
                        "imdb": None,
                        "themoviedb": None,
                    }
                )
            bar()
    pprint.print(
        Platform.FRIBB,
        Status.PASS,
        "Fribb's Animelists data combined with AOD data.",
        "Total linked data:",
        f"{linked},",
        "AOD data:",
        f"{len(aod)}",
        "Fribb's Animelists data:",
        f"{len(fribb)}",
    )
    return aod
