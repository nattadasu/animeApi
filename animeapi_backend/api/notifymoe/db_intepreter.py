"""
SPDX-License-Identifier: MIT

A module to intepret Notify.moe Anime .dat database to be readable by the program
"""

from json import loads
from typing import Any

from alive_progress import alive_bar  # type: ignore
from animeapi_backend.config.variables import is_verbose, is_debug
from animeapi_backend.config.const import PPRINT
from animeapi_backend.prettyprint import Platform, PrettyPrint, Status


def split_database(data: str) -> list[dict[str, Any]]:
    """
    Split the data into a list of dictionary

    :param data: The data
    :type data: str
    :return: The list of dictionary
    :rtype: list[dict[str, Any]]
    """
    # the data was separated by newlines, index in odd, whereas the JSON was in even lines
    # example:
    # aabbccdd_
    # {"a": "b"}

    # remove CR and split the data into lines
    data = data.replace("\r", "")
    lsdata = data.split("\n")
    # remove the last element if it's empty
    if lsdata[-1] == "":
        lsdata.pop()
    # only get the even index
    lsdata = lsdata[::2]
    # convert the JSON to dictionary
    with alive_bar(
        len(lsdata),
        title=PrettyPrint(False, False).string(
              Platform.NOTIFY,
              Status.INFO,
              "Converting database to dictionary",
              end=None)) as bar:  # type: ignore
        for i in range(len(lsdata)):
            if is_verbose:
                PPRINT.print(Platform.NOTIFY,
                             Status.INFO,
                             f"Converting database to dictionary in {lsdata[i]}")

            lsdata[i] = loads(lsdata[i])
            bar()
    lsdata = [loads(i) for i in lsdata]
    return lsdata


def services_replacer(data: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Replace Notify.moe's relation model to the program's relation model

    :param data: The data
    :type data: list[dict[str, Any]]
    :return: The replaced data
    :rtype: list[dict[str, Any]]
    """
    PPRINT.print(Platform.NOTIFY,
                 Status.NOTICE,
                 "Replacing services maps model in Notify.moe to AnimeAPI model")

    with alive_bar(
        len(data),
        title=PrettyPrint(False, False).string(
              Platform.NOTIFY,
              Status.INFO,
              "Replacing services maps model",
              end=None)) as bar:  # type: ignore
        for index in data:
            if is_verbose:
                PPRINT.print(Platform.NOTIFY,
                             Status.INFO,
                             f"Replacing services maps model in {index['title']['romaji']}")
            mappings = index["mappings"]
            final_mappings = {}
            for map in mappings:
                serv: str = map["service"]
                pf = serv.split("/")[0]
                media_id: str | int = map["serviceId"]
                if media_id.isdigit():  # type: ignore
                    media_id = int(media_id)
                if pf != "thetvdb":
                    final_mappings[pf] = media_id
                else:
                    tvdb_id = str(media_id).split("/")
                    media_id = int(tvdb_id[0])
                    final_mappings["tvdb"] = media_id
                    final_mappings["tvdb_season"] = int(tvdb_id[1])
                if is_debug:
                    PPRINT.print(Platform.NOTIFY,
                                 Status.DEBUG,
                                 f"[{{\"service\": \"{serv}\", \"serviceId\": {media_id}}}] -> {{{pf}: {media_id}}}")
            # replace the mappings
            index["mappings"] = final_mappings
        bar()

    return data
