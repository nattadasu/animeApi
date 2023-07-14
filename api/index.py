import json
from datetime import datetime

import flask

app = flask.Flask(__name__)


@app.route("/", methods=["GET"])
@app.route("/status", methods=["GET"])
@app.route("/api", methods=["GET"])
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
