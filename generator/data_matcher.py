# SPDX-License-Identifier: AGPL-3.0-only AND MIT

"""
DataMatcher class for linking external platform data to MyAnimeList IDs.
Encapsulates common linking patterns (slug matching, fuzzy matching, manual mappings).
Reduces code duplication across Kaize, Nautiljon, SilverYasha, OtakOtaku platforms.
"""

import json
from functools import partial
from multiprocessing import Pool, cpu_count
from typing import Any, Callable, Optional

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


class DataMatcher:
    """
    Matches external platform data (Kaize, Nautiljon, SilverYasha, OtakOtaku)
    to MyAnimeList IDs using slug matching, fuzzy matching, and manual mappings.
    """

    def __init__(
        self,
        platform_name: str,
        platform: Platform,
        external_data: list[dict[str, Any]],
        aod_data: list[dict[str, Any]],
        id_field: str,
        slug_or_title_field: str = "title",
        has_slug: bool = False,
        update_func: Optional[Callable[[dict[str, Any], dict[str, Any]], None]] = None,
    ):
        """
        Initialize matcher for a platform.

        :param platform_name: Name for logging (kaize, nautiljon, etc)
        :param platform: Platform enum for logging
        :param external_data: Data from external platform
        :param aod_data: Anime-offline-database reference data
        :param id_field: Field name storing platform ID (e.g., "kaize_id", "entry_id")
        :param slug_or_title_field: Field to use for slug generation
        :param has_slug: Whether this platform has a slug field (True for kaize/nautiljon)
        :param update_func: Custom function to update AOD item with external data
        """
        self.platform_name = platform_name
        self.platform = platform
        self.external_data = external_data
        self.aod_data = aod_data
        self.id_field = id_field
        self.slug_or_title_field = slug_or_title_field
        self.has_slug = has_slug
        self.update_func = update_func
        self.matched_items: list[dict[str, Any]] = []
        self.unmatched_items: list[dict[str, Any]] = []

    def _update_aod_item(
        self, aod_item: dict[str, Any], external_item: dict[str, Any]
    ) -> None:
        """
        Update AOD item with platform ID and optionally slug/title.
        Only sets {platform}_id field if has_slug is True.

        :param aod_item: AOD item to update
        :param external_item: External platform item with data
        """
        if self.update_func:
            self.update_func(aod_item, external_item)
            return

        update_dict = {self.platform_name: external_item.get(self.id_field)}
        if self.has_slug:
            update_dict[f"{self.platform_name}_id"] = external_item.get(
                self.slug_or_title_field
            )
        aod_item.update(update_dict)

    def link_by_mal_id(self, mal_id_field: str = "mal_id") -> "DataMatcher":
        """
        Link external data to AOD by direct MyAnimeList ID match.
        Only processes entries with non-null mal_id field; others remain unmatched.
        This is the fastest linking method (O(1) direct lookup).

        :param mal_id_field: Field name in external data containing MAL ID
        :return: self for chaining
        """
        if not self.unmatched_items:
            return self

        # Build MAL ID lookup in AOD for fast O(1) matching
        aod_by_mal_id = {
            item.get("myanimelist"): item
            for item in self.aod_data
            if item.get("myanimelist") is not None
        }

        matched = []
        remaining = []

        with alive_bar(
            len(self.unmatched_items),
            title=f"Linking {self.platform_name} by direct MAL ID",
            spinner=None,
        ) as bar:  # type: ignore
            for external_item in self.unmatched_items:
                mal_id = external_item.get(mal_id_field)

                if mal_id is not None and mal_id in aod_by_mal_id:
                    # Direct MAL ID match found
                    aod_item = aod_by_mal_id[mal_id]
                    external_item.update(
                        {
                            "anidb": aod_item["anidb"],
                            "anilist": aod_item["anilist"],
                            "myanimelist": aod_item["myanimelist"],
                        }
                    )
                    self._update_aod_item(aod_item, external_item)
                    matched.append(external_item)
                else:
                    # No MAL ID or not in AOD, try other methods
                    remaining.append(external_item)

                bar()

        self.matched_items.extend(matched)
        self.unmatched_items = remaining
        return self

    def link_by_title(self, title_field: str = "title") -> "DataMatcher":
        """
        Link external data to AOD by exact title match.
        Updates matched_items and unmatched_items.

        :param title_field: Field name in external data containing title
        :return: self for chaining
        """
        external_dict = {}
        aod_dict = {}

        with alive_bar(
            len(self.aod_data),
            title=f"Translating AOD list to a dict with {self.platform_name} title",
            spinner=None,
        ) as bar:  # type: ignore
            for item in self.aod_data:
                if item.get("title") not in aod_dict:
                    aod_dict[item["title"]] = item
                bar()

        with alive_bar(
            len(self.external_data),
            title=f"Translating {self.platform_name} list to a dict with title",
            spinner=None,
        ) as bar:  # type: ignore
            for item in self.external_data:
                external_dict[item.get(title_field, "")] = item
                bar()

        with alive_bar(
            len(external_dict),
            title=f"Linking {self.platform_name} to MyAnimeList ID",
            spinner=None,
        ) as bar:  # type: ignore
            for title, external_item in external_dict.items():
                if title in aod_dict:
                    aod_item = aod_dict[title]
                    self._update_aod_item(aod_item, external_item)
                    external_item.update(
                        {
                            "anidb": aod_item["anidb"],
                            "anilist": aod_item["anilist"],
                            "myanimelist": aod_item["myanimelist"],
                        }
                    )
                    self.matched_items.append(external_item)
                else:
                    self.unmatched_items.append(external_item)
                bar()

        return self

    def link_by_slug(self) -> "DataMatcher":
        """
        Link remaining unmatched items by slug matching (fast pre-filtering).
        Updates matched_items and unmatched_items.

        :return: self for chaining
        """
        if not self.unmatched_items:
            return self

        aod_slug_lookup, _ = build_slug_index(self.aod_data, "title")
        slug_matched, remaining = prefilter_by_slug(
            self.unmatched_items, aod_slug_lookup, self.slug_or_title_field
        )

        with alive_bar(
            len(slug_matched),
            title=f"Linking slug-matched {self.platform_name} entries",
            spinner=None,
        ) as bar:  # type: ignore
            for external_item, aod_item in slug_matched:
                external_item.update(
                    {
                        "anidb": aod_item["anidb"],
                        "anilist": aod_item["anilist"],
                        "myanimelist": aod_item["myanimelist"],
                    }
                )
                self.matched_items.append(external_item)
                self._update_aod_item(aod_item, external_item)
                bar()

        self.unmatched_items = remaining
        return self

    def link_by_fuzzy(self, threshold: int = 85) -> "DataMatcher":
        """
        Link remaining unmatched items by fuzzy title matching.
        Uses parallel workers for speed.

        :param threshold: Minimum fuzzy matching score
        :return: self for chaining
        """
        if not self.unmatched_items:
            return self

        aod_normalized_cache = {
            idx: normalize_title(item["title"])
            for idx, item in enumerate(self.aod_data)
        }

        fuzzy_matches = fuzzy_match_batch_parallel(
            self.unmatched_items,
            self.aod_data,
            aod_normalized_cache,
            threshold=threshold,
            title="Fuzzy match title from both databases",
        )

        with alive_bar(
            len(fuzzy_matches),
            title=f"Linking fuzzy-matched {self.platform_name} entries",
            spinner=None,
        ) as bar:  # type: ignore
            for external_item, aod_item, id_count in fuzzy_matches:
                external_item.update(
                    {
                        "anidb": aod_item["anidb"],
                        "anilist": aod_item["anilist"],
                        "myanimelist": aod_item["myanimelist"],
                    }
                )
                self.matched_items.append(external_item)
                self._update_aod_item(aod_item, external_item)
                bar()

        # Update unmatched (those that failed fuzzy matching)
        fuzzy_matched_titles = {item[0].get("title") for item in fuzzy_matches}
        self.unmatched_items = [
            item
            for item in self.unmatched_items
            if item.get("title") not in fuzzy_matched_titles
        ]

        return self

    def apply_manual_mappings(self, manual_file: str) -> "DataMatcher":
        """
        Apply manual mappings from JSON file to override automated linking.

        :param manual_file: Path to JSON file with manual mappings
        :return: self for chaining
        """
        try:
            with open(manual_file, "r", encoding="utf-8") as f:
                manual_link = json.load(f)
        except FileNotFoundError:
            return self

        if not manual_link:
            return self

        with alive_bar(
            len(manual_link), title="Insert manual mappings", spinner=None
        ) as bar:  # type: ignore
            for title, platform_id in manual_link.items():
                if isinstance(platform_id, list):
                    platform_id = platform_id[0]

                for aod_item in self.aod_data:
                    if aod_item["title"] == title:
                        # If platform_id is a dict (e.g., for kaize/kaize_id), directly update
                        # Note: Manual mappings use {platform: slug, platform_id: id} format,
                        # which directly corresponds to aod_item fields
                        if isinstance(platform_id, dict):
                            aod_item.update(platform_id)
                        else:
                            aod_item.update({self.platform_name: platform_id})
                        
                        self.matched_items.append(
                            {
                                "title": title,
                                self.platform_name: platform_id if not isinstance(platform_id, dict) else platform_id.get(self.platform_name),
                                "anidb": aod_item["anidb"],
                                "anilist": aod_item["anilist"],
                                "myanimelist": aod_item["myanimelist"],
                            }
                        )
                        # Remove from unmatched if present
                        self.unmatched_items = [
                            item
                            for item in self.unmatched_items
                            if item.get("title") != title
                        ]
                        break
                bar()

        return self

    def finalize(self) -> list[dict[str, Any]]:
        """
        Finalize linking and return updated AOD data.
        Adds platform fields to records, removes duplicates.

        :return: Updated AOD data with platform IDs added
        """
        # Add platform fields to all AOD items if not present
        for item in self.aod_data:
            if self.platform_name not in item:
                item[self.platform_name] = None
            if self.has_slug and f"{self.platform_name}_id" not in item:
                item[f"{self.platform_name}_id"] = None

        # Log results
        pprint.print(
            self.platform,
            Status.PASS,
            f"{self.platform_name.capitalize()} linked to MyAnimeList ID.",
            f"Total linked data: {len(self.matched_items)},",
            f"total unlinked data: {len(self.unmatched_items)}",
        )

        # Save unlinked items
        try:
            with open(
                f"database/raw/{self.platform_name}_unlinked.json",
                "w",
                encoding="utf-8",
            ) as f:
                json.dump(self.unmatched_items, f)
        except Exception as e:
            pprint.print(
                self.platform,
                Status.WARN,
                f"Failed to save unlinked items: {e}",
            )

        return self.aod_data

    def reintroduce_old_items(
        self, old_aod_data: list[dict[str, Any]]
    ) -> "DataMatcher":
        """
        GENERIC: Merge with old AOD data to preserve historical mappings.
        Adds items from old AOD if they have MAL ID not in current AOD.
        This prevents data loss when anime entries are removed/renamed.
        Applies to all platforms: Kaize, Nautiljon, SilverYasha, OtakOtaku.

        :param old_aod_data: AOD data from previous generation
        :return: self for chaining
        """
        # Build set of existing MAL IDs in current AOD
        existing_mal_ids = {
            item.get("myanimelist") for item in self.aod_data if item.get("myanimelist")
        }

        # Track how many we're adding
        added_count = 0

        with alive_bar(
            len(old_aod_data),
            title="Reintroduce old list items",
            spinner=None,
        ) as bar:  # type: ignore
            for item in old_aod_data:
                mal_id = item.get("myanimelist")
                # Only add if has MAL ID and it's not already in current AOD
                if mal_id and mal_id not in existing_mal_ids:
                    self.aod_data.append(item)
                    existing_mal_ids.add(mal_id)
                    added_count += 1
                bar()

        if added_count > 0:
            pprint.print(
                self.platform,
                Status.INFO,
                f"Reintroduced {added_count} old items to preserve mappings",
            )

        return self

    def apply_title_transformation(
        self, transform_func, title_field: str = "title"
    ) -> "DataMatcher":
        """
        OTAKOTAKU-SPECIFIC: Apply custom title transformation before fuzzy matching.
        Example: Normalize season names (Season 2 → 2nd Season)

        :param transform_func: Function that takes title and returns normalized title
        :param title_field: Field name to transform
        :return: self for chaining
        """
        for item in self.unmatched_items:
            if title_field in item:
                item[title_field] = transform_func(item[title_field])

        return self

    def get_stats(self) -> dict[str, int]:
        """Get matching statistics."""
        return {
            "platform": self.platform_name,
            "matched": len(self.matched_items),
            "unmatched": len(self.unmatched_items),
            "total": len(self.matched_items) + len(self.unmatched_items),
        }
