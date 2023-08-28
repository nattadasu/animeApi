# cSpell:disable
import datetime
import glob
import json as j
import math
import os
import re
import subprocess
import sys
import time

import requests as r
from bs4 import BeautifulSoup as bs
from dotenv import load_dotenv as ld
from slugify import slugify as slug

ld()

DISPATCH = os.getenv('GITHUB_EVENT_NAME')
USE_CACHE = os.getenv('USE_CACHE', False)
DO_NOT_PURGE = os.getenv('DO_NOT_PURGE', False)
try:
    if re.match(r'^(true|yes|y|1)$', USE_CACHE, re.IGNORECASE):
        USE_CACHE = True
    else:
        USE_CACHE = False
except TypeError:
    USE_CACHE = False
try:
    if re.match(r'^(true|yes|y|1)$', DO_NOT_PURGE, re.IGNORECASE):
        DO_NOT_PURGE = True
    else:
        DO_NOT_PURGE = False
except TypeError:
    DO_NOT_PURGE = False

if sys.version_info < (3, 9, 0):
    print('\033[31m[ERROR]\033[0m \033[90m[System]\033[0m Script only runnable for Python 3.9 or above...')
    exit(1)
else:
    print('\033[34m[INFO]\033[0m \033[90m[System]\033[0m Starting AnimeAPI Generator Script...')


def link(uri, label=None):
    if label is None:
        label = uri
    parameters = ''

    # OSC 8 ; params ; URI ST <name> OSC 8 ;; ST
    escape_mask = '\033]8;{};{}\033\\{}\033]8;;\033\\'

    return escape_mask.format(parameters, uri, label)


# Prepare Stuff:
oohead = {
    'authority': 'otakotaku.com',
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.9',
    'cookie': 'lang=id',
    'dnt': '1',
    'referer': 'https://otakotaku.com/anime/view/2623/paradox-live-the-animation',
    'sec-ch-ua': '"Chromium";v="110", "Not(A Brand";v="24", "Brave";v="110"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'sec-gpc': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
    'x-requested-with': 'XMLHttpRequest',
    'Content-Encoding': 'gzip'
}

kzHeaders = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br"
}

nmUri = r"https://notify\.moe/anime/"
malUri = r"https://myanimelist\.net/anime/"
lcUri = r"https://livechart\.me/anime/"
kiUri = r"https://kitsu\.io/anime/"
asUri = r"https://anisearch\.com/anime/"
apUri = r"https://anime\-planet\.com/anime/"
alUri = r"https://anilist\.co/anime/"
adbUri = r"https://anidb\.net/anime/"
annUri = f"https://(www.)?animenewsnetwork\.com/encyclopedia/anime\.php\?id="
bgmUri = r"https://bangumi\.tv/subject/"
dbUri = r"https://movie\.douban\.com/subject/"

# start time
start = time.time()


print('\033[35m[FETCH]\033[0m \033[90m[System]\033[0m Downloading data from sources...')

try:
    if USE_CACHE is True:
        raise Exception('Cache usage activated')
    print('\033[35m[FETCH]\033[0m \033[90m[@manami-project/anime-offline-database]\033[0m Downloading database (This may take a while)')
    aod = r.get("https://raw.githubusercontent.com/manami-project/anime-offline-database/master/anime-offline-database-minified.json")
    if aod.status_code == 200:
        with open('aod.raw.json', 'wb') as f:
            f.write(aod.content)
        aod = aod.json()
    else:
        raise Exception('Failed to download database')
    print('\033[34m[INFO]\033[0m \033[90m[@manami-project/anime-offline-database]\033[0m Successfully download the database')
except Exception as e:
    print('\033[31m[ERROR]\033[0m \033[90m[@manami-project/anime-offline-database]\033[0m Failed to download database, using old database')
    with open('aod.raw.json', 'r') as f:
        aod = j.load(f)

try:
    if USE_CACHE is True:
        raise Exception('Cache usage activated')
    print('\033[35m[FETCH]\033[0m \033[90m[@kawaiioverflow/arm]\033[0m Downloading database (This may take a while)')
    arm = r.get("https://raw.githubusercontent.com/kawaiioverflow/arm/master/arm.json")
    if arm.status_code == 200:
        with open('arm.raw.json', 'wb') as f:
            f.write(arm.content)
        armRaw = arm.json()
    else:
        raise Exception('Failed to download database')
    print('\033[34m[INFO]\033[0m \033[90m[@kawaiioverflow/arm]\033[0m Successfully download the database')
except Exception as e:
    print('\033[31m[ERROR]\033[0m \033[90m[@kawaiioverflow/arm]\033[0m Failed to download database, using old database')
    with open('arm.raw.json', 'r') as f:
        armRaw = j.load(f)

try:
    if USE_CACHE is True:
        raise Exception('Cache usage activated')
    print('\033[35m[FETCH]\033[0m \033[90m[@ryuuganime/aniTrakt-IndexParser]\033[0m Downloading database (This may take a while)')
    atiptv = r.get("https://raw.githubusercontent.com/ryuuganime/aniTrakt-IndexParser/main/db/tv.json")
    atipmovie = r.get("https://raw.githubusercontent.com/ryuuganime/aniTrakt-IndexParser/main/db/movies.json")
    if atiptv.status_code == 200 and atipmovie.status_code == 200:
        ati = []
        ati.extend(atiptv.json())
        ati.extend(atipmovie.json())
        with open('ati.raw.json', 'w', encoding="utf-8") as f:
            j.dump(ati, f, ensure_ascii=False)
        atipmovie = None
        atiptv = None
    else:
        raise Exception('Failed to download database')
    print('\033[34m[INFO]\033[0m \033[90m[@ryuuganime/aniTrakt-IndexParser]\033[0m Successfully download the database')
except Exception as e:
    print('\033[31m[ERROR]\033[0m \033[90m[@ryuuganime/aniTrakt-IndexParser]\033[0m Failed to download database, using old database')
    with open('ati.raw.json', 'r', encoding="utf-8") as f:
        ati = j.load(f)

try:
    if USE_CACHE is True:
        raise Exception('Cache usage activated')
    print('\033[35m[FETCH]\033[0m \033[90m[Silver-Yasha]\033[0m Downloading database (This may take a while)')
    sy = r.get("https://db.silveryasha.web.id/ajax/anime/dtanime")
    if sy.status_code == 200:
        with open("sy.raw.json", "wb") as f:
            f.write(sy.content)
        sy = sy.json()
    else:
        raise Exception('Failed to download database')
    print('\033[34m[INFO]\033[0m \033[90m[Silver-Yasha]\033[0m Successfully download the database')
except Exception as e:
    print('\033[31m[ERROR]\033[0m \033[90m[Silver-Yasha]\033[0m Failed to download database, using old database')
    with open('sy.raw.json', 'r') as f:
        sy = j.load(f)

