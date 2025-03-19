"""Main API file"""

# pylint: disable=import-error

import json
from datetime import datetime as dtime
from datetime import timezone as tz
from time import time
from typing import Any, TypedDict, Union
from urllib.parse import unquote

from flask import (
    Flask,
    Response,
    g,
    jsonify,
    redirect,
    request,
    send_from_directory,  # type: ignore
)
from werkzeug.wrappers import Response as wzResponse

app = Flask(__name__)

runtime = time()


class CorruptedResp(TypedDict):
    error: str
    code: int
    message: str


def platform_id_content(platform: str, platform_id: Union[int, str]) -> dict[str, Any]:
    """Get content of platform ID

    Args:
        platform (str): Platform name
        platform_id (int): Platform ID

    Returns:
        dict[str, Any]: Platform ID content
    """
    extensions_to_remove = [".json", ".html"]
    platform_id = str(platform_id)
    for extension in extensions_to_remove:
        platform_id = platform_id.replace(extension, "")

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
    corrupted_msg: CorruptedResp = {
        "error": "Internal server error",
        "code": 500,
        "message": "myanimelist_object.json is corrupted",
    }
    platform = "myanimelist"
    mid = 1
    try:
        test_mal = platform_id_content(platform, mid)
        if test_mal["myanimelist"] != mid:
            raise KeyError
        end = time()
        return jsonify(
            {
                "status": "OK",
                "code": 200,
                "request_time": f"{round(end - runtime, 3)}s",
                "response_time": f"{round(end - start, 3)}s",
                "request_epoch": g.start,
            }
        )
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
    formatted_time = dtime.fromtimestamp(updated_time, tz=tz.utc).strftime(
        "%m/%d/%Y %H:%M:%S UTC"
    )
    return Response(f"Updated on {formatted_time}", mimetype="text/plain")


@app.route("/robots.txt", methods=["GET"])
def robots():
    """Robots route"""
    with open("api/robots.txt", "r", encoding="utf-8") as file_:
        return Response(file_.read(), mimetype="text/plain", status=200)


@app.route("/trakt/<media_type>/<media_id>", methods=["GET"])
@app.route("/trakt/<media_type>/<media_id>/seasons/<season_id>", methods=["GET"])
@app.route("/trakt/<media_type>/<media_id>/season/<season_id>", methods=["GET"])
def trakt_exclusive_route(
    media_type: str, media_id: int, season_id: Union[str, None] = None
):
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
        return jsonify(
            {
                "error": "Invalid season ID",
                "code": 400,
                "message": "Season ID cannot be 0",
            }
        ), 400
    try:
        if not media_type.endswith("s"):
            media_type_ = f"{media_type}s"
        else:
            media_type_ = media_type
        if season_id is None:
            return platform_id_content("trakt", f"{media_type_}/{media_id}")
        return platform_id_content(
            "trakt", f"{media_type_}/{media_id}/seasons/{season_id}"
        )
    except KeyError:
        return jsonify(
            {
                "error": "Not found",
                "code": 404,
                "message": f"""Media type {media_type} with ID {media_id} {
                    "and season ID " + str(season_id) + " "
                    if season_id is not None
                    else ""
                }not found""",
            }
        ), 404


@app.route("/themoviedb/<media_type>/<media_id>", methods=["GET"])
@app.route("/themoviedb/<media_type>/<media_id>/season/<season_id>", methods=["GET"])
def tmdb_exclusive_route(
    media_type: str, media_id: int, season_id: Union[str, None] = None
):
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
        return jsonify(
            {
                "error": "Invalid request",
                "code": 400,
                "message": "Currently, only `movie` are supported",
            }
        ), 400
    try:
        return platform_id_content("themoviedb", f"movie/{media_id}")
    except KeyError:
        return jsonify(
            {
                "error": "Not found",
                "code": 404,
                "message": f"Media type {media_type} with ID {media_id} not found",
            }
        ), 404


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
    route = request.path
    goto = get_goto(route)

    if route.endswith(".tsv"):
        return serve_tsv_response()

    return redirect_to_github(goto)


