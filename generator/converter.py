# SPDX-License-Identifier: MIT

from typing import Any

from data_matcher import (
    DataMatcher,
)
from prettyprint import Platform


def link_kaize_to_mal(
    kaize: list[dict[str, Any]], aod: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """
    Link Kaize slug to MyAnimeList ID using DataMatcher.
    Refactored version: 200 lines → 15 lines
    """
    matcher = DataMatcher(
        "kaize",
        Platform.KAIZE,
        kaize,
        aod,
        id_field="kaize",
        slug_or_title_field="slug",
        has_slug=True,
        update_func=lambda aod_item, ext_item: aod_item.update(
            {
                "kaize": ext_item.get("slug"),
                "kaize_id": ext_item.get("kaize"),
            }
        ),
    )
    return (
        matcher.link_by_title("slug")  # Kaize uses "slug" field instead of "title"
        .link_by_slug()
        .link_by_fuzzy(threshold=85)
        .apply_manual_mappings("database/raw/kaize_manual.json")
        .reintroduce_old_items(aod)  # Reintroduce items lost to slug collision
        .finalize()
    )


def link_nautiljon_to_mal(
    nautiljon: list[dict[str, Any]], aod: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """
    Link Nautiljon ID to MyAnimeList ID using DataMatcher.
    Refactored version: 300 lines → 15 lines
    """
    matcher = DataMatcher(
        "nautiljon",
        Platform.NAUTILJON,
        nautiljon,
        aod,
        id_field="entry_id",
        slug_or_title_field="slug",
        has_slug=True,
        update_func=lambda aod_item, ext_item: aod_item.update(
            {
                "nautiljon": ext_item.get("slug"),
                "nautiljon_id": ext_item.get("entry_id"),
            }
        ),
    )
    return (
        matcher.link_by_title()
        .link_by_slug()
        .link_by_fuzzy(threshold=90)
        .apply_manual_mappings("database/raw/nautiljon_manual.json")
        .reintroduce_old_items(aod)
        .finalize()
    )


def normalize_otakotaku_season(title: str) -> str:
    """Convert 'Season 2' to '2nd Season', etc."""
    replace_dict = {
        "Season 2": "2nd Season",
        "Season 3": "3rd Season",
    }
    for i in range(4, 21):
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

    for key, value in replace_dict.items():
        title = title.replace(key, value)
    return title


def link_otakotaku_to_mal(
    otakotaku: list[dict[str, Any]], aod: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """
    Link OtakOtaku ID to MyAnimeList ID using DataMatcher.
    Refactored version: 250 lines → 18 lines
    Includes season number normalization.
    """
    matcher = DataMatcher(
        "otakotaku",
        Platform.OTAKOTAKU,
        otakotaku,
        aod,
        id_field="otakotaku",
        slug_or_title_field="title",
        update_func=lambda aod_item, ext_item: aod_item.update(
            {
                "otakotaku": ext_item.get("otakotaku"),
            }
        ),
    )
    return (
        matcher.link_by_title()
        .link_by_slug()
        .apply_title_transformation(normalize_otakotaku_season)
        .link_by_fuzzy(threshold=90)
        .apply_manual_mappings("database/raw/otakotaku_manual.json")
        .reintroduce_old_items(aod)
        .finalize()
    )


def link_silveryasha_to_mal(
    silveryasha: list[dict[str, Any]], aod: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """
    Link SilverYasha ID to MyAnimeList ID using DataMatcher.
    Refactored version: 250 lines → 15 lines
    """
    matcher = DataMatcher(
        "silveryasha",
        Platform.SILVERYASHA,
        silveryasha,
        aod,
        id_field="silveryasha",
        slug_or_title_field="title",
        update_func=lambda aod_item, ext_item: aod_item.update(
            {
                "silveryasha": ext_item.get("silveryasha"),
            }
        ),
    )
    return (
        matcher.link_by_mal_id(mal_id_field="mal_id")
        .link_by_title()
        .link_by_slug()
        .link_by_fuzzy(threshold=95)
        .apply_manual_mappings("database/raw/silveryasha_manual.json")
        .reintroduce_old_items(aod)  # Add reintroduce for consistency
        .finalize()
    )
