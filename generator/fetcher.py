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
        url="https://github.com/manami-project/anime-offline-database/releases/download/latest/anime-offline-database-minified.json.zst",
        file_name="aod",
        file_type="zst",
        platform=Platform.ANIMEOFFLINEDATABASE,
    )
    content: dict[str, Any] = ddump.dumper()
    pprint.print(
        Platform.ANIMEOFFLINEDATABASE,
        Status.PASS,
        "anime-offline-database data retrieved successfully",
    )
    return content


def get_anime_offline_database_2025_52() -> dict[str, Any] | None:
    """
    Get info from manami-project/anime-offline-database 2025-52 snapshot
    (last version with notify.moe support)

    Attempts to download; falls back to locally cached version if available.
    Returns None if neither is available (graceful degradation).

    :return: AOD 2025-52 data or None if unavailable
    :rtype: dict[str, Any] | None
    """
    ddump = Downloader(
        url="https://github.com/manami-project/anime-offline-database/releases/download/2025-52/anime-offline-database-minified.json.zst",
        file_name="aod_2025_52",
        file_type="zst",
        platform=Platform.ANIMEOFFLINEDATABASE,
    )
    try:
        content: dict[str, Any] = ddump.dumper()
        pprint.print(
            Platform.ANIMEOFFLINEDATABASE,
            Status.PASS,
            "anime-offline-database 2025-52 snapshot retrieved successfully",
        )
        return content
    except SystemExit:
        pprint.print(
            Platform.ANIMEOFFLINEDATABASE,
            Status.ERR,
            "2025-52 snapshot unavailable, attempting to use cached version",
        )
        try:
            with open("database/raw/aod_2025_52.json", "r", encoding="utf-8") as file:
                content = json.load(file)
                pprint.print(
                    Platform.ANIMEOFFLINEDATABASE,
                    Status.PASS,
                    "Loaded cached 2025-52 snapshot for notify.moe enrichment",
                )
                return content
        except FileNotFoundError:
            pprint.print(
                Platform.ANIMEOFFLINEDATABASE,
                Status.ERR,
                "No cached snapshot available, notify.moe enrichment will be skipped",
            )
            return None


def get_notify_rensetsu() -> list[dict[str, Any]]:
    """
    Get info from rensetsu/db.notify.rensetsu-mirai

    :return: Notify.moe data from Rensetsu
    :rtype: list[dict[str, Any]]
    """
    ddump = Downloader(
        url="https://github.com/rensetsu/db.notify.rensetsu-mirai/raw/refs/heads/main/notify_min.json",
        file_name="db.notify.rensetsu-mirai",
        file_type="json",
        platform=Platform.SYSTEM,
    )
    data: list[dict[str, Any]] = ddump.dumper()
    pprint.print(
        Platform.SYSTEM,
        Status.PASS,
        "Notify.moe data from Rensetsu retrieved successfully",
    )
    return data


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
    base_url = "https://raw.githubusercontent.com/rensetsu/db.trakt.extended-anitrakt/main/json/output/"
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


