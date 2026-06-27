#!/usr/bin/env python3
# SPDX-License-Identifier: MIT

"""
Fetch future seasonal mapping data from LiveChart and Shikimori,
unify them, detect and pull missing historical MAL IDs from Hikka,
sanitize and normalize all source URLs, and format them as AOD-like entries.
"""

import datetime
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any

import requests
from bs4 import BeautifulSoup
from thefuzz import fuzz

sys.path.append(str(Path(__file__).resolve().parent.parent))
from generator.prettyprint import Platform, PrettyPrint, Status

USER_AGENT = "AnimeAPI/3.0 (github.com/nattadasu/animeApi)"
pprint = PrettyPrint()


# Map month to season
MONTH_TO_SEASON = {
    1: "winter",
    2: "winter",
    3: "winter",
    4: "spring",
    5: "spring",
    6: "spring",
    7: "summer",
    8: "summer",
    9: "summer",
    10: "fall",
    11: "fall",
    12: "fall",
}

SEASONS_ORDER = ["winter", "spring", "summer", "fall"]


def get_seasons_range():
    """Generate list of seasons from winter {this.year - 1} to fall {this.year + 1}"""
    this_year = datetime.datetime.now().year
    seasons = []
    for year in [this_year - 1, this_year, this_year + 1]:
        for s in ["winter", "spring", "summer", "fall"]:
            seasons.append((s, year))
    return seasons


def sanitize_synonym(syn):
    """Remove language tags like [en], [ja-jp] from the beginning of the synonym"""
    if not syn:
        return ""
    return re.sub(r"^\[[a-zA-Z]{2,4}(-[a-zA-Z]{2,4})?\]\s*", "", syn).strip()


def normalize_url(url):
    """Normalize a URL to standard absolute format"""
    if not url:
        return None
    url = url.strip()
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url
    return url


def extract_id_from_url(url, pattern):
    """Extract an ID integer/string from a URL given a regex pattern"""
    if not url:
        return None
    match = re.search(pattern, url)
    if match:
        for group in match.groups():
            if group is not None:
                try:
                    return int(group)
                except ValueError:
                    return group
    return None


def sanitize_source_urls(sources):
    """Sanitize source URLs to make them all https, strip trailing slashes, and generalize AniDB/Kitsu URLs"""
    sanitized = set()
    for url in sources:
        normalized = normalize_url(url)
        if not normalized:
            continue

        # Convert http to https
        if normalized.startswith("http://"):
            normalized = "https://" + normalized[7:]

        # Strip trailing slash
        normalized = normalized.rstrip("/")

        # Standardize kitsu.io to kitsu.app
        if "kitsu.io" in normalized:
            normalized = normalized.replace("kitsu.io", "kitsu.app")

        # Generalize AniDB url to standard recent anidb.net/anime/{id}
        if "anidb.net" in normalized:
            anidb_id = extract_id_from_url(normalized, r"(?:anime/|/a|aid=)(\d+)")
            if anidb_id:
                normalized = f"https://anidb.net/anime/{anidb_id}"

        sanitized.add(normalized)
    return list(sanitized)


def fetch_livechart_season_ids(season, year=None):
    """Scrape LiveChart season page for all anime IDs"""
    if season == "tba":
        slug = "tba"
    else:
        slug = f"{season}-{year}"

    url = f"https://www.livechart.me/{slug}/all"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:151.0) Gecko/20100101 Firefox/151.0"
    }

    pprint.print(Platform.LIVECHART, Status.INFO, f"Scraping LiveChart page: {url}")
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        if resp.status_code != 200:
            pprint.print(
                Platform.LIVECHART,
                Status.INFO,
                f"  LiveChart {slug} returned status: {resp.status_code}",
            )
            return []

        soup = BeautifulSoup(resp.text, "html.parser")
        articles = soup.find_all("article", class_="anime")
        ids = []
        for a in articles:
            anime_id = a.get("data-anime-id")
            if anime_id:
                ids.append(anime_id)
        pprint.print(
            Platform.LIVECHART,
            Status.INFO,
            f"  Found {len(ids)} shows in LiveChart {slug}",
        )
        return ids
    except Exception as e:
        pprint.print(
            Platform.LIVECHART, Status.FAIL, f"  Error scraping LiveChart {slug}: {e}"
        )
        return []


def fetch_livechart_details(ids):
    """Query LiveChart GraphQL API in batches for show details"""
    url = "https://www.livechart.me/graphql"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:151.0) Gecko/20100101 Firefox/151.0",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    results = {}
    batch_size = 50
    pprint.print(
        Platform.LIVECHART,
        Status.INFO,
        f"Querying LiveChart GraphQL details for {len(ids)} shows...",
    )

    for i in range(0, len(ids), batch_size):
        batch = ids[i : i + batch_size]
        fields = []
        for anime_id in batch:
            fields.append(f"""
            anime_{anime_id}: singleAnime(id: "{anime_id}") {{
              databaseId
              romajiTitle
              englishTitle
              nativeTitle
              alternativeTitles
              releaseStatus
              startDate {{
                value
              }}
              anidbUrl
              annUrl
              animePlanetUrl
              anisearchUrl
              kitsuUrl
              malUrl
              anilistUrl
            }}
            """)

        query = "query {\n" + "\n".join(fields) + "\n}"
        try:
            resp = requests.post(
                url, headers=headers, json={"query": query}, timeout=20
            )
            if resp.status_code == 200:
                data = resp.json().get("data", {})
                for key, val in data.items():
                    if val:
                        real_id = key.split("_")[1]
                        results[real_id] = val
            else:
                pprint.print(
                    Platform.LIVECHART,
                    Status.FAIL,
                    f"  Batch {i // batch_size + 1} GraphQL failed (status {resp.status_code})",
                )
        except Exception as e:
            pprint.print(
                Platform.LIVECHART,
                Status.FAIL,
                f"  Error fetching batch {i // batch_size + 1}: {e}",
            )

        # Add rate limit delay between batches to avoid jumpscaring them
        time.sleep(2)

    pprint.print(
        Platform.LIVECHART,
        Status.PASS,
        f"  Successfully fetched details for {len(results)} LiveChart shows.",
    )
    return results


