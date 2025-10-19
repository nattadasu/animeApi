"""Main API file"""

# pylint: disable=import-error

import json
from datetime import datetime as dtime
from datetime import timezone as tz
from time import time
from typing import Any, Tuple, TypedDict, Union
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

# fmt: off
PLATFORM_SYNONYMS = {
    "anidb": ["ad", "adb", "anidb.net"],
    "anilist": ["al", "anilist.co"],
    "animenewsnetwork": ["an", "ann", "animenewsnetwork.com"],
    "animeplanet": ["ap", "anime-planet", "anime-planet.com", "animeplanet.com"],
    "anisearch": ["as", "anisearch.de", "anisearch.es", "anisearch.fr", "anisearch.it", "anisearch.jp", "anisearch.com"],
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
    "shikimori": ["sh", "shk", "shiki", "shikimori.me", "shikimori.one", "shikimori.org"],
    "shoboi": ["sb", "shb", "syb", "syoboi", "shobocal", "syobocal", "cal.syoboi.jp"],
    "silveryasha": ["sy", "dbti", "db.silveryasha.id", "db.silveryasha.web.id"],
    "simkl": ["sm", "smk", "simkl.com", "animecountdown", "animecountdown.com"],
    "themoviedb": ["tm", "tmdb", "tmdb.org", "themoviedb.org"],
    "thetvdb": ["tv", "thetvdb.com", "thetvdb", "tvtime", "tt", "tvtime.com"],
    "trakt": ["tr", "trk", "trakt.tv"],
}
# fmt: on


class CorruptedResp(TypedDict):
    error: str
    code: int
    message: str


def platform_id_content(platform: str, platform_id: Union[int, str]) -> dict[str, Any]:
    """Get content of platform ID

    :param platform: Platform name
    :type platform: str
    :param platform_id: Platform ID
    :type platform_id: Union[int, str]
    :return: Platform ID content
    :rtype: dict[str, Any]
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
    return send_from_directory(".", "favicon.ico", mimetype="image/vnd.microsoft.icon")


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

    :param media_type: Media type, must be `movie` or `show`
    :type media_type: str
    :param media_id: Media ID
    :type media_id: int
    :param season_id: Season ID, defaults to None
    :type season_id: Union[str, None], optional
    :return: Response
    :rtype: Response
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

    Supports both movies and TV shows. Season numbers are from Trakt's verified data.

    :param media_type: Media type, must be `movie` or `tv`
    :type media_type: str
    :param media_id: Media ID
    :type media_id: int
    :param season_id: Season ID (Trakt season number), defaults to None
    :type season_id: Union[str, None], optional
    :return: Response
    :rtype: Response
    """
    try:
        if season_id is None:
            return platform_id_content("themoviedb", f"{media_type}/{media_id}")
        return platform_id_content(
            "themoviedb", f"{media_type}/{media_id}/season/{season_id}"
        )
    except KeyError:
        return jsonify(
            {
                "error": "Not found",
                "code": 404,
                "message": f"Media type {media_type} with ID {media_id} {
                    'and season ' + str(season_id) + ' '
                    if season_id is not None
                    else ''
                }not found",
            }
        ), 404


@app.route("/thetvdb/series/<series_id>", methods=["GET"])
@app.route("/thetvdb/series/<series_id>/seasons/<season_id>", methods=["GET"])
def tvdb_exclusive_route(series_id: int, season_id: Union[str, None] = None):
    """
    TheTVDB exclusive route

    Season numbers are from Trakt's verified data, not TVDB's native season IDs.

    :param series_id: Series ID
    :type series_id: int
    :param season_id: Season number (Trakt season number), defaults to None
    :type season_id: Union[str, None], optional
    :return: Response
    :rtype: Response
    """
    if season_id == "0":
        return jsonify(
            {
                "error": "Invalid season number",
                "code": 400,
                "message": "Season number cannot be 0",
            }
        ), 400
    try:
        if season_id is None:
            return platform_id_content("thetvdb", f"series/{series_id}")
        return platform_id_content("thetvdb", f"series/{series_id}/seasons/{season_id}")
    except KeyError:
        return jsonify(
            {
                "error": "Not found",
                "code": 404,
                "message": f"Series {series_id} {
                    'season ' + str(season_id) + ' ' if season_id is not None else ''
                }not found",
            }
        ), 404


@app.route("/<platform>", methods=["GET"])
@app.route("/<platform>%28%29", methods=["GET"])
def platform_array(platform: str = "animeapi"):
    """
    Platform array route, redirects to the raw JSON file on GitHub

    :param platform: Platform name, defaults to "animeapi"
    :type platform: str, optional
    :return: Redirect response
    :rtype: Response
    """
    route = request.path
    goto = get_goto(route, platform)

    if route in ["/animeapi.tsv", "/aa.tsv"]:
        return serve_tsv_response()

    if is_valid_target(goto.replace("_object", "")) or platform in ["animeapi", "aa"]:
        return redirect_to_github(goto)
    return error_response(
        "Invalid platform",
        400,
        f"Platform {platform} not found, please check if it is a valid platform",
    )


