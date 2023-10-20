# SPDX-License-Identifier: AGPL-3.0-only AND MIT

import csv
import json
import re
from datetime import datetime, timezone
from typing import Any

import requests
from alive_progress import alive_bar  # type: ignore
from const import pprint
from prettyprint import Platform, Status


def populate_contributors(attr: dict[str, Any]) -> dict[str, Any]:
    """
    Read total contributors from GitHub API

    :param attr: attribution dict
    :type attr: dict[str, Any]
    :return: attribution dict that has been updated
    :rtype: dict[str, Any]
    """
    response = requests.get(
        "https://api.github.com/repos/nattadasu/animeApi/contributors?per_page=100",
        headers={
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "nattadasu/animeApi",
        },
    )
    if response.status_code == 200:
        # clear the list first
        attr["contributors"] = []
        attr["contributors"] = [
            contributor["login"] for contributor in response.json()
        ]
    return attr


def save_to_file(data: list[dict[str, Any]], platform: str, attr: dict[str, Any]) -> None:
    """
    Save data to file

    :param data: data to save
    :type data: list[dict[str, Any]]
    :param platform: platform name
    :type platform: str
    :param attr: attribution dict
    :type attr: dict[str, Any]
    :return: None
    :rtype: None
    """
    items: list[dict[str, Any]] = []
    with alive_bar(len(data),
                   title="Removing None values",
                   spinner=None) as bar:  # type: ignore
        for item in data:
            # if platform key in item not None, then add it to items
            pkey = item.get(f"{platform}", None)
            if pkey is not None:
                items.append(item)
            bar()
    with open(f"database/{platform}.json", "w", encoding="utf-8") as file:
        json.dump(items, file)
    # save object-formatted data to file
    obj_data: dict[str, dict[str, Any]] = {}
    with alive_bar(len(items),
                   title="Converting data to object format",
                   spinner=None) as bar:  # type: ignore
        for item in items:
            if platform not in ["trakt", "themoviedb"]:
                obj_data[item[f"{platform}"]] = item
            elif platform == "trakt":
                if item["trakt_type"] in ["movie", "movies"]:
                    obj_data[f"{item['trakt_type']}/{item['trakt']}"] = item
                else:
                    if item["trakt_season"] == 1:
                        obj_data[f"{item['trakt_type']}/{item['trakt']}"] = item
                    obj_data[f"{item['trakt_type']}/{item['trakt']}/seasons/{item['trakt_season']}"] = item
            elif platform == "themoviedb":
                obj_data[f"movie/{item['themoviedb']}"] = item
            bar()
    with open(f"database/{platform}_object.json", "w", encoding="utf-8") as file:
        json.dump(obj_data, file)
    # update attr
    attr["counts"][f"{platform}"] = len(items)  # type: ignore
    return None


def save_platform_loop(data: list[dict[str, Any]], attr: dict[str, Any]) -> dict[str, Any]:
    """
    Loop through platforms and save data to file

    :param data: data to save
    :type data: list[dict[str, Any]]
    :param attr: attribution dict
    :type attr: dict[str, Any]
    :return: attribution dict that has been updated
    :rtype: dict[str, Any]
    """
    platforms = [
        "anidb",
        "anilist",
        "animeplanet",
        "anisearch",
        "annict",
        "imdb",
        "kaize",
        "kitsu",
        "livechart",
        "myanimelist",
        "nautiljon",
        "notify",
        "otakotaku",
        "shikimori",
        "shoboi",
        "silveryasha",
        "trakt",
        "themoviedb",
    ]
    # sort key in data
    pprint.print(
        Platform.SYSTEM,
        Status.INFO,
        "Sorting data by title",
    )
    data = sorted(data, key=lambda k: k["title"])
    for plat in platforms:
        match plat:
            case "anidb":
                name = Platform.ANIDB
            case "anilist":
                name = Platform.ANILIST
            case "animeplanet":
                name = Platform.ANIMEPLANET
            case "anisearch":
                name = Platform.ANISEARCH
            case "annict":
                name = Platform.ANNICT
            case "imdb":
                name = Platform.IMDB
            case "kaize":
                name = Platform.KAIZE
            case "kitsu":
                name = Platform.KITSU
            case "livechart":
                name = Platform.LIVECHART
            case "myanimelist":
                name = Platform.MYANIMELIST
            case "nautiljon":
                name = Platform.NAUTILJON
            case "notify":
                name = Platform.NOTIFY
            case "otakotaku":
                name = Platform.OTAKOTAKU
            case "shikimori":
                name = Platform.SHIKIMORI
            case "shoboi":
                name = Platform.SHOBOI
            case "silveryasha":
                name = Platform.SILVERYASHA
            case "trakt":
                name = Platform.ANITRAKT
            case "themoviedb":
                name = Platform.TMDB
            case _:
                name = Platform.SYSTEM
        pprint.print(
            name,
            Status.INFO,
            f"Saving data to {plat}.json",
        )
        save_to_file(data, plat, attr)
    return attr


