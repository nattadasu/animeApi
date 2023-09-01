# SPDX-License-Identifier: MIT

import subprocess

from const import pprint, GITHUB_DISPATCH
from prettyprint import Platform, Status


def check_git_any_changes() -> bool:
    """Check if there's any changes in git"""
    if GITHUB_DISPATCH:
        pprint.print(
            Platform.SYSTEM,
            Status.INFO,
            "Repository was forced to update, updating data",
        )
        return True
    try:
        subprocess.check_output(["git", "diff", "--quiet"])
        pprint.print(
            Platform.SYSTEM,
            Status.INFO,
            "Git has no changes, skipping data update",
        )
        return False
    except subprocess.CalledProcessError:
        pprint.print(
            Platform.SYSTEM,
            Status.INFO,
            "Git has changes, updating data",
        )
        return True
