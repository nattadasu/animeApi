# SPDX-License-Identifier: AGPL-3.0-only AND MIT

import json
from typing import Any, Union

from alive_progress import alive_bar  # type: ignore
from const import pprint
from fuzzywuzzy import fuzz  # type: ignore
from prettyprint import Platform, Status
from slugify import slugify


def link_kaize_to_mal(
    kaize: list[dict[str, Any]],
    aod: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Link Kaize slug to MyAnimeList ID based similarity in title name over 85% in fuzzy search"""
    # add dummy data to aod
    for item in aod:
        item.update({
            "kaize": None,
            "kaize_id": None,
        })
    unlinked: list[dict[str, Any]] = []
    kz_fixed: list[dict[str, Any]] = []
    kz_dict: dict[str, Any] = {}
    aod_dict: dict[str, Any] = {}
    with alive_bar(len(aod),
                   title="Translating AOD list to a dict with custom slug",
                   spinner=None) as bar:  # type: ignore
        for item in aod:
            aod_slug = slugify(item["title"]).replace("-", "")
            aod_dict[aod_slug] = item
            bar()
    with alive_bar(len(kaize),
                   title="Translating Kaize list to a dict with custom slug",
                   spinner=None) as bar:  # type: ignore
        for item in kaize:
            kz_slug = slugify(item["slug"]).replace("-", "")
            kz_dict[kz_slug] = item
            bar()
    with alive_bar(len(kz_dict),
                   title="Linking Kaize slug to MyAnimeList ID",
                   spinner=None) as bar:  # type: ignore
        for kz_slug, kz_item in kz_dict.items():
            if kz_slug in aod_dict:
                aod_item: Union[dict[str, Any],
                                None] = aod_dict.get(kz_slug, None)
                if aod_item:
                    # add more data from kaize
                    kz_item.update({
                        "anidb": aod_item["anidb"],
                        "anilist": aod_item["anilist"],
                        "kitsu": aod_item["kitsu"],
                        "myanimelist": aod_item["myanimelist"],
                    })
                    kz_fixed.append(kz_item)
                    aod_item.update({
                        "kaize": kz_item["slug"],
                        "kaize_id": None if kz_item["kaize"] == 0 else kz_item["kaize"],
                    })
                else:
                    unlinked.append(kz_item)
            else:
                unlinked.append(kz_item)
            bar()
    # on unlinked, fuzzy search the title name
    with alive_bar(len(unlinked),
                   title="Fuzzy match title from both databases",
                   spinner=None) as bar:  # type: ignore
        for item in unlinked:
            title = item["title"]
            for aod_item in aod:
                aod_title = aod_item["title"]
                ratio = fuzz.ratio(title, aod_title)  # type: ignore
                if ratio >= 85:
                    kz_dat = {
                        "anidb": aod_item["anidb"],
                        "anilist": aod_item["anilist"],
                        "animeplanet": aod_item["animeplanet"],
                        "anisearch": aod_item["anisearch"],
                        "kitsu": aod_item["kitsu"],
                        "myanimelist": aod_item["myanimelist"],
                        "notify": aod_item["notify"],
                        "shikimori": aod_item["shikimori"],
                    }
                    item.update(kz_dat)
                    kz_fixed.append(item)
                    aod_item.update({
                        "kaize": item["slug"],
                        "kaize_id": None if item["kaize"] == 0 else item["kaize"],
                    })
                    break
            bar()
    # load manual link data
    with open("database/raw/kaize_manual.json", "r", encoding="utf-8") as file:
        manual_link: dict[str, dict[str, str | int | None]] = json.load(file)
    with alive_bar(len(manual_link),
                   title="Insert manual mappings",
                   spinner=None) as bar:  # type: ignore
        for title, kz_item in manual_link.items():
            # if kz_item["kaize"] doesn't exist in unlinked under slug key, skip
            if kz_item["kaize"] not in [item["slug"] for item in unlinked]:
                continue
            for aod_item in aod:
                aod_title = aod_item["title"]
                if title == aod_title:
                    kz_dat = {
                        "kaize": kz_item["kaize"],
                        "kaize_id": None if kz_item["kaize"] == 0 else kz_item["kaize"],
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
    with alive_bar(len(kz_fixed),
                   title="Removing unrequired data from unlinked",
                   spinner=None) as bar:  # type: ignore
        for item in kz_fixed:
            if item in unlinked:
                unlinked.remove(item)
            bar()
    aod_list: list[dict[str, Any]] = []
    with alive_bar(len(aod_dict),
                   title="Translating AOD dict to a list",
                   spinner=None) as bar:  # type: ignore
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
    with alive_bar(len(aod_list),
                   title="Reintroduce old list items",
                   spinner=None) as bar:  # type: ignore
        for item in aod_list:
            if item not in aod:
                merged.append(item)
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
    nautiljon: list[dict[str, Any]],
    aod: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Link Nautiljon ID to MyAnimeList ID based similarity in title name over 85% in fuzzy search"""
    for item in aod:
        item.update({
            "nautiljon": None,
            "nautiljon_id": None,
        })
    unlinked: list[dict[str, Any]] = []
    nautiljon_fixed: list[dict[str, Any]] = []
    nautiljon_dict: dict[str, Any] = {}
    aod_dict: dict[str, Any] = {}
    with alive_bar(len(aod),
                   title="Translating AOD list to a dict using title as key",
                   spinner=None) as bar:  # type: ignore
        for item in aod:
            # if previous key exists, skip
            if item["title"] in aod_dict:
                bar()
                continue
            aod_dict[item["title"]] = item
            bar()
    with alive_bar(len(nautiljon),
                   title="Translating Nautiljon list to a dict with title as key",
                   spinner=None) as bar:  # type: ignore
        for item in nautiljon:
            nautiljon_dict[item["title"]] = item
            bar()
    # link nautiljon to aod
    with alive_bar(len(nautiljon_dict),
                   title="Linking Nautiljon ID to AOD",
                   spinner=None) as bar:  # type: ignore
        for title, nautiljon_item in nautiljon_dict.items():
            if title in aod_dict:
                aod_item = aod_dict.get(title)
                if aod_item:
                    aod_item.update({
                        "nautiljon": nautiljon_item["slug"],
                        "nautiljon_id": nautiljon_item["entry_id"],
                    })
                    nautiljon_item.update({
                        "anidb": aod_item["anidb"],
                        "anilist": aod_item["anilist"],
                        "kitsu": aod_item["kitsu"],
                        "myanimelist": aod_item["myanimelist"],
                    })
                    nautiljon_fixed.append(nautiljon_item)
                else:
                    unlinked.append(nautiljon_item)
            else:
                unlinked.append(nautiljon_item)
            bar()
    # fuzzy search the rest of unlinked data
    with alive_bar(len(unlinked),
                   title="Fuzzy match title from both databases",
                   spinner=None) as bar:  # type: ignore
        for item in unlinked:
            title = item["title"]
            for aod_item in aod:
                aod_title = aod_item["title"]
                ratio = fuzz.ratio(title, aod_title)  # type: ignore
                if ratio >= 85:
                    item.update({
                        "anidb": aod_item["anidb"],
                        "anilist": aod_item["anilist"],
                        "kitsu": aod_item["kitsu"],
                        "myanimelist": aod_item["myanimelist"],
                    })
                    nautiljon_fixed.append(item)
                    aod_item.update({
                        "nautiljon": item["slug"],
                        "nautiljon_id": item["entry_id"],
                    })
                    break
            bar()
    # remove fixed data from unlinked
    with alive_bar(len(nautiljon_fixed),
                   title="Removing fixed data from unlinked",
                   spinner=None) as bar:  # type: ignore
        for item in nautiljon_fixed:
            if item in unlinked:
                unlinked.remove(item)
            bar()
    aod_list: list[dict[str, Any]] = []
    with alive_bar(len(aod_dict),
                   title="Translating AOD dict to a list",
                   spinner=None) as bar:  # type: ignore
        for _, value in aod_dict.items():
            aod_list.append(value)
            bar()
    merged: list[dict[str, Any]] = []
    merged.extend(aod_list)
    with alive_bar(len(aod_list),
                   title="Reintroduce old list items",
                   spinner=None) as bar:  # type: ignore
        for item in aod_list:
            if item not in aod:
                merged.append(item)
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
    otakotaku: list[dict[str, Any]],
    aod: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Link Otak Otaku ID to MyAnimeList ID based similarity in title name over 85% in fuzzy search"""
    unlinked: list[dict[str, Any]] = []
    ot_fixed: list[dict[str, Any]] = []
    ot_dict: dict[str, Any] = {}
    aod_dict: dict[str, Any] = {}
    with alive_bar(len(aod),
                   title="Translating AOD list to a dict with MAL ID",
                   spinner=None) as bar:  # type: ignore
        for item in aod:
            if item["myanimelist"]:
                aod_dict[f"{item['myanimelist']}"] = item
            else:
                aod_dict[item["title"]] = item
            bar()
    with alive_bar(len(otakotaku),
                   title="Translating Otakotaku list to a dict with MAL ID",
                   spinner=None) as bar:  # type: ignore
        for item in otakotaku:
            mal_id = item["myanimelist"]
            if mal_id:
                ot_dict[f"{mal_id}"] = {
                    "title": item["title"],
                    "otakotaku": item["otakotaku"],
                    "animeplanet": item["animeplanet"],
                    "anidb": item["anidb"],
                    "animenewsnetwork": item["animenewsnetwork"],
                }
            else:
                ot_dict[item["title"]] = {
                    "title": item["title"],
                    "otakotaku": item["otakotaku"],
                    "animeplanet": item["animeplanet"],
                    "anidb": item["anidb"],
                    "animenewsnetwork": item["animenewsnetwork"],
                }
            bar()
    with alive_bar(len(ot_dict),
                   title="Linking Otak Otaku ID to MyAnimeList ID",
                   spinner=None) as bar:  # type: ignore
        for mal_id, ot_item in ot_dict.items():
            if mal_id in aod_dict:
                aod_item: Union[dict[str, Any], None] = aod_dict.get(
                    f"{mal_id}", None)
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
    with alive_bar(len(unlinked),
                   title="Fuzzy match title from both databases",
                   spinner=None) as bar:  # type: ignore
        for item in unlinked:
            title = item["title"]
            for aod_item in aod:
                aod_title = aod_item["title"]
                ratio = fuzz.ratio(title, aod_title)  # type: ignore
                if ratio >= 85:
                    ot_dat = {
                        "otakotaku": item["otakotaku"],
                    }
                    aod_item.update(ot_dat)
                    ot_fixed.append(aod_item)
                    break
            bar()
    # load manual link data
    with open("database/raw/otakotaku_manual.json", "r", encoding="utf-8") as file:
        manual_link: dict[str, int] = json.load(file)
    with alive_bar(len(manual_link),
                   title="Insert manual mappings",
                   spinner=None) as bar:  # type: ignore
        for title, oo_id in manual_link.items():
            # skip if not in unlinked
            if oo_id not in [item["otakotaku"] for item in unlinked]:
                continue
            for aod_item in aod:
                aod_title = aod_item["title"]
                if title == aod_title:
                    oo_dat = {
                        "otakotaku": oo_id,
                    }
                    aod_item.update(oo_dat)
                    ot_fixed.append(aod_item)
                    # in unlinked, remove the item with the same id
                    for item in unlinked:
                        if item["otakotaku"] == oo_id:
                            unlinked.remove(item)
                    break
            bar()
    # remove if unlinked data is already linked
    with alive_bar(len(ot_fixed),
                   title="Removing unrequired data from unlinked",
                   spinner=None) as bar:  # type: ignore
        for item in ot_fixed:
            if item in unlinked:
                unlinked.remove(item)
            bar()
    aod_list: list[dict[str, Any]] = []
    with alive_bar(len(aod_dict),
                   title="Translating AOD dict to a list",
                   spinner=None) as bar:  # type: ignore
        for _, value in aod_dict.items():
            if "otakotaku" not in value:
                value["otakotaku"] = None
            aod_list.append(value)
            bar()
    merged: list[dict[str, Any]] = []
    merged.extend(aod)

    # add missing items from old AOD data
    with alive_bar(len(aod_list),
                   title="Reintroduce old list items",
                   spinner=None) as bar:  # type: ignore
        for item in aod_list:
            if item not in aod:
                merged.append(item)
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
    silveryasha: list[dict[str, Any]],
    aod: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Link SilverYasha ID to MyAnimeList ID based similarity in title name over 85% in fuzzy search"""
    unlinked: list[dict[str, Any]] = []
    sy_fixed: list[dict[str, Any]] = []
    sy_dict: dict[str, Any] = {}
    aod_dict: dict[str, Any] = {}
    with alive_bar(len(aod),
                   title="Translating AOD list to a dict with MAL ID",
                   spinner=None) as bar:  # type: ignore
        for item in aod:
            if item["myanimelist"]:
                aod_dict[f"{item['myanimelist']}"] = item
            else:
                aod_dict[item["title"]] = item
            bar()
    with alive_bar(len(silveryasha),
                   title="Translating SilverYasha list to a dict with MAL ID",
                   spinner=None) as bar:  # type: ignore
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
    with alive_bar(len(sy_dict),
                   title="Linking SilverYasha ID to MyAnimeList ID",
                   spinner=None) as bar:  # type: ignore
        for mal_id, sy_item in sy_dict.items():
            if mal_id in aod_dict:
                aod_item: Union[dict[str, Any], None] = aod_dict.get(
                    f"{mal_id}", None)
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
    with alive_bar(len(unlinked),
                   title="Fuzzy match title from both databases",
                   spinner=None) as bar:  # type: ignore
        for item in unlinked:
            title = item["title"]
            for aod_item in aod:
                aod_title = aod_item["title"]
                ratio = fuzz.ratio(title, aod_title)  # type: ignore
                if ratio >= 85:
                    sy_dat = {
                        "silveryasha": item["silveryasha"],
                    }
                    aod_item.update(sy_dat)
                    sy_fixed.append(aod_item)
                    break
            bar()
    # load manual link data
    with open("database/raw/silveryasha_manual.json", "r", encoding="utf-8") as file:
        manual_link: dict[str, int] = json.load(file)
    with alive_bar(len(manual_link),
                   title="Insert manual mappings",
                   spinner=None) as bar:  # type: ignore
        for title, sy_id in manual_link.items():
            if sy_id not in [item["silveryasha"] for item in unlinked]:
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
    with alive_bar(len(sy_fixed),
                   title="Removing unrequired data from unlinked",
                   spinner=None) as bar:  # type: ignore
        for item in sy_fixed:
            if item in unlinked:
                unlinked.remove(item)
            bar()
    aod_list: list[dict[str, Any]] = []
    with alive_bar(len(aod_dict),
                   title="Translating AOD dict to a list",
                   spinner=None) as bar:  # type: ignore
        for _, value in aod_dict.items():
            if "silveryasha" not in value:
                value["silveryasha"] = None
            aod_list.append(value)
            bar()
    merged: list[dict[str, Any]] = []
    merged.extend(aod)

    # add missing items from old AOD data
    with alive_bar(len(aod_list),
                   title="Reintroduce old list items",
                   spinner=None) as bar:  # type: ignore
        for item in aod_list:
            if item not in aod:
                merged.append(item)
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