# Start building data on otak otaku
try:
    if USE_CACHE is True:
        raise Exception('Cache usage activated')
    raw_file = r.get("https://raw.githubusercontent.com/nattadasu/animeApi/v3/database/raw/otakotaku.json")
    raw_file.raise_for_status()
    with open('oo.raw.json', 'w', encoding="utf-8") as f:
        j.dump(raw_file, f, ensure_ascii=False)

    print('\033[2K\r\033[34m[INFO]\033[0m \033[90m[Otak Otaku]\033[0m Successfully download the database')
except Exception as e:
    print('\033[31m[ERROR]\033[0m \033[90m[Otak Otaku]\033[0m Failed to fetch information, using old database')
    with open('oo.raw.json', 'r') as f:
        ooRaw = j.load(f)

# Start building for Kaize
try:
    if os.getenv("GITHUB_ACTIONS") == 'true':
        raise Exception('GitHub actions, skipping')
    if USE_CACHE is True:
        raise Exception('Cache usage activated')
    if (os.getenv("KAIZE_XSRF_TOKEN") is None) and (os.getenv("KAIZE_SESSION") is None) and (os.getenv("KAIZE_EMAIL") is None) and (os.getenv("KAIZE_PASSWORD") is None):
        raise Exception('Kaize login info does not available in .env file')
    print("\033[35m[FETCH]\033[0m \033[90m[Kaize]\033[0m Checking latest anime...")

    if (os.getenv("KAIZE_XSRF_TOKEN") is None) and (os.getenv("KAIZE_SESSION") is None):
        print("\033[1;31m[ERROR]\033[0m Kaize XSRF-TOKEN and Session not found in .env file\nUsing Kaize Email and Password to login, this is not recommended as it still missed a lot of information.")
        # On login page, grab the CSRF-TOKEN from the meta tag
        kzLgPg = r.get("https://kaize.io/login")
        soup = bs(kzLgPg.text, "html.parser")
        kzLoginHead = kzHeaders
        kzLoginHead['Cookie'] = kzLgPg.headers['Set-Cookie'].split(",")[0].split(";")[0] + "; " + kzLgPg.headers['Set-Cookie'].split(",")[2].split(";")[0]
        csrf = soup.find("meta", {"name": "csrf-token"})["content"]
        dataRaw = "_token=" + str(csrf) + "&email=" + os.getenv("KAIZE_EMAIL") + "&password=" + os.getenv("KAIZE_PASSWORD")

        # Login to Kaize
        kzLoginHead['Content-Type'] = 'application/x-www-form-urlencoded'
        login = r.post("https://kaize.io/login", data=dataRaw, headers=kzLoginHead)
        if (login.status_code == 302) or (login.status_code == 200):
            print("\033[1;34m[INFO]\033[0m Logged in to Kaize as " + os.getenv("KAIZE_EMAIL"))
        else:
            print("\033[1;31m[ERROR]\033[0m Failed to login to Kaize as " + os.getenv("KAIZE_EMAIL") + "\n        data might slightly incorrect")

        # on login, grab cookies, and add them to the headers
        kzHeaders['Cookie'] = login.headers['Set-Cookie'].split(",")[0].split(";")[0] + "; " + login.headers['Set-Cookie'].split(",")[2].split(";")[0]
    else:
        print("\033[34m[INFO]\033[0m \033[90m[Kaize]\033[0m XSRF-TOKEN and Session found in .env file, logging in.")
        kzHeaders['Cookie'] = "XSRF-TOKEN=" + os.getenv("KAIZE_XSRF_TOKEN") + "; kaize_session=" + os.getenv("KAIZE_SESSION")

    url = "https://kaize.io/anime/top"

    kzDat = []

    def getKaizeIndex(page: int = 1) -> dict:
        uri = url + "?page=" + str(page)
        res = r.get(uri, headers=kzHeaders)
        soup = bs(res.text, "html.parser")
        kzDat = soup.find_all("div", {"class": "anime-list-element"})
        result = []
        for i in kzDat:
            rank = i.find("div", {"class": "rank"}).text
            rank = rank.replace("#", "").strip()
            title = i.find("a", {"class": "name"}).text
            link = i.find("a", {"class": "name"})["href"]
            link = link.split("/")[-1]
            result.append({"rank": int(rank), "title": title, "slug": link})
        return result


    def kaize() -> dict:
        # check in hundredths
        kzp = 0
        pgHundreds = True
        pgTens = True
        pgOnes = True
        while pgHundreds is True:
            kzp = kzp
            print(
                f"\033[2K\r\033[34m[INFO]\033[0m \033[90m[Kaize]\033[0m Checking in hundreds, page " + str(kzp), end="")
            pgCheck = r.get(url + "?page=" + str(kzp), headers=kzHeaders)
            soup = bs(pgCheck.text, "html.parser")
            try:
                kzDat = soup.find_all("div", {"class": "anime-list-element"})
                if kzDat[0].find("div", {"class": "rank"}).text:
                    kzp += 100
                    # set sleep to 1 second to avoid rate limiting
                    time.sleep(3)
            except IndexError:
                kzpg = kzp - 100
                pgHundreds = False

        # Check in tenths
        kzp = kzpg + 10
        while pgTens is True:
            print(
                f"\033[2K\r\033[34m[INFO]\033[0m \033[90m[Kaize]\033[0m Checking in tens, page " + str(kzp), end="")
            pgCheck = r.get(url + "?page=" + str(kzp), headers=kzHeaders)
            soup = bs(pgCheck.text, "html.parser")
            try:
                kzDat = soup.find_all("div", {"class": "anime-list-element"})
                if kzDat[0].find("div", {"class": "rank"}).text:
                    kzp += 10
                    # set sleep to 1 second to avoid rate limiting
                    time.sleep(3)
            except IndexError:
                kzpg = kzp - 10
                pgTens = False

        # Check in ones
        kzp = kzpg + 1
        while pgOnes is True:
            print(
                f"\033[2K\r\033[34m[INFO]\033[0m \033[90m[Kaize]\033[0m Checking in ones, page " + str(kzp), end="")
            pgCheck = r.get(url + "?page=" + str(kzp), headers=kzHeaders)
            soup = bs(pgCheck.text, "html.parser")
            try:
                kzDat = soup.find_all("div", {"class": "anime-list-element"})
                if kzDat[0].find("div", {"class": "rank"}).text:
                    kzp += 1
                    # set sleep to 1 second to avoid rate limiting
                    time.sleep(3)
            except IndexError:
                kzpg = kzp - 1
                pgOnes = False
        print(
            f"\033[2K\r\033[1;34m[INFO]\033[0m \033[90m[Kaize]\033[0m Done checking, total pages: " + str(kzpg))

        for i in range(1, kzpg + 1):
            print(f"\033[2K\r\033[1;34m[INFO]\033[0m \033[90m[Kaize]\033[0m [{int((i/kzpg)*100)}%] Grabbing page " + str(
                i) + " of " + str(kzpg) + ", current total data indexed: " + str(len(kzDat)) + ", expected: " + str((i * 50) - 50) + "/" + str(kzpg*50) + "-ish", end="")
            iraw = getKaizeIndex(i)
            kzDat.extend(iraw)
        print("\033[2K\r\033[1;34m[INFO]\033[0m \033[90m[Kaize]\033[0m Done! Grabbed " +
            str(len(kzDat)) + " anime, or around " + str(math.ceil(len(kzDat)/50)) + " pages, expected " + str(kzpg))
        return kzDat

    kzUnmapped = kaize()
    with open('kz.unmapped.raw.json', 'w') as f:
        j.dump(kzUnmapped, f, ensure_ascii=False)