def save_list_to_tsv(data: list[dict[str, Any]], file_path: str) -> None:
    """
    Save list to TSV

    :param data: data to save
    :type data: list[dict[str, Any]]
    :param file_path: file path
    :type file_path: str
    :return: None
    :rtype: None
    """
    with open(f"{file_path}.tsv", "w", encoding="utf-8", newline="") as file_:
        writer = csv.writer(file_, delimiter="\t", lineterminator="\n")
        writer.writerow(data[0].keys())
        with alive_bar(len(data),
                       title="Saving data to TSV",
                       spinner=None) as bar:  # type: ignore
            for item in data:
                writer.writerow(item.values())
                bar()
    return None


def update_attribution(data: list[dict[str, Any]], attr: dict[str, Any]) -> dict[str, Any]:
    """
    Update attr

    :param data: data to save
    :type data: list[dict[str, Any]]
    :param attr: attribution dict
    :type attr: dict[str, Any]
    :return: attribution dict that has been updated
    :rtype: dict[str, Any]
    """
    pprint.print(
        Platform.SYSTEM,
        Status.INFO,
        "Save data to JSON",
    )
    with open("database/animeapi.json", "w", encoding="utf-8") as file_:
        json.dump(data, file_)
    pprint.print(
        Platform.SYSTEM,
        Status.INFO,
        "Save data to TSV",
    )
    save_list_to_tsv(data, "database/animeapi")

    pprint.print(
        Platform.SYSTEM,
        Status.INFO,
        "Updating attr",
    )
    now = datetime.now(tz=timezone.utc)
    attr["updated"]["iso"] = now.isoformat()  # type: ignore
    attr["updated"]["timestamp"] = int(now.timestamp())  # type: ignore
    attr = populate_contributors(attr)

    total_data = len(data)
    attr = save_platform_loop(data, attr)

    attr["counts"]["total"] = total_data  # type: ignore
    with open("api/status.json", "w", encoding="utf-8") as file:
        json.dump(attr, file)
    pprint.print(
        Platform.SYSTEM,
        Status.PASS,
        "Attribution updated",
    )
    return attr


def add_spaces(data: int, spaces_max: int = 9) -> str:
    """
    Add spaces to data

    :param data: data to add spaces
    :type data: int
    :param spaces_max: maximum spaces, defaults to 9
    :type spaces_max: int, optional
    :return: data with spaces
    :rtype: str
    """
    spaces = spaces_max - len(f"{data}")
    return f"{' ' * spaces}{data}"