def fetch_shikimori_seasonal(season_slug):
    """Query Shikimori GraphQL API for seasonal anime"""
    url = "https://shikimori.io/api/graphql"
    headers = {
        "User-Agent": USER_AGENT,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    query = """
    query GetSeasonalAnimes($season: SeasonString!, $page: Int!) {
      animes(season: $season, limit: 50, page: $page, kind: "!special") {
        id
        malId
        name
        english
        japanese
        synonyms
        status
        releasedOn {
          date
        }
        externalLinks {
          id
          kind
          url
        }
      }
    }
    """

    pprint.print(
        Platform.SHIKIMORI,
        Status.INFO,
        f"Querying Shikimori seasonal GraphQL: {season_slug}",
    )
    animes = []
    page = 1
    while True:
        payload = {"query": query, "variables": {"season": season_slug, "page": page}}
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=15)
            if resp.status_code == 200:
                data = resp.json().get("data", {}).get("animes", [])
                if not data:
                    break
                animes.extend(data)
                pprint.print(
                    Platform.SHIKIMORI,
                    Status.INFO,
                    f"  Page {page}: fetched {len(data)} items",
                )
                if len(data) < 50:
                    break
                page += 1
            else:
                pprint.print(
                    Platform.SHIKIMORI,
                    Status.FAIL,
                    f"  Shikimori query failed with status {resp.status_code}",
                )
                break
        except Exception as e:
            pprint.print(
                Platform.SHIKIMORI,
                Status.FAIL,
                f"  Error querying Shikimori page {page}: {e}",
            )
            break

    pprint.print(
        Platform.SHIKIMORI,
        Status.INFO,
        f"  Total found: {len(animes)} shows in Shikimori season {season_slug}",
    )
    return animes


def fetch_shikimori_anons():
    """Query Shikimori GraphQL API for all announced shows (handles TBA / unknown season)"""
    url = "https://shikimori.io/api/graphql"
    headers = {
        "User-Agent": USER_AGENT,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    query = """
    query GetAnnouncedAnimes($page: Int!) {
      animes(status: "anons", limit: 50, page: $page, kind: "!special") {
        id
        malId
        name
        english
        japanese
        synonyms
        status
        season
        releasedOn {
          date
        }
        externalLinks {
          id
          kind
          url
        }
      }
    }
    """

    pprint.print(
        Platform.SHIKIMORI,
        Status.INFO,
        "Querying Shikimori upcoming/announced (status: anons)...",
    )
    animes = []
    page = 1
    while True:
        payload = {"query": query, "variables": {"page": page}}
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=15)
            if resp.status_code == 200:
                data = resp.json().get("data", {}).get("animes", [])
                if not data:
                    break
                animes.extend(data)
                pprint.print(
                    Platform.SHIKIMORI,
                    Status.INFO,
                    f"  Page {page}: fetched {len(data)} items",
                )
                if len(data) < 50:
                    break
                page += 1
            else:
                pprint.print(
                    Platform.SHIKIMORI,
                    Status.FAIL,
                    f"  Shikimori query failed with status {resp.status_code}",
                )
                break
        except Exception as e:
            pprint.print(
                Platform.SHIKIMORI,
                Status.FAIL,
                f"  Error querying Shikimori page {page}: {e}",
            )
            break

    pprint.print(
        Platform.SHIKIMORI,
        Status.INFO,
        f"  Total found: {len(animes)} announced shows in Shikimori",
    )
    return animes


def extract_ids_from_sources(sources):
    """Extract all database IDs from a list of source URLs"""
    ids = {}
    for url in sources:
        if "myanimelist.net/anime/" in url:
            val = extract_id_from_url(url, r"anime/(\d+)")
            if val:
                ids["mal"] = val
        elif "anilist.co/anime/" in url:
            val = extract_id_from_url(url, r"anime/(\d+)")
            if val:
                ids["anilist"] = val
        elif "anidb.net/anime/" in url or "anidb.net/a" in url:
            val = extract_id_from_url(url, r"anime/(\d+)|/a(\d+)")
            if val:
                ids["anidb"] = val
        elif "kitsu.app/anime/" in url or "kitsu.io/anime/" in url:
            val = extract_id_from_url(url, r"anime/(\d+)|anime/([\w\-]+)")
            if val:
                ids["kitsu"] = val
        elif "livechart.me/anime/" in url:
            val = extract_id_from_url(url, r"anime/(\d+)")
            if val:
                ids["livechart"] = val
        elif "shikimori.one/animes/" in url or "shikimori.io/animes/" in url:
            val = extract_id_from_url(url, r"animes/(\d+)|animes/([\w\-]+)")
            if val:
                ids["shikimori"] = val
        elif "animenewsnetwork.com/" in url and "id=" in url:
            val = extract_id_from_url(url, r"id=(\d+)")
            if val:
                ids["ann"] = val
    return ids


def get_entry_id_strings(sources):
    """Get set of ID strings (e.g. 'mal:123') from sources list"""
    ids = extract_ids_from_sources(sources)
    id_strings = set()
    for name, val in ids.items():
        id_strings.add(f"{name}:{val}")
    return id_strings


def parse_date(date_str):
    """Parse various date formats into a datetime.date object. Returns (date, precision)"""
    if not date_str:
        return None, "none"

    date_str = date_str.strip()
    if "T" in date_str:
        date_str = date_str.split("T")[0]

    # YYYY-MM-DD
    match = re.match(r"^(\d{4})-(\d{2})-(\d{2})$", date_str)
    if match:
        try:
            return datetime.date(
                int(match.group(1)), int(match.group(2)), int(match.group(3))
            ), "day"
        except ValueError:
            pass

    # YYYY-MM
    match = re.match(r"^(\d{4})-(\d{2})$", date_str)
    if match:
        try:
            return datetime.date(int(match.group(1)), int(match.group(2)), 1), "month"
        except ValueError:
            pass

    # YYYY
    match = re.match(r"^(\d{4})$", date_str)
    if match:
        try:
            return datetime.date(int(match.group(1)), 1, 1), "year"
        except ValueError:
            pass

    return None, "none"


def titles_match_fuzzy(title1, synonyms1, title2, synonyms2):
    """Fuzzy match two sets of titles. Returns True if similarity is >= 80"""
    all1 = [title1] + synonyms1
    all2 = [title2] + synonyms2
    for t1 in all1:
        if not t1:
            continue
        for t2 in all2:
            if not t2:
                continue
            if fuzz.token_sort_ratio(t1.lower(), t2.lower()) >= 80:
                return True
    return False


def dates_or_seasons_match(entry1, entry2):
    """Compare seasons or start dates between two entries"""
    # Get seasons
    season1 = entry1.get("animeSeason", {})
    season2 = entry2.get("animeSeason", {})

    s1_name = season1.get("season", "TBA") or "TBA"
    s1_year = season1.get("year")
    s2_name = season2.get("season", "TBA") or "TBA"
    s2_year = season2.get("year")

    # Get release dates
    rd1 = entry1.get("releaseDate")
    rd2 = entry2.get("releaseDate")

    # Helper to check if date/season is completely missing
    has_date1 = rd1 is not None
    has_date2 = rd2 is not None
    has_season1 = s1_name != "TBA" and s1_year is not None
    has_season2 = s2_name != "TBA" and s2_year is not None

    # If one of them has absolutely no date or season info, they don't conflict, so they match!
    if not (has_date1 or has_season1) or not (has_date2 or has_season2):
        return True

    # If both have seasons, check if they match
    if has_season1 and has_season2:
        if s1_name.upper() == s2_name.upper() and s1_year == s2_year:
            return True

    # If both have dates, check if they match
    if has_date1 and has_date2:
        dt1, prec1 = parse_date(rd1)
        dt2, prec2 = parse_date(rd2)

        if dt1 and dt2:
            if prec1 == "day" and prec2 == "day":
                diff = abs((dt1 - dt2).days)
                if diff <= 1:
                    return True
            elif (prec1 in ("month", "day")) and (prec2 in ("month", "day")):
                if dt1.year == dt2.year and dt1.month == dt2.month:
                    return True
            elif prec1 == "year" or prec2 == "year":
                if dt1.year == dt2.year:
                    return True

    # If one has season and the other has date, we can estimate season of the date and compare
    if has_season1 and has_date2:
        dt2, prec2 = parse_date(rd2)
        if dt2:
            estimated_season = MONTH_TO_SEASON.get(dt2.month, "TBA").upper()
            if s1_name.upper() == estimated_season and s1_year == dt2.year:
                return True

    if has_season2 and has_date1:
        dt1, prec1 = parse_date(rd1)
        if dt1:
            estimated_season = MONTH_TO_SEASON.get(dt1.month, "TBA").upper()
            if s2_name.upper() == estimated_season and s2_year == dt1.year:
                return True

    return False