except Exception as e:
    print('\033[31m[ERROR]\033[0m \033[90m[Kaize]\033[0m Failed to fetch information, using old database')
    with open('kz.unmapped.raw.json', 'r') as f:
        kzUnmapped = j.load(f)

def mapKaize(kz: list):
    aodDict = {}
    aodSlug = {}
    aodFix = {}
    kzFix = []
    final = []
    unknown = []

    for i in aod['data']:
        for url in i['sources']:
            if re.match(adbUri, url):
                i['animePlanet'] = re.sub(adbUri, '', url)
            elif re.match(malUri, url):
                i['myAnimeList'] = re.sub(malUri, '', url)
        slugify:str = slug(i['title'])
        slugify = slugify.replace("-", "")
        i = {
            "title": i['title'],
            "myAnimeList": i['myAnimeList'] if 'myAnimeList' in i else None,
            "animePlanet": i['animePlanet'] if 'animePlanet' in i else None,
            "slugged": slugify
        }
        aodDict[i['title']] = i
        aodSlug[slugify] = i
        if i['animePlanet']:
            aodFix[i['animePlanet']] = i

    for i in kz:
        slugify:str = i['title']
        i['slugify'] = slug(slugify).replace('-', "")
        kzFix.append(i)

    # match
    for i in kzFix:
        dtim = {
            "title": i['title'],
            "kaize": i['slug'],
            "slugged": i['slugify']
        }
        if i['title'] in aodDict:
            aodDat = aodDict[i['title']]
            dtim['myanimelist'] = aodDat['myAnimeList']
            dtim['mapped_title'] = aodDat['title']
            final.append(dtim)
        elif i['slugify'] in aodSlug:
            aodDat = aodSlug[i['slugify']]
            dtim['myanimelist'] = aodDat['myAnimeList']
            dtim['mapped_title'] = aodDat['title']
            final.append(dtim)
        elif i['slug'] in aodFix:
            aodDat = aodFix[i['slug']]
            dtim['myanimelist'] = aodDat['myAnimeList']
            dtim['mapped_title'] = aodDat['title']
            final.append(dtim)
        else:
            unknown.append(dtim)

    # write to file
    with open("kz.mapped.raw.json", "w", encoding="utf-8") as f:
        j.dump(final, f, ensure_ascii=False)

    with open("kz.unknown.raw.json", "w", encoding="utf-8") as f:
        j.dump(unknown, f, ensure_ascii=False)

    # print stats

    idk = len(unknown)
    total = len(kz)
    indexed = total - idk

    print(f"\033[34m[INFO]\033[0m \033[90m[Kaize]\033[0m From {total} anime, {indexed} anime were indexed and {idk} anime were not indexed. ({int((indexed/total)*100)}% indexed, {int((idk/total)*100)}% not indexed)")
    return final

print("\033[32m[BUILD]\033[0m \033[90m[Kaize]\033[0m Mapping Kaize to AOD...")
kz = mapKaize(kzUnmapped)

print("\033[32m[BUILD]\033[0m \033[90m[Silver-Yasha]\033[0m Converting array to object...")

syFinal = {}
syUnknown = []
syI = 1
for i in sy['data']:
    print(
        f"\033[2K\r\033[34m[INFO]\033[0m \033[90m[Silver-Yasha]\033[0m [{syI}/{len(sy['data'])}] Processing {i['title']}", end='')
    if i['mal_id'] != None:
        syFinal[f"{i['mal_id']}"] = {
            'silveryasha': i['id'],
            'title': i['title'],
            'myanimelist': i['mal_id'],
            'title_alt': i['title_alt'],
        }
    else:
        syUnknown += [i]
    syI += 1

if len(syUnknown) > 0:
    with open('sy.unknown.json', 'w', encoding='utf-8') as f:
        f.write(j.dumps(syUnknown, indent=4))

print("\033[2K\r\033[32m[BUILD]\033[0m \033[90m[Otak Otaku]\033[0m Converting array to object...")

ooFinal = {}
ooUnknown = []
ooUnknownDict = {}
ooI = 1
for i in ooRaw:
    print(
        f"\033[2K\r\033[34m[INFO]\033[0m \033[90m[Otak Otaku]\033[0m [{ooI}/{len(ooRaw)}] Processing {i['title']}", end='')
    if i['myanimelist'] != None:
        ooFinal[f"{i['myanimelist']}"] = i
    else:
        ooSlug = slug(i['title'])
        ooUnknown += [i]
        ooUnknownDict[ooSlug] = i
    ooI += 1

if len(ooUnknown) > 0:
    with open('oo.unknown.raw.json', 'w', encoding='utf-8') as f:
        f.write(j.dumps(ooUnknown, indent=4))

print("\033[2K\r\033[32m[BUILD]\033[0m \033[90m[@kawaiioverflow/arm]\033[0m Converting array to object...")

armFinal = {}
armI = 1
for i in armRaw:
    try:
        hyper = link(
            f'https://myanimelist.net/anime/{i["mal_id"]}', f'[{i["mal_id"]}]')
        print(
            f"\033[2K\r\033[34m[INFO]\033[0m \033[90m[@kawaiioverflow/arm]\033[0m [{armI}/{len(armRaw)}] Processing {hyper}", end='')
        if i.get('mal_id', None):
            armFinal[f"mal/{i['mal_id']}"] = i
        elif i.get('anilist_id', None):
            armFinal[f"al/{i['anilist_id']}"] = i
        else:
            continue
    except:
        continue
    armI += 1

print("\033[2K\r\033[32m[BUILD]\033[0m \033[90m[@ryuuganime/aniTrakt-IndexParser]\033[0m Converting array to object...")
atiFinal = {}
atiI = 1
for i in ati:
    print(
        f"\033[2K\r\033[34m[INFO]\033[0m \033[90m[@ryuuganime/aniTrakt-IndexParser]\033[0m [{atiI}/{len(ati)}] Processing {i['title']}", end='')
    atiFinal[f"{i['mal_id']}"] = i
    atiI += 1