def get_goto(route: str, raw_platform: str) -> str:
    goto = route.replace("/", "")

    if goto.endswith(".json"):
        goto = goto.replace(".json", "")

    if not (goto.endswith("()") or goto.endswith("%28%29")) and goto != "animeapi":
        goto += "_object"
    else:
        goto = unquote(goto).replace("()", "")

    if goto == "syobocal":
        goto = "shoboi"

    return goto.replace(raw_platform, resolve_platform(raw_platform))


def serve_tsv_response() -> Response:
    with open("database/animeapi.tsv", "r", encoding="utf-8") as file_:
        response = Response(
            file_.read(), mimetype="text/tab-separated-values", status=200
        )
        response.headers["Content-Disposition"] = 'inline; filename="animeapi.tsv"'
        return response


def redirect_to_github(goto: str) -> wzResponse:
    github_url = (
        f"https://raw.githubusercontent.com/nattadasu/animeApi/v3/database/{goto}.json"
    )
    return redirect(github_url)


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
    platform = resolve_platform(platform=platform)
    try:
        data = platform_id_content(platform, platform_id)
        return jsonify(data)
    except FileNotFoundError:
        return jsonify(
            {
                "error": "Not found",
                "code": 404,
                "message": f"Platform {platform} not found",
            }
        ), 404
    except KeyError:
        return jsonify(
            {
                "error": "Not found",
                "code": 404,
                "message": f"Platform {platform} with ID {platform_id} not found",
            }
        ), 404


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
    platform, platform_id, target, israw = extract_params(args)
    israw = israw is not None

    if not platform:
        return error_response(
            "Invalid platform",
            400,
            "Platform not found, please specify platform by adding `platform` parameter.",
        )

    if not platform_id:
        return error_response(
            "Invalid platform ID",
            400,
            "Platform ID not found, please specify platform ID by adding `platform_id` parameter",
        )

    platform = resolve_platform(platform)
    target = resolve_platform(target)

    if not platform:
        return error_response(
            "Invalid platform",
            400,
            f"Platform not found, please check if `{platform}` is a valid platform",
        )

    if target and not is_valid_target(target):
        return error_response("Invalid target", 400, f"Target {target} not found")

    if not target:
        uri = build_uri(platform, platform_id)
        return generate_response(uri, israw)

    if platform == "trakt":
        response = handle_trakt_case(platform_id)
        if response:
            return response
    if platform == "themoviedb" and ("movie" not in platform_id):
        platform_id = f"movie/{platform_id}"

    maps = platform_id_content(platform=platform, platform_id=platform_id)
    uri = build_target_uri(target, maps, platform, platform_id)
    if isinstance(uri, Response):
        return uri

    return generate_response(uri, israw)


def extract_params(args):
    platform = (args.get("platform") or args.get("from") or "").lower()
    platform_id = args.get("mediaid") or args.get("id")
    target = args.get("target") or args.get("to")
    israw = args.get("raw") or args.get("r")
    return platform, platform_id, target, israw


def error_response(error, code, message):
    return jsonify({"error": error, "code": code, "message": message}), code


def resolve_platform(platform):
    synonyms = {
        "anidb": ["adb", "anidb.net"],
        "anilist": ["al", "anilist.co"],
        "animeplanet": ["ap", "anime-planet", "anime-planet.com"],
        "anisearch": ["as", "anisearch.com"],
        "annict": ["anc", "act", "ac", "annict.com"],
        "imdb": ["imdb.com"],
        "kaize": ["kz", "kaize.io"],
        "kitsu": ["kts", "kt", "kitsu.app", "kitsu.io"],
        "kurozora": ["kr", "krz", "kurozora.app"],
        "letterboxd": ["lb", "letterboxd.com"],
        "livechart": ["lc", "livechart.me"],
        "myanimelist": ["mal", "myanimelist.net"],
        "nautiljon": ["ntj", "nautiljon.com"],
        "notify": ["ntf", "notifymoe", "notify.moe"],
        "otakotaku": ["oo", "otakotaku.com"],
        "shikimori": ["shiki", "shikimori.one"],
        "shoboi": ["syoboi", "syb", "cal.syoboi.jp"],
        "silveryasha": ["dbti", "sy"],
        "simkl": ["smk", "simkl.com", "animecountdown", "animecountdown.com"],
        "themoviedb": ["tmdb", "tmdb.org"],
        "trakt": ["trk", "trakt.tv"],
    }
    # Create a lookup dictionary including both proper names and aliases
    lookup = {
        alias: key for key, aliases in synonyms.items() for alias in [key] + aliases
    }
    return lookup.get(platform)