def merge_entries(existing, new_data):
    """Merge two AOD-like entries in place"""
    # Merge sources and sanitize
    existing["sources"] = sanitize_source_urls(
        existing.get("sources", []) + new_data.get("sources", [])
    )

    # Merge synonyms
    syns = set(existing.get("synonyms", []) + new_data.get("synonyms", []))
    existing["synonyms"] = list(syns)

    # Prefer non-TBA season/year if available
    curr_season = existing.get("animeSeason", {})
    new_season = new_data.get("animeSeason", {})
    if curr_season.get("season") == "TBA" and new_season.get("season") != "TBA":
        existing["animeSeason"] = new_season
    elif curr_season.get("year") is None and new_season.get("year") is not None:
        existing["animeSeason"] = new_season

    # Update status if new status is more specific/advanced
    status_priority = {"FINISHED": 3, "ONGOING": 2, "UPCOMING": 1, "UNKNOWN": 0}
    curr_status = existing.get("status", "UPCOMING")
    new_status = new_data.get("status", "UPCOMING")
    if status_priority.get(new_status, 0) > status_priority.get(curr_status, 0):
        existing["status"] = new_status

    # Merge releaseDate
    if not existing.get("releaseDate") and new_data.get("releaseDate"):
        existing["releaseDate"] = new_data["releaseDate"]