print("\033[2K\r\033[32m[BUILD]\033[0m \033[90m[Kaize]\033[0m Converting array to object...")
kzFinal = {}
kzFinalBySlug = {}
kzI = 1
for i in kz:
    print(
        f"\033[2K\r\033[34m[INFO]\033[0m \033[90m[Kaize]\033[0m [{kzI}/{len(kz)}] Processing {i['title']}", end='')
    kzFinal[i['myanimelist']] = i
    kzFinalBySlug[i['slugged']] = i
    kzI += 1

with open("kz.final.json", "w", encoding="utf-8") as f:
    j.dump(kzFinal, f, ensure_ascii=False)

with open("kz.final.json", "r", encoding="utf-8") as f:
    kzFinal = j.load(f)


# Check using git diff to see if there are any changes, if there are, continue, if not, exit 1
if (DISPATCH == 'workflow_dispatch') or DISPATCH is None:
    print("\033[2K\r\033[34m[INFO]\033[0m \033[90m[System]\033[0m You are running this script manually, skipping git diff check...")
else:
    print("\033[2K\r\033[34m[INFO]\033[0m \033[90m[System]\033[0m Checking for differences in files using git diff...")
    # Get a list of all *.raw.json files in the current directory
    file_list = glob.glob("*.raw.json")

    # Loop through the file list and check for differences using git diff
    differences_found = False
    for file in file_list:
        print(f"\033[34m[INFO]\033[0m \033[90m[System]\033[0m Checking for differences in {file}...")
        output = subprocess.check_output(['git', 'diff', file])
        if output:
            differences_found = True

    # If no differences were found in any of the files, exit the script
    if not differences_found:
        print("\033[31m[ERROR]\033[0m \033[90m[System]\033[0m No differences found in any of the files, exiting script...")
        exit(1)
    else:
        # continue with the rest of your script
        pass


# clear all variables to avoid overflow
ooRaw = None
sy = None
ooFeed = None
armRaw = None

# Main function

services = [
    "anidb",
    "anilist",
    "animenewsnetwork",
    "animeplanet",
    "anisearch",
    "annict",
    "bangumi",
    "douban",
    "imdb",
    "kaize",
    "kitsu",
    "livechart",
    "myanimelist",
    "nautiljon",
    "notify",
    "otakotaku",
    "shikimori",
    "shoboi",
    "silveryasha",
    "trakt",
]

if (DO_NOT_PURGE is False) or (DO_NOT_PURGE is None):
    print("\033[2K\r\033[34m[INFO]\033[0m \033[90m[System]\033[0m Cleaning up database...")

    for dir in services:
        try:
            print(
                "\033[2K\r\033[34m[INFO]\033[0m \033[90m[System]\033[0m Cleaning up database: " + dir, end="")
            # Create new dir and files to avoid errors
            os.makedirs(dir, exist_ok=True)
            # Cleanup directory
            if os.name == "nt":
                os.system(f"rmdir /s /q .\\{dir}")
                os.system(f"del /q \".\\{dir}.json\"")
                os.system(f"del /q \".\\{dir}().json\"")
            else:
                os.system(f"rm -rf ./{dir}")
                os.system(f"rm -f ./{dir}.json")
                os.system(f"rm -f \"./{dir}().json\"")
            # Create new dir
            os.makedirs(dir, exist_ok=True)
        except KeyboardInterrupt:
            print(
                f'\033[2K\r\033[31m[ERROR]\033[0m \033[90m[System]\033[0m Folder deletion loop stopped by user, exiting...')
            end = time.time()
            print(f'\n\n\033[34m[INFO]\033[0m \033[90m[Benchmark]\033[0m Total time: {end - start} seconds')
            exit(1)

    os.makedirs("trakt/shows", exist_ok=True)
    os.makedirs("trakt/movies", exist_ok=True)

    print("\033[2K\r\033[34m[INFO]\033[0m \033[90m[System]\033[0m Cleaning up directories completed")
else:
    print("\033[2K\r\033[34m[INFO]\033[0m \033[90m[System]\033[0m Skipping database cleanup...")

acArr = []
adbArr = []
alArr = []
apArr = []
asArr = []
kiArr = []
kzArr = []
lcArr = []
malArr = []
nmArr = []
ooArr = []
sbArr = []
shArr = []
syArr = []
trArr = []
index = []

print("======================================================")

