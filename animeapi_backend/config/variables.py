"""Module for storing global variables that is used in the project"""

# Switches
is_verbose = False
is_debug = False

# Attribution data
attribution = {
    "mainrepo": "https://github.com/nattadasu/animeApi/tree/v4",
    "updated": {
        "timestamp": 0,
        "iso": ""
    },
    "contributors": [
        ""
    ],
    "sources": [
        "https://anilist.co/api",
        "https://db.silveryasha.web.id",
        "https://jikan.moe/api/v3",
        "https://kaize.io",
        "https://kitsu.io/api",
        "https://myanimelist.net",
        "https://nautiljon.com",
        "https://notify.moe/api/types/Anime/download",
        "https://otakotaku.com",
        "https://shikimori.me",
        "kawaiioverflow/arm",
        "ryuuganime/aniTrakt-IndexParser",
    ],
    "license": "MIT",
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
        "auto": r"/auto/\?url={url}",
        "anidb": r"/anidb/{media_id}",
        "anilist": r"/anilist/{media_id}",
        "animeapi_tsv": r"/animeapi.tsv",
        "animeplanet": r"/animeplanet/{media_id}",
        "anisearch": r"/anisearch/{media_id}",
        "annict": r"/annict/{media_id}",
        "heartbeat": r"/heartbeat",
        "imdb": r"/imdb/{media_id}",
        "kaize": r"/kaize/{media_id}",
        "kitsu": r"/kitsu/{media_id}",
        "livechart": r"/livechart/{media_id}",
        "myanimelist": r"/myanimelist/{media_id}",
        "nautiljon": r"/nautiljon/{media_id}",
        "notify": r"/notify/{media_id}",
        "otakotaku": r"/otakotaku/{media_id}",
        "redirect": r"/redirect\?platform={platform}&media_id={media_id}&target={target}",
        "rd": r"/rd\?from={platform}&id={media_id}&to={target}",
        "repo": r"/",
        "schema": r"/schema.json",
        "shikimori": r"/shikimori/{media_id}",
        "shoboi": r"/shoboi/{media_id}",
        "silveryasha": r"/silveryasha/{media_id}",
        "status": r"/status",
        "syobocal": r"/syobocal/{media_id}",
        "themoviedb": r"/themoviedb/movie/{media_id}",
        "trakt": r"/trakt/{shows_or_movies}/{media_id}<seasons/{season_id}>",
        "updated": r"/updated",
    }
}
"""Attribution data"""
