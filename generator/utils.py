# SPDX-License-Identifier: MIT

import glob
import json
import subprocess
import sys
from time import time

from alive_progress import alive_it
from clock import convert_float_to_time as seconds_to_time_context
from const import GITHUB_DISPATCH, pprint
from prettyprint import Platform, Status


def check_git_any_changes() -> bool:
    """
    Check if there's any changes in git

    :return: True if there's any changes, False otherwise
    :rtype: bool
    """
    if GITHUB_DISPATCH:
        pprint.print(
            Platform.SYSTEM,
            Status.INFO,
            "Repository was forced to update, updating data",
        )
        return True
    try:
        subprocess.check_output(["git", "diff", "--quiet"])
        return False
    except subprocess.CalledProcessError:
        pprint.print(
            Platform.SYSTEM,
            Status.INFO,
            "Git has changes, updating data",
        )
        return True


def validate_json_files() -> None:
    """
    Validate all JSON files in the database/raw/ directory
    """
    pprint.print(Platform.SYSTEM, Status.INFO, "Validating JSON files")
    json_files = glob.glob("database/raw/*.json")
    json_files.append("api/schema.json")
    for file in alive_it(json_files):
        try:
            with open(file, "r", encoding="utf-8") as f:
                json.load(f)
        except json.JSONDecodeError as e:
            pprint.print(Platform.SYSTEM, Status.ERR, f"Invalid JSON file: {file}")
            pprint.print(Platform.SYSTEM, Status.ERR, f"Error: {e}")
            sys.exit(1)
    pprint.print(Platform.SYSTEM, Status.PASS, "All JSON files are valid")


def validate_schema() -> None:
    """
    Validate the generated animeapi.json against the schema
    """
    pprint.print(Platform.SYSTEM, Status.INFO, "Validating JSON schema")
    try:
        from jsonschema import validate
    except ImportError:
        pprint.print(
            Platform.SYSTEM,
            Status.ERR,
            "jsonschema not installed, skipping schema validation",
        )
        return

    with open("api/schema.json", "r", encoding="utf-8") as f:
        schema = json.load(f)

    with open("database/animeapi.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    try:
        validate(instance={"data": data}, schema=schema)
    except Exception as e:
        pprint.print(Platform.SYSTEM, Status.ERR, "JSON schema validation failed")
        pprint.print(Platform.SYSTEM, Status.ERR, f"Error: {e}")
        sys.exit(1)
    pprint.print(Platform.SYSTEM, Status.PASS, "JSON schema is valid")


def proc_stop(
    start_time: float,
    status: Status,
    message: str | None = None,
    exit_code: int = 0,
    show_traceback: bool = False,
) -> None:
    """
    Show message and exit from program

    :param start_time: start time
    :type start_time: float
    :param status: status
    :type status: Status
    :param message: message, defaults to None
    :type message: str, optional
    :param exit_code: exit code, defaults to 0
    :type exit_code: int, optional
    :param show_traceback: show traceback, defaults to False
    :type show_traceback: bool, optional
    :return: None
    :rtype: None
    """
    end_time = time()
    subtract_time = end_time - start_time
    context = seconds_to_time_context(subtract_time)
    print()
    pprint.print(Platform.SYSTEM, Status.INFO, f"Generator finished in {context}")
    if message:
        pprint.print(Platform.SYSTEM, status, message)
    if show_traceback:
        import traceback

        traceback.print_exc()
    sys.exit(exit_code)