print("\033[34m[INFO]\033[0m \033[90m[AnimeAPI]\033[0m Starting main loop, this will take some times to finish, as it depends on CPU and storage speed...")
total = len(aod['data'])
i = 1
try:
    for data in aod['data']:
        acId = None
        adbId = None
        alId = None
        apId = None
        asId = None
        kiId = None
        kzId = None
        lcId = None
        malId = None
        nmId = None
        ooId = None
        sbId = None
        syId = None
        trId = None
        trSeason = 0
        trType = None
        armFound = False
        timestamp = datetime.datetime.now(tz=datetime.timezone.utc).isoformat()
        title = data['title']
        titleSlug = slug(title)
        dashless = titleSlug.replace('-', '')
        print(
            f'\033[2K\r\033[32m[BUILD]\033[0m \033[90m[AnimeAPI]\033[0m \033[37m[{i}/{total}, {int((i / total) * 100)}%]\033[0m ' + title, end='')
        for url in data['sources']:
            if re.match(adbUri, url):
                adbId = re.sub(adbUri, '', url)
            elif re.match(alUri, url):
                alId = re.sub(alUri, '', url)
            elif re.match(apUri, url):
                apId = re.sub(apUri, '', url)
            elif re.match(asUri, url):
                asId = re.sub(asUri, '', url)
            elif re.match(kiUri, url):
                kiId = re.sub(kiUri, '', url)
            elif re.match(lcUri, url):
                lcId = re.sub(lcUri, '', url)
            elif re.match(malUri, url):
                malId = re.sub(malUri, '', url)
            elif re.match(nmUri, url):
                nmId = re.sub(nmUri, '', url)

        try:
            kzId = kzFinal[malId]["kaize"]
        except KeyError:
            kzId = None

        try:
            if kzId is None:
                kzId = kzFinalBySlug[dashless]["kaize"]
        except KeyError:
            kzId = None

        if malId is not None:
            syMalId = str(malId)
            ooMalId = str(malId)
            if syFinal.get(syMalId):
                syId = syFinal[syMalId]["silveryasha"]
            else:
                syId = None
            if ooFinal.get(ooMalId):
                ooId = ooFinal[ooMalId]["otakotaku"]
            elif ooUnknownDict.get(titleSlug):
                ooId = ooUnknownDict[titleSlug]["otakotaku"]
            else:
                pass

            if armFinal.get(f"mal/{malId}", None):
                acId = armFinal[f"mal/{malId}"].get("annict_id", None)
                sbId = armFinal[f"mal/{malId}"].get("syobocal_tid", None)
                armFound = True if acId is not None or sbId is not None else False

            if atiFinal.get(malId, None):
                trId = atiFinal[malId].get("trakt_id", None)
                trType = atiFinal[malId].get("type", None)
                trSeason = atiFinal[malId].get("season", None)
                if trType == "shows":
                    trIdFix = f"{trType}/{trId}/season/{trSeason}"
                else:
                    trIdFix = f"{trType}/{trId}"

        if (armFound is False) and (alId is not None):
            if armFinal.get(f"al/{malId}"):
                acId = armFinal[f"al/{alId}"].get("annict_id", None)
                sbId = armFinal[f"al/{alId}"].get("syobocal_tid", None)

        finalData = {
            "title": title,
            "anidb": int(adbId) if adbId is not None else None,
            "anilist": int(alId) if alId is not None else None,
            "animeplanet": str(apId) if apId is not None else None,
            "anisearch": int(asId) if asId is not None else None,
            "annict": int(acId) if acId is not None else None,
            "kaize": str(kzId) if kzId is not None else None,
            "kitsu": int(kiId) if kiId is not None else None,
            "livechart": int(lcId) if lcId is not None else None,
            "myanimelist": int(malId) if malId is not None else None,
            "notify": str(nmId) if nmId is not None else None,
            "otakotaku": ooId,
            "shikimori": int(malId) if malId is not None else None,
            "shoboi": int(sbId) if sbId is not None else None,
            "silveryasha": syId,
            "trakt": trId,
            "trakt_type": trType,
            "trakt_season": trSeason,
        }

        index += [finalData]
        if adbId is not None:
            adbArr += [finalData]
            with open(f"anidb/{adbId}", "w", encoding='utf-8') as f:
                f.write(j.dumps(finalData, ensure_ascii=False))
        if alId is not None:
            alArr += [finalData]
            with open(f"anilist/{alId}", "w", encoding='utf-8') as f:
                f.write(j.dumps(finalData, ensure_ascii=False))
        if apId is not None:
            apArr += [finalData]
            with open(f"animeplanet/{apId}", "w", encoding='utf-8') as f:
                f.write(j.dumps(finalData, ensure_ascii=False))
        if asId is not None:
            asArr += [finalData]
            with open(f"anisearch/{asId}", "w", encoding='utf-8') as f:
                f.write(j.dumps(finalData, ensure_ascii=False))
        if acId is not None:
            acArr += [finalData]
            with open(f"annict/{acId}", "w", encoding='utf-8') as f:
                f.write(j.dumps(finalData, ensure_ascii=False))
        if kzId is not None:
            kzArr += [finalData]
            with open(f"kaize/{kzId}", "w", encoding='utf-8') as f:
                f.write(j.dumps(finalData, ensure_ascii=False))
        if kiId is not None:
            kiArr += [finalData]
            with open(f"kitsu/{kiId}", "w", encoding='utf-8') as f:
                f.write(j.dumps(finalData, ensure_ascii=False))
        if lcId is not None:
            lcArr += [finalData]
            with open(f"livechart/{lcId}", "w", encoding='utf-8') as f:
                f.write(j.dumps(finalData, ensure_ascii=False))
        if malId is not None:
            malArr += [finalData]
            with open(f"myanimelist/{malId}", "w", encoding='utf-8') as f:
                f.write(j.dumps(finalData, ensure_ascii=False))
            with open(f"shikimori/{malId}", "w", encoding='utf-8') as f:
                f.write(j.dumps(finalData, ensure_ascii=False))
        if nmId is not None:
            nmArr += [finalData]
            with open(f"notify/{nmId}", "w", encoding='utf-8') as f:
                f.write(j.dumps(finalData, ensure_ascii=False))
        if ooId is not None:
            ooArr += [finalData]
            with open(f"otakotaku/{ooId}", "w", encoding='utf-8') as f:
                f.write(j.dumps(finalData, ensure_ascii=False))
        if sbId is not None:
            sbArr += [finalData]
            with open(f"shoboi/{sbId}", "w", encoding='utf-8') as f:
                f.write(j.dumps(finalData, ensure_ascii=False))
        if syId is not None:
            syArr += [finalData]
            with open(f"silveryasha/{syId}", "w", encoding='utf-8') as f:
                f.write(j.dumps(finalData, ensure_ascii=False))
        if trId is not None:
            trArr += [finalData]
            if trType == "shows":
                os.makedirs(f"trakt/{trType}/{trId}/seasons/", exist_ok=True)
                with open(f"trakt/{trType}/{trId}/seasons/{trSeason}", "w", encoding='utf-8') as f:
                    f.write(j.dumps(finalData, ensure_ascii=False))
                if trSeason == 1:
                    with open(f"trakt/{trType}/{trId}/index.json", "w", encoding='utf-8') as f:
                        f.write(j.dumps(finalData, ensure_ascii=False))
            else:
                with open(f"trakt/{trType}/{trId}", "w", encoding='utf-8') as f:
                    f.write(j.dumps(finalData, ensure_ascii=False))
        i += 1
except KeyboardInterrupt:
    print(
        f'\033[2K\r\033[31m[ERROR]\033[0m \033[90m[System]\033[0m Main loop stopped by user, exiting...')
    end = time.time()
    print(f'\n\n\033[34m[INFO]\033[0m \033[90m[Benchmark]\033[0m Total time: {end - start} seconds')
    exit(1)
except Exception as e:
    print(f'\033[2K\r\033[31m[ERROR]\033[0m \033[90m[System]\033[0m Unknown error while processing anime: {title}, error: {e}')
    end = time.time()
    print(f'\n\n\033[34m[INFO]\033[0m \033[90m[Benchmark]\033[0m Total time: {end - start} seconds')
    exit(1)

print(f'\033[2K\r\033[34m[INFO]\033[0m \033[90m[System]\033[0m Saving data to files...')
with open("animeApi.json", "w", encoding='utf-8') as f:
    f.write(j.dumps(index, ensure_ascii=False))


acDict = {}
adbDict = {}
alDict = {}
apDict = {}
asDict = {}
kiDict = {}
kzDict = {}
lcDict = {}
malDict = {}
nmDict = {}
ooDict = {}
sbDict = {}
syDict = {}
trDict = {}


print(f'\033[34m[INFO]\033[0m \033[90m[System]\033[0m Exporting AniDB...')
with open("anidb().json", "w", encoding='utf-8') as f:
    f.write(j.dumps(adbArr, ensure_ascii=False))
for i in adbArr:
    adbDict[i["anidb"]] = i
with open("anidb.json", "w", encoding='utf-8') as f:
    f.write(j.dumps(adbDict, ensure_ascii=False))
adbDict = {}

print(f'\033[34m[INFO]\033[0m \033[90m[System]\033[0m Exporting AniList...')
with open("anilist().json", "w", encoding='utf-8') as f:
    f.write(j.dumps(alArr, ensure_ascii=False))
