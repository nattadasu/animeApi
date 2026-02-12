# SPDX-License-Identifier: AGPL-3.0-only AND MIT

import json
from functools import partial
from multiprocessing import Pool, cpu_count
from typing import Any, Union

from alive_progress import alive_bar  # type: ignore
from const import pprint
from prettyprint import Platform, Status
from slugify import slugify
from thefuzz import fuzz  # type: ignore

# Constants for fuzzy matching logic
# When ID count is this many times higher, prefer it even if score is lower
ID_COUNT_MULTIPLIER_THRESHOLD = 2
# When scores are within this many points, prefer the one with more IDs
SCORE_DIFFERENCE_THRESHOLD = 5
# Number of workers for parallel fuzzy matching (0 = auto-detect CPUs)
FUZZY_MATCH_WORKERS = 0


def _score_single_match(
    aod_list: list[dict[str, Any]],
    aod_normalized_cache: dict[int, str],
    threshold: int,
    unlinked_item: dict[str, Any],
) -> tuple[dict[str, Any] | None, int]:
    """
    Worker function for parallel fuzzy matching.
    Scores a single unlinked item against all AOD entries.

    :param aod_list: List of AOD entries
    :param aod_normalized_cache: Pre-normalized titles
    :param threshold: Minimum fuzzy score
    :param unlinked_item: Item to match
    :return: Tuple of (matched_item, id_count)
    """
    return fuzzy_match_with_id_check(
        unlinked_item["title"], aod_list, aod_normalized_cache, threshold
    )


def normalize_title(title: str) -> str:
    """
    Normalize title by removing all whitespace and converting to lowercase
    for accurate fuzzy matching.

    :param title: Title to normalize
    :return: Normalized title without whitespace, in lowercase
    """
    return "".join(title.split()).lower()


def build_slug_index(
    items: list[dict[str, Any]], key_field: str = "title"
) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    """
    Build a slug-based index for fast pre-filtering before fuzzy matching.
    Slugified exact matches are O(1) and eliminate most items before expensive fuzzy logic.

    :param items: List of items to index
    :param key_field: Field name to use for slug generation (default: title)
    :return: Tuple of (slug_lookup dict, original items dict by index)
    """
    slug_lookup: dict[str, dict[str, Any]] = {}
    items_by_index = {}

    for idx, item in enumerate(items):
        items_by_index[idx] = item
        if key_field in item:
            slug = slugify(item[key_field]).replace("-", "")
            if slug:  # Only index non-empty slugs
                # Keep track of duplicates - store in list if collision
                if slug not in slug_lookup:
                    slug_lookup[slug] = item
                else:
                    # Handle slug collisions by storing first match
                    # (rare but possible with different titles)
                    pass

    return slug_lookup, items_by_index