def get_goto(route: str, raw_platform: str) -> str:
    """
    Redirect to the raw JSON file on GitHub

    :param route: Route
    :type route: str
    :param raw_platform: Raw platform
    :type raw_platform: str
    :return: Redirect URL
    :rtype: str
    """
    goto = unquote(route.strip("/"))
    raw_platform = unquote(raw_platform)

    if goto.endswith(".json"):
        goto = goto[:-5]
        raw_platform = raw_platform[:-5]
    is_array = raw_platform.endswith("()")

    raw_platform = raw_platform.rstrip("()")
    goto = resolve_platform(raw_platform)
    goto = goto.replace("aa", "animeapi")

    if not is_array and "animeapi" not in goto:
        goto = f"{goto}_object"

    return goto


def serve_tsv_response() -> Response:
    """
    Serve TSV response

    :return: Response
    :rtype: Response
    """
    with open("database/animeapi.tsv", "r", encoding="utf-8") as file_:
        response = Response(
            file_.read(), mimetype="text/tab-separated-values", status=200
        )
        response.headers["Content-Disposition"] = 'inline; filename="animeapi.tsv"'
        return response


def redirect_to_github(goto: str) -> wzResponse:
    """
    Redirect to GitHub

    :param goto: Goto
    :type goto: str
    :return: Redirect response
    :rtype: wzResponse
    """
    github_url = (
        f"https://raw.githubusercontent.com/nattadasu/animeApi/v3/database/{goto}.json"
    )
    return redirect(github_url)