for i in alArr:
    alDict[i["anilist"]] = i
with open("anilist.json", "w", encoding='utf-8') as f:
    f.write(j.dumps(alDict, ensure_ascii=False))
alDict = {}

print(f'\033[34m[INFO]\033[0m \033[90m[System]\033[0m Exporting Anime-Planet...')
with open("animeplanet().json", "w", encoding='utf-8') as f:
    f.write(j.dumps(apArr, ensure_ascii=False))
for i in apArr:
    apDict[i["animeplanet"]] = i
with open("animeplanet.json", "w", encoding='utf-8') as f:
    f.write(j.dumps(apDict, ensure_ascii=False))
apDict = {}

print(f'\033[34m[INFO]\033[0m \033[90m[System]\033[0m Exporting aniSearch...')
with open("anisearch().json", "w", encoding='utf-8') as f:
    f.write(j.dumps(asArr, ensure_ascii=False))
for i in asArr:
    asDict[i["anisearch"]] = i
with open("anisearch.json", "w", encoding='utf-8') as f:
    f.write(j.dumps(asDict, ensure_ascii=False))
asDict = {}

print(f"\033[34m[INFO]\033[0m \033[90m[System]\033[0m Exporting Annict...")
with open("annict().json", "w", encoding='utf-8') as f:
    f.write(j.dumps(acArr, ensure_ascii=False))
for i in acArr:
    acDict[i["annict"]] = i
with open("annict.json", "w", encoding='utf-8') as f:
    f.write(j.dumps(acDict, ensure_ascii=False))
acDict = {}

print(f'\033[34m[INFO]\033[0m \033[90m[System]\033[0m Exporting Kaize...')
with open("kaize().json", "w", encoding='utf-8') as f:
    f.write(j.dumps(kzArr, ensure_ascii=False))
for i in kzArr:
    kzDict[i["kaize"]] = i
with open("kaize.json", "w", encoding='utf-8') as f:
    f.write(j.dumps(kzDict, ensure_ascii=False))
kzDict = {}

print(f'\033[34m[INFO]\033[0m \033[90m[System]\033[0m Exporting Kitsu...')
with open("kitsu().json", "w", encoding='utf-8') as f:
    f.write(j.dumps(kiArr, ensure_ascii=False))
for i in kiArr:
    kiDict[i["kitsu"]] = i
with open("kitsu.json", "w", encoding='utf-8') as f:
    f.write(j.dumps(kiDict, ensure_ascii=False))
kiDict = {}

print(f'\033[34m[INFO]\033[0m \033[90m[System]\033[0m Exporting LiveChart...')
with open("livechart().json", "w", encoding='utf-8') as f:
    f.write(j.dumps(lcArr, ensure_ascii=False))
for i in lcArr:
    lcDict[i["livechart"]] = i
with open("livechart.json", "w", encoding='utf-8') as f:
    f.write(j.dumps(lcDict, ensure_ascii=False))
lcDict = {}

print(f'\033[34m[INFO]\033[0m \033[90m[System]\033[0m Exporting MyAnimeList...')
with open("myanimelist().json", "w", encoding='utf-8') as f:
    f.write(j.dumps(malArr, ensure_ascii=False))
for i in malArr:
    malDict[i["myanimelist"]] = i
with open("myanimelist.json", "w", encoding='utf-8') as f:
    f.write(j.dumps(malDict, ensure_ascii=False))

print(f'\033[34m[INFO]\033[0m \033[90m[System]\033[0m Exporting Notify.moe...')
with open("notify().json", "w", encoding='utf-8') as f:
    f.write(j.dumps(nmArr, ensure_ascii=False))
for i in nmArr:
    nmDict[i["notify"]] = i
with open("notify.json", "w", encoding='utf-8') as f:
    f.write(j.dumps(nmDict, ensure_ascii=False))
nmDict = {}

print(f'\033[34m[INFO]\033[0m \033[90m[System]\033[0m Exporting Otak Otaku...')
with open("otakotaku().json", "w", encoding='utf-8') as f:
    f.write(j.dumps(ooArr, ensure_ascii=False))
for i in ooArr:
    ooDict[i["otakotaku"]] = i
with open("otakotaku.json", "w", encoding='utf-8') as f:
    f.write(j.dumps(ooDict, ensure_ascii=False))
ooDict = {}

print(f'\033[34m[INFO]\033[0m \033[90m[System]\033[0m Exporting Shikimori...')
# Duplicate MyAnimeList JSON files as Shikimori
if os.name == "nt":
    os.system("copy myanimelist.json shikimori.json")
    os.system("copy myanimelist().json shikimori().json")
else:
    os.system("cp myanimelist.json shikimori.json")
    os.system("cp myanimelist\\(\\).json shikimori\\(\\).json")

print(f'\033[34m[INFO]\033[0m \033[90m[System]\033[0m Exporting Shoboi Calendar...')
with open("shoboi().json", "w", encoding='utf-8') as f:
    f.write(j.dumps(sbArr, ensure_ascii=False))
for i in sbArr:
    sbDict[i["shoboi"]] = i
with open("shoboi.json", "w", encoding='utf-8') as f:
    f.write(j.dumps(sbDict, ensure_ascii=False))
sbDict = {}

print(f'\033[34m[INFO]\033[0m \033[90m[System]\033[0m Exporting Silveryasha...')
with open("silveryasha().json", "w", encoding='utf-8') as f:
    f.write(j.dumps(syArr, ensure_ascii=False))
for i in syArr:
    syDict[i["silveryasha"]] = i
with open("silveryasha.json", "w", encoding='utf-8') as f:
    f.write(j.dumps(syDict, ensure_ascii=False))
syDict = {}

print(f'\033[34m[INFO]\033[0m \033[90m[System]\033[0m Exporting Trakt...')
with open("trakt().json", "w", encoding='utf-8') as f:
    f.write(j.dumps(trArr, ensure_ascii=False))
for i in trArr:
    if i['trakt_type'] == "movies":
        trDict[f"{i['trakt_type']}/{i['trakt']}"] = i
    elif i['trakt_type'] == "shows":
        if i['trakt_season'] == 1:
            trDict[f"{i['trakt_type']}/{i['trakt']}"] = i
        trDict[f"{i['trakt_type']}/{i['trakt']}/season/{i['trakt_season']}"] = i
with open("trakt.json", "w", encoding='utf-8') as f:
    f.write(j.dumps(trDict, ensure_ascii=False))
trDict = {}

print(f'\033[34m[INFO]\033[0m \033[90m[System]\033[0m Create updated file...')
updated = f"Updated on {datetime.datetime.now(tz=datetime.timezone.utc).strftime('%m/%d/%Y %H:%M:%S')} UTC"
with open("updated", "w", encoding='utf-8') as f:
    f.write(updated)

