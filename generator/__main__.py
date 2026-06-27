# SPDX-License-Identifier: MIT

import argparse
import os
import sys


def _parse_args() -> argparse.Namespace:
    """Parse CLI arguments and inject them into os.environ before const.py loads."""
    parser = argparse.ArgumentParser(
        prog="generator",
        description="AnimeAPI database generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Each flag can also be set via the corresponding environment variable
(true/1/yes are all accepted):

  FORCE_FETCH_HIKKA       --force-fetch-hikka
  FORCE_FETCH_NAUTILJON   --force-fetch-nautiljon
  FORCE_FETCH_KAIZE       --force-fetch-kaize
  FORCE_FETCH_OTAKOTAKU   --force-fetch-otakotaku
  FORCE_DUMP              --force-dump

CLI flags take precedence: if either the flag or the env var is set,
the feature is enabled.

Examples:
  uv run python3 generator
  uv run python3 generator --force-fetch-hikka --force-dump
  uv run python3 generator --force-fetch-kaize --force-fetch-nautiljon
        """,
    )

    fetch_group = parser.add_argument_group("force-fetch options")
    fetch_group.add_argument(
        "--force-fetch-hikka",
        action="store_true",
        default=False,
        help="Bypass the day-3/17 gate and fetch Hikka data live",
    )
    fetch_group.add_argument(
        "--force-fetch-nautiljon",
        action="store_true",
        default=False,
        help="Bypass the day-2/16 gate and scrape Nautiljon live",
    )
    fetch_group.add_argument(
        "--force-fetch-kaize",
        action="store_true",
        default=False,
        help="Force a live Kaize scrape (errors loudly instead of using cached file)",
    )
    fetch_group.add_argument(
        "--force-fetch-otakotaku",
        action="store_true",
        default=False,
        help="Bypass the day-1/15 gate and do a full OtakOtaku re-fetch from ID 1",
    )

    dump_group = parser.add_argument_group("dump options")
    dump_group.add_argument(
        "--force-dump",
        action="store_true",
        default=False,
        help="Regenerate and commit the database even when git reports no changes",
    )

    return parser.parse_args()


def _apply_args_to_env(args: argparse.Namespace) -> None:
    """
    Merge parsed CLI flags into os.environ so const.py picks them up.
    Existing env vars already set to a truthy value are left untouched.
    """
    flag_map = {
        "force_fetch_hikka": "FORCE_FETCH_HIKKA",
        "force_fetch_nautiljon": "FORCE_FETCH_NAUTILJON",
        "force_fetch_kaize": "FORCE_FETCH_KAIZE",
        "force_fetch_otakotaku": "FORCE_FETCH_OTAKOTAKU",
        "force_dump": "FORCE_DUMP",
    }
    for attr, env_key in flag_map.items():
        if getattr(args, attr):
            os.environ[env_key] = "true"


def main() -> None:
    """Main function"""
    args = _parse_args()
    _apply_args_to_env(args)

    # Import main *after* env vars are injected so const.py reads the
    # correct values when it is first imported.
    from main import main as _main

    _main()


if __name__ == "__main__":
    if sys.version_info < (3, 10):
        raise RuntimeError("Python version >= 3.10 is required.")
    main()
