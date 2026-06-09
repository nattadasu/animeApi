#!/usr/bin/env python3
# SPDX-License-Identifier: MIT

"""
Regenerate pickle database from TSV file.

This script loads the animeapi.tsv file and converts it to a pickle file
for fast loading in the API. Useful after manual data corrections or TSV updates.
"""

import pickle
from pathlib import Path

import pandas as pd

# Column data types matching dumper.py load_tsv_for_counting()
TSV_DTYPES = {
    "title": str,
    "anidb": "Int64",
    "anilist": "Int64",
    "animenewsnetwork": "Int64",
    "animeplanet": str,
    "anisearch": "Int64",
    "annict": "Int64",
    "hikka": str,
    "imdb": str,
    "kaize": str,
    "kaize_id": "Int64",
    "kitsu": "Int64",
    "letterboxd_lid": str,
    "letterboxd_slug": str,
    "letterboxd_uid": "Int64",
    "livechart": "Int64",
    "myanimelist": "Int64",
    "nautiljon": str,
    "nautiljon_id": "Int64",
    "notify": str,
    "otakotaku": "Int64",
    "shikimori": "Int64",
    "shoboi": "Int64",
    "silveryasha": "Int64",
    "simkl": "Int64",
    "themoviedb": "Int64",
    "themoviedb_season_id": "Int64",
    "themoviedb_type": str,
    "thetvdb": "Int64",
    "thetvdb_season_id": "Int64",
    "trakt": "Int64",
    "trakt_may_invalid": str,
    "trakt_season": "Int64",
    "trakt_season_id": "Int64",
    "trakt_slug": str,
    "trakt_type": str,
}


def main() -> None:
    """Regenerate pickle from TSV."""
    tsv_path = Path("database/animeapi.tsv")
    pkl_path = Path("database/animeapi.pkl")

    if not tsv_path.exists():
        print(f"Error: {tsv_path} not found")
        return

    print(f"Loading TSV from {tsv_path}...")
    df = pd.read_csv(
        tsv_path,
        sep="\t",
        dtype=TSV_DTYPES,
        keep_default_na=True,
    )

    # Convert boolean columns
    df["trakt_may_invalid"] = df["trakt_may_invalid"].replace(
        {"True": True, "False": False, "": None}
    )

    print(f"Loaded {len(df)} entries with {len(df.columns)} columns")

    # Save to pickle
    print(f"Saving pickle to {pkl_path}...")
    with open(pkl_path, "wb") as file_:
        pickle.dump(df, file_, protocol=pickle.HIGHEST_PROTOCOL)

    file_size = pkl_path.stat().st_size / 1024 / 1024
    print(f"Pickle saved: {file_size:.1f}MB")

    # Verify
    print("Verifying pickle...")
    with open(pkl_path, "rb") as file_:
        df_loaded = pickle.load(file_)
        if len(df_loaded) == len(df) and list(df.columns) == list(df_loaded.columns):
            print("✓ Verification passed")
        else:
            print("✗ Verification failed")
            return

    print("Done!")


if __name__ == "__main__":
    main()