def merge_notify_with_aod(
    aod_latest: list[dict[str, Any]],
    aod_2025_52: dict[str, Any] | None,
    notify_data: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Merge notify.moe data with latest AOD data.

    Process:
    1. Parse 2025-52 AOD snapshot to extract notify.moe IDs (if available)
    2. Create mapping of (other IDs) -> notify ID from 2025-52
    3. Apply notify IDs to latest AOD entries based on matching IDs
    4. Use notify.moe Rensetsu data to fill any remaining gaps

    :param aod_latest: Latest AOD data (simplified)
    :type aod_latest: list[dict[str, Any]]
    :param aod_2025_52: AOD 2025-52 snapshot (raw) or None if unavailable
    :type aod_2025_52: dict[str, Any] | None
    :param notify_data: Notify.moe data from Rensetsu
    :type notify_data: list[dict[str, Any]]
    :return: AOD data with notify.moe IDs merged
    :rtype: list[dict[str, Any]]
    """
    pprint.print(
        Platform.SYSTEM,
        Status.NOTICE,
        "Starting notify.moe merge process",
    )

    # Step 1: Extract notify IDs from 2025-52 snapshot (if available)
    notify_lookup_from_old: dict[tuple[str, Any], str] = {}

    if aod_2025_52:
        pprint.print(
            Platform.SYSTEM,
            Status.NOTICE,
            "Extracting notify.moe IDs from 2025-52 snapshot",
        )

        old_aod_simplified = simplify_aod_data(aod_2025_52)

        # Create lookup maps for 2025-52 data
        # Map structure: {(id_type, id_value): notify_id}

        with alive_bar(
            len(old_aod_simplified),
            title="Building notify.moe lookup from 2025-52",
            spinner=None,
        ) as bar:  # type: ignore
            for entry in old_aod_simplified:
                notify_id = entry.get("notify")
                if notify_id:
                    # Create lookups for all available IDs
                    for id_type in [
                        "anidb",
                        "anilist",
                        "animenewsnetwork",
                        "animeplanet",
                        "anisearch",
                        "kitsu",
                        "livechart",
                        "myanimelist",
                        "simkl",
                    ]:
                        id_value = entry.get(id_type)
                        if id_value:
                            notify_lookup_from_old[(id_type, id_value)] = notify_id
                bar()

        pprint.print(
            Platform.SYSTEM,
            Status.PASS,
            f"Built lookup with {len(notify_lookup_from_old)} ID mappings",
        )
    else:
        pprint.print(
            Platform.SYSTEM,
            Status.NOTICE,
            "2025-52 snapshot unavailable, will use Rensetsu data only",
        )

    # Step 2: Create lookup from notify Rensetsu data
    pprint.print(
        Platform.SYSTEM,
        Status.NOTICE,
        "Building notify.moe lookup from Rensetsu data",
    )

    notify_lookup_from_rensetsu: dict[tuple[str, Any], str] = {}

    with alive_bar(
        len(notify_data),
        title="Processing Rensetsu notify.moe data",
        spinner=None,
    ) as bar:  # type: ignore
        for entry in notify_data:
            mappings = entry.get("mappings", {})
            notify_id = mappings.get("notify")

            if notify_id:
                # Extract IDs from mappings
                if "anidb" in mappings:
                    notify_lookup_from_rensetsu[("anidb", mappings["anidb"])] = (
                        notify_id
                    )
                if "anilist" in mappings:
                    notify_lookup_from_rensetsu[("anilist", mappings["anilist"])] = (
                        notify_id
                    )
                if "kitsu" in mappings and isinstance(mappings["kitsu"], dict):
                    kitsu_id = mappings["kitsu"].get("id")
                    if kitsu_id:
                        notify_lookup_from_rensetsu[("kitsu", kitsu_id)] = notify_id
                if "myanimelist" in mappings:
                    notify_lookup_from_rensetsu[
                        ("myanimelist", mappings["myanimelist"])
                    ] = notify_id
            bar()

    pprint.print(
        Platform.SYSTEM,
        Status.PASS,
        f"Built Rensetsu lookup with {len(notify_lookup_from_rensetsu)} ID mappings",
    )

    # Step 3: Apply notify IDs to latest AOD entries
    pprint.print(
        Platform.SYSTEM,
        Status.NOTICE,
        "Merging notify.moe IDs into latest AOD data",
    )

    matches_from_old = 0
    matches_from_rensetsu = 0

    with alive_bar(
        len(aod_latest),
        title="Applying notify.moe IDs to latest AOD",
        spinner=None,
    ) as bar:  # type: ignore
        for entry in aod_latest:
            # Try to find notify ID from 2025-52 snapshot first
            notify_id = None

            for id_type in [
                "anidb",
                "anilist",
                "animenewsnetwork",
                "animeplanet",
                "anisearch",
                "kitsu",
                "livechart",
                "myanimelist",
                "simkl",
            ]:
                id_value = entry.get(id_type)
                if id_value:
                    lookup_key = (id_type, id_value)
                    if lookup_key in notify_lookup_from_old:
                        notify_id = notify_lookup_from_old[lookup_key]
                        matches_from_old += 1
                        break

            # If not found in old snapshot, try Rensetsu data
            if not notify_id:
                for id_type in ["anidb", "anilist", "kitsu", "myanimelist"]:
                    id_value = entry.get(id_type)
                    if id_value:
                        lookup_key = (id_type, id_value)
                        if lookup_key in notify_lookup_from_rensetsu:
                            notify_id = notify_lookup_from_rensetsu[lookup_key]
                            matches_from_rensetsu += 1
                            break

            # Add notify ID if found
            if notify_id:
                entry["notify"] = notify_id

            bar()

    pprint.print(
        Platform.SYSTEM,
        Status.PASS,
        f"Merge complete: {matches_from_old} from 2025-52, {matches_from_rensetsu} from Rensetsu",
    )

    return aod_latest


def restore_notify_safe(
    new_data: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Restore notify.moe IDs from previous database with confidence scoring.

    For each title in the new data, check if the previous database had a notify.moe ID.
    Use confidence scoring based on overlapping critical IDs (MAL, AniDB, AniList, Kitsu)
    to ensure the entries are truly the same anime before restoring the notify ID.

    :param new_data: Newly generated database entries
    :type new_data: list[dict[str, Any]]
    :return: Database with restored notify.moe mappings
    :rtype: list[dict[str, Any]]
    """
    pprint.print(
        Platform.SYSTEM,
        Status.NOTICE,
        "Restoring notify.moe mappings with ID confidence scoring",
    )

    try:
        with open("database/animeapi.json", "r", encoding="utf-8") as file:
            previous_data = json.load(file)
    except FileNotFoundError:
        pprint.print(
            Platform.SYSTEM,
            Status.NOTICE,
            "No previous database found, skipping notify.moe restoration",
        )
        return new_data

    if not isinstance(previous_data, list):
        pprint.print(
            Platform.SYSTEM,
            Status.ERR,
            "Previous database has invalid format, skipping restoration",
        )
        return new_data

    # Confidence scoring IDs
    confidence_ids = ["myanimelist", "anidb", "anilist", "kitsu"]

    # Create lookup by title for previous database
    prev_by_title: dict[str, dict[str, Any]] = {}

    for entry in previous_data:
        title = entry.get("title")
        if title:
            if title not in prev_by_title:
                prev_by_title[title] = entry

    # Track results
    restored_count = 0
    high_confidence_count = 0
    low_confidence_count = 0

    # Restore notify.moe mappings with confidence checking
    with alive_bar(
        len(new_data),
        title="Restoring notify.moe with confidence scoring",
        spinner=None,
    ) as bar:  # type: ignore
        for entry in new_data:
            title = entry.get("title")

            # Only restore if new entry doesn't have notify.moe ID
            if title and not entry.get("notify") and title in prev_by_title:
                prev_entry = prev_by_title[title]
                prev_notify = prev_entry.get("notify")

                if prev_notify:
                    # Calculate confidence score based on matching IDs
                    matching_ids = 0
                    total_ids = 0

                    for id_type in confidence_ids:
                        new_id = entry.get(id_type)
                        prev_id = prev_entry.get(id_type)

                        if prev_id is not None:
                            total_ids += 1
                            # Perfect match or both missing is good confidence
                            if new_id == prev_id:
                                matching_ids += 1

                    # Restore if high confidence (majority match) or have any matching ID
                    if total_ids > 0:
                        confidence_ratio = matching_ids / total_ids
                        if matching_ids > 0:  # Optimistic: restore if any ID matches
                            entry["notify"] = prev_notify
                            restored_count += 1
                            if confidence_ratio >= 0.5:
                                high_confidence_count += 1
                            else:
                                low_confidence_count += 1

            bar()

    pprint.print(
        Platform.SYSTEM,
        Status.PASS,
        f"Restored {restored_count} notify.moe mappings ({high_confidence_count} high confidence, {low_confidence_count} low confidence)",
    )

    return new_data