def prefilter_by_slug(
    unlinked: list[dict[str, Any]],
    aod_slug_lookup: dict[str, dict[str, Any]],
    title_field: str = "title",
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """
    Split unlinked items into matched (slug matches) and unmatched (need fuzzy).

    :param unlinked: Items to pre-filter
    :param aod_slug_lookup: AOD slug index from build_slug_index()
    :param title_field: Field name for slug generation
    :return: Tuple of (matched_items, remaining_unlinked)
    """
    matched = []
    remaining = []

    for item in unlinked:
        item_slug = slugify(item[title_field]).replace("-", "")
        if item_slug in aod_slug_lookup:
            matched.append((item, aod_slug_lookup[item_slug]))
        else:
            remaining.append(item)

    return matched, remaining


def fuzzy_match_batch_parallel(
    unlinked: list[dict[str, Any]],
    aod_list: list[dict[str, Any]],
    aod_normalized_cache: dict[int, str],
    threshold: int = 85,
    workers: int = 0,
    title: str = "Fuzzy match title from both databases",
) -> list[tuple[dict[str, Any], dict[str, Any], int]]:
    """
    Perform parallel fuzzy matching on batch of unlinked items.
    Uses multiprocessing to parallelize across multiple CPUs (avoids GIL).

    :param unlinked: Items to fuzzy match
    :param aod_list: AOD list to match against
    :param aod_normalized_cache: Pre-normalized titles
    :param threshold: Minimum fuzzy score
    :param workers: Number of workers (0 = auto-detect)
    :param title: Progress bar title
    :return: List of (unlinked_item, matched_aod_item, id_count) tuples for matches
    """
    if not unlinked:
        return []

    # Auto-detect workers if not specified
    if workers <= 0:
        workers = max(1, cpu_count() - 1)  # Leave one core free

    results = []

    # For small datasets, sequential is faster than multiprocessing overhead
    if len(unlinked) < 10:
        with alive_bar(len(unlinked), title=title, spinner=None) as bar:  # type: ignore
            for item in unlinked:
                aod_item, id_count = fuzzy_match_with_id_check(
                    item["title"], aod_list, aod_normalized_cache, threshold
                )
                if aod_item:
                    results.append((item, aod_item, id_count))
                bar()
    else:
        # Use multiprocessing for larger batches
        with Pool(processes=workers) as pool:
            # Create partial function with fixed arguments
            # Item is passed as last parameter for imap_unordered
            worker_func = partial(
                _score_single_match, aod_list, aod_normalized_cache, threshold
            )

            # imap_unordered yields results as they complete
            # Progress bar updates in real-time as workers finish
            with alive_bar(len(unlinked), title=title, spinner=None) as bar:  # type: ignore
                matches = pool.imap_unordered(worker_func, unlinked, chunksize=10)
                for item, (aod_item, id_count) in zip(unlinked, matches):
                    if aod_item:
                        results.append((item, aod_item, id_count))
                    bar()

    return results


def fuzzy_match_with_id_check(
    unlinked_title: str,
    aod_list: list[dict[str, Any]],
    aod_normalized_cache: dict[int, str] | None = None,
    threshold: int = 85,
) -> tuple[dict[str, Any] | None, int]:
    """
    Perform fuzzy matching but prefer entries with more IDs mapped.
    Uses cached normalized titles for O(n) performance.
    Returns the best match that has the most IDs.

    When multiple matches are above the threshold, prefer the one with
    the most IDs mapped, as it's more likely to be correct and complete.

    This function handles duplicate titles correctly by evaluating all
    entries with the same title and choosing the one with the most IDs.

    :param unlinked_title: Title to match
    :param aod_list: List of AOD entries to match against
    :param aod_normalized_cache: Pre-computed normalized titles indexed by list position
    :param threshold: Minimum fuzzy match score
    :return: Tuple of (matched entry or None, number of IDs in matched entry)
    """
    normalized_unlinked = normalize_title(unlinked_title)
    best_match = None
    best_id_count = 0
    best_score = 0

    for idx, aod_item in enumerate(aod_list):
        # Use cached normalized title if available, otherwise normalize on-the-fly
        if aod_normalized_cache is not None:
            normalized_title = aod_normalized_cache.get(
                idx, normalize_title(aod_item["title"])
            )
        else:
            normalized_title = normalize_title(aod_item["title"])

        score = fuzz.ratio(normalized_unlinked, normalized_title)  # type: ignore

        if score < threshold:
            continue

        # Count non-null IDs
        id_count = sum(
            1
            for key in [
                "anidb",
                "anilist",
                "animenewsnetwork",
                "animeplanet",
                "anisearch",
                "kitsu",
                "livechart",
                "myanimelist",
                "notify",
                "simkl",
            ]
            if aod_item.get(key) is not None
        )

        # Decision logic:
        # 1. If this is the first match, use it
        # 2. If ID count is significantly higher (2x or more), prefer it even if score is lower
        # 3. If scores are close (within 5 points), prefer the one with more IDs
        # 4. Otherwise, prefer higher score
        if best_match is None:
            best_match = aod_item
            best_id_count = id_count
            best_score = score
        elif (
            id_count >= best_id_count * ID_COUNT_MULTIPLIER_THRESHOLD
            and best_id_count > 0
        ):
            # Significantly more IDs, prefer this match
            best_match = aod_item
            best_id_count = id_count
            best_score = score
        elif abs(score - best_score) <= SCORE_DIFFERENCE_THRESHOLD:
            # Scores are close, prefer more IDs
            if id_count > best_id_count:
                best_match = aod_item
                best_id_count = id_count
                best_score = score
        elif score > best_score:
            # Better score wins
            best_match = aod_item
            best_id_count = id_count
            best_score = score

    return best_match, best_id_count


def link_kaize_to_mal(
    kaize: list[dict[str, Any]], aod: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """
    Link Kaize slug to MyAnimeList ID based similarity in title name over 85% in
    fuzzy search

    :param kaize: Kaize data
    :type kaize: list[dict[str, Any]]
    :param aod: AOD data
    :type aod: list[dict[str, Any]]
    :return: Crude AniAPI data, requires refinement after the process
    :rtype: list[dict[str, Any]]
    """
    # add dummy data to aod
    for item in aod:
        item.update(
            {
                "kaize": None,
                "kaize_id": None,
            }
        )
    unlinked: list[dict[str, Any]] = []
    kz_fixed: list[dict[str, Any]] = []
    kz_dict: dict[str, Any] = {}
    aod_dict: dict[str, Any] = {}
    with alive_bar(
        len(aod), title="Translating AOD list to a dict with custom slug", spinner=None
    ) as bar:  # type: ignore
        for item in aod:
            aod_slug = slugify(item["title"]).replace("-", "")
            aod_dict[aod_slug] = item
            bar()
    with alive_bar(
        len(kaize),
        title="Translating Kaize list to a dict with custom slug",
        spinner=None,
    ) as bar:  # type: ignore
        for item in kaize:
            kz_slug = slugify(item["slug"]).replace("-", "")
            kz_dict[kz_slug] = item
            bar()
    with alive_bar(
        len(kz_dict), title="Linking Kaize slug to MyAnimeList ID", spinner=None
    ) as bar:  # type: ignore
        for kz_slug, kz_item in kz_dict.items():
            if kz_slug in aod_dict:
                aod_item: Union[dict[str, Any], None] = aod_dict.get(kz_slug, None)
                if aod_item:
                    # add more data from kaize
                    kz_item.update(
                        {
                            "anidb": aod_item["anidb"],
                            "anilist": aod_item["anilist"],
                            "myanimelist": aod_item["myanimelist"],
                        }
                    )
                    kz_fixed.append(kz_item)
                    aod_item.update(
                        {
                            "kaize": kz_item["slug"],
                            "kaize_id": None
                            if kz_item["kaize"] == 0
                            else kz_item["kaize"],
                        }
                    )
                else:
                    unlinked.append(kz_item)
            else:
                unlinked.append(kz_item)
            bar()
    # on unlinked, fuzzy search the title name
    # Build normalized title cache for all AOD entries (done once)
    aod_normalized_cache = {
        idx: normalize_title(item["title"]) for idx, item in enumerate(aod)
    }
    if unlinked:
        fuzzy_matches = fuzzy_match_batch_parallel(
            unlinked,
            aod,
            aod_normalized_cache,
            threshold=85,
            title="Fuzzy match title from both databases",
        )
        with alive_bar(
            len(fuzzy_matches),
            title="Linking fuzzy-matched Kaize entries",
            spinner=None,
        ) as bar:  # type: ignore
            for item, aod_item, id_count in fuzzy_matches:
                kz_dat = {
                    "anidb": aod_item["anidb"],
                    "anilist": aod_item["anilist"],
                    "myanimelist": aod_item["myanimelist"],
                }
                item.update(kz_dat)
                kz_fixed.append(item)
                aod_item.update(
                    {
                        "kaize": item["slug"],
                        "kaize_id": None if item["kaize"] == 0 else item["kaize"],
                    }
                )
                bar()
    # load manual link data
    with open("database/raw/kaize_manual.json", "r", encoding="utf-8") as file:
        manual_link: dict[str, dict[str, str | int | None]] = json.load(file)
    with alive_bar(
        len(manual_link), title="Insert manual mappings", spinner=None
    ) as bar:  # type: ignore
        for title, kz_item in manual_link.items():
            if isinstance(kz_item, list):
                kz_item = kz_item[0]
                override = True
            else:
                override = False
            # if kz_item["kaize"] doesn't exist in unlinked under slug key, skip
            if override is False and kz_item["kaize"] not in [
                item["slug"] for item in unlinked
            ]:
                bar()
                continue
            for aod_item in aod:
                aod_title = aod_item["title"]
                if title == aod_title:
                    kz_dat = {
                        "kaize": kz_item["kaize"],
                        "kaize_id": None
                        if kz_item["kaize_id"] == 0
                        else kz_item["kaize_id"],
                    }
                    aod_item.update(kz_dat)
                    kz_fixed.append(aod_item)
                    # in unlinked, remove the item with the same id
                    for item in unlinked:
                        if item["kaize"] == kz_item["kaize"]:
                            unlinked.remove(item)
                            break
                    break
            bar()
    # remove if unlinked data is already linked
    with alive_bar(
        len(kz_fixed), title="Removing unrequired data from unlinked", spinner=None
    ) as bar:  # type: ignore
        for item in kz_fixed:
            # if item exist with same id, remove
            for unlinked_item in unlinked:
                if item["kaize"] == unlinked_item["kaize"]:
                    unlinked.remove(unlinked_item)
                    break
            bar()
    aod_list: list[dict[str, Any]] = []
    with alive_bar(
        len(aod_dict), title="Translating AOD dict to a list", spinner=None
    ) as bar:  # type: ignore
        for _, value in aod_dict.items():
            # check if kaize_id or kaize key not exists, then set it to None
            if "kaize" not in value:
                value["kaize"] = None
            if "kaize_id" not in value:
                value["kaize_id"] = None
            aod_list.append(value)
            bar()
    merged: list[dict[str, Any]] = []
    merged.extend(aod)

    # add missing items from old AOD data
    with alive_bar(
        len(aod_list), title="Reintroduce old list items", spinner=None
    ) as bar:  # type: ignore
        # Create a set of existing MAL IDs for faster lookup
        existing_mal_ids = {
            item.get("myanimelist") for item in merged if item.get("myanimelist")
        }

        for item in aod_list:
            mal_id = item.get("myanimelist")
            # Only add if has MAL ID and it's not already in merged
            if mal_id and mal_id not in existing_mal_ids:
                merged.append(item)
                existing_mal_ids.add(mal_id)
            bar()

    aod_list = merged

    pprint.print(
        Platform.KAIZE,
        Status.PASS,
        "Kaize slug linked to MyAnimeList ID, unlinked data will be saved to kaize_unlinked.json.",
        "Total linked data:",
        f"{len(kz_fixed)},",
        "total unlinked data:",
        f"{len(unlinked)}",
    )
    with open("database/raw/kaize_unlinked.json", "w", encoding="utf-8") as file:
        json.dump(unlinked, file)
    return aod_list


def link_nautiljon_to_mal(
    nautiljon: list[dict[str, Any]], aod: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """
    Link Nautiljon ID to MyAnimeList ID based similarity in title name over 85%
    in fuzzy search

    :param nautiljon: Nautiljon data
    :type nautiljon: list[dict[str, Any]]
    :param aod: AOD data
    :type aod: list[dict[str, Any]]
    :return: Crude AniAPI data, requires refinement after the process
    :rtype: list[dict[str, Any]]
    """
    for item in aod:
        item.update(
            {
                "nautiljon": None,
                "nautiljon_id": None,
            }
        )
    unlinked: list[dict[str, Any]] = []
    nautiljon_fixed: list[dict[str, Any]] = []
    nautiljon_dict: dict[str, Any] = {}
    aod_dict: dict[str, Any] = {}
    with alive_bar(
        len(aod),
        title="Translating AOD list to a dict using title as key",
        spinner=None,
    ) as bar:  # type: ignore
        for item in aod:
            # if previous key exists, skip
            if item["title"] in aod_dict:
                bar()
                continue
            aod_dict[item["title"]] = item
            bar()
    with alive_bar(
        len(nautiljon),
        title="Translating Nautiljon list to a dict with title as key",
        spinner=None,
    ) as bar:  # type: ignore
        for item in nautiljon:
            nautiljon_dict[item["title"]] = item
            bar()
    # link nautiljon to aod
    with alive_bar(
        len(nautiljon_dict), title="Linking Nautiljon ID to AOD", spinner=None
    ) as bar:  # type: ignore
        for title, nautiljon_item in nautiljon_dict.items():
            if title in aod_dict:
                aod_item = aod_dict.get(title)
                if aod_item:
                    aod_item.update(
                        {
                            "nautiljon": nautiljon_item["slug"],
                            "nautiljon_id": nautiljon_item["entry_id"],
                        }
                    )
                    nautiljon_item.update(
                        {
                            "anidb": aod_item["anidb"],
                            "anilist": aod_item["anilist"],
                            "myanimelist": aod_item["myanimelist"],
                        }
                    )
                    nautiljon_fixed.append(nautiljon_item)
                else:
                    unlinked.append(nautiljon_item)
            else:
                unlinked.append(nautiljon_item)
            bar()
    # fuzzy search the rest of unlinked data
    # Build slug index and pre-filter
    aod_slug_lookup, _ = build_slug_index(aod, "title")
    slug_matched, unlinked_for_fuzzy = prefilter_by_slug(unlinked, aod_slug_lookup)

    # Update records from slug matches
    with alive_bar(
        len(slug_matched), title="Linking slug-matched Nautiljon entries", spinner=None
    ) as bar:  # type: ignore
        for item, aod_item in slug_matched:
            item.update(
                {
                    "anidb": aod_item["anidb"],
                    "anilist": aod_item["anilist"],
                    "myanimelist": aod_item["myanimelist"],
                }
            )
            nautiljon_fixed.append(item)
            aod_item.update(
                {
                    "nautiljon": item["slug"],
                    "nautiljon_id": item["entry_id"],
                }
            )
            bar()

    # Fuzzy match remaining items with parallel workers
    aod_normalized_cache = {
        idx: normalize_title(item["title"]) for idx, item in enumerate(aod)
    }
    if unlinked_for_fuzzy:
        fuzzy_matches = fuzzy_match_batch_parallel(
            unlinked_for_fuzzy,
            aod,
            aod_normalized_cache,
            threshold=90,
            title="Fuzzy match title from both databases",
        )
        with alive_bar(
            len(fuzzy_matches),
            title="Linking fuzzy-matched Nautiljon entries",
            spinner=None,
        ) as bar:  # type: ignore
            for item, aod_item, id_count in fuzzy_matches:
                item.update(
                    {
                        "anidb": aod_item["anidb"],
                        "anilist": aod_item["anilist"],
                        "myanimelist": aod_item["myanimelist"],
                    }
                )
                nautiljon_fixed.append(item)
                aod_item.update(
                    {
                        "nautiljon": item["slug"],
                        "nautiljon_id": item["entry_id"],
                    }
                )
                bar()

    # Build normalized title cache for remaining unlinked AOD entries
    aod_normalized_cache = {
        idx: normalize_title(item["title"]) for idx, item in enumerate(aod)
    }
    # remove fixed data from unlinked
    with alive_bar(
        len(nautiljon_fixed), title="Removing fixed data from unlinked", spinner=None
    ) as bar:  # type: ignore
        for item in nautiljon_fixed:
            for unlinked_item in unlinked:
                if item["slug"] == unlinked_item["slug"]:
                    unlinked.remove(unlinked_item)
                    break
            bar()
    aod_list: list[dict[str, Any]] = []
    with alive_bar(
        len(aod_dict), title="Translating AOD dict to a list", spinner=None
    ) as bar:  # type: ignore
        for _, value in aod_dict.items():
            aod_list.append(value)
            bar()
    merged: list[dict[str, Any]] = []
    merged.extend(aod_list)
    with alive_bar(
        len(aod_list), title="Reintroduce old list items", spinner=None
    ) as bar:  # type: ignore
        # Create a set of existing MAL IDs for faster lookup
        existing_mal_ids = {
            item.get("myanimelist") for item in merged if item.get("myanimelist")
        }

        for item in aod_list:
            mal_id = item.get("myanimelist")
            # Only add if has MAL ID and it's not already in merged
            if mal_id and mal_id not in existing_mal_ids:
                merged.append(item)
                existing_mal_ids.add(mal_id)
            bar()

    pprint.print(
        Platform.NAUTILJON,
        Status.PASS,
        "Nautiljon slug linked to MyAnimeList ID, unlinked data will be saved to nautiljon_unlinked.json.",
        "Total linked data:",
        f"{len(nautiljon_fixed)},",
        "total unlinked data:",
        f"{len(unlinked)}",
    )
    with open("database/raw/nautiljon_unlinked.json", "w", encoding="utf-8") as file:
        json.dump(unlinked, file)
    return merged


def link_otakotaku_to_mal(
    otakotaku: list[dict[str, Any]], aod: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """
    Link Otak Otaku ID to MyAnimeList ID based similarity in title name over 85%
    in fuzzy search

    :param otakotaku: Otak Otaku data
    :type otakotaku: list[dict[str, Any]]
    :param aod: AOD data
    :type aod: list[dict[str, Any]]
    :return: Crude AniAPI data, requires refinement after the process
    :rtype: list[dict[str, Any]]
    """
    unlinked: list[dict[str, Any]] = []
    ot_fixed: list[dict[str, Any]] = []
    ot_dict: dict[str, Any] = {}
    aod_dict: dict[str, Any] = {}
    with alive_bar(
        len(aod), title="Translating AOD list to a dict with MAL ID", spinner=None
    ) as bar:  # type: ignore
        for item in aod:
            aod_dict[item["title"]] = item
            bar()
    with alive_bar(
        len(otakotaku),
        title="Translating Otakotaku list to a dict with MAL ID",
        spinner=None,
    ) as bar:  # type: ignore
        for item in otakotaku:
            ot_dict[item["title"]] = item
            bar()
    with alive_bar(
        len(ot_dict), title="Linking Otak Otaku ID to MyAnimeList ID", spinner=None
    ) as bar:  # type: ignore
        for title, ot_item in ot_dict.items():
            if title in aod_dict:
                aod_item: Union[dict[str, Any], None] = aod_dict.get(title, None)
                if aod_item:
                    # add more data from otakotaku
                    ot_dat = {
                        "otakotaku": ot_item["otakotaku"],
                    }
                    aod_item.update(ot_dat)
                    ot_fixed.append(aod_item)
                else:
                    unlinked.append(ot_item)
            else:
                unlinked.append(ot_item)
            bar()
    # on unlinked, fuzzy search the title name
    # Build slug index for fast pre-filtering (eliminates ~70-80% of items)
    aod_slug_lookup, _ = build_slug_index(aod, "title")
    unlinked_filtered: list[dict[str, Any]] = []

    # Pre-filter using slugs before expensive fuzzy matching
    with alive_bar(
        len(unlinked), title="Pre-filtering unlinked with slug matching", spinner=None
    ) as bar:  # type: ignore
        for item in unlinked:
            ot_slug = slugify(item["title"]).replace("-", "")
            if ot_slug not in aod_slug_lookup:
                # Only add to fuzzy matching queue if slug doesn't match
                unlinked_filtered.append(item)
            else:
                # Slug matched - use it directly
                aod_item = aod_slug_lookup[ot_slug]
                ot_dat = {"otakotaku": item["otakotaku"]}
                aod_item.update(ot_dat)
                ot_fixed.append(aod_item)
            bar()

    # Build normalized title cache for remaining unlinked AOD entries
    aod_normalized_cache = {
        idx: normalize_title(item["title"]) for idx, item in enumerate(aod)
    }

    # Pre-process titles for season normalization
    replace_dict = {
        "Season 2": "2nd Season",
        "Season 3": "3rd Season",
    }
    # autopopulate the replace dict with ordinal numbers from 4 to 100
    for i in range(4, 21):
        # if it's 11, 12, 13, use th, else use st, nd, rd
        if i in [11, 12, 13]:
            replace_dict[f"Season {i}"] = f"{i}th Season"
        elif i % 10 == 1:
            replace_dict[f"Season {i}"] = f"{i}st Season"
        elif i % 10 == 2:
            replace_dict[f"Season {i}"] = f"{i}nd Season"
        elif i % 10 == 3:
            replace_dict[f"Season {i}"] = f"{i}rd Season"
        else:
            replace_dict[f"Season {i}"] = f"{i}th Season"

    # Apply season replacements before fuzzy matching
    unlinked_normalized = []
    for item in unlinked_filtered:
        normalized_item = item.copy()
        title = item["title"]
        for key, value in replace_dict.items():
            title = title.replace(key, value)
        normalized_item["title"] = title
        unlinked_normalized.append(normalized_item)

    if unlinked_normalized:
        fuzzy_matches = fuzzy_match_batch_parallel(
            unlinked_normalized,
            aod,
            aod_normalized_cache,
            threshold=90,
            title="Fuzzy match title from both databases",
        )
        with alive_bar(
            len(fuzzy_matches),
            title="Linking fuzzy-matched OtakOtaku entries",
            spinner=None,
        ) as bar:  # type: ignore
            for item, aod_item, id_count in fuzzy_matches:
                ot_dat = {
                    "otakotaku": item["otakotaku"],
                }
                aod_item.update(ot_dat)
                ot_fixed.append(aod_item)
                bar()
    # load manual link data
    with open("database/raw/otakotaku_manual.json", "r", encoding="utf-8") as file:
        manual_link: dict[str, int] = json.load(file)
    with alive_bar(
        len(manual_link), title="Insert manual mappings", spinner=None
    ) as bar:  # type: ignore
        for title, oo_id in manual_link.items():
            if isinstance(oo_id, list):
                oo_id = oo_id[0]
                override = True
            else:
                override = False
            # skip if not in unlinked
            if override is False and oo_id not in [
                item["otakotaku"] for item in unlinked
            ]:
                bar()
                continue
            for aod_item in aod:
                aod_title = aod_item["title"]
                if title == aod_title:
                    oo_dat = {"otakotaku": oo_id}
                    aod_item.update(oo_dat)
                    ot_fixed.append(aod_item)
                    # in unlinked, remove the item with the same id
                    for item in unlinked:
                        if item["otakotaku"] == oo_id:
                            unlinked.remove(item)
                    break
            bar()
    # remove if unlinked data is already linked
    with alive_bar(
        len(ot_fixed), title="Removing unrequired data from unlinked", spinner=None
    ) as bar:  # type: ignore
        for item in ot_fixed:
            # if item exist with same id, remove
            for unlinked_item in unlinked:
                if item["otakotaku"] == unlinked_item["otakotaku"]:
                    unlinked.remove(unlinked_item)
                    break
            bar()
    aod_list: list[dict[str, Any]] = []
    with alive_bar(
        len(aod_dict), title="Translating AOD dict to a list", spinner=None
    ) as bar:  # type: ignore
        for _, value in aod_dict.items():
            if "otakotaku" not in value:
                value["otakotaku"] = None
            aod_list.append(value)
            bar()
    merged: list[dict[str, Any]] = []
    merged.extend(aod)

    # add missing items from old AOD data
    with alive_bar(
        len(aod_list), title="Reintroduce old list items", spinner=None
    ) as bar:  # type: ignore
        # Create a set of existing MAL IDs for faster lookup
        existing_mal_ids = {
            item.get("myanimelist") for item in merged if item.get("myanimelist")
        }

        for item in aod_list:
            mal_id = item.get("myanimelist")
            # Only add if has MAL ID and it's not already in merged
            if mal_id and mal_id not in existing_mal_ids:
                merged.append(item)
                existing_mal_ids.add(mal_id)
            bar()

    aod_list = merged
    pprint.print(
        Platform.OTAKOTAKU,
        Status.PASS,
        "Otak Otaku entries linked to MyAnimeList ID, unlinked data will be saved to otakotaku_unlinked.json.",
        "Total linked data:",
        f"{len(ot_fixed)},",
        "total unlinked data:",
        f"{len(unlinked)}",
    )
    with open("database/raw/otakotaku_unlinked.json", "w", encoding="utf-8") as file:
        json.dump(unlinked, file)
    return aod_list


def link_silveryasha_to_mal(
    silveryasha: list[dict[str, Any]], aod: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """
    Link SilverYasha ID to MyAnimeList ID based similarity in title name over
    85% in fuzzy search

    :param silveryasha: SilverYasha data
    :type silveryasha: list[dict[str, Any]]
    :param aod: AOD data
    :type aod: list[dict[str, Any]]
    :return: Crude AniAPI data, requires refinement after the process
    :rtype: list[dict[str, Any]]
    """
    unlinked: list[dict[str, Any]] = []
    sy_fixed: list[dict[str, Any]] = []
    sy_dict: dict[str, Any] = {}
    aod_dict: dict[str, Any] = {}
    with alive_bar(
        len(aod), title="Translating AOD list to a dict with MAL ID", spinner=None
    ) as bar:  # type: ignore
        for item in aod:
            if item["myanimelist"]:
                aod_dict[f"{item['myanimelist']}"] = item
            else:
                aod_dict[item["title"]] = item
            bar()
    with alive_bar(
        len(silveryasha),
        title="Translating SilverYasha list to a dict with MAL ID",
        spinner=None,
    ) as bar:  # type: ignore
        for item in silveryasha:
            mal_id = item["myanimelist"]
            if mal_id:
                sy_dict[f"{mal_id}"] = {
                    "title": item["title"],
                    "silveryasha": item["silveryasha"],
                }
            else:
                sy_dict[item["title"]] = {
                    "title": item["title"],
                    "silveryasha": item["silveryasha"],
                }
            bar()
    with alive_bar(
        len(sy_dict), title="Linking SilverYasha ID to MyAnimeList ID", spinner=None
    ) as bar:  # type: ignore
        for mal_id, sy_item in sy_dict.items():
            if mal_id in aod_dict:
                aod_item: Union[dict[str, Any], None] = aod_dict.get(f"{mal_id}", None)
                if aod_item:
                    # add more data from silveryasha
                    sy_dat = {
                        "silveryasha": sy_item["silveryasha"],
                    }
                    aod_item.update(sy_dat)
                    sy_fixed.append(aod_item)
                else:
                    unlinked.append(sy_item)
            else:
                unlinked.append(sy_item)
            bar()
    # on unlinked, fuzzy search the title name
    # Build slug index for fast pre-filtering (eliminates ~70-80% of items)
    aod_slug_lookup, _ = build_slug_index(aod, "title")
    unlinked_filtered: list[dict[str, Any]] = []

    # Pre-filter using slugs before expensive fuzzy matching
    with alive_bar(
        len(unlinked), title="Pre-filtering unlinked with slug matching", spinner=None
    ) as bar:  # type: ignore
        for item in unlinked:
            sy_slug = slugify(item["title"]).replace("-", "")
            if sy_slug not in aod_slug_lookup:
                # Only add to fuzzy matching queue if slug doesn't match
                unlinked_filtered.append(item)
            else:
                # Slug matched - use it directly
                aod_item = aod_slug_lookup[sy_slug]
                sy_dat = {"silveryasha": item["silveryasha"]}
                aod_item.update(sy_dat)
                sy_fixed.append(aod_item)
            bar()

    # Build normalized title cache for remaining unlinked AOD entries
    aod_normalized_cache = {
        idx: normalize_title(item["title"]) for idx, item in enumerate(aod)
    }
    if unlinked_filtered:
        fuzzy_matches = fuzzy_match_batch_parallel(
            unlinked_filtered,
            aod,
            aod_normalized_cache,
            threshold=95,
            title="Fuzzy match title from both databases",
        )
        with alive_bar(
            len(fuzzy_matches),
            title="Linking fuzzy-matched SilverYasha entries",
            spinner=None,
        ) as bar:  # type: ignore
            for item, aod_item, id_count in fuzzy_matches:
                sy_dat = {
                    "silveryasha": item["silveryasha"],
                }
                aod_item.update(sy_dat)
                sy_fixed.append(aod_item)
                bar()
    # load manual link data
    with open("database/raw/silveryasha_manual.json", "r", encoding="utf-8") as file:
        manual_link: dict[str, int] = json.load(file)
    with alive_bar(
        len(manual_link), title="Insert manual mappings", spinner=None
    ) as bar:  # type: ignore
        for title, sy_id in manual_link.items():
            if isinstance(sy_id, list):
                sy_id = sy_id[0]
                override = True
            else:
                override = False
            if override is False and sy_id not in [
                item["silveryasha"] for item in unlinked
            ]:
                bar()
                continue
            for aod_item in aod:
                aod_title = aod_item["title"]
                if title == aod_title:
                    sy_dat = {
                        "silveryasha": sy_id,
                    }
                    aod_item.update(sy_dat)
                    sy_fixed.append(aod_item)
                    # in unlinked, remove the item with the same id
                    for item in unlinked:
                        if item["silveryasha"] == sy_id:
                            unlinked.remove(item)
                    break
            bar()
    # remove if unlinked data is already linked
    with alive_bar(
        len(sy_fixed), title="Removing unrequired data from unlinked", spinner=None
    ) as bar:  # type: ignore
        for item in sy_fixed:
            # if item exist with same id, remove
            for unlinked_item in unlinked:
                if item["silveryasha"] == unlinked_item["silveryasha"]:
                    unlinked.remove(unlinked_item)
                    break
            bar()
    aod_list: list[dict[str, Any]] = []
    with alive_bar(
        len(aod_dict), title="Translating AOD dict to a list", spinner=None
    ) as bar:  # type: ignore
        for _, value in aod_dict.items():
            if "silveryasha" not in value:
                value["silveryasha"] = None
            aod_list.append(value)
            bar()
    merged: list[dict[str, Any]] = []
    merged.extend(aod)

    # add missing items from old AOD data
    with alive_bar(
        len(aod_list), title="Reintroduce old list items", spinner=None
    ) as bar:  # type: ignore
        # Create a set of existing MAL IDs for faster lookup
        existing_mal_ids = {
            item.get("myanimelist") for item in merged if item.get("myanimelist")
        }

        for item in aod_list:
            mal_id = item.get("myanimelist")
            # Only add if has MAL ID and it's not already in merged
            if mal_id and mal_id not in existing_mal_ids:
                merged.append(item)
                existing_mal_ids.add(mal_id)
            bar()

    aod_list = merged
    pprint.print(
        Platform.SILVERYASHA,
        Status.PASS,
        "SilverYasha entry linked to MyAnimeList ID, unlinked data will be saved to silveryasha_unlinked.json.",
        "Total linked data:",
        f"{len(sy_fixed)},",
        "total unlinked data:",
        f"{len(unlinked)}",
    )
    with open("database/raw/silveryasha_unlinked.json", "w", encoding="utf-8") as file:
        json.dump(unlinked, file)
    return aod_list
