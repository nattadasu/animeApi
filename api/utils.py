"""Utility functions for the API"""

from typing import Any, Dict
from urllib.parse import unquote

# Platform synonyms mapping
PLATFORM_SYNONYMS = {
    "anidb": ["ad", "adb", "anidb.net"],
    "anilist": ["al", "anilist.co"],
    "animenewsnetwork": ["an", "ann", "animenewsnetwork.com"],
    "animeplanet": ["ap", "anime-planet", "anime-planet.com", "animeplanet.com"],
    "anisearch": [
        "as",
        "anisearch.de",
        "anisearch.es",
        "anisearch.fr",
        "anisearch.it",
        "anisearch.jp",
        "anisearch.com",
    ],
    "annict": ["ac", "act", "anc", "annict.com", "annict.jp", "en.annict.com"],
    "imdb": ["im", "imdb.com"],
    "kaize": ["kz", "kaize.io"],
    "kitsu": ["kt", "kts", "kitsu.app", "kitsu.io"],
    "kurozora": ["kr", "krz", "kurozora.app"],
    "letterboxd": ["lb", "lx", "letterboxd.com"],
    "livechart": ["lc", "livechart.me"],
    "myanili": ["my", "myani.li"],
    "myanimelist": ["ma", "mal", "myanimelist.net"],
    "nautiljon": ["nj", "ntj", "nautiljon.com"],
    "notify": ["nf", "ntf", "ntm", "notifymoe", "notify.moe"],
    "otakotaku": ["oo", "otakotaku.com"],
    "shikimori": [
        "sh",
        "shk",
        "shiki",
        "shikimori.me",
        "shikimori.one",
        "shikimori.org",
    ],
    "shoboi": ["sb", "shb", "syb", "syoboi", "shobocal", "syobocal", "cal.syoboi.jp"],
    "silveryasha": ["sy", "dbti", "db.silveryasha.id", "db.silveryasha.web.id"],
    "simkl": ["sm", "smk", "simkl.com", "animecountdown", "animecountdown.com"],
    "themoviedb": ["tm", "tmdb", "tmdb.org", "themoviedb.org"],
    "thetvdb": ["tv", "thetvdb.com", "thetvdb", "tvtime", "tt", "tvtime.com"],
    "trakt": ["tr", "trk", "trakt.tv"],
}


def resolve_platform(platform: str) -> str:
    """
    Resolve platform input to a standard platform name

    :param platform: Platform name
    :type platform: str
    :return: Standard platform name
    :rtype: str
    """
    platform = platform.lower()
    # Create a lookup dictionary including both proper names and aliases
    lookup = {
        alias: key
        for key, aliases in PLATFORM_SYNONYMS.items()
        for alias in [key] + aliases
    }
    return lookup.get(platform, platform)


def is_valid_target(target: str) -> bool:
    """
    Check if target is valid

    :param target: Target
    :type target: str
    :return: True if valid, False otherwise
    :rtype: bool
    """
    target = resolve_platform(target)
    valid_targets = PLATFORM_SYNONYMS.keys()
    return target in valid_targets


def alias_get(data: Dict[str, Any], known_aliases: list[str]) -> str:
    """
    Get data from alias

    :param data: Data
    :type data: dict[str, Any]
    :param known_aliases: Known aliases
    :type known_aliases: list[str]
    :return: Alias
    :rtype: str
    """
    for alias in known_aliases:
        if data.get(alias):
            return data[alias]
    return ""


def clean_platform_id(platform_id: str) -> str:
    """
    Clean platform ID by removing common extensions

    :param platform_id: Platform ID
    :type platform_id: str
    :return: Cleaned platform ID
    :rtype: str
    """
    extensions_to_remove = [".json", ".html"]
    platform_id = str(platform_id)
    for extension in extensions_to_remove:
        platform_id = platform_id.replace(extension, "")
    return unquote(platform_id)
