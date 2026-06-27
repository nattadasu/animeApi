import os
from typing import Any

from dotenv import load_dotenv
from prettyprint import PrettyPrint

# if .env file exists, load it
if os.path.isfile(".env"):
    load_dotenv()

KAIZE_EMAIL = os.getenv("KAIZE_EMAIL")
"""User email for Kaize login"""
KAIZE_PASSWORD = os.getenv("KAIZE_PASSWORD")
"""User password for Kaize login"""

GITHUB_DISPATCH = os.getenv("GITHUB_EVENT_NAME") == "workflow_dispatch"
"""Whether the script is running from GitHub Actions workflow_dispatch event"""

FORCE_FETCH_HIKKA = os.getenv("FORCE_FETCH_HIKKA", "").lower() in ("true", "1", "yes")
"""Force a live Hikka API fetch regardless of the scheduled day gate"""

FORCE_FETCH_NAUTILJON = os.getenv("FORCE_FETCH_NAUTILJON", "").lower() in (
    "true",
    "1",
    "yes",
)
"""Force a live Nautiljon scrape regardless of the scheduled day gate"""

FORCE_FETCH_KAIZE = os.getenv("FORCE_FETCH_KAIZE", "").lower() in ("true", "1", "yes")
"""Force a live Kaize scrape instead of falling back to the cached local file"""

FORCE_FETCH_OTAKOTAKU = os.getenv("FORCE_FETCH_OTAKOTAKU", "").lower() in (
    "true",
    "1",
    "yes",
)
"""Force a full OtakOtaku re-fetch from ID 1 regardless of the scheduled day gate"""

FORCE_DUMP = os.getenv("FORCE_DUMP", "").lower() in ("true", "1", "yes")
"""Force regeneration and commit of the database even when git reports no changes"""

pprint = PrettyPrint()
"""PrettyPrint class instance"""

attribution: dict[str, Any] = {
    "mainrepo": "https://github.com/nattadasu/animeApi/tree/v3",
    "updated": {"timestamp": 0, "iso": ""},
    "contributors": [""],
    "sources": [
        "gh:kawaiioverflow/arm",
        "gh:manami-project/anime-offline-database",
        "gh:rensetsu/db.rensetsu.public-dump",
        "gh:rensetsu/db.trakt.extended-anitrakt",
        "gh:Fribb/anime-lists",
        "https://kaize.io",
        "https://nautiljon.com",
        "https://otakotaku.com",
        "https://livechart.me",
        "https://shikimori.one",
        "https://geckyzz.my.id",
        "https://anilist.co",
        "https://kitsu.app",
    ],
    "license": "MIT AND ODbL-1.0 AND DbCL-1.0 AND CC0-1.0",
    "website": "https://animeapi.my.id",
    "counts": {
        "anidb": 0,
        "anilist": 0,
        "animenewsnetwork": 0,
        "animeplanet": 0,
        "anisearch": 0,
        "annict": 0,
        "hikka": 0,
        "imdb": 0,
        "kaize": 0,
        "kitsu": 0,
        "letterboxd": 0,
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
        "thetvdb": 0,
        "trakt": 0,
        "total": 0,
    },
    "endpoints": {
        "$comment": "The endpoints are stated in Python regex format. Platform aliases supported for direct lookup for platform specific endpoints (see ?P<alias> in regex).",
        "anidb": r"/(?P<alias>anidb)/(?P<media_id>\d+)",
        "anilist": r"/(?P<alias>anilist)/(?P<media_id>\d+)",
        "animeapi_dump": r"/(anime(?:a|A)pi|aa)(?:\\\.json)?",
        "animeapi_tsv": r"/(anime(?:a|A)pi|aa).tsv",
        "animenewsnetwork": r"(?P<alias>animenewsnetwork)/(?P<media_id>\d+)",
        "animeplanet": r"/(?P<alias>animeplanet)/(?P<media_id>[\w\-]+)",
        "anisearch": r"/(?P<alias>anisearch)/(?P<media_id>\d+)",
        "annict": r"/(?P<alias>annict)/(?P<media_id>\d+)",
        "heartbeat": r"/(heartbeat|ping)",
        "hikka": r"/(?P<alias>hikka)/(?P<media_id>\d+)",
        "imdb": r"/(?P<alias>imdb)/(?P<media_id>tt[\d]+)",
        "kaize": r"/(?P<alias>kaize)/(?P<media_id>[\w\-]+)",
        "kitsu": r"/(?P<alias>kitsu)/(?P<media_id>\d+)",
        "letterboxd": r"/(?P<alias>letterboxd)/(?P<media_id>[\w\-]+)",
        "livechart": r"/(?P<alias>livechart)/(?P<media_id>\d+)",
        "myanimelist": r"/(?P<alias>myanimelist)/(?P<media_id>\d+)",
        "nautiljon": r"/(?P<alias>nautiljon)/(?P<media_id>[\w\+!\-_\(\)\[\]]+)",
        "notify": r"/(?P<alias>notify)/(?P<media_id>[\w\-_]+)",
        "otakotaku": r"/(?P<alias>otakotaku)/(?P<media_id>\d+)",
        "redirect": r"/(redirect|rd)",
        "repo": r"/",
        "schema": r"/schema(?:\\\.json)?",
        "shikimori": r"/(?P<alias>shikimori)/(?P<media_id>\d+)",
        "shoboi": r"/(?P<alias>shoboi)/(?P<media_id>\d+)",
        "silveryasha": r"/(?P<alias>silveryasha)/(?P<media_id>\d+)",
        "simkl": r"/(?P<alias>simkl)/(?P<media_id>\d+)",
        "status": r"/status",
        "syobocal": r"/(?P<alias>syobocal)/(?P<media_id>\d+)",
        "themoviedb": r"/(?P<alias>themoviedb)/(?P<media_type>movie|tv)/(?P<media_id>\d+)(?:/seasons?/(?P<season_id>\d+))?",
        "thetvdb": r"/(?P<alias>thetvdb)/series/(?P<media_id>\d+)(?:/seasons?/(?P<season_id>\d+))?",
        "trakt": r"/(?P<alias>trakt)/(?P<media_type>show|movie)(s)?/(?P<media_id>\w\-+)(?:/seasons?/(?P<season_id>\d+))?",
        "updated": r"/updated",
    },
}
"""Attribution data"""
