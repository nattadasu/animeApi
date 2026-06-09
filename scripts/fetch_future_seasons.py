#!/usr/bin/env python3
# SPDX-License-Identifier: MIT

"""
Fetch future seasonal mapping data from LiveChart and Shikimori,
unify them, detect and pull missing historical MAL IDs from Hikka,
sanitize and normalize all source URLs, and format them as AOD-like entries.
"""

import datetime
import json
import re
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from thefuzz import fuzz

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

    print(f"Scraping LiveChart page: {url}")
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        if resp.status_code != 200:
            print(f"  LiveChart {slug} returned status: {resp.status_code}")
            return []

        soup = BeautifulSoup(resp.text, "html.parser")
        articles = soup.find_all("article", class_="anime")
        ids = []
        for a in articles:
            anime_id = a.get("data-anime-id")
            if anime_id:
                ids.append(anime_id)
        print(f"  Found {len(ids)} shows in LiveChart {slug}")
        return ids
    except Exception as e:
        print(f"  Error scraping LiveChart {slug}: {e}")
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
    print(f"Querying LiveChart GraphQL details for {len(ids)} shows...")

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
                print(
                    f"  Batch {i // batch_size + 1} GraphQL failed (status {resp.status_code})"
                )
        except Exception as e:
            print(f"  Error fetching batch {i // batch_size + 1}: {e}")

        # Add rate limit delay between batches to avoid jumpscaring them
        time.sleep(2)

    print(f"  Successfully fetched details for {len(results)} LiveChart shows.")
    return results


def fetch_shikimori_seasonal(season_slug):
    """Query Shikimori GraphQL API for seasonal anime"""
    url = "https://shikimori.io/api/graphql"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:151.0) Gecko/20100101 Firefox/151.0",
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

    print(f"Querying Shikimori seasonal GraphQL: {season_slug}")
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
                print(f"  Page {page}: fetched {len(data)} items")
                if len(data) < 50:
                    break
                page += 1
            else:
                print(f"  Shikimori query failed with status {resp.status_code}")
                break
        except Exception as e:
            print(f"  Error querying Shikimori page {page}: {e}")
            break

    print(f"  Total found: {len(animes)} shows in Shikimori season {season_slug}")
    return animes


def fetch_shikimori_anons():
    """Query Shikimori GraphQL API for all announced shows (handles TBA / unknown season)"""
    url = "https://shikimori.io/api/graphql"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:151.0) Gecko/20100101 Firefox/151.0",
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

    print("Querying Shikimori upcoming/announced (status: anons)...")
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
                print(f"  Page {page}: fetched {len(data)} items")
                if len(data) < 50:
                    break
                page += 1
            else:
                print(f"  Shikimori query failed with status {resp.status_code}")
                break
        except Exception as e:
            print(f"  Error querying Shikimori page {page}: {e}")
            break

    print(f"  Total found: {len(animes)} announced shows in Shikimori")
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
    print("Seasons range to crawl:")
    for s_name, s_year in seasons:
        print(f"  - {s_name.capitalize()} {s_year}")
    print("  - TBA (Unknown season)")

    # Scan AOD database for existing IDs to prevent duplicates/conflicts
    aod_id_strings = set()
    if aod_path.exists():
        print("Scanning AOD database for existing IDs...")
        try:
            with open(aod_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                for item in data.get("data", []):
                    aod_id_strings.update(get_entry_id_strings(item.get("sources", [])))
            print(f"  Found {len(aod_id_strings)} unique ID strings in AOD.")
        except Exception as e:
            print(f"  Error reading AOD IDs: {e}")

    # Load existing sideloaded data (persistence)
    existing_sideload_entries = []
    if output_path.exists():
        print(f"Loading existing sideload data from {output_path}...")
        try:
            with open(output_path, "r", encoding="utf-8") as f:
                existing_sideload_entries = json.load(f)
            print(f"  Loaded {len(existing_sideload_entries)} existing entries.")
        except Exception as e:
            print(f"  Failed to load existing sideload data: {e}")

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

    print(
        f"  De-duplicated sideload entries: reduced from {len(existing_sideload_entries)} to {len(deduplicated_sideload_entries)}"
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
    print(
        f"  Retained {len(filtered_sideload_entries)} existing sideload entries after purging upstream AOD matches."
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
    print("Processing LiveChart shows...")
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

    print(
        f"LiveChart shows merged: added {lc_added}, merged {lc_merged}, skipped (already in AOD) {lc_skipped}"
    )

    # Step 5: Merge Shikimori shows into filtered sideload entries
    print("Processing Shikimori shows...")
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

    print(
        f"Shikimori shows merged: added {shiki_added}, merged {shiki_merged}, skipped (already in AOD) {shiki_skipped}"
    )

    # Format and sort entries to be git-diff friendly
    sorted_entries = []
    for entry in filtered_sideload_entries:
        sorted_entry = {
            "sources": sorted(entry.get("sources", [])),
            "title": entry.get("title", ""),
            "type": entry.get("type", "TV"),
            "status": entry.get("status", "UPCOMING"),
            "animeSeason": entry.get("animeSeason", {"season": "TBA", "year": None}),
            "synonyms": sorted(entry.get("synonyms", [])),
        }
        if "releaseDate" in entry and entry["releaseDate"]:
            sorted_entry["releaseDate"] = entry["releaseDate"]
        sorted_entries.append(sorted_entry)

    sorted_entries.sort(key=lambda x: x.get("title", "").lower())

    print(
        f"Writing {len(sorted_entries)} de-duplicated, persistent sideload entries to {output_path}..."
    )
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(sorted_entries, f, indent=2)

    print("Success! Persistent, duplicate-free sideload database written successfully.")


if __name__ == "__main__":
    main()
