"""
SPDX-License-Identifier: MIT

A module to fetch .dat database from Notify.moe
"""

from animeapi_backend.controller.httprequest import HTTPRequest
from animeapi_backend.config.const import PPRINT, USER_AGENT
from animeapi_backend.prettyprint import Platform, Status


def fetch_database() -> str:
    """
    Fetch the database from Notify.moe

    :return: The database
    :rtype: str
    """
    PPRINT.print(Platform.NOTIFY, Status.INFO, "Fetching database")
    request = HTTPRequest(user_agent=USER_AGENT, platform=Platform.NOTIFY)
    download = request.download("notify_new",
                                "dat",
                                "https://notify.moe/api/types/Anime/download")
    if type(download) == str:
        return download
    else:
        raise ValueError("Database is not a string!")