print(f"""\033[34m[INFO]\033[0m \033[90m[Statistic]\033[0m \033[1;32mMapping completed!\033[0m
                   \033[1mTotal anime        \033[0m: {len(index)}
                   \033[1mUpdated on\033[90m.........\033[0m: {updated.replace('Updated on ','')}
                   \033[1maniDB              \033[0m: {len(adbArr)}
                   \033[1mAniList\033[90m............\033[0m: {len(alArr)}
                   \033[1mAnime-Planet       \033[0m: {len(apArr)}
                   \033[1mAnime News Network\033[90m.\033[0m: 0 (\033[3;90mNot yet implemented\033[0m)
                   \033[1maniSearch          \033[0m: {len(asArr)}
                   \033[1mAnnict\033[90m.............\033[0m: {len(acArr)}
                   \033[1mBangumi            \033[0m: 0 (\033[3;90mNot yet implemented\033[0m)
                   \033[1mDouban\033[90m.............\033[0m: 0 (\033[3;90mNot yet implemented\033[0m)
                   \033[1mIMDb               \033[0m: 0 (\033[3;90mNot yet implemented\033[0m)
                   \033[1mKaize\033[90m..............\033[0m: {len(kzArr)}
                   \033[1mKitsu              \033[0m: {len(kiArr)}
                   \033[1mLiveChart\033[90m..........\033[0m: {len(lcArr)}
                   \033[1mMyAnimeList        \033[0m: {len(malArr)}
                   \033[1mNautiljon\033[90m..........\033[0m: 0 (\033[3;90mNot yet implemented\033[0m)
                   \033[1mNotify.moe         \033[0m: {len(nmArr)}
                   \033[1mOtak Otaku\033[90m.........\033[0m: {len(ooArr)}
                   \033[1mShikimori          \033[0m: {len(malArr)}
                   \033[1mShoboi Calendar\033[90m....\033[0m: {len(sbArr)}
                   \033[1mSilverYasha        \033[0m: {len(syArr)}
                   \033[1mTrakt\033[90m..............\033[0m: {len(trArr)}
""")

# Save as markdown

md = """<!-- omit in toc -->
# nattadasu's Mock REST API for Anime (AnimeAPI)

<!-- DO NOT EDIT THIS FILE, IT IS AUTO-GENERATED FROM MAIN.PY -->

<!-- omit in toc -->
## Table of Contents

* [About the project](#about-the-project)
* [Supported Providers](#supported-providers)
* [Statistics](#statistics)
* [Returned Value](#returned-value)
* [Usage](#usage)
  * [Get all items in Array](#get-all-items-in-array)
  * [Get All ID in Object/Dictionary format of each provider](#get-all-id-in-objectdictionary-format-of-each-provider)
  * [Get All ID in Array/List format of each provider](#get-all-id-in-arraylist-format-of-each-provider)
  * [Get a relation of ID to title](#get-a-relation-of-id-to-title)
    * [Provider exclusive rules](#provider-exclusive-rules)
      * [Shikimori](#shikimori)
      * [Trakt](#trakt)
* [Repository Files](#repository-files)
* [Acknowledgements](#acknowledgements)

## About the project

This is a mock REST API by utilizing GitHub Pages to host, GitHub Actions to
automate, and Python for backend.

## Supported Providers

- [x] [aniDb](https://anidb.net/)
- [x] [AniList](https://anilist.co/)
- [x] [Anime-Planet](https://www.anime-planet.com/)
- [x] [aniSearch](https://anisearch.com/)
- [x] [Annict](https://en.annict.com/)
- [x] [Kaize][kz]
- [x] [Kitsu](https://kitsu.io/)
- [x] [LiveChart](https://livechart.me/)
- [x] [MyAnimeList](https://myanimelist.net/)
- [x] [Notify](https://notify.moe/)
- [x] [Otak Otaku][oo]
- [x] [Shikimori](https://shikimori.one/) (uses MyAnimeList ID)
- [x] [Shoboi Calendar](https://cal.syoboi.jp/)
- [x] [Silver-Yasha DB Tontonan Indonesia][sy]
- [x] [Trakt](https://trakt.tv/)"""

md += f"""

## Statistics

This API has been updated on {updated.replace('Updated on ','')}, with a total of **{len(index)}** titles indexed.

|              Provider |     Code      | Count  |
| --------------------: | :-----------: | :----- |
|                 aniDb |    `anidb`    | {len(adbArr)} |
|               AniList |   `anilist`   | {len(alArr)} |
|          Anime-Planet | `animeplanet` | {len(apArr)} |
|             aniSearch |  `anisearch`  | {len(asArr)} |
|                Annict |   `annict`    | {len(acArr)} |
|                 Kaize |    `kaize`    | {len(kzArr)} |
|                 Kitsu |    `kitsu`    | {len(kiArr)} |
|             LiveChart |  `livechart`  | {len(lcArr)} |
|           MyAnimeList | `myanimelist` | {len(malArr)} |
|                Notify |    `notify`   | {len(nmArr)} |
|            Otak Otaku |  `otakotaku`  | {len(ooArr)} |
|             Shikimori |  `shikimori`  | {len(malArr)} |
|       Shoboi Calendar |    `shoboi`   | {len(sbArr)} |
| DB Tontonan Indonesia | `silveryasha` | {len(syArr)} |
|                 Trakt |    `trakt`    | {len(trArr)} |"""

md += """

## Returned Value

```ts
type StringNull = string | null;
type NumberNull = number | null;
type TraktType = "movies" | "shows" | null;

interface Anime = {
    title:            string;
    anidb:        NumberNull;
    anilist:      NumberNull;
    animeplanet:  StringNull;
    anisearch:    NumberNull;
    annict:       NumberNull;
    kaize:        StringNull;
    kitsu:        NumberNull; // Kitsu ID, slug is not supported
    livechart:    NumberNull;
    myanimelist:  NumberNull;
    notify:       StringNull;
    otakotaku:    NumberNull;
    shikimori:    NumberNull;
    shoboi:       NumberNull;
    silveryasha:  NumberNull;
    trakt:        NumberNull; // Trakt ID, slug is currently not supported
    trakt_type:    TraktType;
    trakt_season: NumberNull;
}

// Array/List format
type AnimeList = Anime[];

// Object/Dictionary format
type AnimeObject = {
    [key: string]: Anime;
}
```

Or, in Python >= 3.10:

```py
from enum import Enum
from typing import List, Dict, Literal

StringNull = str | None
NumberNull = int | None

TraktType = Literal["shows", "movies"] | None

@dataclass
class Anime:
    title:               str
    anidb:        NumberNull
    anilist:      NumberNull
    animeplanet:  StringNull  # Slug based
    anisearch:    NumberNull
    annict:       NumberNull
    kaize:        StringNull  # Slug based
    kitsu:        NumberNull  # Kitsu ID, slug is not supported
    livechart:    NumberNull
    myanimelist:  NumberNull
    notify:       StringNull  # Base64 based
    otakotaku:    NumberNull
    shikimori:    NumberNull
    shoboi:       NumberNull
    silveryasha:  NumberNull
    trakt:        NumberNull  # Trakt ID, slug is currently not supported
    trakt_type:    TraktType
    trakt_season: NumberNull

# Array/List format
anime_list = List[Anime]

# Object/Dictionary format
anime_object = Dict[str, Anime]
```

Or, in old-plain JSON:

```jsonc
"$Anime": {
    "title": "string",
    "anidb": 0,
    "anilist": 0,
    "animeplanet": "string",
    "anisearch": 0,
    "annict": 0,
    "kaize": "string",
    "kitsu": 0,
    "livechart": 0,
    "myanimelist": 0,
    "notify": "string",
    "otakotaku": 0,
    "shikimori": 0,
    "shoboi": 0,
    "silveryasha": 0,
    "trakt": 0,
    "trakt_type": "string(shows|movies)",
    "trakt_season": 0
}

// Array/List format
["$Anime"]

// Object/Dictionary format
{
    "id": "$Anime"
}
```

All keys is always present, but the value can be `null` if service/provider
does not have the ID of the title, except for `title` key value, which will be
always present.

Example of `myanimelist/1`:

```json
"""