def main():
    aod_path = Path("database/raw/aod.json")
    output_path = Path("database/raw/sideload_future.json")

    # Get seasons range: winter {this.year - 1} to fall {this.year + 1}
    seasons = get_seasons_range()
    pprint.print(Platform.SYSTEM, Status.INFO, "Seasons range to crawl:")
    for s_name, s_year in seasons:
        pprint.print(
            Platform.SYSTEM, Status.INFO, f"  - {s_name.capitalize()} {s_year}"
        )
    pprint.print(Platform.SYSTEM, Status.INFO, "  - TBA (Unknown season)")

    # Scan AOD database for existing IDs to prevent duplicates/conflicts
    aod_id_strings = set()
    if aod_path.exists():
        pprint.print(
            Platform.ANIMEOFFLINEDATABASE,
            Status.INFO,
            "Scanning AOD database for existing IDs...",
        )
        try:
            with open(aod_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                for item in data.get("data", []):
                    aod_id_strings.update(get_entry_id_strings(item.get("sources", [])))
            pprint.print(
                Platform.ANIMEOFFLINEDATABASE,
                Status.INFO,
                f"  Found {len(aod_id_strings)} unique ID strings in AOD.",
            )
        except Exception as e:
            pprint.print(
                Platform.ANIMEOFFLINEDATABASE,
                Status.FAIL,
                f"  Error reading AOD IDs: {e}",
            )

    # Load existing sideloaded data (persistence)
    existing_sideload_entries = []
    if output_path.exists():
        pprint.print(
            Platform.SYSTEM,
            Status.INFO,
            f"Loading existing sideload data from {output_path}...",
        )
        try:
            with open(output_path, "r", encoding="utf-8") as f:
                existing_sideload_entries = json.load(f)
            pprint.print(
                Platform.SYSTEM,
                Status.INFO,
                f"  Loaded {len(existing_sideload_entries)} existing entries.",
            )
        except Exception as e:
            pprint.print(
                Platform.SYSTEM,
                Status.FAIL,
                f"  Failed to load existing sideload data: {e}",
            )

    # De-duplicate / merge existing sideload entries first
    deduplicated_sideload_entries = []
    for entry in existing_sideload_entries:
        entry_ids = get_entry_id_strings(entry.get("sources", []))

        # Try to match with an entry we already put in deduplicated_sideload_entries
        matched = None
        for existing in deduplicated_sideload_entries:
            existing_ids = get_entry_id_strings(existing.get("sources", []))
            # Match by IDs
            if entry_ids & existing_ids:
                matched = existing
                break
            # Match by fuzzy title + dates/seasons
            if titles_match_fuzzy(
                entry["title"],
                entry.get("synonyms", []),
                existing["title"],
                existing.get("synonyms", []),
            ):
                if dates_or_seasons_match(entry, existing):
                    matched = existing
                    break
        if matched:
            merge_entries(matched, entry)
        else:
            deduplicated_sideload_entries.append(entry)

    pprint.print(
        Platform.SYSTEM,
        Status.INFO,
        f"  De-duplicated sideload entries: reduced from {len(existing_sideload_entries)} to {len(deduplicated_sideload_entries)}",
    )

    # Filter out any sideload entries already officially present in AOD
    id_to_sideload_entry = {}
    filtered_sideload_entries = []
    for entry in deduplicated_sideload_entries:
        entry_ids = get_entry_id_strings(entry.get("sources", []))
        if entry_ids & aod_id_strings:
            # Already officially present in AOD, purge from sideload_future.json
            continue
        filtered_sideload_entries.append(entry)
        for id_str in entry_ids:
            id_to_sideload_entry[id_str] = entry
    pprint.print(
        Platform.ANIMEOFFLINEDATABASE,
        Status.INFO,
        f"  Retained {len(filtered_sideload_entries)} existing sideload entries after purging upstream AOD matches.",
    )

    # Step 1: Collect all LiveChart IDs
    lc_ids = []
    season_details = {}

    # Normal projected seasons
    for s_name, s_year in seasons:
        ids = fetch_livechart_season_ids(s_name, s_year)
        lc_ids.extend(ids)
        for anime_id in ids:
            season_details[anime_id] = (s_name, s_year)
        time.sleep(3)  # Delay to prevent 429

    # TBA season
    tba_ids = fetch_livechart_season_ids("tba")
    lc_ids.extend(tba_ids)
    for anime_id in tba_ids:
        season_details[anime_id] = ("tba", None)

    # De-duplicate LiveChart IDs
    lc_ids = list(set(lc_ids))

    # Step 2: Fetch LiveChart details
    lc_shows = fetch_livechart_details(lc_ids)

    # Step 3: Fetch Shikimori shows
    shiki_shows = []
    for s_name, s_year in seasons:
        shows = fetch_shikimori_seasonal(f"{s_name}_{s_year}")
        shiki_shows.extend(shows)

    # Also fetch all upcoming/announced shows from Shikimori (handles TBA/unknown season)
    anons_shows = fetch_shikimori_anons()
    shiki_shows.extend(anons_shows)

    # Step 4: Merge LiveChart shows into filtered sideload entries
    pprint.print(Platform.LIVECHART, Status.INFO, "Processing LiveChart shows...")
    lc_added = 0
    lc_merged = 0
    lc_skipped = 0
    for lc_id, show in lc_shows.items():
        database_id = show.get("databaseId")

        title = (
            show.get("romajiTitle")
            or show.get("englishTitle")
            or show.get("nativeTitle")
        )
        if not title:
            continue

        sources = [f"https://www.livechart.me/anime/{database_id}"]
        for field in [
            "malUrl",
            "anilistUrl",
            "anidbUrl",
            "kitsuUrl",
            "animePlanetUrl",
            "anisearchUrl",
            "annUrl",
        ]:
            u = normalize_url(show.get(field))
            if u:
                sources.append(u)

        s_name, s_year = season_details.get(str(database_id), ("spring", 2026))

        status_map = {
            "FINISHED": "FINISHED",
            "RELEASING": "ONGOING",
            "NOT_YET_RELEASED": "UPCOMING",
        }
        status = status_map.get(show.get("releaseStatus"), "UPCOMING")

        # Extract release date
        release_date = None
        start_date = show.get("startDate")
        if start_date:
            release_date = start_date.get("value")

        new_entry = {
            "title": title,
            "sources": sanitize_source_urls(sources),
            "type": "TV",
            "status": status,
            "animeSeason": {
                "season": s_name.upper(),
                "year": s_year if s_year else None,
            },
            "synonyms": show.get("alternativeTitles") or [],
            "releaseDate": release_date,
        }

        # Check if any ID overlaps with upstream AOD
        new_ids = get_entry_id_strings(new_entry["sources"])
        if new_ids & aod_id_strings:
            lc_skipped += 1
            continue

        # Check if matches any existing sideload entry by ID
        matched_entry = None
        for id_str in new_ids:
            if id_str in id_to_sideload_entry:
                matched_entry = id_to_sideload_entry[id_str]
                break

        # If no ID match, try fuzzy matching by title + date/season
        if not matched_entry:
            for entry in filtered_sideload_entries:
                if titles_match_fuzzy(
                    new_entry["title"],
                    new_entry.get("synonyms", []),
                    entry["title"],
                    entry.get("synonyms", []),
                ):
                    if dates_or_seasons_match(new_entry, entry):
                        matched_entry = entry
                        break

        if matched_entry:
            merge_entries(matched_entry, new_entry)
            for id_str in get_entry_id_strings(matched_entry["sources"]):
                id_to_sideload_entry[id_str] = matched_entry
            lc_merged += 1
        else:
            filtered_sideload_entries.append(new_entry)
            for id_str in new_ids:
                id_to_sideload_entry[id_str] = new_entry
            lc_added += 1

    pprint.print(
        Platform.LIVECHART,
        Status.INFO,
        f"LiveChart shows merged: added {lc_added}, merged {lc_merged}, skipped (already in AOD) {lc_skipped}",
    )

    # Step 5: Merge Shikimori shows into filtered sideload entries
    pprint.print(Platform.SHIKIMORI, Status.INFO, "Processing Shikimori shows...")
    shiki_added = 0
    shiki_merged = 0
    shiki_skipped = 0
    for show in shiki_shows:
        shiki_id = show.get("id")
        mal_id = show.get("malId")
        if mal_id:
            mal_id = int(mal_id)

        shiki_sources = [f"https://shikimori.one/animes/{shiki_id}"]
        if mal_id:
            shiki_sources.append(f"https://myanimelist.net/anime/{mal_id}")

        for link in show.get("externalLinks", []):
            url = normalize_url(link.get("url"))
            if url:
                shiki_sources.append(url)

        title = show.get("name") or show.get("english") or show.get("japanese")
        if not title:
            continue

        s_name = "tba"
        s_year = None
        if show.get("season"):
            parts = show.get("season").split("_")
            if len(parts) == 2:
                s_name = parts[0]
                try:
                    s_year = int(parts[1])
                except ValueError:
                    pass

        status_map = {"released": "FINISHED", "ongoing": "ONGOING", "anons": "UPCOMING"}
        status = status_map.get(show.get("status"), "UPCOMING")

        # Extract release date
        release_date = None
        released_on = show.get("releasedOn")
        if released_on:
            release_date = released_on.get("date")

        new_entry = {
            "title": title,
            "sources": sanitize_source_urls(shiki_sources),
            "type": "TV",
            "status": status,
            "animeSeason": {"season": s_name.upper(), "year": s_year},
            "synonyms": show.get("synonyms") or [],
            "releaseDate": release_date,
        }

        # Check if any ID overlaps with upstream AOD
        new_ids = get_entry_id_strings(new_entry["sources"])
        if new_ids & aod_id_strings:
            shiki_skipped += 1
            continue

        # Check if matches any existing sideload entry by ID
        matched_entry = None
        for id_str in new_ids:
            if id_str in id_to_sideload_entry:
                matched_entry = id_to_sideload_entry[id_str]
                break

        # If no ID match, try fuzzy matching by title + date/season
        if not matched_entry:
            for entry in filtered_sideload_entries:
                if titles_match_fuzzy(
                    new_entry["title"],
                    new_entry.get("synonyms", []),
                    entry["title"],
                    entry.get("synonyms", []),
                ):
                    if dates_or_seasons_match(new_entry, entry):
                        matched_entry = entry
                        break

        if matched_entry:
            merge_entries(matched_entry, new_entry)
            for id_str in get_entry_id_strings(matched_entry["sources"]):
                id_to_sideload_entry[id_str] = matched_entry
            shiki_merged += 1
        else:
            filtered_sideload_entries.append(new_entry)
            for id_str in new_ids:
                id_to_sideload_entry[id_str] = new_entry
            shiki_added += 1

    pprint.print(
        Platform.SHIKIMORI,
        Status.INFO,
        f"Shikimori shows merged: added {shiki_added}, merged {shiki_merged}, skipped (already in AOD) {shiki_skipped}",
    )

    # Step 6: Fetch and merge AniList shows
    anilist_shows = fetch_anilist_upcoming()
    pprint.print(Platform.ANILIST, Status.INFO, "Processing AniList shows...")
    al_added = 0
    al_merged = 0
    al_skipped = 0
    for show in anilist_shows:
        al_id = show.get("id")
        mal_id = show.get("idMal")

        al_sources = [f"https://anilist.co/anime/{al_id}"]
        if mal_id:
            al_sources.append(f"https://myanimelist.net/anime/{mal_id}")

        title = (
            show.get("title", {}).get("romaji")
            or show.get("title", {}).get("english")
            or show.get("title", {}).get("native")
        )
        if not title:
            continue

        synonyms = show.get("synonyms") or []
        for t_type in ["english", "native"]:
            val = show.get("title", {}).get(t_type)
            if val and val != title:
                synonyms.append(val)
        synonyms = list(set(synonyms))

        # Map format to type
        format_map = {
            "TV": "TV",
            "TV_SHORT": "TV",
            "MOVIE": "MOVIE",
            "SPECIAL": "SPECIAL",
            "OVA": "OVA",
            "ONA": "ONA",
            "MUSIC": "MUSIC",
        }
        media_type = format_map.get(show.get("format"), "TV")

        status_map = {
            "FINISHED": "FINISHED",
            "RELEASING": "ONGOING",
            "NOT_YET_RELEASED": "UPCOMING",
        }
        status = status_map.get(show.get("status"), "UPCOMING")

        # Season/year
        s_name = show.get("season") or "TBA"
        s_year = show.get("seasonYear")

        # Release date
        release_date = None
        sd = show.get("startDate", {})
        if sd.get("year") and sd.get("month") and sd.get("day"):
            release_date = f"{sd['year']:04d}-{sd['month']:02d}-{sd['day']:02d}"

        new_entry = {
            "title": title,
            "sources": sanitize_source_urls(al_sources),
            "type": media_type,
            "status": status,
            "animeSeason": {"season": s_name.upper(), "year": s_year},
            "synonyms": synonyms,
            "releaseDate": release_date,
        }

        # Check if any ID overlaps with upstream AOD
        new_ids = get_entry_id_strings(new_entry["sources"])
        if new_ids & aod_id_strings:
            al_skipped += 1
            continue

        # Check if matches any existing sideload entry by ID
        matched_entry = None
        for id_str in new_ids:
            if id_str in id_to_sideload_entry:
                matched_entry = id_to_sideload_entry[id_str]
                break

        # If no ID match, try fuzzy matching by title + date/season
        if not matched_entry:
            for entry in filtered_sideload_entries:
                if titles_match_fuzzy(
                    new_entry["title"],
                    new_entry.get("synonyms", []),
                    entry["title"],
                    entry.get("synonyms", []),
                ):
                    if dates_or_seasons_match(new_entry, entry):
                        matched_entry = entry
                        break

        if matched_entry:
            merge_entries(matched_entry, new_entry)
            for id_str in get_entry_id_strings(matched_entry["sources"]):
                id_to_sideload_entry[id_str] = matched_entry
            al_merged += 1
        else:
            filtered_sideload_entries.append(new_entry)
            for id_str in new_ids:
                id_to_sideload_entry[id_str] = new_entry
            al_added += 1

    pprint.print(
        Platform.ANILIST,
        Status.INFO,
        f"AniList shows merged: added {al_added}, merged {al_merged}, skipped (already in AOD) {al_skipped}",
    )

    # Step 7: Fetch and merge Kitsu shows
    kitsu_shows = fetch_kitsu_upcoming()
    pprint.print(Platform.KITSU, Status.INFO, "Processing Kitsu shows...")
    kt_added = 0
    kt_merged = 0
    kt_skipped = 0
    for show in kitsu_shows:
        slug = show.get("slug")

        kt_sources = [f"https://kitsu.app/anime/{slug}"]
        mappings = show.get("mappings", {}).get("nodes", []) or []
        for mapping in mappings:
            site = mapping.get("externalSite")
            ext_id = mapping.get("externalId")
            if not ext_id:
                continue

            if site == "MYANIMELIST_ANIME":
                kt_sources.append(f"https://myanimelist.net/anime/{ext_id}")
            elif site == "ANILIST_ANIME":
                kt_sources.append(f"https://anilist.co/anime/{ext_id}")
            elif site == "ANIDB":
                kt_sources.append(f"https://anidb.net/anime/{ext_id}")
            elif site == "THETVDB_SERIES":
                kt_sources.append(f"https://www.thetvdb.com/series/{ext_id}")
            elif site == "TRAKT":
                kt_sources.append(f"https://trakt.tv/shows/{ext_id}")

        title = show.get("titles", {}).get("canonical")
        if not title:
            continue

        synonyms = show.get("titles", {}).get("alternatives") or []
        for t_field in ["romanized", "original"]:
            val = show.get("titles", {}).get(t_field)
            if val and val != title:
                synonyms.append(val)
        localized = show.get("titles", {}).get("localized") or {}
        for lang, val in localized.items():
            if val and val != title:
                synonyms.append(val)
        synonyms = list(set(synonyms))

        subtype_map = {
            "TV": "TV",
            "MOVIE": "MOVIE",
            "OVA": "OVA",
            "ONA": "ONA",
            "SPECIAL": "SPECIAL",
            "MUSIC": "MUSIC",
        }
        media_type = subtype_map.get(show.get("subtype"), "TV")

        status_map = {
            "FINISHED": "FINISHED",
            "CURRENT": "ONGOING",
            "UPCOMING": "UPCOMING",
            "UNRELEASED": "UPCOMING",
            "TBA": "UPCOMING",
        }
        status = status_map.get(show.get("status"), "UPCOMING")

        season = show.get("season") or "TBA"
        start_date = show.get("startDate")
        year = None
        if start_date:
            try:
                year = int(start_date.split("-")[0])
            except (ValueError, IndexError):
                pass

        new_entry = {
            "title": title,
            "sources": sanitize_source_urls(kt_sources),
            "type": media_type,
            "status": status,
            "animeSeason": {"season": season.upper(), "year": year},
            "synonyms": synonyms,
            "releaseDate": start_date,
        }

        new_ids = get_entry_id_strings(new_entry["sources"])
        if new_ids & aod_id_strings:
            kt_skipped += 1
            continue

        matched_entry = None
        for id_str in new_ids:
            if id_str in id_to_sideload_entry:
                matched_entry = id_to_sideload_entry[id_str]
                break

        if not matched_entry:
            for entry in filtered_sideload_entries:
                if titles_match_fuzzy(
                    new_entry["title"],
                    new_entry.get("synonyms", []),
                    entry["title"],
                    entry.get("synonyms", []),
                ):
                    if dates_or_seasons_match(new_entry, entry):
                        matched_entry = entry
                        break

        if matched_entry:
            merge_entries(matched_entry, new_entry)
            for id_str in get_entry_id_strings(matched_entry["sources"]):
                id_to_sideload_entry[id_str] = matched_entry
            kt_merged += 1
        else:
            filtered_sideload_entries.append(new_entry)
            for id_str in new_ids:
                id_to_sideload_entry[id_str] = new_entry
            kt_added += 1

    pprint.print(
        Platform.KITSU,
        Status.INFO,
        f"Kitsu shows merged: added {kt_added}, merged {kt_merged}, skipped (already in AOD) {kt_skipped}",
    )

    # Step 8: Fetch and merge Annict shows
    # Load previous database generation to skip existing mappings
    mapped_mal_ids = set()
    mal_to_annict = {}
    import pandas as pd

    try:
        if Path("database/animeapi.tsv").exists():
            pprint.print(
                Platform.ANNICT,
                Status.INFO,
                "Loading previous database generation (animeapi.tsv) to detect missing mappings...",
            )
            existing_df = pd.read_csv("database/animeapi.tsv", sep="\t", dtype=str)
            if "myanimelist" in existing_df.columns:
                mapped_mal_ids = set(existing_df["myanimelist"].dropna())
                if "annict" in existing_df.columns:
                    temp_df = existing_df.dropna(subset=["myanimelist", "annict"])
                    for _, row in temp_df.iterrows():
                        mal_to_annict[row["myanimelist"]] = row["annict"]
    except Exception as e:
        pprint.print(
            Platform.ANNICT,
            Status.NOTICE,
            f"  Note: Could not load previous animeapi.tsv: {e}",
        )

    annict_shows = fetch_annict_upcoming()
    pprint.print(Platform.ANNICT, Status.INFO, "Processing Annict shows...")
    an_added = 0
    an_merged = 0
    an_skipped = 0
    for show in annict_shows:
        annict_id = show.get("annictId")
        mal_id = show.get("malAnimeId")
        shobocal_tid = show.get("syobocalTid")

        # Skip if this MAL -> Annict mapping is already recorded in the database
        if mal_id and str(mal_id) in mapped_mal_ids:
            if mal_to_annict.get(str(mal_id)) == str(annict_id):
                an_skipped += 1
                continue

        an_sources = [f"https://annict.com/works/{annict_id}"]
        if mal_id:
            an_sources.append(f"https://myanimelist.net/anime/{mal_id}")
        if shobocal_tid:
            an_sources.append(f"https://cal.syoboi.jp/tid/{shobocal_tid}")

        # Prefer Romanized or English titles as the main title for standard schema consistency
        title = show.get("titleRo") or show.get("titleEn") or show.get("title")
        if not title:
            continue

        synonyms = []
        for t_field in ["title", "titleEn", "titleRo"]:
            val = show.get(t_field)
            if val and val != title:
                synonyms.append(val)
        synonyms = list(set(synonyms))

        media_map = {
            "TV": "TV",
            "MOVIE": "MOVIE",
            "OVA": "OVA",
            "ONA": "ONA",
            "WEB": "ONA",
            "OTHER": "SPECIAL",
        }
        media_type = media_map.get(show.get("media"), "TV")

        # Map Annict seasons: WINTER, SPRING, SUMMER, AUTUMN
        season_map = {
            "WINTER": "WINTER",
            "SPRING": "SPRING",
            "SUMMER": "SUMMER",
            "AUTUMN": "FALL",
        }
        s_name = season_map.get(show.get("seasonName"), "TBA")
        s_year = show.get("seasonYear")

        new_entry = {
            "title": title,
            "sources": sanitize_source_urls(an_sources),
            "type": media_type,
            "status": "UPCOMING",
            "animeSeason": {"season": s_name, "year": s_year},
            "synonyms": synonyms,
        }

        new_ids = get_entry_id_strings(new_entry["sources"])
        if new_ids & aod_id_strings:
            an_skipped += 1
            continue

        matched_entry = None
        for id_str in new_ids:
            if id_str in id_to_sideload_entry:
                matched_entry = id_to_sideload_entry[id_str]
                break

        if not matched_entry:
            for entry in filtered_sideload_entries:
                if titles_match_fuzzy(
                    new_entry["title"],
                    new_entry.get("synonyms", []),
                    entry["title"],
                    entry.get("synonyms", []),
                ):
                    if dates_or_seasons_match(new_entry, entry):
                        matched_entry = entry
                        break

        if matched_entry:
            merge_entries(matched_entry, new_entry)
            for id_str in get_entry_id_strings(matched_entry["sources"]):
                id_to_sideload_entry[id_str] = matched_entry
            an_merged += 1
        else:
            filtered_sideload_entries.append(new_entry)
            for id_str in new_ids:
                id_to_sideload_entry[id_str] = new_entry
            an_added += 1

    pprint.print(
        Platform.ANNICT,
        Status.INFO,
        f"Annict shows merged: added {an_added}, merged {an_merged}, skipped (already in AOD) {an_skipped}",
    )

    # Format and sort entries to be git-diff friendly
    sorted_entries = []
    for entry in filtered_sideload_entries:
        title = sanitize_synonym(entry.get("title", ""))
        synonyms = [sanitize_synonym(s) for s in entry.get("synonyms", []) if s]
        # De-duplicate synonyms and remove if it equals the title
        synonyms = list(set(synonyms))
        if title in synonyms:
            synonyms.remove(title)

        sorted_entry = {
            "sources": sorted(entry.get("sources", [])),
            "title": title,
            "type": entry.get("type", "TV"),
            "status": entry.get("status", "UPCOMING"),
            "animeSeason": entry.get("animeSeason", {"season": "TBA", "year": None}),
            "synonyms": sorted(synonyms),
        }
        if "releaseDate" in entry and entry["releaseDate"]:
            sorted_entry["releaseDate"] = entry["releaseDate"]
        sorted_entries.append(sorted_entry)

    # Sort key: year (ascending, nulls/TBA at the end) -> season -> title
    def get_sort_key(entry):
        anime_season = entry.get("animeSeason", {})
        year = anime_season.get("year")
        if year is None:
            year = 9999

        season = (anime_season.get("season") or "TBA").lower()
        season_order = ["winter", "spring", "summer", "fall"]
        if season in season_order:
            season_idx = season_order.index(season)
        else:
            season_idx = 4

        title = entry.get("title", "").lower()
        return (year, season_idx, title)

    sorted_entries.sort(key=get_sort_key)

    pprint.print(
        Platform.SYSTEM,
        Status.INFO,
        f"Writing {len(sorted_entries)} de-duplicated, persistent sideload entries to {output_path}...",
    )
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(sorted_entries, f, indent=2)

    pprint.print(
        Platform.SYSTEM,
        Status.PASS,
        "Success! Persistent, duplicate-free sideload database written successfully.",
    )


def fetch_anilist_upcoming() -> list[dict[str, Any]]:
    """
    Query AniList GraphQL API for seasonal anime in the 3-year window
    (last year, this year, next year).
    """
    url = "https://graphql.anilist.co"
    query = """
    query ($season: MediaSeason, $seasonYear: Int, $page: Int, $perPage: Int) {
      Page (page: $page, perPage: $perPage) {
        pageInfo {
          hasNextPage
        }
        media (type: ANIME, season: $season, seasonYear: $seasonYear) {
          id
          idMal
          title {
            romaji
            english
            native
          }
          format
          status
          season
          seasonYear
          synonyms
          startDate {
            year
            month
            day
          }
        }
      }
    }
    """

    anilist_data: list[dict[str, Any]] = []
    this_year = datetime.datetime.now().year
    seasons = ["WINTER", "SPRING", "SUMMER", "FALL"]
    years = [this_year - 1, this_year, this_year + 1]

    headers = {
        "User-Agent": USER_AGENT,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    for year in years:
        for season in seasons:
            pprint.print(
                Platform.ANILIST,
                Status.INFO,
                f"Querying AniList GraphQL for {year} {season}...",
            )
            page = 1
            while True:
                variables = {
                    "season": season,
                    "seasonYear": year,
                    "page": page,
                    "perPage": 50,
                }
                try:
                    resp = requests.post(
                        url,
                        headers=headers,
                        json={"query": query, "variables": variables},
                        timeout=15,
                    )
                    if resp.status_code == 200:
                        page_data = resp.json().get("data", {}).get("Page", {})
                        media = page_data.get("media", [])
                        if not media:
                            break
                        anilist_data.extend(media)
                        pprint.print(
                            Platform.ANILIST,
                            Status.INFO,
                            f"  Page {page}: fetched {len(media)} items",
                        )
                        if not page_data.get("pageInfo", {}).get("hasNextPage"):
                            break
                        page += 1
                        time.sleep(1)
                    elif resp.status_code == 429:
                        retry_after = int(resp.headers.get("Retry-After", 5))
                        pprint.print(
                            Platform.ANILIST,
                            Status.WARN,
                            f"  Rate limited. Retrying after {retry_after} seconds...",
                        )
                        time.sleep(retry_after)
                    else:
                        pprint.print(
                            Platform.ANILIST,
                            Status.FAIL,
                            f"  AniList query failed with status {resp.status_code}",
                        )
                        break
                except Exception as e:
                    pprint.print(
                        Platform.ANILIST,
                        Status.FAIL,
                        f"  Error querying AniList {year} {season} page {page}: {e}",
                    )
                    break

    # Also fetch upcoming/announced with status to make sure we don't miss anything that doesn't have a season set yet
    pprint.print(
        Platform.ANILIST,
        Status.INFO,
        "Querying AniList GraphQL for remaining upcoming anime (no season/TBA)...",
    )
    tba_query = """
    query ($page: Int, $perPage: Int) {
      Page (page: $page, perPage: $perPage) {
        pageInfo {
          hasNextPage
        }
        media (type: ANIME, status: NOT_YET_RELEASED, season: null) {
          id
          idMal
          title {
            romaji
            english
            native
          }
          format
          status
          season
          seasonYear
          synonyms
          startDate {
            year
            month
            day
          }
        }
      }
    }
    """
    page = 1
    while True:
        variables = {"page": page, "perPage": 50}
        try:
            resp = requests.post(
                url,
                headers=headers,
                json={"query": tba_query, "variables": variables},
                timeout=15,
            )
            if resp.status_code == 200:
                page_data = resp.json().get("data", {}).get("Page", {})
                media = page_data.get("media", [])
                if not media:
                    break
                anilist_data.extend(media)
                pprint.print(
                    Platform.ANILIST,
                    Status.INFO,
                    f"  Page {page} (TBA): fetched {len(media)} items",
                )
                if not page_data.get("pageInfo", {}).get("hasNextPage"):
                    break
                page += 1
                time.sleep(1)
            elif resp.status_code == 429:
                retry_after = int(resp.headers.get("Retry-After", 5))
                time.sleep(retry_after)
            else:
                break
        except Exception:
            break

    # Deduplicate AniList data by media ID
    seen_ids = set()
    deduped_anilist_data = []
    for item in anilist_data:
        if item.get("id") not in seen_ids:
            seen_ids.add(item.get("id"))
            deduped_anilist_data.append(item)

    return deduped_anilist_data


def fetch_kitsu_upcoming_graphql() -> list[dict[str, Any]]:
    """
    Query Kitsu GraphQL API for upcoming and releasing anime with mapping data.
    """
    url = "https://kitsu.app/api/graphql"
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    query = """
    query GetSeasonal($status: ReleaseStatusEnum!, $first: Int!, $after: String) {
      animeByStatus(status: $status, first: $first, after: $after) {
        pageInfo {
          hasNextPage
          endCursor
        }
        nodes {
          id
          slug
          status
          season
          startDate
          subtype
          titles {
            canonical
            romanized
            original
            alternatives
            localized
          }
          mappings(first: 50) {
            nodes {
              externalSite
              externalId
            }
          }
        }
      }
    }
    """

    kitsu_data: list[dict[str, Any]] = []
    for status in ["CURRENT", "UPCOMING"]:
        pprint.print(
            Platform.KITSU,
            Status.INFO,
            f"Querying Kitsu GraphQL for status {status}...",
        )
        after = None
        while True:
            variables = {"status": status, "first": 50, "after": after}
            try:
                resp = requests.post(
                    url,
                    headers=headers,
                    json={"query": query, "variables": variables},
                    timeout=15,
                )
                if resp.status_code == 200:
                    data = resp.json().get("data", {}).get("animeByStatus", {})
                    nodes = data.get("nodes", [])
                    if not nodes:
                        break
                    kitsu_data.extend(nodes)
                    pprint.print(
                        Platform.KITSU,
                        Status.INFO,
                        f"  Fetched {len(nodes)} Kitsu items ({status})...",
                    )

                    page_info = data.get("pageInfo", {})
                    if not page_info.get("hasNextPage"):
                        break
                    after = page_info.get("endCursor")
                    time.sleep(1)
                elif resp.status_code == 429:
                    pprint.print(
                        Platform.KITSU,
                        Status.WARN,
                        "  Rate limited, retrying in 5 seconds...",
                    )
                    time.sleep(5)
                else:
                    pprint.print(
                        Platform.KITSU,
                        Status.FAIL,
                        f"  Kitsu query failed with status {resp.status_code}",
                    )
                    break
            except Exception as e:
                pprint.print(
                    Platform.KITSU, Status.FAIL, f"  Error querying Kitsu: {e}"
                )
                break
    return kitsu_data


def fetch_kitsu_upcoming() -> list[dict[str, Any]]:
    """
    Query Kitsu JSON:API (REST) for seasonal anime in the 3-year window
    (last year, this year, next year).
    """
    url = "https://kitsu.io/api/edge/anime"
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/vnd.api+json",
        "Content-Type": "application/vnd.api+json",
    }

    kitsu_data = []
    this_year = datetime.datetime.now().year
    seasons = ["winter", "spring", "summer", "fall"]
    years = [this_year - 1, this_year, this_year + 1]

    for year in years:
        for season in seasons:
            pprint.print(
                Platform.KITSU,
                Status.INFO,
                f"Querying Kitsu REST API for {year} {season}...",
            )
            offset = 0
            while True:
                params = {
                    "filter[season]": season,
                    "filter[seasonYear]": str(year),
                    "include": "mappings",
                    "page[limit]": 20,
                    "page[offset]": offset,
                }
                try:
                    resp = requests.get(url, headers=headers, params=params, timeout=15)
                    if resp.status_code == 200:
                        res_json = resp.json()
                        data = res_json.get("data", [])
                        if not data:
                            break

                        # Process mappings included in the response
                        included = res_json.get("included", [])
                        mappings_map = {}
                        for inc in included:
                            if inc.get("type") == "mappings":
                                mappings_map[inc.get("id")] = {
                                    "externalSite": inc.get("attributes", {}).get(
                                        "externalSite"
                                    ),
                                    "externalId": inc.get("attributes", {}).get(
                                        "externalId"
                                    ),
                                }

                        for item in data:
                            attributes = item.get("attributes", {})

                            item_mappings = []
                            rel_mappings = (
                                item.get("relationships", {})
                                .get("mappings", {})
                                .get("data", [])
                            )
                            for rm in rel_mappings:
                                m_id = rm.get("id")
                                if m_id in mappings_map:
                                    site = mappings_map[m_id]["externalSite"]
                                    if site == "myanimelist/anime":
                                        site_gq = "MYANIMELIST_ANIME"
                                    elif site == "anilist/anime":
                                        site_gq = "ANILIST_ANIME"
                                    elif site == "anidb":
                                        site_gq = "ANIDB"
                                    elif site == "thetvdb/series":
                                        site_gq = "THETVDB_SERIES"
                                    elif site == "thetvdb/season":
                                        site_gq = "THETVDB"
                                    elif site == "trakt":
                                        site_gq = "TRAKT"
                                    else:
                                        site_gq = site.upper()

                                    item_mappings.append(
                                        {
                                            "externalSite": site_gq,
                                            "externalId": mappings_map[m_id][
                                                "externalId"
                                            ],
                                        }
                                    )

                            kitsu_data.append(
                                {
                                    "id": item.get("id"),
                                    "slug": attributes.get("slug"),
                                    "status": attributes.get("status"),
                                    "season": attributes.get("season"),
                                    "startDate": attributes.get("startDate"),
                                    "subtype": attributes.get("subtype"),
                                    "titles": {
                                        "canonical": attributes.get("canonicalTitle"),
                                        "romanized": attributes.get("titles", {}).get(
                                            "en_jp"
                                        ),
                                        "original": attributes.get("titles", {}).get(
                                            "ja_jp"
                                        ),
                                        "alternatives": attributes.get(
                                            "abbreviatedTitles"
                                        )
                                        or [],
                                        "localized": attributes.get("titles") or {},
                                    },
                                    "mappings": {"nodes": item_mappings},
                                }
                            )

                        pprint.print(
                            Platform.KITSU,
                            Status.INFO,
                            f"  Offset {offset}: fetched {len(data)} items",
                        )
                        if len(data) < 20:
                            break
                        offset += 20
                        time.sleep(1)
                    elif resp.status_code == 429:
                        pprint.print(
                            Platform.KITSU,
                            Status.WARN,
                            "  Rate limited, waiting 5 seconds...",
                        )
                        time.sleep(5)
                    else:
                        pprint.print(
                            Platform.KITSU,
                            Status.FAIL,
                            f"  Kitsu REST API failed with status {resp.status_code}",
                        )
                        break
                except Exception as e:
                    pprint.print(
                        Platform.KITSU,
                        Status.FAIL,
                        f"  Error querying Kitsu REST for {year} {season}: {e}",
                    )
                    break

    # Also fetch current and upcoming via GraphQL status to ensure we catch TBA and unseasoned works
    pprint.print(
        Platform.KITSU,
        Status.INFO,
        "Querying Kitsu GraphQL for remaining current and upcoming anime (unseasoned)...",
    )
    gql_shows = fetch_kitsu_upcoming_graphql()
    kitsu_data.extend(gql_shows)

    # Deduplicate Kitsu data by ID
    seen_ids = set()
    deduped_kitsu_data = []
    for item in kitsu_data:
        if item.get("id") not in seen_ids:
            seen_ids.add(item.get("id"))
            deduped_kitsu_data.append(item)

    return deduped_kitsu_data


def fetch_annict_upcoming() -> list[dict[str, Any]]:
    """
    Query Annict GraphQL API for upcoming and current seasonal works.
    """
    token = os.environ.get("ANNICT_TOKEN")
    if not token:
        pprint.print(
            Platform.ANNICT,
            Status.INFO,
            "  Annict token not found in environment, skipping Annict sideload crawl.",
        )
        return []

    url = "https://api.annict.com/graphql"
    headers = {
        "User-Agent": USER_AGENT,
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    # Annict seasons format is YYYY-season (winter, spring, summer, autumn)
    this_year = datetime.datetime.now().year
    season_names_map = {
        "winter": "winter",
        "spring": "spring",
        "summer": "summer",
        "fall": "autumn",
    }

    seasons_to_query = []
    for y in [this_year - 1, this_year, this_year + 1]:
        for s in ["winter", "spring", "summer", "fall"]:
            seasons_to_query.append(f"{y}-{season_names_map[s]}")

    pprint.print(
        Platform.ANNICT,
        Status.INFO,
        f"Querying Annict GraphQL for seasons: {seasons_to_query}...",
    )

    query = """
    query GetSeasonal($seasons: [String!], $first: Int!, $after: String) {
      searchWorks(seasons: $seasons, first: $first, after: $after) {
        pageInfo {
          hasNextPage
          endCursor
        }
        nodes {
          id
          annictId
          malAnimeId
          syobocalTid
          title
          titleEn
          titleRo
          media
          seasonName
          seasonYear
          officialSiteUrl
          wikipediaUrl
        }
      }
    }
    """

    annict_data: list[dict[str, Any]] = []
    after = None
    while True:
        variables = {"seasons": seasons_to_query, "first": 50, "after": after}
        try:
            resp = requests.post(
                url,
                headers=headers,
                json={"query": query, "variables": variables},
                timeout=15,
            )
            if resp.status_code == 200:
                data = resp.json().get("data", {}).get("searchWorks", {})
                nodes = data.get("nodes", [])
                if not nodes:
                    break
                annict_data.extend(nodes)
                pprint.print(
                    Platform.ANNICT,
                    Status.INFO,
                    f"  Fetched {len(nodes)} Annict items...",
                )

                page_info = data.get("pageInfo", {})
                if not page_info.get("hasNextPage"):
                    break
                after = page_info.get("endCursor")
                time.sleep(1)
            elif resp.status_code == 429:
                pprint.print(
                    Platform.ANNICT,
                    Status.WARN,
                    "  Rate limited, retrying in 5 seconds...",
                )
                time.sleep(5)
            else:
                pprint.print(
                    Platform.ANNICT,
                    Status.FAIL,
                    f"  Annict query failed with status {resp.status_code}",
                )
                break
        except Exception as e:
            pprint.print(Platform.ANNICT, Status.FAIL, f"  Error querying Annict: {e}")
    return annict_data


if __name__ == "__main__":
    main()
