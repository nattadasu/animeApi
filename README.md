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
  * [Get status and statistics](#get-status-and-statistics)
  * [Get latency report](#get-latency-report)
  * [Get updated date and time](#get-updated-date-and-time)
  * [Get all items in Array](#get-all-items-in-array)
  * [Fetch all item as TSV (Tab Separated Values) file](#fetch-all-item-as-tsv-tab-separated-values-file)
  * [Get All ID in Object/Dictionary format of each provider](#get-all-id-in-objectdictionary-format-of-each-provider)
  * [Get All ID in Array/List format of each provider](#get-all-id-in-arraylist-format-of-each-provider)
  * [Get anime relation mapping data](#get-anime-relation-mapping-data)
    * [Provider exclusive rules](#provider-exclusive-rules)
      * [Kitsu](#kitsu)
      * [SIMKL](#simkl)
      * [Shikimori](#shikimori)
      * [The Movie DB](#the-movie-db)
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

<!-- markdownlint-disable MD013 -->

| Highlights                      | AnimeAPI                                        | [ARM][arm]                  | [BQA][bq]          | [Hato][hato]              | [SIMKL][smk]            | [Trakt][trk] | [AOD][aod]                                                          | [FAL][fal]    | [ALAL][alal]                           | [ATIP][atip]     |
| ------------------------------- | ----------------------------------------------- | --------------------------- | ------------------ | ------------------------- | ----------------------- | ------------ | ------------------------------------------------------------------- | ------------- | -------------------------------------- | ---------------- |
| License                         | AGPL-3.0-only, MIT, CC0                         | MIT                         | AGPL-3.0           | Apache-2.0                | Proprietary             | Proprietary  | AGPL-3.0                                                            | Unknown       | Unknown                                | Unknown          |
| Access                          | Public                                          | Public                      | Public             | Paid, API Key             | API Key                 | API Key      | Public                                                              | Public        | Public                                 | Public           |
| Format                          | REST, JSON, TSV                                 | Node.js Package, REST, JSON | REST               | REST                      | REST                    | REST         | JSON                                                                | JSON          | XML                                    | JSON             |
| Main Languages                  | Python, JSON                                    | JavaScript, JSON            | TypeScript, SQLite | C#, MySQL, PostgreSQL     | -                       | -            | JSON                                                                | JSON          | XLSL, XML                              | PowerShell, JSON |
| Base Data                       | AOD, ARM, ATIP, FAL<br>![f:kz] ![f:oo] ![f:ntj] | ![f:ntf]                    | FAL                | ![f:al] ![f:kts] ![f:ntf] | ![f:tvdb] ![f:adb]      | ![f:tmdb]    | ![f:mal] ![f:al] ![f:adb] ![f:kts] ![f:lc] ![f:as] ![f:ap] ![f:ntf] | AOD, ALAL     | ![f:adb] ![f:tvdb] ![f:tmdb] ![f:imdb] | [aniTrakt][atrk] |
| Rate Limit                      | -                                               | -                           | -                  | -                         | 1000/day for unverified | 1000/5 mins  | Unapplicable                                                        | Unapplicable  | Unapplicable                           | Unapplicable     |
|                                 |                                                 |                             |                    |                           |                         |              |                                                                     |               |                                        |                  |
| Anime Title                     | ✔                                               | ❌                           | ❌                  | ❌                         | ✔                       | ✔            | ✔                                                                   | ❌             | ✔                                      | ✔                |
| [![f:adb] aniDB][adb]           | ✔                                               | ❌                           | ✔                  | ✔                         | ✔                       | ❌            | ✔                                                                   | ✔             | ❌                                      | ❌                |
| [![f:al] AniList][al]           | ✔                                               | ✔                           | ✔                  | ✔                         | ✔ Result Only           | ❌            | ✔                                                                   | ✔             | ❌                                      | ❌                |
| [![f:ap] Anime-Planet][ap]      | ✔                                               | ❌                           | ✔                  | ❌                         | ✔ Result Only           | ❌            | ✔                                                                   | ✔             | ❌                                      | ❌                |
| [![f:as] AniSearch][as]         | ✔                                               | ❌                           | ✔                  | ❌                         | ✔ Result Only           | ❌            | ✔                                                                   | ✔             | ❌                                      | ❌                |
| [![f:an] Annict][an]            | ✔                                               | ✔                           | ❌                  | ❌                         | ❌                       | ❌            | ❌                                                                   | ❌             | ❌                                      | ❌                |
| [![f:bgm] Bangumi][bgm]         | ❌                                               | ❌                           | ❌                  | ❌                         | ❌                       | ❌            | ❌                                                                   | ❌             | ❌                                      | ❌                |
| [![f:imdb] IMDB][imdb]          | ✔                                               | ❌                           | ✔                  | ❌                         | ✔                       | ✔            | ❌                                                                   | ✔             | ✔                                      | ❌                |
| [![f:kz] Kaize][kz]             | ✔                                               | ❌                           | ❌                  | ❌                         | ❌                       | ❌            | ❌                                                                   | ❌             | ❌                                      | ❌                |
| [![f:kts] Kitsu][kts]           | ✔                                               | ❌                           | ✔                  | ✔                         | ✔ Result Only           | ❌            | ✔                                                                   | ✔             | ❌                                      | ❌                |
| [![f:lc] LiveChart][lc]         | ✔                                               | ❌                           | ✔                  | ❌                         | ✔ Result Only           | ❌            | ✔                                                                   | ✔             | ❌                                      | ❌                |
| [![f:mal] MyAnimeList][mal]     | ✔                                               | ✔                           | ✔                  | ✔                         | ✔                       | ❌            | ✔                                                                   | ✔             | ❌                                      | ✔                |
| [![f:ntj] Nautiljon][ntj]       | ✔                                               | ❌                           | ❌                  | ❌                         | ❌                       | ❌            | ❌                                                                   | ❌             | ❌                                      | ❌                |
| [![f:ntf] Notify][ntf]          | ✔                                               | ❌                           | ✔                  | ✔                         | ❌                       | ❌            | ✔                                                                   | ✔             | ❌                                      | ❌                |
| [![f:oo] Otak Otaku][oo]        | ✔                                               | ❌                           | ❌                  | ❌                         | ❌                       | ❌            | ❌                                                                   | ❌             | ❌                                      | ❌                |
| [![f:shk] Shikimori][shk]       | ✔                                               | ✔ via MAL                   | ✔ via MAL          | ✔ via MAL                 | ✔ via MAL               | ❌            | ✔ via MAL                                                           | ✔ via MAL     | ❌                                      | ✔ via MAL        |
| [![f:shb] Shoboi Calendar][shb] | ✔                                               | ✔                           | ❌                  | ❌                         | ❌                       | ❌            | ❌                                                                   | ❌             | ❌                                      | ❌                |
| [![f:sy] SilverYasha DBTI][sy]  | ✔                                               | ❌                           | ❌                  | ❌                         | ❌                       | ❌            | ❌                                                                   | ❌             | ❌                                      | ❌                |
| [![f:smk] SIMKL][smk]           | ✔                                               | ❌                           | ❌                  | ❌                         | ✔                       | ❌            | ✔                                                                   | ❌             | ❌                                      | ❌                |
| [![f:tmdb] TMDB][tmdb]          | ✔, only movie                                   | ❌                           | ✔, only movie      | ❌                         | ✔                       | ✔            | ❌                                                                   | ✔, only movie | ✔, only movie                          | ❌                |
| [![f:trk] Trakt][trk]           | ✔                                               | ❌                           | ❌                  | ❌                         | ✔                       | ✔            | ❌                                                                   | ❌             | ❌                                      | ✔                |
| [![f:tvdb] TVDB][tvdb]          | ❌                                               | ❌                           | ❌                  | ❌                         | ✔                       | ✔            | ❌                                                                   | ✔             | ✔                                      | ❌                |
| [![f:tvtm] TVTime][tvtm]        | ❌                                               | ❌                           | ❌                  | ❌                         | ✔ via TVDB              | ✔ via TVDB   | ❌                                                                   | ✔ via TVDB    | ✔ via TVDB                             | ❌                |

<!-- markdownlint-enable MD013 -->
<!-- omit in toc -->
### Legends

* ALAL: [Anime-Lists/anime-lists][alal]
* AOD: [manami-project/anime-offline-database][aod]
* ARM: [kawaiioverflow/arm][arm]
* ATIP: [ryuuganime/aniTrakt-IndexParser][atip]
* BQA: [BeeeQueue/arm-server][bq]
* FAL: [Fribb/anime-lists][fal]

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

> [!NOTE]
>
> * The aliases are case-insensitive. You can use any of the aliases to get the
>   data you want.
> * 2K is the two-letter abbreviation for the platform.

|      Platform |  2K   | Aliases                                                                                         |
| ------------: | :---: | ----------------------------------------------------------------------------------------------- |
|       `anidb` | `ad`  | `adb`, `anidb.net`                                                                              |
|     `anilist` | `al`  | `anilist.co`                                                                                    |
| `animeplanet` | `ap`  | `anime-planet.com` `anime-planet`, `animeplanet.com`                                            |
|   `anisearch` | `as`  | `anisearch.com`, `anisearch.de`, `anisearch.it`, `anisearch.es`, `anisearch.fr`, `anisearch.jp` |
|      `annict` | `ac`  | `anc`, `act`, `annict.com`, `annict.jp`, `en.annict.com`                                        |
|        `imdb` | `im`  | `imdb.com`                                                                                      |
|       `kaize` | `kz`  | `kaize.io`                                                                                      |
|       `kitsu` | `kt`  | `kts`, `kitsu.io`, `kitsu.app`                                                                  |
|   `livechart` | `lc`  | `livechart.me`                                                                                  |
| `myanimelist` | `ma`  | `mal`, `myanimelist.net`                                                                        |
|   `nautiljon` | `nj`  | `ntj`, `nautiljon.com`                                                                          |
|      `notify` | `nf`  | `ntf`, `ntm`, `notifymoe`, `notify.moe`                                                         |
|   `otakotaku` | `oo`  | `otakotaku.com`                                                                                 |
|   `shikimori` | `sh`  | `shiki`, `shk`, `shikimori.me`, `shikimori.one`, `shikimori.org`                                |
|      `shoboi` | `sb`  | `shb`, `syb`, `shobocal`, `syoboi`, `syobocal`, `cal.syoboi.jp`                                 |
| `silveryasha` | `sy`  | `dbti`, `db.silveryasha.id`, `db.silveryasha.web.id`                                            |
|       `simkl` | `sm`  | `smk`, `simkl.com`, `animecountdown`, `animecountdown.com`                                      |
|  `themoviedb` | `tm`  | `tmdb`, `themoviedb.org`                                                                        |
|       `trakt` | `tr`  | `trk`, `trakt.tv`                                                                               |

<!-- markdownlint-enable MD034 MD013 -->

## Statistic

So far, AnimeAPI has indexed data from 17 databases, with details as follows:

<!-- updated -->
Last updated: 22 May 2025 05:18:03 UTC
<!-- /updated -->

<!-- counters -->
| Platform           |     Count |
| :----------------- | --------: |
| aniDB              |     13801 |
| AniList            |     21293 |
| Anime-Planet       |     25677 |
| aniSearch          |     19736 |
| Annict             |     11715 |
| IMDb               |      2268 |
| Kaize              |     23162 |
| Kitsu              |     21154 |
| LiveChart          |     11704 |
| MyAnimeList        |     28927 |
| Nautiljon          |      8619 |
| Notify.moe         |     16757 |
| Otak Otaku         |      2925 |
| Shikimori          |     28927 |
| Shoboi/Syobocal    |      5262 |
| Silver Yasha       |      4853 |
| SIMKL              |     13783 |
| The Movie Database |       591 |
| Trakt              |      4928 |
|                    |           |
| **Total**          | **35645** |
<!-- /counters -->

## Usage

To use this API, you can access the following base URLs:

* Latest/v3:
  
  ```http
  GET https://animeapi.my.id
  ```

All requests must be `GET`, and response always will be in JSON format.

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
    "timestamp": 1747891083,
    "iso": "2025-05-22T05:18:03.454963+00:00"
  },
  "contributors": [
    "nattadasu"
  ],
  "sources": [
    "kawaiioverflow/arm",
    "manami-project/anime-offline-database",
    "rensetsu/db.rensetsu.public-dump",
    "rensetsu/db.trakt.anitrakt",
    "https://kaize.io",
    "https://nautiljon.com",
    "https://otakotaku.com"
  ],
  "license": "AGPL-3.0-only AND MIT AND CC0-1.0+",
  "website": "https://animeapi.my.id",
  "counts": {
    "anidb": 13801,
    "anilist": 21293,
    "animeplanet": 25677,
    "anisearch": 19736,
    "annict": 11715,
    "imdb": 2268,
    "kaize": 23162,
    "kitsu": 21154,
    "livechart": 11704,
    "myanimelist": 28927,
    "nautiljon": 8619,
    "notify": 16757,
    "otakotaku": 2925,
    "shikimori": 28927,
    "shoboi": 5262,
    "silveryasha": 4853,
    "simkl": 13783,
    "themoviedb": 591,
    "trakt": 4928,
    "total": 35645
  },
  "endpoints": {
    "$comment": "The endpoints are stated in Python regex format. Platform aliases supported for direct lookup for platform specific endpoints (see ?P<alias> in regex).",
    "anidb": "/(?P<alias>anidb)/(?P<media_id>\\d+)",
    "anilist": "/(?P<alias>anilist)/(?P<media_id>\\d+)",
    "animeapi_dump": "/(anime(?:a|A)pi|aa)(?:\\\\\\.json)?",
    "animeapi_tsv": "/(anime(?:a|A)pi|aa).tsv",
    "animeplanet": "/(?P<alias>animeplanet)/(?P<media_id>[\\w\\-]+)",
    "anisearch": "/(?P<alias>anisearch)/(?P<media_id>\\d+)",
    "annict": "/(?P<alias>annict)/(?P<media_id>\\d+)",
    "heartbeat": "/(heartbeat|ping)",
    "imdb": "/(?P<alias>imdb)/(?P<media_id>tt[\\d]+)",
    "kaize": "/(?P<alias>kaize)/(?P<media_id>[\\w\\-]+)",
    "kitsu": "/(?P<alias>kitsu)/(?P<media_id>\\d+)",
    "livechart": "/(?P<alias>livechart)/(?P<media_id>\\d+)",
    "myanimelist": "/(?P<alias>myanimelist)/(?P<media_id>\\d+)",
    "nautiljon": "/(?P<alias>nautiljon)/(?P<media_id>[\\w\\+!\\-_\\(\\)\\[\\]]+)",
    "notify": "/(?P<alias>notify)/(?P<media_id>[\\w\\-_]+)",
    "otakotaku": "/(?P<alias>otakotaku)/(?P<media_id>\\d+)",
    "platform_dump": "/(?P<alias>[\\w\\-]+)(?:\\\\\\.json)?",
    "redirect": "/(redirect|rd)",
    "repo": "/",
    "schema": "/schema(?:\\\\\\.json)?",
    "shikimori": "/(?P<alias>shikimori)/(?P<media_id>\\d+)",
    "shoboi": "/(?P<alias>shoboi)/(?P<media_id>\\d+)",
    "silveryasha": "/(?P<alias>silveryasha)/(?P<media_id>\\d+)",
    "simkl": "/(?P<alias>simkl)/(?P<media_id>\\d+)",
    "status": "/status",
    "syobocal": "/(?P<alias>syobocal)/(?P<media_id>\\d+)",
    "themoviedb": "/(?P<alias>themoviedb)/movie/(?P<media_id>\\d+)",
    "trakt": "/(?P<alias>trakt)/(?P<media_type>show|movie)(s)?/(?P<media_id>\\d+)(?:/season(s)?/(?P<season_id>\\d+))?",
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
Updated on 05/22/2025 05:18:03 UTC
```
<!-- /updated-txt -->

</details>

### Get all items in Array

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

### Get All ID in Object/Dictionary format of each provider

HTTP Status Code: `302` (redirect to GitHub raw file URL)\
MIME Type: `application/json`

```http
GET /:platform.json
```

`:platform` can be one of the following listed in
[Supported Platforms and Aliases](#supported-platforms-and-aliases).

### Get All ID in Array/List format of each provider

HTTP Status Code: `302` (redirect to GitHub raw file URL)\
MIME Type: `application/json`

```http
GET /:platform().json
```

`:platform` can be one of the following listed in
[Supported Platforms and Aliases](#supported-platforms-and-aliases).

> [!NOTE]
>
> The `()` in the endpoint is not a typo, it's part of the endpoint.
> If you can't access the endpoint, try to encode the `()` to `%28%29`.

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
{
  "title": "Cowboy Bebop",
  "anidb": 23,
  "anilist": 1,
  "animeplanet": "cowboy-bebop",
  "anisearch": 1572,
  "annict": 360,
  "imdb": null,
  "kaize": "cowboy-bebop",
  "kaize_id": 265,
  "kitsu": 1,
  "livechart": 3418,
  "myanimelist": 1,
  "nautiljon": null,
  "nautiljon_id": null,
  "notify": "Tk3ccKimg",
  "otakotaku": 1149,
  "shikimori": 1,
  "shoboi": 538,
  "silveryasha": 2652,
  "simkl": 37089,
  "themoviedb": null,
  "trakt": 30857,
  "trakt_type": "shows",
  "trakt_season": 1
}
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
where `:mediatype` is only `movie` and `:mediaid` is the ID of the title in the
provider instead of typical `:provider/:mediaid` format.

##### Trakt

For Trakt, the ID is in the format of `:provider/:mediatype/:mediaid` where
`:mediatype` is either `movies` or `shows` and `:mediaid` is the ID of the title
in the provider instead of typical `:provider/:mediaid` format.

An ID on Trakt must in numerical value. If your application obtained slug as ID
instead, you can resolve/convert it to ID using following Trakt API endpoint:

```http
GET https://api.trakt.tv/search/trakt/<ID>?type=<movie|show>
```

> [!NOTE]
>
> The Trakt API requires an API key to access the endpoint. You can get the API
> key by registering on the Trakt website.

To get exact season mapping, append `/seasons/:season_inc` to the end of the ID,
where `:season_inc` is the season number of the title in the provider.

> [!WARNING]
>
> `/seasons/0` is invalid, and will return `400` status code.

For example, to get the ID of Mairimashita Iruma-kun Season 3, you can use:

```http
GET https://animeapi.my.id/trakt/shows/152334/seasons/3
```

<details>
<summary>Response example from Trakt</summary>

<!-- trakt152334 -->
```json
{
  "title": "Mairimashita! Iruma-kun 3rd Season",
  "anidb": 16627,
  "anilist": 139092,
  "animeplanet": "welcome-to-demon-school-iruma-kun-3",
  "anisearch": 16582,
  "annict": 8883,
  "imdb": null,
  "kaize": "mairimashita-iruma-kun-3rd-season",
  "kaize_id": 4989,
  "kitsu": 45154,
  "livechart": 10780,
  "myanimelist": 49784,
  "nautiljon": null,
  "nautiljon_id": null,
  "notify": "Okl9YtInR",
  "otakotaku": null,
  "shikimori": 49784,
  "shoboi": 6489,
  "silveryasha": 3702,
  "simkl": 1728821,
  "themoviedb": null,
  "trakt": 152334,
  "trakt_type": "shows",
  "trakt_season": 3
}
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

  |     Platform |  2K   | Aliases               | Additional Notes                            |
  | -----------: | :---: | --------------------- | :------------------------------------------ |
  |   `kurozora` | `kr`  | `krz`, `kurozora.app` | Requires Kurozora+ subscription and MAL ID  |
  | `letterboxd` | `lb`  | `letterboxd.com`      | Only available for movies, requires TMDB ID |
  |    `myanili` | `my`  | `myani.li`            | Requires MAL ID; a web app to manage list   |

  <!-- markdownlint-enable MD013 -->

* `:mediaid` is the ID of the anime in the platform. Please follow the instruction
  written in [Provider exclusive rules](#provider-exclusive-rules) to avoid any
  conflict during redirection.

#### Redirect: Parameters

In AnimeAPI, we use query parameters to specify the output of the API. The query
parameters are as follows:

<!-- markdownlint-disable MD013 -->

| Parameter  | Aliases      | Is Required | Description                                                                                                                        |
| ---------- | ------------ | ----------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| `platform` | `from`, `f`  | Yes         | The platform you want to get the data from.                                                                                        |
| `mediaid`  | `id`, `i`    | Yes         | The ID of the anime in the platform.                                                                                               |
| `target`   | `to`, `t`    | No          | The platform you want to redirect to. If you don't specify this parameter, the API will redirect to specified platform's homepage. |
| `israw`    | `raw`, `r`   | No          | As long as this parameter is present, the API will return the raw URL instead of redirecting.                                     |

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
Location: https://shikimori.me/animes/52991
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
            "themoviedb_season": {
              "type": "number"
            }
          },
          "required": [
            "themoviedb_season"
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
          "description": "Nautiljon slug in plus, website: https://www.nautiljon.com/",
          "title": "Nautiljon"
        },
        "nautiljon_id": {
          "$ref": "#/definitions/numbernull",
          "description": "Nautiljon ID in integer format, used internally",
          "title": "Nautiljon ID"
        },
        "notify": {
          "$ref": "#/definitions/stringnull",
          "description": "Notify.moe Base64 ID, website: https://notify.moe/",
          "pattern": "^[a-zA-Z0-9\\-\\_]+$",
          "title": "Notify.moe"
        },
        "otakotaku": {
          "$ref": "#/definitions/numbernull",
          "description": "Otak Otaku ID, website: https://otakotaku.com/",
          "title": "Otak Otaku"
        },
        "shikimori": {
          "$ref": "#/definitions/numbernull",
          "description": "Shikimori ID (nonprefixed), based on MyAnimeList ID. Remove prefix if found on the ID, website: https://shikimori.one/",
          "title": "Shikimori/Шикимори"
        },
        "shoboi": {
          "$ref": "#/definitions/numbernull",
          "description": "Shoboi ID, website: http://cal.syoboi.jp/",
          "title": "Shoboi/Syobocal/しょぼいカレンダー"
        },
        "silveryasha": {
          "$ref": "#/definitions/numbernull",
          "description": "Silveryasha ID, website: https://db.silveryasha.id/",
          "title": "Silveryasha"
        },
        "simkl": {
          "$ref": "#/definitions/numbernull",
          "description": "SIMKL ID, website: https://simkl.com/",
          "title": "SIMKL"
        },
        "themoviedb": {
          "$ref": "#/definitions/numbernull",
          "description": "The Movie Database ID, website: https://www.themoviedb.org/",
          "title": "The Movie Database (TMDB)"
        },
        "themoviedb_season": {
          "$ref": "#/definitions/numbernull",
          "description": "The Movie Database season number, only used if themoviedb_type is 'shows', else null",
          "title": "The Movie Database (TMDB) Season"
        },
        "themoviedb_type": {
          "$ref": "#/definitions/themoviedbtype",
          "description": "The Movie Database type, either 'movie' or 'tv'",
          "title": "The Movie Database (TMDB) Type"
        },
        "title": {
          "description": "Title of the anime",
          "title": "Title",
          "type": "string"
        },
        "trakt": {
          "$ref": "#/definitions/numbernull",
          "description": "Trakt ID, slug not supported, website: https://trakt.tv/",
          "title": "Trakt"
        },
        "trakt_season": {
          "$ref": "#/definitions/numbernull",
          "description": "Trakt season number, only used if trakt_type is 'shows', else null",
          "title": "Trakt Season"
        },
        "trakt_type": {
          "$ref": "#/definitions/trakttype",
          "description": "Trakt type, either 'movies' or 'shows'",
          "title": "Trakt Type"
        }
      },
      "required": [
        "title",
        "anidb",
        "anilist",
        "animeplanet",
        "anisearch",
        "annict",
        "imdb",
        "kaize",
        "kaize_id",
        "kitsu",
        "livechart",
        "myanimelist",
        "nautiljon",
        "nautiljon_id",
        "notify",
        "otakotaku",
        "shikimori",
        "shoboi",
        "silveryasha",
        "simkl",
        "themoviedb",
        "trakt",
        "trakt_type",
        "trakt_season"
      ],
      "title": "Anime Schema",
      "type": "object"
    },
    "numbernull": {
      "$comment": "Type: number or null",
      "anyOf": [
        {
          "type": "number"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Type: this field value is either number or null",
      "title": "Number or Null"
    },
    "stringnull": {
      "$comment": "Type: string or null",
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Type: this field value is either string or null",
      "title": "String or Null"
    },
    "themoviedbtype": {
      "$comment": "Type: 'movie', 'tv', or null",
      "anyOf": [
        {
          "enum": [
            "movie",
            "tv"
          ],
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Type: this field value is either an enum of['movie', 'tv'], or null",
      "title": "The Movie Database Type"
    },
    "trakttype": {
      "$comment": "Type: 'movies', 'shows', or null",
      "anyOf": [
        {
          "enum": [
            "movies",
            "shows"
          ],
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Type: this field value is either an enum of['movies', 'shows'], or null",
      "title": "Trakt Type"
    }
  },
  "description": "This schema is used to validate the JSON response from AnimeAPI V3. Schema is not backward compatible with previous versions. Website: https://animeapi.my.id",
  "oneOf": [
    {
      "$comment": "Use this schema if you want to validate an array of anime",
      "description": "Schema for array of anime",
      "items": {
        "$ref": "#/definitions/anime"
      },
      "title": "Array of Anime",
      "type": "array"
    },
    {
      "$comment": "Use this schema if you want to validate an object known in each provider",
      "description": "Schema for anime object",
      "oneOf": [
        {
          "$ref": "#/definitions/anime"
        },
        {
          "additionalProperties": {
            "$ref": "#/definitions/anime"
          }
        }
      ],
      "title": "Anime Object",
      "type": "object"
    }
  ],
  "title": "JSON Schema for AnimeAPI V3"
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

* [GitHub:kawaiioverflow/arm][arm]
* [GitHub:manami-project/anime-offline-database][aod]
* [GitHub:ryuuganime/aniTrakt-IndexParser][atip], which an automatic parser of
  [AniTrakt][atrk] index page.
* [Nautiljon][ntj]
* [Kaize][kz]
* [Otak Otaku][oo]
* [Silver-Yasha][sy]

<!-- Reference -->
[adb]: https://anidb.net
[al]: https://anilist.co
[alal]: https://github.com/Anime-Lists/anime-lists
[an]: https://annict.com
[aod]: https://github.com/manami-project/anime-offline-database
[ap]: https://anime-planet.com
[arm]: https://github.com/kawaiioverflow/arm
[as]: https://anisearch.com
[atip]: https://github.com/ryuuganime/aniTrakt-IndexParser
[atrk]: https://anitrakt.huere.net/
[bgm]: https://bgm.tv
[bq]: https://github.com/BeeeQueue/arm-server
[fal]: https://github.com/Fribb/anime-lists
[hato]: https://github.com/Atelier-Shiori/Hato
[imdb]: https://imdb.com
[ko]: https://github.com/kawaiioverflow
[kts]: https://kitsu.app
[kz]: https://kaize.io
[lc]: https://livechart.me
[mal]: https://myanimelist.net
[mp]: https://github.com/manami-project
[ntf]: https://notify.moe
[ntj]: https://nautiljon.com
[oo]: https://otakotaku.com
[shb]: https://cal.syoboi.jp
[shk]: https://shikimori.me
[smk]: https://simkl.com
[sy]: https://db.silveryasha.id
[tmdb]: https://themoviedb.org
[trk]: https://trakt.tv
[tvdb]: https://thetvdb.com
[tvtm]: https://tvtime.com
[f:adb]: https://favicone.com/anidb.net
[f:al]: https://www.google.com/s2/favicons?domain=anilist.co&sz=16
[f:an]: https://www.google.com/s2/favicons?domain=annict.com&sz=16
[f:ap]: https://www.google.com/s2/favicons?domain=anime-planet.com&sz=16
[f:as]: https://www.google.com/s2/favicons?domain=anisearch.com&sz=16
[f:bgm]: https://favicone.com/bgm.tv
[f:imdb]: https://www.google.com/s2/favicons?domain=imdb.com&sz=16
[f:kts]: https://favicone.com/kitsu.app
[f:kz]: https://www.google.com/s2/favicons?domain=kaize.io&sz=16
[f:lc]: https://www.google.com/s2/favicons?domain=livechart.me&sz=16
[f:mal]: https://www.google.com/s2/favicons?domain=myanimelist.net&sz=16
[f:ntf]: https://www.google.com/s2/favicons?domain=notify.moe&sz=16
[f:ntj]: https://www.google.com/s2/favicons?domain=nautiljon.com&sz=16
[f:oo]: https://www.google.com/s2/favicons?domain=otakotaku.com&sz=16
[f:shb]: https://www.google.com/s2/favicons?domain=cal.syoboi.jp&sz=16
[f:shk]: https://www.google.com/s2/favicons?domain=shikimori.me&sz=16
[f:smk]: https://www.google.com/s2/favicons?domain=simkl.com&sz=16
[f:sy]: https://www.google.com/s2/favicons?domain=db.silveryasha.id&sz=16
[f:tmdb]: https://www.google.com/s2/favicons?domain=themoviedb.org&sz=16
[f:trk]: https://www.google.com/s2/favicons?domain=trakt.tv&sz=16
[f:tvdb]: https://www.google.com/s2/favicons?domain=thetvdb.com&sz=16
[f:tvtm]: https://www.google.com/s2/favicons?domain=tvtime.com&sz=16
