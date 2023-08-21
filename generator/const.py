import os

from prettyprint import PrettyPrint

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

attribution = {
    "mainrepo": "https://github.com/nattadasu/animeApi/tree/v3",
    "updated": {
        "timestamp": 0,
        "iso": ""
    },
    "contributors": [
        ""
    ],
    "sources": [
        "manami-project/anime-offline-database",
        "kawaiioverflow/arm",
        "ryuuganime/aniTrakt-IndexParser",
        "https://db.silveryasha.web.id",
        "https://kaize.io",
        "https://nautiljon.com",
        "https://otakotaku.com",
    ],
    "license": "AGPL-3.0",
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
        "themoviedb": 0,
        "trakt": 0,
        "total": 0,
    },
    "endpoints": {
        "$comment": "The endpoints are stated in Python regex format",
        "anidb": r"/anidb/(?P<media_id>\d+)",
        "anilist": r"/anilist/(?P<media_id>\d+)",
        "animeapi_tsv": r"/anime(a|A)pi.tsv",
        "animeplanet": r"/animeplanet/(?P<media_id>[\w\-]+)",
        "anisearch": r"/anisearch/(?P<media_id>\d+)",
        "annict": r"/annict/(?P<media_id>\d+)",
        "heartbeat": r"/(heartbeat|ping)",
        "imdb": r"/imdb/(?P<media_id>tt[\d]+)",
        "kaize": r"/kaize/(?P<media_id>[\w\-]+)",
        "kitsu": r"/kitsu/(?P<media_id>\d+)",
        "livechart": r"/livechart/(?P<media_id>\d+)",
        "myanimelist": r"/myanimelist/(?P<media_id>\d+)",
        "nautiljon": r"/nautiljon/(?P<media_id>[\w\+!\-_\(\)\[\]]+)",
        "notify": r"/notify/(?P<media_id>[\w\-_]+)",
        "otakotaku": r"/otakotaku/(?P<media_id>\d+)",
        "repo": r"/",
        "schema": r"/schema(?:.json)?",
        "shikimori": r"/shikimori/(?P<media_id>\d+)",
        "shoboi": r"/shoboi/(?P<media_id>\d+)",
        "silveryasha": r"/silveryasha/(?P<media_id>\d+)",
        "status": r"/status",
        "syobocal": r"/syobocal/(?P<media_id>\d+)",
        "themoviedb": r"/themoviedb/movie/(?P<media_id>\d+)",
        "trakt": r"/trakt/(?P<media_type>show|movie)(s)?/(?P<media_id>\d+)(?:/season(s)?/(?P<season_id>\d+))?",
        "updated": r"/updated",
    }
}
"""Attribution data"""
