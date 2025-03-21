import os
from typing import Any

from dotenv import load_dotenv
from prettyprint import PrettyPrint

# if .env file exists, load it
if os.path.isfile(".env"):
    load_dotenv()

KAIZE_XSRF_TOKEN = os.getenv("KAIZE_XSRF_TOKEN")
"""Kaize XSRF token"""
KAIZE_SESSION = os.getenv("KAIZE_SESSION")
"""Kaize session cookie"""
KAIZE_EMAIL = os.getenv("KAIZE_EMAIL")
"""User email for Kaize login"""
KAIZE_PASSWORD = os.getenv("KAIZE_PASSWORD")
"""User password for Kaize login"""

GITHUB_DISPATCH = os.getenv("GITHUB_EVENT_NAME") == "workflow_dispatch"
"""Whether the script is running from GitHub Actions workflow_dispatch event"""

pprint = PrettyPrint()
"""PrettyPrint class instance"""

attribution: dict[str, Any] = {
    "mainrepo": "https://github.com/nattadasu/animeApi/tree/v3",
    "updated": {"timestamp": 0, "iso": ""},
    "contributors": [""],
    "sources": [
        "kawaiioverflow/arm",
        "manami-project/anime-offline-database",
        "rensetsu/db.rensetsu.public-dump",
        "rensetsu/db.trakt.anitrakt",
        "https://kaize.io",
        "https://nautiljon.com",
        "https://otakotaku.com",
    ],
    "license": "AGPL-3.0-only AND MIT AND CC0-1.0+",
    "website": "https://animeapi.my.id",
    "counts": {
        "anidb": 0,
        "anilist": 0,
        "animeplanet": 0,
        "anisearch": 0,
        "annict": 0,
        "imdb": 0,
        "kaize": 0,
        "kitsu": 0,
        "livechart": 0,
        "myanimelist": 0,
        "nautiljon": 0,
        "notify": 0,
        "otakotaku": 0,
        "shikimori": 0,
        "shoboi": 0,
        "silveryasha": 0,
        "simkl": 0,
        "themoviedb": 0,
        "trakt": 0,
        "total": 0,
    },
    "endpoints": {
        "$comment": "The endpoints are stated in Python regex format. Platform aliases supported for direct lookup for platform specific endpoints (see ?P<alias> in regex).",
        "anidb": r"/(?P<alias>anidb)/(?P<media_id>\d+)",
        "anilist": r"/(?P<alias>anilist)/(?P<media_id>\d+)",
        "animeapi_dump": r"/(anime(?:a|A)pi|aa)(?:\\\.json)?",
        "animeapi_tsv": r"/(anime(?:a|A)pi|aa).tsv",
        "animeplanet": r"/(?P<alias>animeplanet)/(?P<media_id>[\w\-]+)",
        "anisearch": r"/(?P<alias>anisearch)/(?P<media_id>\d+)",
        "annict": r"/(?P<alias>annict)/(?P<media_id>\d+)",
        "heartbeat": r"/(heartbeat|ping)",
        "imdb": r"/(?P<alias>imdb)/(?P<media_id>tt[\d]+)",
        "kaize": r"/(?P<alias>kaize)/(?P<media_id>[\w\-]+)",
        "kitsu": r"/(?P<alias>kitsu)/(?P<media_id>\d+)",
        "livechart": r"/(?P<alias>livechart)/(?P<media_id>\d+)",
        "myanimelist": r"/(?P<alias>myanimelist)/(?P<media_id>\d+)",
        "nautiljon": r"/(?P<alias>nautiljon)/(?P<media_id>[\w\+!\-_\(\)\[\]]+)",
        "notify": r"/(?P<alias>notify)/(?P<media_id>[\w\-_]+)",
        "otakotaku": r"/(?P<alias>otakotaku)/(?P<media_id>\d+)",
        "platform_dump": r"/(?P<alias>[\w\-]+)(?:\\\.json)?",
        "redirect": r"/(redirect|rd)",
        "repo": r"/",
        "schema": r"/schema(?:\\\.json)?",
        "shikimori": r"/(?P<alias>shikimori)/(?P<media_id>\d+)",
        "shoboi": r"/(?P<alias>shoboi)/(?P<media_id>\d+)",
        "silveryasha": r"/(?P<alias>silveryasha)/(?P<media_id>\d+)",
        "simkl": r"/(?P<alias>simkl)/(?P<media_id>\d+)",
        "status": r"/status",
        "syobocal": r"/(?P<alias>syobocal)/(?P<media_id>\d+)",
        "themoviedb": r"/(?P<alias>themoviedb)/movie/(?P<media_id>\d+)",
        "trakt": r"/(?P<alias>trakt)/(?P<media_type>show|movie)(s)?/(?P<media_id>\d+)(?:/season(s)?/(?P<season_id>\d+))?",
        "updated": r"/updated",
    },
}
"""Attribution data"""
