# cSpell:disable
import datetime
import glob
import json as j
import os
import re
import subprocess
import sys
import time

import requests as r
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
    print('\033[35m[FETCH]\033[0m \033[90m[Silver-Yasha]\033[0m Downloading database from v3 (This may take a while)')
    sy = r.get("https://raw.githubusercontent.com/nattadasu/animeApi/v3/database/raw/silveryasha.json")
    if sy.status_code == 200:
        with open("sy.raw.json", "wb") as f:
            f.write(sy.content)
        sy = sy.json()
    else:
        sy.raise_for_status()
    print('\033[34m[INFO]\033[0m \033[90m[Silver-Yasha]\033[0m Successfully download the database')
except Exception as e:
    print('\033[31m[ERROR]\033[0m \033[90m[Silver-Yasha]\033[0m Failed to download database, using old database')
    with open('sy.raw.json', 'r') as f:
        sy = j.load(f)

# Start building data on otak otaku
try:
    if USE_CACHE is True:
        raise Exception('Cache usage activated')
    print('\033[35m[FETCH]\033[0m \033[90m[Otak Otaku]\033[0m Downloading database from v3 (This may take a while)')
    raw_file = r.get("https://raw.githubusercontent.com/nattadasu/animeApi/v3/database/raw/otakotaku.json")
    if raw_file.status_code == 200:
        raw_json = raw_file.json()
        with open('oo.raw.json', 'w', encoding="utf-8") as f:
            j.dump(raw_json, f, ensure_ascii=False)
    else:
        raw_file.raise_for_status()

    print('\033[2K\r\033[34m[INFO]\033[0m \033[90m[Otak Otaku]\033[0m Successfully download the database')
except Exception as e:
    print('\033[31m[ERROR]\033[0m \033[90m[Otak Otaku]\033[0m Failed to fetch information, using old database')
    with open('oo.raw.json', 'r', encoding="utf-8") as f:
        ooRaw = j.load(f)

# Start building for Kaize
try:
    if USE_CACHE is True:
        raise Exception('Cache usage activated')
    print('\033[35m[FETCH]\033[0m \033[90m[Kaize]\033[0m Downloading database from v3 (This may take a while)')
    kzUnmapped = r.get("https://raw.githubusercontent.com/nattadasu/animeApi/v3/database/raw/kaize.json")
    if kzUnmapped.status_code == 200:
        with open('kz.unmapped.raw.json', 'w') as f:
            j.dump(kzUnmapped.json(), f, ensure_ascii=False)
    else:
        kzUnmapped.raise_for_status()
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
    atiFinal[f"{i['mal_id']}"] = i
    atiI += 1

print("\033[2K\r\033[32m[BUILD]\033[0m \033[90m[Kaize]\033[0m Converting array to object...")
kzFinal = {}
kzFinalBySlug = {}
kzI = 1
for i in kz:
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

# Load README

with open("README.md", "r", encoding="utf-8") as file:
    md = file.read()

table = f"""
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
|                 Trakt |    `trakt`    | {len(trArr)} |
"""

readme = re.sub(
    r"<!-- statistic -->(.|\n)*<!-- \/statistic -->",
    f"<!-- statistic -->\n{table}<!-- /statistic -->",
    readme,
)

with open('myanimelist/1') as f:
    js = j.load(f)
    sample = j.dumps(js, indent=4)
    readme = re.sub(
        r"<!-- mal-1 -->(.|\n)*<!-- \/mal-1 -->",
        f"<!-- mal-1 -->\n```json\n{sample}\n```\n<!-- /mal-1 -->",
        readme,
    )

with open('trakt/shows/152334/seasons/3') as f:
    js = j.load(f)
    sample = j.dumps(js, indent=4)
    readme = re.sub(
        r"<!-- trakt-152334-3 -->(.|\n)*<!-- \/trakt-152334-3 -->",
        f"<!-- trakt-152334-3 -->\n```json\n{sample}\n```\n<!-- /trakt-152334-3 -->",
        readme,
    )

with open('README.md', 'w', encoding="utf-8") as file:
    file.write(readme)

end = time.time()
print(f'\033[34m[INFO]\033[0m \033[90m[Benchmark]\033[0m Total time: {end - start} seconds')