def update_markdown(
    attr: dict[str, dict[str, int | str] | str | int | list[str]]
) -> dict[str, Any]:
    """
    Update counters in README.md by looking <!-- counters --><!-- /counters -->

    :param attr: attribution
    :type attr: dict[str, dict[str, int | str] | str | int | list[str]]
    :param now: current datetime
    :type now: datetime
    :return: attribution
    :rtype: dict[str, Any]
    """
    pprint.print(
        Platform.SYSTEM,
        Status.INFO,
        "Updating counters in README.md",
    )
    with open("README.md", "r", encoding="utf-8") as file:
        readme = file.read()
    counts: dict[str, int] = attr["counts"]  # type: ignore
    adb = add_spaces(counts["anidb"])
    anl = add_spaces(counts["anilist"])
    apl = add_spaces(counts["animeplanet"])
    ase = add_spaces(counts["anisearch"])
    anc = add_spaces(counts["annict"])
    idb = add_spaces(counts["imdb"])
    kze = add_spaces(counts["kaize"])
    kts = add_spaces(counts["kitsu"])
    lvc = add_spaces(counts["livechart"])
    mal = add_spaces(counts["myanimelist"])
    nau = add_spaces(counts["nautiljon"])
    ntf = add_spaces(counts["notify"])
    ook = add_spaces(counts["otakotaku"])
    shk = add_spaces(counts["shikimori"])
    shb = add_spaces(counts["shoboi"])
    sys = add_spaces(counts["silveryasha"])
    tmd = add_spaces(counts["themoviedb"])
    trk = add_spaces(counts["trakt"])
    ttl = counts["total"]
    table = f"""| Platform           |            ID |     Count |
| :----------------- | ------------: | --------: |
| aniDB              |       `anidb` | {adb} |
| AniList            |     `anilist` | {anl} |
| Anime-Planet       | `animeplanet` | {apl} |
| aniSearch          |   `anisearch` | {ase} |
| Annict             |      `annict` | {anc} |
| IMDb               |        `imdb` | {idb} |
| Kaize              |       `kaize` | {kze} |
| Kitsu              |       `kitsu` | {kts} |
| LiveChart          |   `livechart` | {lvc} |
| MyAnimeList        | `myanimelist` | {mal} |
| Nautiljon          |   `nautiljon` | {nau} |
| Notify.moe         |      `notify` | {ntf} |
| Otak Otaku         |   `otakotaku` | {ook} |
| Shikimori          |   `shikimori` | {shk} |
| Shoboi/Syobocal    |      `shoboi` | {shb} |
| Silver Yasha       | `silveryasha` | {sys} |
| The Movie Database |  `themoviedb` | {tmd} |
| Trakt              |       `trakt` | {trk} |
|                    |               |           |
|                    |     **Total** | **{ttl}** |
"""
    readme = re.sub(
        r"<!-- counters -->(.|\n)*<!-- \/counters -->",
        f"<!-- counters -->\n{table}<!-- /counters -->",
        readme,
    )

    pprint.print(
        Platform.SYSTEM,
        Status.INFO,
        "Updating status example in README.md",
    )
    status = json.dumps(attr, indent=2,
                        ensure_ascii=False).replace('\\', '\\\\')
    readme = re.sub(
        r"<!-- status -->(.|\n)*<!-- \/status -->",
        f"<!-- status -->\n```json\n{status}\n```\n<!-- /status -->",
        readme,
    )

    pprint.print(
        Platform.SYSTEM,
        Status.INFO,
        "Updating updated timestamp in README.md",
    )
    # update updated timestamp
    now: int = attr["updated"]["timestamp"]  # type: ignore
    readme = re.sub(
        r"<!-- updated -->(.|\n)*<!-- \/updated -->",
        f"<!-- updated -->\nLast updated: {datetime.fromtimestamp(now).strftime('%d %B %Y %H:%M:%S UTC')}\n<!-- /updated -->",  # type: ignore
        readme,
    )
    formatted_time = datetime.utcfromtimestamp(
        now).strftime("%m/%d/%Y %H:%M:%S UTC")  # type: ignore
    readme = re.sub(
        r"<!-- updated-txt -->(.|\n)*<!-- \/updated-txt -->",
        f"<!-- updated-txt -->\n```txt\nUpdated on {formatted_time}\n```\n<!-- /updated-txt -->",
        readme,
    )

    pprint.print(
        Platform.SYSTEM,
        Status.INFO,
        "Updating JSON Schema in README.md",
    )
    with open("api/schema.json", "r", encoding="utf-8") as file:
        jschema = json.dumps(
            json.load(file),
            indent=2,
            ensure_ascii=False)
        jschema = jschema.replace("\\", "\\\\")
    readme = re.sub(
        r"<!-- jsonschema -->(.|\n)*<!-- \/jsonschema -->",
        f"<!-- jsonschema -->\n```json\n{jschema}\n```\n<!-- /jsonschema -->",
        readme
    )

    pprint.print(
        Platform.SYSTEM,
        Status.INFO,
        "Updating sample data in README.md, using MyAnimeList ID 1",
    )
    with open("database/myanimelist_object.json", "r", encoding="utf-8") as file:
        sample = json.load(file)
        sample = sample["1"]
        readme = re.sub(
            r"<!-- sample -->(.|\n)*<!-- \/sample -->",
            f"<!-- sample -->\n```json\n{json.dumps(sample, indent=2)}\n```\n<!-- /sample -->",
            readme,
        )

    pprint.print(
        Platform.SYSTEM,
        Status.INFO,
        "Updating sample data in README.md, using Trakt ID 152334, season 3",
    )
    with open("database/trakt_object.json", "r", encoding="utf-8") as file:
        sampler = json.load(file)
        readme = re.sub(
            r"<!-- trakt152334 -->(.|\n)*<!-- \/trakt152334 -->",
            f"<!-- trakt152334 -->\n```json\n{json.dumps(sampler['shows/152334/seasons/3'], indent=2)}\n```\n<!-- /trakt152334 -->",
            readme,
        )
    with open("README.md", "w", encoding="utf-8") as file:
        file.write(readme)
    pprint.print(
        Platform.SYSTEM,
        Status.PASS,
        "Counters updated in README.md",
    )
    return attr
