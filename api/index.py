"""Main API file"""

# pylint: disable=import-error

import json
from datetime import datetime
from time import time
from typing import Any, Union
from urllib.parse import unquote

from flask import send_from_directory  # type: ignore
from flask import Flask, Response, g, jsonify, redirect, request

app = Flask(__name__)


def platform_id_content(platform: str, platform_id: Union[int, str]) -> dict[str, Any]:
    """Get content of platform ID

    Args:
        platform (str): Platform name
        platform_id (int): Platform ID

    Returns:
        dict[str, Any]: Platform ID content
    """
    extensions_to_remove = ['.json', '.html']
    platform_id = str(platform_id)
    for extension in extensions_to_remove:
        platform_id = platform_id.replace(extension, '')

    platform_id = unquote(platform_id)

    with open(f"database/{platform}_object.json", "r", encoding="utf-8") as file_:
        data = json.loads(file_.read())
    return data[str(platform_id)]


@app.before_request
def before_request():
    """Before request"""
    g.start = time()


@app.route("/", methods=["GET"])
def index():
    """Index route"""
    # redirect user to GitHub repo
    return redirect("https://github.com/nattadasu/animeApi")


@app.route("/status", methods=["GET"])
def status():
    """Status route"""
    with open("api/status.json", "r", encoding="utf-8") as file_:
        return jsonify(json.loads(file_.read()))


@app.route("/heartbeat", methods=["GET"])
@app.route("/ping", methods=["GET"])
def heartbeat():
    """Heartbeat route"""
    # get request time
    start = time()
    corrupted_msg = {
        "error": "Internal server error",
        "code": 500,
        "message": "myanimelist_object.json is corrupted"
    }
    platform = "myanimelist"
    mid = 1
    try:
        test_mal = platform_id_content(platform, mid)
        if test_mal["myanimelist"] != mid:
            raise KeyError
        end = time()
        return jsonify({
            "status": "OK",
            "code": 200,
            "response_time": f"{round(end - start, 3)}s",
            # get info from g.start
            "request_time": f"{round(end - g.start, 3)}s",
            "request_epoch": g.start,
        })
    except FileNotFoundError:
        return jsonify(corrupted_msg), 500
    except KeyError:
        return jsonify(corrupted_msg), 500


@app.route("/favicon.ico", methods=["GET"])
def favicon():
    """Favicon route, if browser/SEO bot requests it"""
    return send_from_directory("api", "favicon.ico")  # type: ignore


@app.route("/schema.json", methods=["GET"])
@app.route("/schema", methods=["GET"])
def schema_json():
    """Schema route"""
    with open("api/schema.json", "r", encoding="utf-8") as file_:
        return jsonify(json.loads(file_.read()))


@app.route("/updated", methods=["GET"])
def updated():
    """Updated route"""
    with open("api/status.json", "r", encoding="utf-8") as file_:
        updated_time = json.loads(file_.read())["updated"]["timestamp"]
    formatted_time = datetime.utcfromtimestamp(
        updated_time).strftime("%m/%d/%Y %H:%M:%S UTC")
    return Response(f"Updated on {formatted_time}", mimetype="text/plain")


@app.route("/robots.txt", methods=["GET"])
def robots():
    """Robots route"""
    with open("api/robots.txt", "r", encoding="utf-8") as file_:
        return Response(file_.read(), mimetype="text/plain", status=200)


@app.route("/trakt/<media_type>/<media_id>", methods=["GET"])
@app.route("/trakt/<media_type>/<media_id>/seasons/<season_id>", methods=["GET"])
@app.route("/trakt/<media_type>/<media_id>/season/<season_id>", methods=["GET"])
def trakt_exclusive_route(media_type: str, media_id: int, season_id: Union[str, None] = None):
    """
    Trakt exclusive route

    Args:
        media_type (str): Media type, must be `movie` or `show`
        media_id (int): Media ID
        season_id (Union[str, None], optional): Season ID. Defaults to None.

    Returns:
        Response: Response
    """
    if season_id == "0" and media_type in ["shows", "show"]:
        return jsonify({
            "error": "Invalid season ID",
            "code": 400,
            "message": "Season ID cannot be 0"
        }), 400
    try:
        if not media_type.endswith("s"):
            media_type_ = f"{media_type}s"
        else:
            media_type_ = media_type
        if season_id is None:
            return platform_id_content("trakt", f"{media_type_}/{media_id}")
        return platform_id_content("trakt", f"{media_type_}/{media_id}/seasons/{season_id}")
    except KeyError:
        return jsonify({
            "error": "Not found",
            "code": 404,
            "message": f"""Media type {media_type} with ID {media_id} {
                'and season ID ' + str(season_id) + ' '
                if season_id is not None
                else ''
            }not found"""
        }), 404