with open('myanimelist/1') as f:
    js = j.load(f)
    md += j.dumps(js, indent=4)

md += """
```

## Usage

To use this API, you can access the following endpoints:

```http
GET https://aniapi.nattadasu.my.id/
```

All requests must be `GET`, and response always will be in JSON format.

> **Warning**
>
> If an entry can not be found, the API will return `404` status code and GitHub
> Pages' default 404 page.

### Get all items in Array

```http
GET /animeApi.json
```

### Get All ID in Object/Dictionary format of each provider

> **Note**
>
> Use this endpoint as "cache"-like for your application, so you don't have to
> query the API for every title you want to get the ID, which is useful for
> offline indexer that already have the ID from supported providers.

```http
GET /<PROVIDER>.json
```

`<PROVIDER>` can be one of the following:

`anidb`, `anilist`, `animeplanet`, `anisearch`, `annict`, `kaize`, `kitsu`,
`livechart`, `myanimelist`, `notify`, `otakotaku`, `shikimori`,
`shoboi`, `silveryasha`, `trakt`

### Get All ID in Array/List format of each provider

```http
GET /<PROVIDER>().json
```

`<PROVIDER>` can be one of the following:

`anidb`, `anilist`, `animeplanet`, `anisearch`, `annict`, `kaize`, `kitsu`,
`livechart`, `myanimelist`, `notify`, `otakotaku`, `shikimori`,
`shoboi`, `silveryasha`, `trakt`

If your application unable to reach the endpoint, replace `()` to `%28%29`.

### Get a relation of ID to title

```http
GET /<PROVIDER>/<ID>
```

`<PROVIDER>` can be one of the following:

`anidb`, `anilist`, `animeplanet`, `anisearch`, `annict`, `kaize`, `kitsu`,
`livechart`, `myanimelist`, `notify`, `otakotaku`, `shikimori`,
`shoboi`, `silveryasha`, `trakt`

`<ID>` is the ID of the title in the provider.

#### Provider exclusive rules

##### Kitsu

`kitsu` ID must in numerical value. If your application obtained slug as ID
instead, you can resolve/convert it to ID using following Kitsu API endpoint:

```http
GET https://kitsu.io/api/edge/anime?filter[slug]=<ID>
```

##### Shikimori

`shikimori` IDs are basically the same as `myanimelist` IDs. If you get a
`404` status code, remove any alphabetical prefix from the ID and try again.

For example: `z218` -> `218`

##### Trakt

For `trakt` provider, the ID is in the format of `<TYPE>/<ID>` where `<TYPE>`
is either `movies` or `shows` and `<ID>` is the ID of the title in the provider.

An ID on Trakt must in numerical value. If your application obtained slug as ID
instead, you can resolve/convert it to ID using following Trakt API endpoint:

```http
GET https://api.trakt.tv/search/trakt/<ID>?type=<movie|show>
```

To get exact season mapping, append `/seasons/<SEASON>` to the end of the ID,
where `<SEASON>` is the season number of the title in the provider.

For example, to get the ID of `Mairimashita Iruma-kun` Season 3, you can use:

```http
GET https://aniapi.nattadasu.my.id/trakt/shows/152334/seasons/3
```

The response will be:

```json
"""

with open('trakt/shows/152334/seasons/3') as f:
    js = j.load(f)
    md += j.dumps(js, indent=4)

md += """
```

## Repository Files

This repository contains multiple cache files, alongside main files, which are:

- `.editorconfig`: EditorConfig file.
- `.gitattributes`: Git attributes file.
- `.gitignore`: Git ignore file.
- `animeApi.json`: All data in Array format.
- `aod.raw.json`: [Anime Offline Database][aod] raw data.
- `arm.raw.json`: [Anime Relations Mapping][koarm] raw data.
- `ati.raw.json`: [AniTrakt Index Parser][atip] raw data.
- `kz.mapped.raw.json`: [Kaize][kz] raw data, mapped to MyAnimeList ID.
- `kz.unknown.raw.json`: [Kaize][kz] raw data, with unknown MyAnimeList ID.
- `kz.unmapped.raw.json`: [Kaize][kz] (true) raw data.
- `oo.raw.json`: [Otak Otaku][oo] raw data.
- `oo.unknown.raw.json`: [Otak Otaku][oo] raw data, with unknown MyAnimeList ID.
- `README.md`: This file.
- `requirements.txt`: Python requirements file.
- `robots.txt`: Robots.txt file.
- `sy.raw.json`: [Silver-Yasha][sy] raw data.

## Acknowledgements

This project uses multiple sources to compile the data, including:

- [GitHub:kawaiioverflow/arm][koarm]
- [GitHub:manami-project/anime-offline-database][aod]
- [GitHub:ryuuganime/aniTrakt-IndexParser][atip], which an automatic parser of
  [AniTrakt](https://anitrakt.huere.net/) index page.
- [Kaize][kz]
- [Otak Otaku][oo]
- [Silver-Yasha][sy]

<!-- References -->
[aod]: https://github.com/manami-project/anime-offline-database
[atip]: https://github.com/ryuuganime/aniTrakt-IndexParser
[koarm]: https://github.com/kawaiioverflow/arm
[kz]: https://kaize.io/
[oo]: https://otakotaku.com/
[sy]: https://db.silveryasha.web.id/
"""

with open('README.md', 'w') as f:
    f.write(md)

end = time.time()
print(f'\033[34m[INFO]\033[0m \033[90m[Benchmark]\033[0m Total time: {end - start} seconds')
