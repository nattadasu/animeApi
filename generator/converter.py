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


def combine_arm(
    arm: list[dict[str, Any]],
    aod: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Combine ARM data with AOD data"""
    linked = 0
    with alive_bar(len(aod),
                   title="Combining ARM data with AOD data",
                   spinner=None) as bar:  # type: ignore
        for item in aod:
            myanimelist = item['myanimelist']
            anilist = item['anilist']
            # Skip if both myanimelist and anilist are null
            if myanimelist is None and anilist is None:
                item.update({
                    'shoboi': None,
                    'annict': None,
                })
                bar()
                continue

            # Check if mal_id and anilist_id exist in arm_data
            for arm_item in arm:
                mal_id = arm_item.get('mal_id', None)
                anilist_id = arm_item.get('anilist_id', None)
                syoboi = arm_item.get('syobocal_tid', None)
                annict = arm_item.get('annict_id', None)
                if myanimelist is not None and mal_id == myanimelist:
                    # Combine the data from arm_item with the item in aod_data
                    item.update({
                        'shoboi': syoboi,
                        'annict': annict,
                        'anilist': anilist if anilist is not None else anilist_id,
                    })

                    linked += 1
                    break
                elif anilist is not None and anilist_id == anilist:
                    # Combine the data from arm_item with the item in aod_data
                    item.update({
                        'shoboi': syoboi,
                        'annict': annict,
                        'myanimelist': myanimelist if myanimelist is not None else mal_id,
                        'shikimori': myanimelist if myanimelist is not None else mal_id,
                    })
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
    anitrakt: list[dict[str, Any]],
    aod: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Combine AniTrakt data with AOD data"""
    linked = 0
    with alive_bar(len(aod),
                   title="Combining AniTrakt data with AOD data",
                   spinner=None) as bar:  # type: ignore
        for item in aod:
            matched = False
            myanimelist = item['myanimelist']
            # Skip if both myanimelist and anilist are null
            if myanimelist is None:
                item.update({
                    'trakt': None,
                    'trakt_type': None,
                    'trakt_season': None,
                })
                bar()
                continue

            # Check if mal_id and anilist_id exist in anitrakt_data
            for anitrakt_item in anitrakt:
                mal_id = anitrakt_item.get('mal_id', None)
                trakt = anitrakt_item.get('trakt_id', None)
                media_type = anitrakt_item.get('type', None)
                media_season = anitrakt_item.get('season', None)
                if myanimelist is not None and mal_id == myanimelist:
                    # Combine the data from anitrakt_item with the item in aod_data
                    item.update({
                        'trakt': trakt,
                        'trakt_type': media_type,
                        'trakt_season': media_season,
                    })
                    linked += 1
                    matched = True
                    break

            if not matched:
                item.update({
                    'trakt': None,
                    'trakt_type': None,
                    'trakt_season': None,
                })
            bar()
    pprint.print(
        Platform.ANITRAKT,
        Status.PASS,
        "AniTrakt data combined with AOD data.",
        "Total linked data:",
        f"{linked},",
        "AOD data:",
        f"{len(aod)}",
        "AniTrakt data:",
        f"{len(anitrakt)}",
    )
    return aod


def combine_fribb(
    fribb: list[dict[str, Any]],
    aod: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Combine Fribb's Animelists data with AOD data to obtain IMDb and TMDB IDs via AniDB"""
    linked = 0
    with alive_bar(len(aod),
                   title="Combining Fribb's Animelists data with AOD data",
                   spinner=None) as bar:  # type: ignore
        for item in aod:
            matched = False
            anidb = item['anidb']
            # Skip if anidb is null
            if anidb is None:
                item.update({
                    'imdb': None,
                    'themoviedb': None,
                })
                bar()
                continue

            # Check if anidb_id exist in fribb_data
            for fbi in fribb:
                anidb_id = fbi.get('anidb_id', None)
                imdb = fbi.get('imdb_id', None)
                tmdb: str | int | None = fbi.get('themoviedb_id', None)
                if anidb is not None and anidb_id == anidb:
                    # Combine the data from fribb_item with the item in aod_data
                    data_fbi = {}
                    data_fbi['imdb'] = imdb
                    if isinstance(tmdb, str):
                        tmdbl = tmdb.split(",")
                        tmdb = int(tmdbl[0])
                    data_fbi['themoviedb'] = tmdb
                    item.update(data_fbi)
                    linked += 1
                    matched = True
                    break

            if not matched:
                item.update({
                    'imdb': None,
                    'themoviedb': None,
                })
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