@app.route("/themoviedb/<media_type>/<media_id>", methods=["GET"])
@app.route("/themoviedb/<media_type>/<media_id>/season/<season_id>", methods=["GET"])
def tmdb_exclusive_route(media_type: str, media_id: int, season_id: Union[str, None] = None):
    """
    The Movie Database exclusive route

    Args:
        media_type (str): Media type, must be `movie`
        media_id (int): Media ID
        season_id (Union[str, None], optional): Season ID. Defaults to None.

    Returns:
        Response: Response
    """
    if media_type == "tv" or season_id is not None:
        return jsonify({
            "error": "Invalid request",
            "code": 400,
            "message": "Currently, only `movie` are supported"
        }), 400
    try:
        return platform_id_content("themoviedb", f"movie/{media_id}")
    except KeyError:
        return jsonify({
            "error": "Not found",
            "code": 404,
            "message": f"Media type {media_type} with ID {media_id} not found"
        }), 404


@app.route("/<platform>", methods=["GET"])
@app.route("/<platform>%28%29", methods=["GET"])
def platform_array(platform: str = "animeapi"):
    """
    Platform array route, redirects to the raw JSON file on GitHub

    Args:
        platform (str, optional): Platform name. Defaults to "animeapi".

    Returns:
        Response: Redirect response
    """
    # get current route
    route = request.path
    platform = platform.lower()
    if route.endswith(".tsv"):
        with open("database/animeapi.tsv", "r", encoding="utf-8") as file_:
            response = Response(
                file_.read(), mimetype="text/tab-separated-values", status=200)
            response.headers['Content-Disposition'] = 'inline; filename="animeapi.tsv"'
            return response
    # remove .json if present
    if route.endswith(".json"):
        route = route.replace(".json", "")
    if not (route.endswith("()") or route.endswith("%28%29")) and platform != "animeapi":
        platform = platform + "_object"
    else:
        platform = unquote(platform).replace('()', '')
    if platform == "syobocal":
        platform = "shoboi"
    return redirect(
        f"https://raw.githubusercontent.com/nattadasu/animeApi/v3/database/{platform}.json")


@app.route("/<platform>/<platform_id>", methods=["GET"])
def platform_lookup(platform: str, platform_id: Union[int, str]):
    """
    Platform lookup route

    Args:
        platform (str): Platform name
        platform_id (int): Platform ID

    Returns:
        Response: JSON response
    """
    platform = platform.lower()
    if platform == "syobocal":
        platform = "shoboi"
    try:
        data = platform_id_content(platform, platform_id)
        return jsonify(data)
    except FileNotFoundError:
        return jsonify({
            "error": "Not found",
            "code": 404,
            "message": f"Platform {platform} not found"
        }), 404
    except KeyError:
        return jsonify({
            "error": "Not found",
            "code": 404,
            "message": f"Platform {platform} with ID {platform_id} not found"
        }), 404

# redirect route
# example: /rd?platform=anilist&platform_id=1&to=kitsu


