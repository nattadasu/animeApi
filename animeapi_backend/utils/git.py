import subprocess

from animeapi_backend.config.const import PPRINT, GITHUB_DISPATCH
from prettyprint import Platform, Status

def check_git_any_changes() -> bool:
    """
    Check if there's any changes in git

    :return: True if there's any changes, False otherwise
    :rtype: bool
    """
    if GITHUB_DISPATCH:
        PPRINT.print(
            Platform.SYSTEM,
            Status.INFO,
            "Repository was forced to update, updating data",
        )
        return True
    try:
        subprocess.check_output(["git", "diff", "--quiet"])
        return False
    except subprocess.CalledProcessError:
        PPRINT.print(
            Platform.SYSTEM,
            Status.INFO,
            "Git has changes, updating data",
        )
        return True