def is_valid_target(target):
    # fmt: off
    valid_targets = [
        "anidb", "anilist", "animeplanet", "anisearch", "annict", "imdb", "kaize",
        "kitsu", "kurozora", "livechart", "myanimelist", "nautiljon", "notify",
        "otakotaku", "shikimori", "shoboi", "silveryasha", "themoviedb", "trakt",
        "simkl", "letterboxd",
    ]
    return target in valid_targets


route_path = {
    "anidb": "https://anidb.net/anime/",
    "anilist": "https://anilist.co/anime/",
    "animeplanet": "https://www.anime-planet.com/anime/",
    "anisearch": "https://www.anisearch.com/anime/",
    "annict": "https://annict.com/works/",
    "imdb": "https://www.imdb.com/title/",
    "kaize": "https://kaize.io/anime/",
    "kitsu": "https://kitsu.app/anime/",
    "kurozora": "https://kurozora.app/myanimelist.net/anime/",
    "letterboxd": "https://letterboxd.com/tmdb/",
    "livechart": "https://www.livechart.me/anime/",
    "myanimelist": "https://myanimelist.net/anime/",
    "nautiljon": "https://www.nautiljon.com/animes/",
    "notify": "https://notify.moe/anime/",
    "otakotaku": "https://otakotaku.com/anime/view/",
    "shikimori": "https://shikimori.one/animes/",
    "shoboi": "https://cal.syoboi.jp/tid/",
    "silveryasha": "https://db.silveryasha.id/anime/",
    "simkl": "https://simkl.com/anime/",
    "themoviedb": "https://www.themoviedb.org/movie/",
    "trakt": "https://trakt.tv/",
}


def build_uri(platform, platform_id):
    return route_path.get(platform, "") + str(platform_id)


def generate_response(uri, israw):
    if not israw:
        return redirect(uri)
    else:
        return Response(uri, mimetype="text/plain", status=200)


def handle_trakt_case(platform_id):
    trakt_arr = platform_id.split("/")
    if len(trakt_arr) > 1 and not trakt_arr[1].isdigit():
        final_id = "/".join(trakt_arr[:2])
        return error_response(
            "Invalid Trakt ID",
            400,
            f"Trakt ID for {final_id} is not an `int`. Please convert the slug to `int` ID using Trakt API to proceed.",
        )


def build_target_uri(target, maps, platform, platform_id):
    try:
        if target == "trakt":
            return build_trakt_uri(maps, target)
        if target == "kurozora":
            if not maps.get("myanimelist"):
                return error_response(
                    "Not found",
                    404,
                    "MyAnimeList ID not found, which is requirement for Kurozora's Universal Link.",
                )
            else:
                return f"{route_path[target]}{maps['myanimelist']}"
        if target == "letterboxd":
            if not maps.get("themoviedb"):
                return error_response(
                    "Not found",
                    404,
                    "TheMovieDB ID not found, which is the main database source for Letterboxd.",
                )
            else:
                return f"{route_path[target]}{maps['themoviedb']}"
        return build_generic_uri(maps, target)
    except ValueError:
        title = maps.get("title", "(Unknown title)")
        return error_response(
            "Not found",
            404,
            f"{title} does not exist on {target} using {platform} with ID {platform_id}",
        )
    except KeyError:
        return error_response(
            "Not found", 404, f"{target} not found on {platform} with ID {platform_id}"
        )


def build_trakt_uri(maps, target):
    tgt_id = maps.get("trakt")
    if tgt_id is None:
        raise ValueError
    media_type = maps.get("trakt_type")
    season = maps.get("trakt_season")
    if not season:
        return f"{route_path[target]}{media_type}/{tgt_id}"
    else:
        return f"{route_path[target]}{media_type}/{tgt_id}/seasons/{season}"


def build_generic_uri(maps, target):
    tgt_id = maps.get(target)
    if tgt_id is None:
        raise ValueError
    return f"{route_path[target]}{tgt_id}"


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
