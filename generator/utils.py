import subprocess

from const import pprint
from prettyprint import Platform, Status


def check_git_any_changes() -> bool:
    """Check if there's any changes in git"""
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