@app.route("/<platform>/<platform_id>", methods=["GET"])
def platform_lookup(
    platform: str, platform_id: Union[int, str]
) -> Tuple[Response, int]:
    """
    Platform lookup route

    :param platform: Platform name
    :type platform: str
    :param platform_id: Platform ID
    :type platform_id: Union[int, str]
    :return: JSON response
    :rtype: Tuple[Response, int]
    """
    platform = platform.lower()
    platform = resolve_platform(platform=platform)
    try:
        data = platform_id_content(platform, platform_id)
        return jsonify(data), 200
    except FileNotFoundError:
        return jsonify(
            {
                "error": "Not found",
                "code": 404,
                "message": f"Platform {platform} not found or not supported",
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
    israw = True if israw else False

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

    if platform in ["kurozora", "myanili"]:
        return error_response(
            "Invalid platform source",
            400,
            f"Platform `{platform}` is not supported as redirect source (one-way)",
        )

    if target and not is_valid_target(target):
        return error_response("Invalid target", 400, f"Target {target} not found")

    if not target:
        uri = build_uri(platform, platform_id)
        return generate_response(uri, israw)

    if platform == "trakt":
        response = handle_trakt_case(str(platform_id))
        if response:
            return response
    if platform == "themoviedb" and ("movie" not in str(platform_id)):
        platform_id = f"movie/{platform_id}"

    maps = platform_id_content(platform=platform, platform_id=platform_id)
    uri = build_target_uri(target, maps, platform, str(platform_id))
    if isinstance(uri, Response):
        return uri

    if isinstance(uri, tuple):
        return uri
    return generate_response(uri, israw)


def alias_get(data: dict[str, Any], known_aliases: list[str]) -> str:
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


def extract_params(args: dict[str, Any]) -> tuple[str, Union[int, str], str, bool]:
    """
    Extract parameters

    :param args: Arguments
    :type args: dict[str, Any]
    :return: Platform, platform ID, target, is raw
    :rtype: tuple[str, Union[int, str], str, bool]
    """
    platform = alias_get(args, ["platform", "from", "f"]).lower()
    platform = resolve_platform(platform)
    platform_id = alias_get(args, ["mediaid", "id", "i"])
    platform_id = platform_id if platform_id else 0
    target = alias_get(args, ["target", "to", "t"]).lower()
    target = resolve_platform(target) if target else platform
    try:
        try:
            try:
                israw = args["israw"]
            except KeyError:
                israw = args["raw"]
        except KeyError:
            israw = args["r"]
        israw = True
    except KeyError:
        israw = False
    return platform, platform_id, target, israw


def error_response(error: str, code: int, message: str) -> Tuple[Response, int]:
    """
    Error response

    :param error: Error
    :type error: str
    :param code: Code
    :type code: int
    :param message: Message
    :type message: str
    :return: JSON response
    :rtype: Tuple[Response, int]
    """
    return jsonify({"error": error, "code": code, "message": message}), code


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


route_path = {
    "anidb": "https://anidb.net/anime/",
    "anilist": "https://anilist.co/anime/",
    "animenewsnetwork": "https://animenewsnetwork/encyclopedia/anime?id=",
    "animeplanet": "https://www.anime-planet.com/anime/",
    "anisearch": "https://www.anisearch.com/anime/",
    "annict": "https://annict.com/works/",
    "imdb": "https://www.imdb.com/title/",
    "kaize": "https://kaize.io/anime/",
    "kitsu": "https://kitsu.app/anime/",
    "kurozora": "https://kurozora.app/myanimelist.net/anime/",
    "letterboxd": "https://letterboxd.com/film/",
    "livechart": "https://www.livechart.me/anime/",
    "myanili": "https://myani.li/#/anime/details/",
    "myanimelist": "https://myanimelist.net/anime/",
    "nautiljon": "https://www.nautiljon.com/animes/",
    "notify": "https://notify.moe/anime/",
    "otakotaku": "https://otakotaku.com/anime/view/",
    "shikimori": "https://shikimori.one/animes/",
    "shoboi": "https://cal.syoboi.jp/tid/",
    "silveryasha": "https://db.silveryasha.id/anime/",
    "simkl": "https://simkl.com/anime/",
    "themoviedb": "https://www.themoviedb.org/movie/",
    "thetvdb": "https://www.thetvdb.com/",
    "trakt": "https://trakt.tv/",
}


def build_uri(platform: str, platform_id: Union[int, str]) -> str:
    """
    Build URI

    :param platform: Platform
    :type platform: str
    :param platform_id: Platform ID
    :type platform_id: Union[int, str]
    :return: URI
    :rtype: str
    """
    return route_path.get(platform, "") + str(platform_id)


def generate_response(uri: str, israw: bool) -> Union[Response, wzResponse]:
    """
    Generate response

    :param uri: URI
    :type uri: str
    :param israw: Return raw response
    :type israw: bool
    :return: Response
    :rtype: Union[Response, wzResponse]
    """
    if israw:
        return Response(uri, mimetype="text/plain", status=200)
    return redirect(uri)


def handle_trakt_case(platform_id: str) -> Union[Tuple[Response, int], None]:
    """
    Handle Trakt case

    :param platform_id: Platform ID
    :type platform_id: str
    :return: Response or None
    :rtype: Union[Response, None]
    """
    trakt_arr = platform_id.split("/")
    if len(trakt_arr) > 1 and not trakt_arr[1].isdigit():
        final_id = "/".join(trakt_arr[:2])
        return error_response(
            "Invalid Trakt ID",
            400,
            f"Trakt ID for {final_id} is not an `int`. Please convert the slug to `int` ID using Trakt API to proceed.",
        )


# def build_target_uri(target, maps, platform, platform_id):
def build_target_uri(
    target: str, maps: dict[str, Any], platform: str, platform_id: str
) -> Union[str, Tuple[Response, int]]:
    """
    Build target URI

    :param target: Target
    :type target: str
    :param maps: Maps
    :type maps: dict[str, Any]
    :param platform: Platform
    :type platform: str
    :param platform_id: Platform ID
    :type platform_id: str
    :return: URI or Response
    :rtype: Union[str, Tuple[Response, int]]
    """
    try:
        if target == "trakt":
            return build_trakt_uri(maps, target)
        if target == "kurozora" or target == "myanili":
            if maps.get("myanimelist"):
                return f"{route_path[target]}{maps['myanimelist']}"
            return error_response(
                "Not found",
                404,
                f"MyAnimeList ID not found, which is requirement for {target}.",
            )
        if target == "thetvdb":
            thetvdb_id = maps.get("thetvdb")
            trakt_season = maps.get("trakt_season")
            if thetvdb_id:
                base_uri = f"{route_path[target]}series/{thetvdb_id}"
                if trakt_season and trakt_season > 0:
                    tvdb_sid = maps.get("thetvdb_season_id")
                    if tvdb_sid:
                        return f"{base_uri}/seasons/{tvdb_sid}"
                    return f"{base_uri}/seasons/{trakt_season}"
                return base_uri
            return error_response(
                "Not found",
                404,
                "TheTVDB ID not found for this entry.",
            )
        if target == "letterboxd":
            letterboxd_slug = maps.get("letterboxd_slug")
            if letterboxd_slug:
                return f"{route_path[target]}{letterboxd_slug}"
            raise ValueError
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


def build_trakt_uri(maps: dict[str, Any], target: str) -> str:
    """
    Build Trakt URI

    :param maps: Maps
    :type maps: dict[str, Any]
    :param target: Target
    :type target: str
    :return: URI
    :rtype: str
    """
    tgt_id = maps.get("trakt")
    if tgt_id is None:
        raise ValueError
    media_type = maps.get("trakt_type")
    season = maps.get("trakt_season")
    if season:
        return f"{route_path[target]}{media_type}/{tgt_id}/seasons/{season}"
    return f"{route_path[target]}{media_type}/{tgt_id}"


def build_generic_uri(maps: dict[str, Any], target: str) -> str:
    """
    Build generic URI

    :param maps: Maps
    :type maps: dict[str, Any]
    :param target: Target
    :type target: str
    :return: URI
    :rtype: str
    """
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
    data: dict[str, Union[str, int]] = {
        "error": " ".join(err_split[-1:]).strip(),
        "code": int(get_code[0]),
    }
    return jsonify(data), int(get_code[0])
