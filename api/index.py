import json
from datetime import datetime
from os.path import getsize
from typing import Any, Union

import flask

app = flask.Flask(__name__)


def platform_id_content(platform: str, platform_id: int) -> dict[str, Any]:
    with open(f"database/{platform}_object.json", "r") as f:
        data = json.loads(f.read())
    return data[str(platform_id)]


@app.route("/", methods=["GET"])
@app.route("/status", methods=["GET"])
def index():
    with open("api/status.json", "r") as f:
        return flask.jsonify(json.loads(f.read()))


@app.route("/updated", methods=["GET"])
def updated():
    with open("api/status.json", "r") as f:
        updated_time = json.loads(f.read())["updated"]["timestamp"]
    formatted_time = datetime.utcfromtimestamp(
        updated_time).strftime("%m/%d/%Y %H:%M:%S UTC")
    return flask.Response(f"Updated on {formatted_time}", mimetype="text/plain")


@app.route("/robots.txt", methods=["GET"])
def robots():
    with open("api/robots.txt", "r") as f:
        return flask.Response(f.read(), mimetype="text/plain", status=200)


@app.route("/animeApi.json", methods=["GET"])
@app.route("/animeApi", methods=["GET"])
@app.route("/animeapi.json", methods=["GET"])
@app.route("/animeapi", methods=["GET"])
def anime_api():
    return flask.jsonify({
        "error": "File too large",
        "code": 413,
        "message": f"To bypass this, prefer to download from GitHub raw directly. Your path is: https://raw.githubusercontent.com/nattadasu/animeApi/v3/database/animeapi.json"
    }), 413


@app.route("/<platform>().json", methods=["GET"])
@app.route("/<platform>()", methods=["GET"])
def platform(platform: str):
    with open(f"database/{platform}_object.json", "r") as f:
        file_size = getsize(f"database/{platform}_object.json")
        # if above 5MB, throw error
        if file_size > 5000000:
            return flask.jsonify({
                "error": "File too large",
                "code": 413,
                "message": f"To bypass this, prefer to download from GitHub raw directly. Your path is: https://raw.githubusercontent.com/nattadasu/animeApi/v3/database/{platform}_object.json"
            }), 413
        return flask.jsonify(json.loads(f.read()))


@app.route("/trakt/<media_type>/<media_id>.json", methods=["GET"])
@app.route("/trakt/<media_type>/<media_id>", methods=["GET"])
@app.route("/trakt/<media_type>/<media_id>/seasons/<season_id>.json", methods=["GET"])
@app.route("/trakt/<media_type>/<media_id>/seasons/<season_id>", methods=["GET"])
def trakt_exclusive_route(media_type: str, media_id: int, season_id: Union[int, None] = None):
    with open(f"database/trakt_object.json", "r") as f:
        data = json.loads(f.read())
    if season_id is None:
        return flask.jsonify(data[f"{media_type}/{media_id}"])
    return flask.jsonify(data[f"{media_type}/{media_id}/seasons/{season_id}"])


@app.route("/<platform>.json", methods=["GET"])
@app.route("/<platform>", methods=["GET"])
def platform_array(platform: str):
    with open(f"database/{platform}.json", "r") as f:
        file_size = getsize(f"database/{platform}.json")
        # if above 5MB, throw error
        if file_size > 5000000:
            return flask.jsonify({
                "error": "File too large",
                "code": 413,
                "message": f"To bypass this, prefer to download from GitHub raw directly. Your path is: https://raw.githubusercontent.com/nattadasu/animeApi/v3/database/{platform}.json"
            }), 413
        return flask.jsonify(json.loads(f.read()))


@app.route("/<platform>/<platform_id>.json", methods=["GET"])
@app.route("/<platform>/<platform_id>", methods=["GET"])
def platform_id(platform: str, platform_id: int):
    data = platform_id_content(platform, platform_id)
    return flask.jsonify(data)


# general error handler
@app.errorhandler(Exception)
def handle_error(err: Exception):
    err_split = str(err).split(":")
    get_code = err_split[0].split(" ")
    data = {
        "error": " ".join(err_split[-1:]).strip(),
        "code": int(get_code[0]),
    }
    return flask.jsonify(data), int(get_code[0])