@app.route("/rd", methods=["GET"])
@app.route("/redirect", methods=["GET"])
def redirect_route():
    """
    Redirect route

    Returns:
        Response: Redirect response
    """
    args = request.args
    # get platform and platform ID
    platform = args.get("platform") or args.get("from")
    platform = str(platform).lower()
    platform_id = args.get("mediaid") or args.get("id")
    target = args.get("target") or args.get("to")
    israw = args.get("raw") or args.get("r")
    # convert to switch bool whatever the value is in raw if exist
    israw = israw is not None
    route_path = {
        "anidb": "https://anidb.net/anime/",
        "anilist": "https://anilist.co/anime/",
        "animeplanet": "https://www.anime-planet.com/anime/",
        "anisearch": "https://www.anisearch.com/anime/",
        "annict": "https://annict.com/works/",
        "imdb": "https://www.imdb.com/title/",
        "kaize": "https://kaize.io/anime/",
        "kitsu": "https://kitsu.io/anime/",
        "livechart": "https://www.livechart.me/anime/",
        "myanimelist": "https://myanimelist.net/anime/",
        "nautiljon": "https://www.nautiljon.com/animes/",
        "notify": "https://notify.moe/anime/",
        "otakotaku": "https://otakotaku.com/anime/view/",
        "shikimori": "https://shikimori.one/animes/",
        "shoboi": "https://cal.syoboi.jp/tid/",
        "silveryasha": "https://db.silveryasha.web.id/anime/",
        "themoviedb": "https://www.themoviedb.org/movie/",
        "trakt": "https://trakt.tv/",
        "simkl": "https://simkl.com/",
    }
    # handle synonyms
    synonyms = {
        "anidb":       ["anidb", "adb", "anidb.net"],
        "anilist":     ["anilist", "al", "anilist.co"],
        "animeplanet": ["animeplanet", "ap", "anime-planet", "anime-planet.com"],
        "anisearch":   ["anisearch", "as", "anisearch.com", "anisearch.de",
                        "anisearch.fr", "anisearch.jp", "anisearch.es",
                        "anisearch.it"],
        "annict":      ["annict", "anc", "act", "ac", "annict.com", "annict.jp",
                        "en.annict.com"],
        "imdb":        ["imdb", "imdb.com"],
        "kaize":       ["kaize", "kz", "kaize.io"],
        "kitsu":       ["kitsu", "kts", "kt", "kitsu.io"],
        "livechart":   ["livechart", "lc", "livechart.me"],
        "myanimelist": ["myanimelist", "mal", "myanimelist.net"],
        "nautiljon":   ["nautiljon", "ntj", "nautiljon.com"],
        "notify":      ["notify", "ntf", "ntm", "nm", "nf", "notifymoe",
                        "notify.moe"],
        "otakotaku":   ["otakotaku", "oo", "otakotaku.com"],
        "simkl":       ["simkl", "smk", "simkl.com"],
        "shikimori":   ["shikimori", "shiki", "shk", "shikimori.org",
                        "shikimori.one", "shikimori.me"],
        "shoboi":      ["shoboi", "shobocal", "syoboi", "syobocal", "syb", "shb",
                        "sb", "cal.syoboi.jp"],
        "silveryasha": ["silveryasha", "dbti", "sy", "db.silveryasha.web.id"],
        "themoviedb":  ["themoviedb", "tmdb", "tmdb.org"],
        "trakt":       ["trakt", "trk", "trakt.tv"],
    }

    pf_check = False
    tg_check = False if target else True
    for key, value in synonyms.items():
        if not pf_check:
            if platform in value:
                pf_check = True
                platform = key
        if not tg_check:
            if target in value:
                tg_check = True
                target = key
        if pf_check and tg_check:
            break

    # if platform not found, return error
    if not pf_check or not platform:
        return jsonify({
            "error": "Invalid platform",
            "code": 400,
            "message": f"Platform not found, please specify platform by adding `platform` parameter, or check if `{platform}` is a valid platform"
        }), 400

    # if platform ID not found, return error
    if not platform_id:
        return jsonify({
            "error": "Invalid platform ID",
            "code": 400,
            "message": "Platform ID not found, please specify platform ID by adding `platform_id` parameter"
        }), 400

    # if target specified but not found, return error
    if not tg_check and target:
        return jsonify({
            "error": "Invalid target",
            "code": 400,
            "message": f"Target {target} not found"
        }), 400

    # if target not specified, redirect to platform ID
    if not target:
        uri = route_path[platform] + str(platform_id)
        if not israw:
            return redirect(uri)
        else:
            return Response(uri, mimetype="text/plain", status=200)

    # if target specified, redirect to target
    maps = platform_id_content(platform=platform, platform_id=platform_id)
    uri = ""
    try:
        if target not in ["trakt", "simkl"]:
            tgt_id = maps[target]
            if tgt_id is None:
                raise ValueError
            uri = f"{route_path[target]}{tgt_id}"
        elif target == "trakt":
            tgt_id = maps["trakt"]
            if tgt_id is None:
                raise ValueError
            media_type = maps["trakt_type"]
            season = maps["trakt_season"]
            if not season:
                uri = f"{route_path[target]}{media_type}/{tgt_id}"
            else:
                uri = f"{route_path[target]}{media_type}/{tgt_id}/seasons/{season}"
        elif target == "simkl":
            # if does not have anidb id, raise error
            if not maps["anidb"]:
                return jsonify({
                    "error": "Not found",
                    "code": 404,
                    "message": "AniDB ID not found, which is the main database source for Simkl. Please issue missing show to SIMKL or create a creq on AniDB if the entry is not a special or OVA"
                }), 404
            uri = f"https://api.simkl.com/redirect?to=Simkl&anidb={maps['anidb']}"
    except ValueError:
        try:
            title = maps["title"]
        except KeyError:
            title = "(Unknown title)"
        return jsonify({
            "error": "Not found",
            "code": 404,
            "message": f"{title} does not exist on {target} using {platform} with ID {platform_id}"
        }), 404
    except KeyError:
        return jsonify({
            "error": "Not found",
            "code": 404,
            "message": f"{target} not found on {platform} with ID {platform_id}"
        }), 404

    if not israw:
        return redirect(uri)
    else:
        return Response(uri, mimetype="text/plain", status=200)

# general error handler


@app.errorhandler(Exception)
def handle_error(err: Exception):
    """
    Error handler

    Args:
        err (Exception): Exception

    Returns:
        Response: JSON response
    """
    err_split = str(err).split(":")
    get_code = err_split[0].split(" ")
    data = {
        "error": " ".join(err_split[-1:]).strip(),
        "code": int(get_code[0]),
    }
    return jsonify(data), int(get_code[0])
