<!-- markdownlint-disable MD028 MD033 -->
<!-- omit in toc -->
# nattadasu's AnimeAPI RESTful API

AnimeAPI (also known as aniApi) is a RESTful API that provides anime relation
mapping across multiple anime databases. It mainly focuses on providing
relations between anime titles from different databases.

This project was derived on [anime-offline-database][aod] by [manami-project][mp]
and [arm] by [kawaiioverflow][ko], while adding support for more databases.

This project is primarily licensed under AGPL-3.0-only, unless otherwise stated.
Please read more information regarding using the API on your project in
[Why avoid using AnimeAPI?](#why-avoid-using-animeapi).

<!-- omit in toc -->
## Table of Contents

<details>
<summary>Click to expand</summary>

* [Why use AnimeAPI?](#why-use-animeapi)
* [Why Avoid Using AnimeAPI?](#why-avoid-using-animeapi)
* [Featured on](#featured-on)
  * [Libraries](#libraries)
  * [Projects, Apps, and Websites](#projects-apps-and-websites)
* [Supported Platforms and Aliases](#supported-platforms-and-aliases)
* [Statistic](#statistic)
* [Usage](#usage)
  * [Response Headers](#response-headers)
  * [Get status and statistics](#get-status-and-statistics)
  * [Get latency report](#get-latency-report)
  * [Get updated date and time](#get-updated-date-and-time)
  * [Get all items in Array (Master Array)](#get-all-items-in-array-master-array)
  * [Fetch all item as TSV (Tab Separated Values) file](#fetch-all-item-as-tsv-tab-separated-values-file)
  * [Get anime relation mapping data](#get-anime-relation-mapping-data)
    * [Provider exclusive rules](#provider-exclusive-rules)
      * [Kitsu](#kitsu)
      * [Letterboxd](#letterboxd)
      * [SIMKL](#simkl)
      * [Shikimori](#shikimori)
      * [The Movie DB](#the-movie-db)
      * [The TVDB](#the-tvdb)
      * [Trakt](#trakt)
  * [Redirect to provider's page](#redirect-to-providers-page)
    * [Redirect: Parameters](#redirect-parameters)
    * [Redirect: Response](#redirect-response)
      * [Recommended/verbose path format](#recommendedverbose-path-format)
      * [Short/aliased/alternative path format](#shortaliasedalternative-path-format)
      * [Provider with slash (`/`) in `mediaid`](#provider-with-slash--in-mediaid)
      * [Raw path format](#raw-path-format)
* [Schema](#schema)
  * [JSON Schema](#json-schema)
  * [TypeScript](#typescript)
  * [Python Dataclass](#python-dataclass)
* [Acknowledgements](#acknowledgements)

</details>

## Why use AnimeAPI?

Compared to other relation mapping API, AnimeAPI provides more databases yet
it's still easy to use. It also provides more data than other relation mapping
API, such as the anime title itself.

Also, AnimeAPI uses object/dictionary format instead of array/list for each
provider when you want to [get individual relation mapping data](#get-anime-relation-mapping-data).
This makes it easier and faster to get the data you want since the machine
doesn't need to iterate through the array/list to get the data you want,
although with the cost of larger repository size.

Below is the comparison between AnimeAPI and other relation mapping API.

<!-- markdownlint-disable MD013 MD060 -->

| Highlights                      | AnimeAPI                                                         | [ARM][arm]                  | [BQA][bq]          | [Hato][hato]              | [SIMKL][smk]            | [Trakt][trk] | [Letterboxd][lbx] | [AOD][aod]                                                          | [FAL][fal]    | [ALAL][alal]                           | [ATIP][atip]     |
| ------------------------------- | ---------------------------------------------------------------- | --------------------------- | ------------------ | ------------------------- | ----------------------- | ------------ | ----------------- | ------------------------------------------------------------------- | ------------- | -------------------------------------- | ---------------- |
| License                         | AGPL-3.0-only, MIT, CC0                                          | MIT                         | AGPL-3.0           | Apache-2.0                | Proprietary             | Proprietary  | Proprietary       | AGPL-3.0                                                            | Unknown       | Unknown                                | Unknown          |
| Access                          | Public                                                           | Public                      | Public             | Paid, API Key             | API Key                 | API Key      | API Key           | Public                                                              | Public        | Public                                 | Public           |
| Format                          | REST, JSON, TSV                                                  | Node.js Package, REST, JSON | REST               | REST                      | REST                    | REST         | REST              | JSON                                                                | JSON          | XML                                    | JSON             |
| Main Languages                  | Python, JSON                                                     | JavaScript, JSON            | TypeScript, SQLite | C#, MySQL, PostgreSQL     | -                       | -            | -                 | JSON                                                                | JSON          | XLSL, XML                              | PowerShell, JSON |
| Base Data                       | AOD, ARM, ATIP, FAL<br>![f:kz] ![f:oo] ![f:ntj] ![f:hka] ![f:sy] | ![f:ntf]                    | FAL                | ![f:al] ![f:kts] ![f:ntf] | ![f:tvdb] ![f:adb]      | ![f:tmdb]    | -                 | ![f:mal] ![f:al] ![f:adb] ![f:kts] ![f:lc] ![f:as] ![f:ap] ![f:ntf] | AOD, ALAL     | ![f:adb] ![f:tvdb] ![f:tmdb] ![f:imdb] | [aniTrakt][atrk] |
| Rate Limit                      | -                                                                | -                           | -                  | -                         | 1000/day for unverified | 1000/5 mins  | 1000/day          | Unapplicable                                                        | Unapplicable  | Unapplicable                           | Unapplicable     |
|                                 |                                                                  |                             |                    |                           |                         |              |                   |                                                                     |               |                                        |                  |
| Anime Title                     | ✔                                                                | ❌                           | ❌                  | ❌                         | ✔                       | ✔            | ✔                 | ✔                                                                   | ❌             | ✔                                      | ✔                |
| [![f:adb] aniDB][adb]           | ✔                                                                | ❌                           | ✔                  | ✔                         | ✔                       | ❌            | ❌                 | ✔                                                                   | ✔             | ❌                                      | ❌                |
| [![f:al] AniList][al]           | ✔                                                                | ✔                           | ✔                  | ✔                         | ✔ Result Only           | ❌            | ❌                 | ✔                                                                   | ✔             | ❌                                      | ❌                |
| [![f:an] ANN][an]               | ✔                                                                | ❌                           | ❌                  | ❌                         | ✔ Result Only           | ❌            | ❌                 | ✔                                                                   | ❌             | ❌                                      | ❌                |
| [![f:ap] Anime-Planet][ap]      | ✔                                                                | ❌                           | ✔                  | ❌                         | ✔ Result Only           | ❌            | ❌                 | ✔                                                                   | ✔             | ❌                                      | ❌                |
| [![f:as] AniSearch][as]         | ✔                                                                | ❌                           | ✔                  | ❌                         | ✔ Result Only           | ❌            | ❌                 | ✔                                                                   | ✔             | ❌                                      | ❌                |
| [![f:ac] Annict][ac]            | ✔                                                                | ✔                           | ❌                  | ❌                         | ❌                       | ❌            | ❌                 | ❌                                                                   | ❌             | ❌                                      | ❌                |
| [![f:hka] Hikka][hka]           | ✔                                                                | ❌                           | ❌                  | ❌                         | ❌                       | ❌            | ❌                 | ❌                                                                   | ❌             | ❌                                      | ❌                |
| [![f:imdb] IMDB][imdb]          | ✔                                                                | ❌                           | ✔                  | ❌                         | ✔                       | ✔            | ✔                 | ❌                                                                   | ✔             | ✔                                      | ❌                |
| [![f:kz] Kaize][kz]             | ✔                                                                | ❌                           | ❌                  | ❌                         | ❌                       | ❌            | ❌                 | ❌                                                                   | ❌             | ❌                                      | ❌                |
| [![f:kts] Kitsu][kts]           | ✔                                                                | ❌                           | ✔                  | ✔                         | ✔ Result Only           | ❌            | ❌                 | ✔                                                                   | ✔             | ❌                                      | ❌                |
| [![f:lbx] Letterboxd][lbx]      | ✔                                                                | ❌                           | ❌                  | ❌                         | ❌                       | ❌            | ✔                 | ❌                                                                   | ❌             | ❌                                      | ❌                |
| [![f:lc] LiveChart][lc]         | ✔                                                                | ❌                           | ✔                  | ❌                         | ✔ Result Only           | ❌            | ❌                 | ✔                                                                   | ✔             | ❌                                      | ❌                |
| [![f:mal] MyAnimeList][mal]     | ✔                                                                | ✔                           | ✔                  | ✔                         | ✔                       | ❌            | ❌                 | ✔                                                                   | ✔             | ❌                                      | ✔                |
| [![f:ntj] Nautiljon][ntj]       | ✔                                                                | ❌                           | ❌                  | ❌                         | ❌                       | ❌            | ❌                 | ❌                                                                   | ❌             | ❌                                      | ❌                |
| [![f:ntf] Notify][ntf]          | ✔                                                                | ❌                           | ✔                  | ✔                         | ❌                       | ❌            | ❌                 | ❌                                                                   | ✔             | ❌                                      | ❌                |
| [![f:oo] Otak Otaku][oo]        | ✔                                                                | ❌                           | ❌                  | ❌                         | ❌                       | ❌            | ❌                 | ❌                                                                   | ❌             | ❌                                      | ❌                |
| [![f:shk] Shikimori][shk]       | ✔                                                                | ✔ via MAL                   | ✔ via MAL          | ✔ via MAL                 | ✔ via MAL               | ❌            | ❌                 | ✔ via MAL                                                           | ✔ via MAL     | ❌                                      | ✔ via MAL        |
| [![f:shb] Shoboi Calendar][shb] | ✔                                                                | ✔                           | ❌                  | ❌                         | ❌                       | ❌            | ❌                 | ❌                                                                   | ❌             | ❌                                      | ❌                |
| [![f:sy] SilverYasha DBTI][sy]  | ✔                                                                | ❌                           | ❌                  | ❌                         | ❌                       | ❌            | ❌                 | ❌                                                                   | ❌             | ❌                                      | ❌                |
| [![f:smk] SIMKL][smk]           | ✔                                                                | ❌                           | ❌                  | ❌                         | ✔                       | ❌            | ❌                 | ✔                                                                   | ❌             | ❌                                      | ❌                |
| [![f:tmdb] TMDB][tmdb]          | ✔                                                                | ❌                           | ✔, only movie      | ❌                         | ✔                       | ✔            | ✔                 | ❌                                                                   | ✔, only movie | ✔, only movie                          | ❌                |
| [![f:trk] Trakt][trk]           | ✔                                                                | ❌                           | ❌                  | ❌                         | ✔                       | ✔            | ❌                 | ❌                                                                   | ❌             | ❌                                      | ✔                |
| [![f:tvdb] TVDB][tvdb]          | ✔                                                                | ❌                           | ❌                  | ❌                         | ✔                       | ✔            | ❌                 | ❌                                                                   | ✔             | ✔                                      | ❌                |
| [![f:tvtm] TVTime][tvtm]        | ✔ via TVDB                                                       | ❌                           | ❌                  | ❌                         | ✔ via TVDB              | ✔ via TVDB   | ❌                 | ❌                                                                   | ✔ via TVDB    | ✔ via TVDB                             | ❌                |

<!-- markdownlint-enable MD013 MD060 -->
<!-- omit in toc -->
### Legends

* ALAL: [Anime-Lists/anime-lists][alal]
* AOD: [manami-project/anime-offline-database][aod]
* ARM: [kawaiioverflow/arm][arm]
* ATIP: [ryuuganime/aniTrakt-IndexParser][atip]
* BQA: [BeeeQueue/arm-server][bq]
* FAL: [Fribb/anime-lists][fal]
* LBX: [Letterboxd][lbx]

## Why Avoid Using AnimeAPI?

AnimeAPI is licensed under the AGPL-3.0-only, primarily because it's derived
from the [manami-project/anime-offline-database][aod]. We strongly discourage
integrating this project into your own if you intend to maintain a permissive
licensing model for your work.

There is an alternative approach you can consider. You could make your project
closed-source and set up a private instance of AnimeAPI for your specific use.
However, it's essential to recognize that this approach raises ethical
considerations, and we recommend proceeding with caution while also exploring
other options or alternatives.

It's worth noting that there are exceptions to this rule, particularly regarding
the raw files from original sources. The scraper scripts for Kaize, Nautiljon,
and Otak-Otaku are licensed under the MIT license, and the raw JSON files they
generate are licensed under the CC0 license instead. You are free to use these
files and build your own database with them. For more information, please refer
to [`database/raw/README.md`](database/raw/README.md).

Additionally, since the project is object/key-value based and not array, the
relation assumed by AnimeAPI is the same across database, where in fact it's
not the case, especially with heavily moderated databases like AniDB, AniList,
and Anime News Network. So, for any episode 0/prequel, specials, OVAs, movies,
or older titles might get incorrect relationship.

## Featured on

Do you want to integrate AnimeAPI into your project? Or do you want to see how
AnimeAPI is used in other projects and their use cases? Check out the list below!

> [!TIP]
>
> If you want to add your project to this list, please open a pull request
> adding your project to the table below. Please make sure to add a short
> description of your project and a link to your project's homepage.

<!-- markdownlint-disable MD034 MD013 -->
### Libraries

| Package Name  | Language | Package Link                                  | Description                                                                  |
| :------------ | :------- | :-------------------------------------------- | :--------------------------------------------------------------------------- |
| `animeapi-py` | Python   | [pypi](https://pypi.org/project/animeapi-py/) | A Python wrapper for AnimeAPI with type hinting and additional async support |

### Projects, Apps, and Websites

| Name                    | Language           | Homepage                                                               | Description                                                                                 |
| :---------------------- | :----------------- | :--------------------------------------------------------------------- | :------------------------------------------------------------------------------------------ |
| Ryuuzaki Ryuusei        | Python             | [GitHub](https://github.com/nattadasu/ryuuRyuusei)                     | A Discord bot that uses AnimeAPI to fetch anime maps                                        |
| animeManga-autoBackup   | Powershell, Python | [GitHub](https://github.com/Animanga-Initiative/animeManga-autoBackup) | A script that uses AnimeAPI to get info one of your anime/manga lists and save it to a file |
| Hikaru Aegis (codename) | Python             | [GitHub](https://github.com/Animanga-Initiative/hikaru-aegis)          | Rewrite of animeManga-autoBackup in Python                                                  |

## Supported Platforms and Aliases

AnimeAPI supported following sites for media lookup. You can use this as an
alias cheatsheet as well.

> [!IMPORTANT]
>
> * The aliases are case-insensitive. You can use any of the aliases to get the
>   data you want.
> * 2K is the two-letter abbreviation for the platform.

|           Platform |  2K   | Aliases                                                                                         |
| -----------------: | :---: | ----------------------------------------------------------------------------------------------- |
|            `anidb` | `ad`  | `adb`, `anidb.net`                                                                              |
|          `anilist` | `al`  | `anilist.co`                                                                                    |
| `animenewsnetwork` | `an`  | `ann`, `animenewsnetwork.com`                                                                   |
|      `animeplanet` | `ap`  | `anime-planet.com`, `anime-planet`, `animeplanet.com`                                           |
|        `anisearch` | `as`  | `anisearch.com`, `anisearch.de`, `anisearch.it`, `anisearch.es`, `anisearch.fr`, `anisearch.jp` |
|           `annict` | `ac`  | `anc`, `act`, `annict.com`, `annict.jp`, `en.annict.com`                                        |
|            `hikka` | `hk`  | `hka`, `hikka.io`                                                                               |
|             `imdb` | `im`  | `imdb.com`                                                                                      |
|            `kaize` | `kz`  | `kaize.io`                                                                                      |
|            `kitsu` | `kt`  | `kts`, `kitsu.io`, `kitsu.app`                                                                  |
|       `letterboxd` | `lb`  | `lx`, `letterboxd.com`                                                                          |
|        `livechart` | `lc`  | `livechart.me`                                                                                  |
|      `myanimelist` | `ma`  | `mal`, `myanimelist.net`                                                                        |
|        `nautiljon` | `nj`  | `ntj`, `nautiljon.com`                                                                          |
|           `notify` | `nf`  | `ntf`, `ntm`, `notifymoe`, `notify.moe`                                                         |
|        `otakotaku` | `oo`  | `otakotaku.com`                                                                                 |
|        `shikimori` | `sh`  | `shiki`, `shk`, `shiki.one`, `shikimori.io`, `shikimori.me`, `shikimori.one`, `shikimori.org`   |
|           `shoboi` | `sb`  | `shb`, `syb`, `shobocal`, `syoboi`, `syobocal`, `cal.syoboi.jp`                                 |
|      `silveryasha` | `sy`  | `dbti`, `db.silveryasha.id`, `db.silveryasha.web.id`                                            |
|            `simkl` | `sm`  | `smk`, `simkl.com`, `animecountdown`, `animecountdown.com`                                      |
|       `themoviedb` | `tm`  | `tmdb`, `themoviedb.org`                                                                        |
|          `thetvdb` | `tv`  | `tvdb`, `thetvdb.com`, `thetvdb`, `tvtime`, `tt`, `tvtime.com`                                  |
|            `trakt` | `tr`  | `trk`, `trakt.tv`                                                                               |

<!-- markdownlint-enable MD034 MD013 -->

## Statistic

So far, AnimeAPI has indexed data from 19 databases, with details as follows:

<!-- updated -->
Last updated: 30 March 2026 05:52:20 UTC
<!-- /updated -->

<!-- counters -->
| Platform           |     Count |
| :----------------- | --------: |
| aniDB              |     14335 |
| AniList            |     22322 |
| Anime News Network |     12210 |
| Anime-Planet       |     26616 |
| aniSearch          |     20636 |
| Annict             |     12653 |
| Hikka              |     28418 |
| IMDb               |      5820 |
| Kaize              |     24430 |
| Kitsu              |     21867 |
| Letterboxd         |         0 |
| LiveChart          |     12125 |
| MyAnimeList        |     30377 |
| Nautiljon          |      9149 |
| Notify.moe         |     16968 |
| Otak Otaku         |      3000 |
| Shikimori          |     30377 |
| Shoboi/Syobocal    |      5975 |
| Silver Yasha       |      4954 |
| SIMKL              |     14325 |
| The Movie Database |      8259 |
| The TVDB           |      3760 |
| Trakt              |      5110 |
|                    |           |
| **Total**          | **40002** |
<!-- /counters -->

## Usage

To use this API, you can access the following base URLs:

* Latest/v3:
  
  ```http
  GET https://animeapi.my.id
  ```

All requests must be `GET`, and response always will be in JSON format.

### Response Headers

> [!IMPORTANT]
>
> This feature was added in Oct 29, 2025. Make sure your program/custom library
> supports this to avoid errors.

All API responses include the following custom headers:

<!-- markdownlint-disable MD013 -->

| Header                      | Description                                                                         | Example Value |
| --------------------------- | ----------------------------------------------------------------------------------- | ------------- |
| `X-ANIMEAPI-VERSION`        | Current API version                                                                 | `v3`          |
| `X-ANIMEAPI-UPDATED`        | Database last update timestamp (Unix epoch)                                         | `1761714944`  |
| `X-ANIMEAPI-SERVER-UPDATED` | API server code last update timestamp (Unix epoch, tracks changes to `api/` folder) | `1761762026`  |

<!-- markdownlint-enable MD013 -->

These headers are useful for:

* **Cache invalidation**: Use `X-ANIMEAPI-UPDATED` to detect when the database
  has been updated
* **Version checking**: Ensure your application is compatible with the current
  API version
* **Server monitoring**: Track when the API server code was last modified

Example:

```http
GET /status HTTP/1.1
Host: animeapi.my.id

HTTP/1.1 200 OK
X-ANIMEAPI-VERSION: v3
X-ANIMEAPI-UPDATED: 1761714944
X-ANIMEAPI-SERVER-UPDATED: 1761762026
Content-Type: application/json
```

### Get status and statistics

MIME Type: `application/json`

```http
GET /status
```

<details>
<summary>Response example</summary>

<!-- markdownlint-disable MD034 MD013 -->
<!-- status -->
```json
{
  "mainrepo": "https://github.com/nattadasu/animeApi/tree/v3",
  "updated": {
    "timestamp": 1774849940,
    "iso": "2026-03-30T05:52:20.157650+00:00"
  },
  "contributors": [
    "nattadasu",
    "Copilot",
    "github-actions[bot]"
  ],
  "sources": [
    "gh:kawaiioverflow/arm",
    "gh:manami-project/anime-offline-database",
    "gh:rensetsu/db.rensetsu.public-dump",
    "gh:rensetsu/db.trakt.extended-anitrakt",
    "gh:Fribb/anime-lists",
    "https://kaize.io",
    "https://nautiljon.com",
    "https://otakotaku.com"
  ],
  "license": "AGPL-3.0-only AND MIT AND CC0-1.0+",
  "website": "https://animeapi.my.id",
  "counts": {
    "anidb": 14335,
    "anilist": 22322,
    "animenewsnetwork": 12210,
    "animeplanet": 26616,
    "anisearch": 20636,
    "annict": 12653,
    "hikka": 28418,
    "imdb": 5820,
    "kaize": 24430,
    "kitsu": 21867,
    "letterboxd": 0,
    "livechart": 12125,
    "myanimelist": 30377,
    "nautiljon": 9149,
    "notify": 16968,
    "otakotaku": 3000,
    "shikimori": 30377,
    "shoboi": 5975,
    "silveryasha": 4954,
    "simkl": 14325,
    "themoviedb": 8259,
    "thetvdb": 3760,
    "trakt": 5110,
    "total": 40002
  },
  "endpoints": {
    "$comment": "The endpoints are stated in Python regex format. Platform aliases supported for direct lookup for platform specific endpoints (see ?P<alias> in regex).",
    "anidb": "/(?P<alias>anidb)/(?P<media_id>\\d+)",
    "anilist": "/(?P<alias>anilist)/(?P<media_id>\\d+)",
    "animeapi_dump": "/(anime(?:a|A)pi|aa)(?:\\\\\\.json)?",
    "animeapi_tsv": "/(anime(?:a|A)pi|aa).tsv",
    "animenewsnetwork": "(?P<alias>animenewsnetwork)/(?P<media_id>\\d+)",
    "animeplanet": "/(?P<alias>animeplanet)/(?P<media_id>[\\w\\-]+)",
    "anisearch": "/(?P<alias>anisearch)/(?P<media_id>\\d+)",
    "annict": "/(?P<alias>annict)/(?P<media_id>\\d+)",
    "heartbeat": "/(heartbeat|ping)",
    "hikka": "/(?P<alias>hikka)/(?P<media_id>\\d+)",
    "imdb": "/(?P<alias>imdb)/(?P<media_id>tt[\\d]+)",
    "kaize": "/(?P<alias>kaize)/(?P<media_id>[\\w\\-]+)",
    "kitsu": "/(?P<alias>kitsu)/(?P<media_id>\\d+)",
    "letterboxd": "/(?P<alias>letterboxd)/(?P<media_id>[\\w\\-]+)",
    "livechart": "/(?P<alias>livechart)/(?P<media_id>\\d+)",
    "myanimelist": "/(?P<alias>myanimelist)/(?P<media_id>\\d+)",
    "nautiljon": "/(?P<alias>nautiljon)/(?P<media_id>[\\w\\+!\\-_\\(\\)\\[\\]]+)",
    "notify": "/(?P<alias>notify)/(?P<media_id>[\\w\\-_]+)",
    "otakotaku": "/(?P<alias>otakotaku)/(?P<media_id>\\d+)",
    "redirect": "/(redirect|rd)",
    "repo": "/",
    "schema": "/schema(?:\\\\\\.json)?",
    "shikimori": "/(?P<alias>shikimori)/(?P<media_id>\\d+)",
    "shoboi": "/(?P<alias>shoboi)/(?P<media_id>\\d+)",
    "silveryasha": "/(?P<alias>silveryasha)/(?P<media_id>\\d+)",
    "simkl": "/(?P<alias>simkl)/(?P<media_id>\\d+)",
    "status": "/status",
    "syobocal": "/(?P<alias>syobocal)/(?P<media_id>\\d+)",
    "themoviedb": "/(?P<alias>themoviedb)/(?P<media_type>movie|tv)/(?P<media_id>\\d+)(?:/seasons?/(?P<season_id>\\d+))?",
    "thetvdb": "/(?P<alias>thetvdb)/series/(?P<media_id>\\d+)(?:/seasons?/(?P<season_id>\\d+))?",
    "trakt": "/(?P<alias>trakt)/(?P<media_type>show|movie)(s)?/(?P<media_id>\\w\\-+)(?:/seasons?/(?P<season_id>\\d+))?",
    "updated": "/updated"
  }
}
```
<!-- /status -->
<!-- markdownlint-enable MD034 MD013 -->

</details>

### Get latency report

MIME Type: `application/json`

```http
GET /heartbeat
```

<details>
<summary>Response example</summary>

```json
{
  "status": "OK",
  "code": 200,
  "response_time": "0.000s",
  "request_time": "0.000s",
  "request_epoch": 1626682566.0,
}
```

</details>

### Get updated date and time

MIME Type: `text/plain`

```http
GET /updated
```

<details>
<summary>Response example</summary>

<!-- updated-txt -->
```txt
Updated on 03/30/2026 05:52:20 UTC
```
<!-- /updated-txt -->

</details>

### Get all items in Array (Master Array)

HTTP Status Code: `302` (redirect to GitHub raw file URL)\
MIME Type: `application/json`

```http
GET /animeApi.json
```

or

```http
GET /aa.json
```

### Fetch all item as TSV (Tab Separated Values) file

> [!TIP]
>
> Use this endpoint if you want to import the data to spreadsheet.

MIME Type: `text/tab-separated-values`

```http
GET /animeApi.tsv
```

or

```http
GET /aa.tsv
```

### ~~Get All ID in Object/Dictionary format of each provider~~

> [!CAUTION]
>
> **This endpoint has been removed as of January 19, 2026.**
>
> This endpoint was deprecated since October 22, 2025 and now returns
> **HTTP 410 Gone**. Please use the TSV/master array endpoint and convert it to
> your desired format locally.

HTTP Status Code: `410` (Gone)\
MIME Type: `application/json`

```http
GET /:platform.json
```

`:platform` can be one of the following listed in
[Supported Platforms and Aliases](#supported-platforms-and-aliases).

**Response:**

```json
{
  "error": "Endpoint deprecated",
  "code": 410,
  "message": "Platform-specific object dumps have been deprecated since October 22, 2025. Please use /animeapi.json or /animeapi.tsv and filter locally.",
  "alternatives": {
    "master_json": "/animeapi.json",
    "master_tsv": "/animeapi.tsv"
  }
}
```

### ~~Get All ID in Array/List format of each provider~~

> [!CAUTION]
>
> **This endpoint has been removed as of January 19, 2026.**
>
> This endpoint was deprecated since October 22, 2025 and now returns
> **HTTP 410 Gone**. Please use the TSV/master array endpoint and convert it to
> your desired format locally.

HTTP Status Code: `410` (Gone)\
MIME Type: `application/json`

```http
GET /:platform().json
```

`:platform` can be one of the following listed in
[Supported Platforms and Aliases](#supported-platforms-and-aliases).

> [!IMPORTANT]
>
> The `()` in the endpoint is not a typo, it's part of the endpoint.
> If you can't access the endpoint, try to encode the `()` to `%28%29`.

**Response:**

```json
{
  "error": "Endpoint deprecated",
  "code": 410,
  "message": "Platform-specific array dumps have been deprecated since October 22, 2025. Please use /animeapi.json or /animeapi.tsv and filter locally.",
  "alternatives": {
    "master_json": "/animeapi.json",
    "master_tsv": "/animeapi.tsv"
  }
}
```

### Get anime relation mapping data

MIME Type: `application/json`

```http
GET /:platform/:mediaid
```

* `:platform` can be one of the following listed in
  [Supported Platforms and Aliases](#supported-platforms-and-aliases).
* `:mediaid` is the ID of the anime in the platform.
* To use `kitsu`, `simkl`, `shikimori`, `themoviedb`, and `trakt` path, please
  read additional information in [# Provider exclusive rules](#provider-exclusive-rules)
  before proceeding to avoid unwanted error.

<details>
<summary>Response example</summary>

```http
GET https://animeapi.my.id/myanimelist/1
```

<!-- sample -->
```json
{}
```
<!-- /sample -->

</details>

#### Provider exclusive rules

##### Kitsu

`kitsu` ID must in numerical value. If your application obtained slug as ID
instead, you can resolve/convert it to ID using following Kitsu API endpoint:

```http
GET https://kitsu.app/api/edge/anime?filter[slug]=<ID>
```

For example, if you want to get anime data from Kitsu with slug `cowboy-bebop`,
you can use the following endpoint:

```http
GET https://kitsu.app/api/edge/anime?filter[slug]=cowboy-bebop
```

The response will be in JSON format, and you can get the ID from `data[0].id`

##### Letterboxd

`letterboxd` supports multiple ID formats with priority-based lookup:

1. **Slug** (`letterboxd_slug`) - Primary format (e.g., `your-name`)
2. **Letter ID** (`letterboxd_lid`) - Fallback format (e.g., `cUqs`), useful
   if you iterate from Letterboxd's official API directly.
3. **Unique ID** (`letterboxd_uid`) - Alternative fallback (e.g., `307684`),
   this ID is only used by Letterboxd internally, you may unable to interact
   with the ID directly.

When querying the API, it will automatically try these formats in order:

```http
GET https://animeapi.my.id/letterboxd/your-name      # Slug lookup
GET https://animeapi.my.id/letterboxd/cUqs           # Letter ID lookup
GET https://animeapi.my.id/letterboxd/307684         # Unique ID lookup
```

The API will return the Letterboxd film URL using the stored `letterboxd_slug`
value.

##### SIMKL

> [!NOTE]
>
> Also applicable to AnimeCountdown

`simkl` ID is only applicable for media entries in Anime category.

##### Shikimori

`shikimori` IDs are basically the same as `myanimelist` IDs. If you get a 404
status code, remove any alphabetical prefix from the ID and try again.

For example: `z218` → `218`

##### The Movie DB

For The Movie DB (TMDB), the ID is in the format of `:provider/:mediatype/:mediaid`
where `:mediatype` is either `movie` or `tv` and `:mediaid` is the ID of the title
in the provider instead of typical `:provider/:mediaid` format. For TV shows, you
can also specify a season by using the format of
`:provider/:mediatype/:mediaid/seasons/:seasonid` where `:season_id` can be season
index defined by Trakt's season number, or TMDB internal season ID.

**Supported formats:**

```http
GET https://animeapi.my.id/themoviedb/tv/30991                # TV show
GET https://animeapi.my.id/themoviedb/movie/60669             # Movie
GET https://animeapi.my.id/themoviedb/tv/30991/seasons/1      # TV show with season
```

> [!NOTE]
>
> The media type (`movie` or `tv`) is required in the URL path and must match
> the stored `themoviedb_type` value in the database.

##### The TVDB

For The TVDB, the ID follows the format `:provider/series/:mediaid` or
`:provider/series/:mediaid/seasons/:season_id` for season-specific entries.

When querying season data, you can use either the season number (from `trakt_season`)
or the TVDB season ID (from `thetvdb_season_id`). Season 1 entries can be accessed
using the base series URL.

For example:

```http
GET https://animeapi.my.id/thetvdb/series/12345
GET https://animeapi.my.id/thetvdb/series/12345/seasons/2
GET https://animeapi.my.id/thetvdb/series/12345/seasons/789012
```

##### Trakt

For Trakt, the ID is in the format of `:provider/:mediatype/:mediaid` where
`:mediatype` is either `movies` or `shows` and `:mediaid` can be either a
**numeric ID** or a **slug**.

**Supported formats:**

<!-- markdownlint-disable MD013 -->

```http
GET https://animeapi.my.id/trakt/movies/224301                 # Numeric ID
GET https://animeapi.my.id/trakt/movies/your-name-2016         # Slug
GET https://animeapi.my.id/trakt/shows/152334/seasons/3        # With season (numeric)
GET https://animeapi.my.id/trakt/shows/cowboy-bebop/seasons/1  # With season (slug)
```

<!-- markdownlint-enable MD013 -->

The API will first attempt to parse `:mediaid` as a numeric ID. If that fails, it
will fall back to slug lookup using the `trakt_slug` field.

> [!NOTE]
>
> While you can now use slugs directly, numeric IDs are still recommended for
> better performance. If you need to convert a slug to numeric ID externally,
> you can use the Trakt API:
>
> ```http
> GET https://api.trakt.tv/search/trakt/<ID>?type=<movie|show>
> ```
>
> Note: The Trakt API requires an API key to access this endpoint.

To get exact season mapping, append `/seasons/:season_inc` to the end of the ID,
where `:season_inc` is the season number of the title in the provider.

> [!CAUTION]
>
> `/seasons/0` is invalid, and will return `400` status code.

> [!IMPORTANT]
>
> Since Oct 19, 2025, AnimeAPI now features a split cour flag, where
> `trakt_may_invalid` indicates whether a season mapping may be unreliable:
>
> * **`none`**: The entry is either a special, or a movie
> * **`false`**: Season found on Trakt and mapping is reliable.
> * **`true`**: Season not found separately on Trakt (split cour). Season
>   fields on Trakt, TMDB, and TVDB will be `null`.
>
> MAL may list split cours as separate seasons while Trakt/TMDB combines them
> into one continuous season. When `true`, episodes are likely in the previous
> season on Trakt.
>
> For more information, head to [db.trakt.extended-anitrakt][atip].

For example, to get the ID of Mairimashita Iruma-kun Season 3, you can use:

```http
GET https://animeapi.my.id/trakt/shows/152334/seasons/3
```

<details>
<summary>Response example from Trakt</summary>

<!-- trakt152334 -->
```json
{}
```
<!-- /trakt152334 -->

</details>

### Redirect to provider's page

HTTP Status Code: `302` OR `200` (if required)\
MIME Type: None OR `text/plain` (if required)

```http
GET /redirect?platform=:platform&mediaid=:mediaid&target=:platform
```

or

```http
GET /rd?from=:platform&id=:mediaid&to=:platform
```

* `:platform` can be one of the following listed in
  [Supported Platforms and Aliases](#supported-platforms-and-aliases).

  Additionally, on `target`/`to` parameter, there are additional supported
  platforms, and can't be used as source/`from` due to some limitations:

  <!-- markdownlint-disable MD013 -->

  |   Platform |  2K   | Aliases               | Additional Notes                           |
  | ---------: | :---: | --------------------- | :----------------------------------------- |
  | `kurozora` | `kr`  | `krz`, `kurozora.app` | Requires Kurozora+ subscription and MAL ID |
  |  `myanili` | `my`  | `myani.li`            | Requires MAL ID; a web app to manage list  |

  <!-- markdownlint-enable MD013 -->

* `:mediaid` is the ID of the anime in the platform. Please follow the instruction
  written in [Provider exclusive rules](#provider-exclusive-rules) to avoid any
  conflict during redirection.

#### Redirect: Parameters

In AnimeAPI, we use query parameters to specify the output of the API. The query
parameters are as follows:

<!-- markdownlint-disable MD013 -->

| Parameter  | Aliases     | Is Required | Description                                                                                                                        |
| ---------- | ----------- | ----------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| `platform` | `from`, `f` | Yes         | The platform you want to get the data from.                                                                                        |
| `mediaid`  | `id`, `i`   | Yes         | The ID of the anime in the platform.                                                                                               |
| `target`   | `to`, `t`   | No          | The platform you want to redirect to. If you don't specify this parameter, the API will redirect to specified platform's homepage. |
| `israw`    | `raw`, `r`  | No          | As long as this parameter is present, the API will return the raw URL instead of redirecting.                                      |

<!-- markdownlint-enable MD013 -->

#### Redirect: Response

##### Recommended/verbose path format

```http
GET https://animeapi.my.id/redirect?platform=myanimelist&mediaid=1&target=trakt

HTTP/1.1 302 Found
Location: https://trakt.tv/shows/30857/seasons/1
```

##### Short/aliased/alternative path format

```http
GET https://animeapi.my.id/rd?from=al&id=154587&to=shk

HTTP/1.1 302 Found
Location: https://shikimori.io/animes/52991
```

##### Provider with slash (`/`) in `mediaid`

There is no exclusive rule in this, as AnimeAPI will automatically understand
your query

```http
GET https://animeapi.my.id/redirect?platform=trakt&mediaid=shows/152334/seasons/3&target=myanimelist

HTTP/1.1 302 Found
Location: https://myanimelist.net/anime/49784
```

##### Raw path format

```http
GET https://animeapi.my.id/redirect?platform=animeplanet&mediaid=cells-at-work&target=simkl&israw

HTTP/1.1 200 OK
Content-Type: text/plain; charset=utf-8

https://simkl.com/anime/757695
```

## Schema

If you want to validate the response from the API, you can use the following
schema in JSON Schema, TypeScript, or Python Dataclass.

### JSON Schema

Add the following schema URI to your JSON file.

```json
{ "$schema": "https://animeapi.my.id/schema.json" }
```

<details>
<summary>Click to expand, if you want to see the content of the schema</summary>

<!-- markdownlint-disable MD013 -->
<!-- jsonschema -->
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "definitions": {
    "anime": {
      "$comment": "Interface: Anime",
      "additionalProperties": false,
      "dependencies": {
        "themoviedb_type": {
          "properties": {
            "themoviedb_season_id": {
              "type": "number"
            }
          },
          "required": [
            "themoviedb_season_id"
          ]
        },
        "trakt_type": {
          "properties": {
            "trakt_season": {
              "type": "number"
            }
          },
          "required": [
            "trakt_season"
          ]
        }
      },
      "description": "Schema for anime",
      "properties": {
        "anidb": {
          "$ref": "#/definitions/numbernull",
          "description": "aniDB ID, website: https://anidb.net/",
          "title": "aniDB"
        },
        "anilist": {
          "$ref": "#/definitions/numbernull",
          "description": "AniList ID, website: https://anilist.co/",
          "title": "AniList"
        },
        "animenewsnetwork": {
          "$ref": "#/definitions/numbernull",
          "description": "Anime News Network, website: https://animenewsnetwork.com",
          "title": "Anime News Network"
        },
        "animeplanet": {
          "$ref": "#/definitions/stringnull",
          "description": "Anime-Planet slug, website: https://www.anime-planet.com/",
          "pattern": "^[a-z0-9\\-]+$",
          "title": "Anime-Planet"
        },
        "anisearch": {
          "$ref": "#/definitions/numbernull",
          "description": "AniSearch ID, website: https://www.anisearch.com/, https://anisearch.de, https://anisearch.it, https://anisearch.es, https://anisearch.fr, https://anisearch.jp",
          "title": "AniSearch"
        },
        "annict": {
          "$ref": "#/definitions/numbernull",
          "description": "Annict ID, website: https://annict.com/, https://en.annict.com/, https://annict.jp/",
          "title": "Annict"
        },
        "hikka": {
          "$ref": "#/definitions/stringnull",
          "description": "Hikka slug + hash, website: https://hikka.io/",
          "title": "Hikka"
        },
        "imdb": {
          "$ref": "#/definitions/stringnull",
          "description": "IMDb ID, website: https://www.imdb.com/",
          "pattern": "^tt[\\d]+$",
          "title": "IMDb"
        },
        "kaize": {
          "$ref": "#/definitions/stringnull",
          "description": "Kaize slug, website: https://kaize.io/",
          "pattern": "^[a-z0-9\\-]+$",
          "title": "Kaize"
        },
        "kaize_id": {
          "$ref": "#/definitions/numbernull",
          "description": "Kaize ID in integer format, not recommended as some entry can't be found its ID compared to slug",
          "title": "Kaize ID"
        },
        "kitsu": {
          "$ref": "#/definitions/numbernull",
          "description": "Kitsu ID in integer, slug not suppported, website: https://kitsu.app/",
          "title": "Kitsu"
        },
        "letterboxd_slug": {
          "$ref": "#/definitions/stringnull",
          "description": "Letterboxd slug, website: https://letterboxd.com/",
          "pattern": "^[a-z0-9\\-]+",
          "title": "Letterboxd Slug"
        },
        "letterboxd_lid": {
          "$ref": "#/definitions/stringnull",
          "description": "Letterboxd Letter ID, only being used on 1st party API requests",
          "title": "Letterboxd ID"
        },
        "letterboxd_uid": {
          "$ref": "#/definitions/numbernull",
          "description": "Letterboxd General ID, internally used",
          "title": "Letterboxd General ID"
        },
        "livechart": {
          "$ref": "#/definitions/numbernull",
          "description": "LiveChart ID, website: https://www.livechart.me/",
          "title": "LiveChart"
        },
        "myanimelist": {
          "$ref": "#/definitions/numbernull",
          "description": "MyAnimeList ID, website: https://myanimelist.net/",
          "title": "MyAnimeList"
        },
        "nautiljon": {
          "$ref": "#/definitions/stringnull",
          "description": "Nautiljon slug, website: https://www.nautiljon.com/",
          "pattern": "^[a-z0-9\\-]+",
          "title": "Nautiljon"
        },
        "nautiljon_id": {
          "$ref": "#/definitions/numbernull",
          "description": "Nautiljon ID in integer format, not recommended as some entry can't be found its ID compared to slug",
          "title": "Nautiljon ID"
        },
        "notify": {
          "$ref": "#/definitions/stringnull",
          "description": "Notify.moe slug, website: https://notify.moe/",
          "pattern": "^[a-zA-Z0-9]+$",
          "title": "Notify.moe"
        },
        "otakotaku": {
          "$ref": "#/definitions/numbernull",
          "description": "Otak Otaku ID, website: https://otakotaku.com/",
          "title": "Otak Otaku"
        },
        "shikimori": {
          "$ref": "#/definitions/numbernull",
          "description": "Shikimori ID, website: https://shikimori.io/",
          "title": "Shikimori"
        },
        "shoboi": {
          "$ref": "#/definitions/numbernull",
          "description": "Shoboi/Syobocal ID, website: http://cal.syoboi.jp/",
          "title": "Shoboi/Syobocal"
        },
        "silveryasha": {
          "$ref": "#/definitions/numbernull",
          "description": "Silver Yasha ID, website: https://db.silveryasha.id/",
          "title": "Silver Yasha"
        },
        "simkl": {
          "$ref": "#/definitions/numbernull",
          "description": "SIMKL ID, website: https://simkl.com/",
          "title": "SIMKL"
        },
        "themoviedb": {
          "$ref": "#/definitions/numbernull",
          "description": "The Movie Database ID, can be used for movie or tv, website: https://www.themoviedb.org/",
          "title": "The Movie Database"
        },
        "themoviedb_season_id": {
          "$ref": "#/definitions/numbernull",
          "description": "The Movie Database internal season ID, only available for TV shows",
          "title": "The Movie Database season ID"
        },
        "themoviedb_type": {
          "$ref": "#/definitions/stringnull",
          "description": "The Movie Database media type, can be movie or tv",
          "enum": [
            "movie",
            "tv"
          ],
          "title": "The Movie Database type"
        },
        "thetvdb": {
          "$ref": "#/definitions/numbernull",
          "description": "The TVDB ID, website: https://thetvdb.com/, only to be prefixed with series/ to deep link",
          "title": "The TVDB"
        },
        "thetvdb_season_id": {
          "$ref": "#/definitions/numbernull",
          "description": "The TVDB internal season ID, can be used to build URL",
          "title": "The TVDB season ID"
        },
        "title": {
          "type": "string",
          "description": "Title of the anime in English or Romaji",
          "title": "Title"
        },
        "trakt": {
          "$ref": "#/definitions/numbernull",
          "description": "Trakt ID, can be used for movie or show, website: https://trakt.tv/",
          "title": "Trakt"
        },
        "trakt_may_invalid": {
          "$ref": "#/definitions/booleannull",
          "description": "Whether the entry is actually a split cour, which both Trakt and TMDB merge it into one",
          "title": "Trakt May Invalid"
        },
        "trakt_season": {
          "$ref": "#/definitions/numbernull",
          "description": "Trakt season number, only available for shows",
          "title": "Trakt season"
        },
        "trakt_season_id": {
          "$ref": "#/definitions/numbernull",
          "description": "Trakt season ID",
          "title": "Trakt Season ID"
        },
        "trakt_slug": {
          "$ref": "#/definitions/stringnull",
          "description": "Trakt slug",
          "pattern": "^[a-z0-9\\-]+",
          "title": "Trakt Slug"
        },
        "trakt_type": {
          "$ref": "#/definitions/stringnull",
          "description": "Trakt media type, can be movie or show",
          "enum": [
            "movies",
            "shows"
          ],
          "title": "Trakt type"
        }
      },
      "required": [
        "title"
      ],
      "title": "Anime",
      "type": "object"
    },
    "numbernull": {
      "type": [
        "number",
        "null"
      ]
    },
    "stringnull": {
      "type": [
        "string",
        "null"
      ]
    },
    "booleannull": {
      "type": [
        "boolean",
        "null"
      ]
    }
  },
  "properties": {
    "data": {
      "items": {
        "$ref": "#/definitions/anime"
      },
      "type": "array"
    }
  },
  "title": "anime-api",
  "type": "object"
}
```
<!-- /jsonschema -->
<!-- markdownlint-enable MD013 -->
</details>

You can also read human-readable schema in [JSON Schema](api/SCHEMA.md) if you
want to create your own wrapper.

### TypeScript

<details>
<summary>Click to expand</summary>

```typescript
type StringNull = string | null;
type NumberNull = number | null;
// type TmdbType = "movie" | "tv" | null;
type TraktType = "movies" | "shows" | null;

interface Anime = {
    title:                 string; // Required, title of the anime
    anidb:             NumberNull;
    anilist:           NumberNull;
    animenewsnetwork:  NumberNull;
    animeplanet:       StringNull; // Slug based
    anisearch:         NumberNull;
    annict:            NumberNull;
    imdb:              StringNull; // ttXXXXXXX format
    kaize:             StringNull; // Slug based
    kaize_id:          NumberNull; // int counterpart of Kaize slug, not recommended
    kitsu:             NumberNull; // Kitsu ID, slug is not supported
    livechart:         NumberNull;
    myanimelist:       NumberNull;
    nautiljon:         StringNull; // Plus Slug based
    nautiljon_id:      NumberNull; // int counterpart of Nautiljon slug, used internally
    notify:            StringNull; // Base64 based
    otakotaku:         NumberNull;
    simkl:             NumberNull;
    shikimori:         NumberNull;
    shoboi:            NumberNull;
    silveryasha:       NumberNull;
    themoviedb:        NumberNull;
 // themoviedb_type:     TmdbType; // Not supported yet
 // themoviedb_season: NumberNull; // Not supported yet
    trakt:             NumberNull; // Trakt ID, slug is not supported
    trakt_type:         TraktType;
    trakt_season:      NumberNull;
}

// Array/List format
type AnimeList = Anime[];

// Object/Dictionary format
type AnimeObject = {
    [key: string]: Anime;
}
```

</details>

### Python Dataclass

<details>
<summary>Click to expand</summary>

```python
from enum import Enum
from typing import Dict, List, Literal, Optional

StringNull = Optonal[str]
NumberNull = Optional[int]

# TmdbType = Optional[Literal["movie", "tv"]]
TraktType = Optional[Literal["shows", "movies"]]

@dataclass
class Anime:
    title:                    str  # Required, title of the anime
    anidb:             NumberNull
    anilist:           NumberNull
    animenewsnetwork:  NumberNull
    animeplanet:       StringNull  # Slug based
    anisearch:         NumberNull
    annict:            NumberNull
    imdb:              StringNull  # ttXXXXXXX format
    kaize:             StringNull  # Slug based
    kaize_id:          NumberNull  # int counterpart of Kaize slug, not recommended
    kitsu:             NumberNull  # Kitsu ID, slug is not supported
    livechart:         NumberNull
    myanimelist:       NumberNull
    nautiljon:         StringNull  # Plus Slug based
    nautijlon_id:      NumberNull  # int counterpart of Nautiljon slug, used internally
    notify:            StringNull  # Base64 based
    otakotaku:         NumberNull
    simkl:             NumberNull
    shikimori:         NumberNull
    shoboi:            NumberNull
    silveryasha:       NumberNull
    themoviedb:        NumberNull
  # themoviedb_type:     TmdbType  # Not supported yet
  # themoviedb_season: NumberNull  # Not supported yet
    trakt:             NumberNull  # Trakt ID, slug is currently not supported
    trakt_type:         TraktType
    trakt_season:      NumberNull

# Array/List format
anime_list = List[Anime]

# Object/Dictionary format
anime_object = Dict[str, Anime]
```

</details>

## Acknowledgements

This project uses multiple sources to compile the data, including:

* [gh:kawaiioverflow/arm][arm]
* [gh:manami-project/anime-offline-database][aod]
* [gh:rensetsu/db.trakt.extended-anitrakt][atip], which an automatic parser of
  [AniTrakt][atrk] index page.
* [gh:Fribb/anime-lists][fal]
* [Hikka][hka]
* [Nautiljon][ntj]
* [Notify.moe][ntf] through Rensetsu's data dump
* [Kaize][kz]
* [Otak Otaku][oo]
* [Silver-Yasha][sy]

<!-- Reference -->
[adb]: https://anidb.net
[al]: https://anilist.co
[alal]: https://github.com/Anime-Lists/anime-lists
[ac]: https://annict.com
[an]: https://animenewsnetwork.com
[aod]: https://github.com/manami-project/anime-offline-database
[ap]: https://anime-planet.com
[arm]: https://github.com/kawaiioverflow/arm
[as]: https://anisearch.com
[atip]: https://github.com/rensetsu/db.trakt.extended-anitrakt
[atrk]: https://anitrakt.huere.net/
[bq]: https://github.com/BeeeQueue/arm-server
[fal]: https://github.com/Fribb/anime-lists
[hato]: https://github.com/Atelier-Shiori/Hato
[hka]: https://hikka.io
[imdb]: https://imdb.com
[ko]: https://github.com/kawaiioverflow
[kts]: https://kitsu.app
[kz]: https://kaize.io
[lbx]: https://letterboxd.com
[lc]: https://livechart.me
[mal]: https://myanimelist.net
[mp]: https://github.com/manami-project
[ntf]: https://notify.moe
[ntj]: https://nautiljon.com
[oo]: https://otakotaku.com
[shb]: https://cal.syoboi.jp
[shk]: https://shikimori.io
[smk]: https://simkl.com
[sy]: https://db.silveryasha.id
[tmdb]: https://themoviedb.org
[trk]: https://trakt.tv
[tvdb]: https://thetvdb.com
[tvtm]: https://tvtime.com
[f:adb]: https://favicone.com/anidb.net
[f:al]: https://www.google.com/s2/favicons?domain=anilist.co&sz=16
[f:ac]: https://www.google.com/s2/favicons?domain=annict.com&sz=16
[f:an]: https://www.google.com/s2/favicons?domain=animenewsnetwork.com&sz=16
[f:ap]: https://www.google.com/s2/favicons?domain=anime-planet.com&sz=16
[f:as]: https://www.google.com/s2/favicons?domain=anisearch.com&sz=16
[f:hka]: https://www.google.com/s2/favicons?domain=hikka.io&sz=16
[f:imdb]: https://www.google.com/s2/favicons?domain=imdb.com&sz=16
[f:kts]: https://favicone.com/kitsu.app
[f:kz]: https://www.google.com/s2/favicons?domain=kaize.io&sz=16
[f:lbx]: https://www.google.com/s2/favicons?domain=letterboxd.com&sz=16
[f:lc]: https://www.google.com/s2/favicons?domain=livechart.me&sz=16
[f:mal]: https://www.google.com/s2/favicons?domain=myanimelist.net&sz=16
[f:ntf]: https://favicone.com/notify.moe
[f:ntj]: https://www.google.com/s2/favicons?domain=nautiljon.com&sz=16
[f:oo]: https://www.google.com/s2/favicons?domain=otakotaku.com&sz=16
[f:shb]: https://www.google.com/s2/favicons?domain=cal.syoboi.jp&sz=16
[f:shk]: https://favicone.com/shikimori.io
[f:smk]: https://www.google.com/s2/favicons?domain=simkl.com&sz=16
[f:sy]: https://www.google.com/s2/favicons?domain=db.silveryasha.id&sz=16
[f:tmdb]: https://www.google.com/s2/favicons?domain=themoviedb.org&sz=16
[f:trk]: https://www.google.com/s2/favicons?domain=trakt.tv&sz=16
[f:tvdb]: https://www.google.com/s2/favicons?domain=thetvdb.com&sz=16
[f:tvtm]: https://www.google.com/s2/favicons?domain=tvtime.com&sz=16
