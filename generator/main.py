# SPDX-License-Identifier: AGPL-3.0-only AND MIT

import datetime
import json
from time import time
from typing import Any

from alive_progress import alive_bar  # type: ignore
from combiner import combine_anitrakt, combine_arm, combine_fribb, combine_hikka
from const import (
    KAIZE_EMAIL,
    KAIZE_PASSWORD,
    attribution,
    pprint,
)
from converter import (
    link_kaize_to_mal,
    link_nautiljon_to_mal,
    link_otakotaku_to_mal,
    link_silveryasha_to_mal,
)
from dumper import update_attribution, update_markdown
from fetcher import (
    get_anime_offline_database,
    get_anime_offline_database_2025_52,
    get_anitrakt,
    get_arm,
    get_fribb_animelists,
    get_notify_rensetsu,
    merge_notify_with_aod,
    restore_notify_safe,
    simplify_aod_data,
    simplify_silveryasha_data,
)
from hikka import Hikka
from kaize import Kaize
from nautiljon import Nautiljon
from otakotaku import OtakOtaku
from prettyprint import Platform, Status
from utils import check_git_any_changes, proc_stop, validate_json_files


def main() -> None:
    """Main function"""

    start_time = time()
    run_metrics: dict[str, Any] = {
        "timestamp": datetime.datetime.now().isoformat(),
        "status": "failed",
        "duration_seconds": 0,
        "stages": {},
    }

    try:
        pprint.print(Platform.SYSTEM, Status.READY, "Generator ready to use")

        stage_start = time()
        aod = get_anime_offline_database()

        # Sideload future seasonal mapping data
        sideload_path = "database/raw/sideload_future.json"
        try:
            with open(sideload_path, "r", encoding="utf-8") as sf:
                sideload_data = json.load(sf)
                if "data" in aod:
                    from aod_entry import AodEntry

                    # Index existing AOD entries by their extracted IDs
                    id_to_aod_entry = {}
                    for item in aod["data"]:
                        entry = AodEntry.from_aod_dict(item)
                        for id_str in entry.id_set:
                            id_to_aod_entry[id_str] = item

                    merged_count = 0
                    added_count = 0

                    for sideloaded_item in sideload_data:
                        sideload_entry = AodEntry.from_aod_dict(sideloaded_item)

                        # Check if any ID overlap exists
                        matched_item = None
                        for id_str in sideload_entry.id_set:
                            if id_str in id_to_aod_entry:
                                matched_item = id_to_aod_entry[id_str]
                                break

                        if matched_item:
                            # Merge sources and synonyms instead of appending a duplicate
                            merged_sources = set(
                                matched_item.get("sources", [])
                                + sideloaded_item.get("sources", [])
                            )
                            matched_item["sources"] = list(merged_sources)

                            merged_synonyms = set(
                                matched_item.get("synonyms", [])
                                + sideloaded_item.get("synonyms", [])
                            )
                            matched_item["synonyms"] = list(merged_synonyms)

                            merged_count += 1
                        else:
                            # Truly new entry - add it and index its IDs
                            aod["data"].append(sideloaded_item)
                            for id_str in sideload_entry.id_set:
                                id_to_aod_entry[id_str] = sideloaded_item
                            added_count += 1

                    pprint.print(
                        Platform.SYSTEM,
                        Status.PASS,
                        f"Processed {len(sideload_data)} future season entries: added {added_count}, merged {merged_count} with existing entries",
                    )
        except FileNotFoundError:
            pprint.print(
                Platform.SYSTEM,
                Status.WARN,
                f"Sideload file {sideload_path} not found, skipping future seasons",
            )

        aod_arr = simplify_aod_data(aod)
        run_metrics["stages"]["fetch_aod"] = time() - stage_start

        # Get old AOD snapshot and notify data for merging
        pprint.print(
            Platform.SYSTEM,
            Status.INFO,
            "Fetching 2025-52 snapshot and notify.moe data for merging",
        )
        stage_start = time()
        aod_2025_52 = get_anime_offline_database_2025_52()
        notify_rensetsu = get_notify_rensetsu()
        run_metrics["stages"]["fetch_notify"] = time() - stage_start

        # Merge notify.moe data (snapshot optional, Rensetsu is fallback)
        stage_start = time()
        aod_arr = merge_notify_with_aod(aod_arr, aod_2025_52, notify_rensetsu)
        run_metrics["stages"]["merge_notify"] = time() - stage_start

        sy_ = simplify_silveryasha_data()
        arm = get_arm()
        anitrakt = get_anitrakt()
        fribb = get_fribb_animelists()
        ota = OtakOtaku().get_anime()
        kza = Kaize(
            email=KAIZE_EMAIL,
            password=KAIZE_PASSWORD,
        ).get_anime()
        nau = Nautiljon().get_animes()
        hka = Hikka().get_animes()
        validate_json_files()
        git_changes = check_git_any_changes()
        if git_changes is False:
            proc_stop(start_time, Status.INFO, "No changes in git, exiting")
        pprint.print(Platform.SYSTEM, Status.INFO, "Build database")

        stage_start = time()
        pprint.print(
            Platform.KAIZE,
            Status.BUILD,
            "Linking Kaize slug to MyAnimeList ID by fuzzy matching",
        )
        aod_arr = link_kaize_to_mal(kza, aod_arr)
        pprint.print(
            Platform.NAUTILJON,
            Status.BUILD,
            "Linking Nautiljon slug to MyAnimeList ID by fuzzy matching",
        )
        aod_arr = link_nautiljon_to_mal(nau, aod_arr)
        pprint.print(
            Platform.OTAKOTAKU, Status.BUILD, "Linking Otak Otaku ID to MyAnimeList ID"
        )
        aod_arr = link_otakotaku_to_mal(ota, aod_arr)
        pprint.print(
            Platform.SILVERYASHA,
            Status.BUILD,
            "Linking SilverYasha ID to MyAnimeList ID",
        )
        aod_arr = link_silveryasha_to_mal(sy_, aod_arr)
        run_metrics["stages"]["link_platforms"] = time() - stage_start

        stage_start = time()
        pprint.print(Platform.ARM, Status.BUILD, "Combining ARM data with AOD data")
        aod_arr = combine_arm(arm, aod_arr)
        pprint.print(
            Platform.FRIBB,
            Status.BUILD,
            "Combining Fribb's Animelists data with AOD data",
        )
        aod_arr = combine_fribb(fribb, aod_arr)
        pprint.print(
            Platform.ANITRAKT, Status.BUILD, "Combining AniTrakt data with AOD data"
        )
        aod_arr = combine_anitrakt(anitrakt, aod_arr)
        pprint.print(Platform.HIKKA, Status.BUILD, "Combining Hikka data with AOD data")
        aod_arr = combine_hikka(hka, aod_arr)
        run_metrics["stages"]["combine_external"] = time() - stage_start

        stage_start = time()
        final_arr: list[dict[str, Any]] = []
        with alive_bar(len(aod_arr), title="Fixing missing keys", spinner=None) as bar:  # type: ignore
            for item in aod_arr:
                # Keys sorted alphabetically, but title must be first
                data = {
                    "title": item.get("title", None),
                    "anidb": item.get("anidb", None),
                    "anilist": item.get("anilist", None),
                    "animenewsnetwork": item.get("animenewsnetwork", None),
                    "animeplanet": item.get("animeplanet", None),
                    "anisearch": item.get("anisearch", None),
                    "annict": item.get("annict", None),
                    "hikka": item.get("hikka", None),
                    "imdb": item.get("imdb", None),
                    "kaize": item.get("kaize", None),
                    "kaize_id": item.get("kaize_id", None),
                    "kitsu": item.get("kitsu", None),
                    "letterboxd_lid": item.get("letterboxd_lid", None),
                    "letterboxd_slug": item.get("letterboxd_slug", None),
                    "letterboxd_uid": item.get("letterboxd_uid", None),
                    "livechart": item.get("livechart", None),
                    "myanimelist": item.get("myanimelist", None),
                    "nautiljon": item.get("nautiljon", None),
                    "nautiljon_id": item.get("nautiljon_id", None),
                    "notify": item.get("notify", None),
                    "otakotaku": item.get("otakotaku", None),
                    "shikimori": item.get("shikimori", None),
                    "shoboi": item.get("shoboi", None),
                    "silveryasha": item.get("silveryasha", None),
                    "simkl": item.get("simkl", None),
                    "themoviedb": item.get("themoviedb", None),
                    "themoviedb_season_id": item.get("themoviedb_season_id", None),
                    "themoviedb_type": item.get("themoviedb_type", None),
                    "thetvdb": item.get("thetvdb", None),
                    "thetvdb_season_id": item.get("thetvdb_season_id", None),
                    "trakt": item.get("trakt", None),
                    "trakt_may_invalid": item.get("trakt_may_invalid", None),
                    "trakt_season": item.get("trakt_season", None),
                    "trakt_season_id": item.get("trakt_season_id", None),
                    "trakt_slug": item.get("trakt_slug", None),
                    "trakt_type": item.get("trakt_type", None),
                }
                final_arr.append(data)
                bar()

        # Restore notify.moe mappings from previous database with confidence scoring
        final_arr = restore_notify_safe(final_arr)
        run_metrics["stages"]["finalize"] = time() - stage_start

        stage_start = time()
        with open("database/animeapi.json", "w", encoding="utf-8") as file:
            json.dump(final_arr, file)
        run_metrics["stages"]["write_output"] = time() - stage_start

        attr = update_attribution(final_arr, attribution)
        attr = update_markdown(attr=attr)
        counts: dict[str, int] = attr["counts"]  # type: ignore
        run_metrics["final_counts"] = counts
        print("Data parsed:")
        for key, value in counts.items():
            if key == "total":
                continue
            print(f"* {key}: {value}")

        # Log successful run
        run_metrics["status"] = "success"
        _log_run_metrics(run_metrics)
        proc_stop(start_time, Status.INFO)
    except KeyboardInterrupt:
        run_metrics["status"] = "interrupted"
        _log_run_metrics(run_metrics)
        proc_stop(start_time, Status.ERR, "Stopped by user", 1)
    except Exception as err:
        run_metrics["status"] = "error"
        run_metrics["error"] = str(err)
        _log_run_metrics(run_metrics)
        proc_stop(start_time, Status.ERR, f"Error: {err}", 1, True)


def _log_run_metrics(metrics: dict[str, Any]) -> None:
    """Append run metrics to runs.json for historical tracking."""
    try:
        runs_file = "database/runs.json"
        runs: list[dict[str, Any]] = []

        # Load existing runs
        try:
            with open(runs_file, "r", encoding="utf-8") as f:
                runs = json.load(f)
        except FileNotFoundError:
            runs: list[dict[str, Any]] = []

        # Add total duration
        metrics["duration_seconds"] = sum(
            v for _, v in metrics["stages"].items() if isinstance(v, (int, float))
        )

        # Append new run
        runs.append(metrics)

        # Write back (keep only last 10 runs to avoid huge file)
        with open(runs_file, "w", encoding="utf-8") as f:
            json.dump(runs[-10:], f)
    except Exception as e:
        # Don't crash if logging fails
        pprint.print(Platform.SYSTEM, Status.WARN, f"Failed to log metrics: {e}")
