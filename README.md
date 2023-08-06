<!-- markdownlint-disable MD028 MD033 -->
<!-- omit in toc -->
# nattadasu's AnimeAPI RESTful API

AnimeAPI (also known as aniApi) is a RESTful API that provides anime relation
mapping across multiple anime databases. It mainly focuses on providing
relations between anime titles from different databases.

This project was derived on [anime-offline-database][aod] by [manami-project][mp]
and [arm] by [kawaiioverflow][ko], while adding support for more databases.

<!-- omit in toc -->
## Table of Contents

<details>
<summary>Click to expand</summary>

* [Why use AnimeAPI?](#why-use-animeapi)
* [Statistic](#statistic)
* [Usage](#usage)
  * [Differences between v1, v2, and v3](#differences-between-v1-v2-and-v3)
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
      * [Shikimori](#shikimori)
      * [The Movie DB](#the-movie-db)
      * [Trakt](#trakt)
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

| Highlights                      | AnimeAPI                               | [ARM][arm]                  | [BQA][bq]          | [Hato][hato]              | [SIMKL][smk]            | [Trakt][trk] | [AOD][aod]                                                          | [FAL][fal]    | [ALAL][alal]                           | [ATIP][atip]     |
| ------------------------------- | -------------------------------------- | --------------------------- | ------------------ | ------------------------- | ----------------------- | ------------ | ------------------------------------------------------------------- | ------------- | -------------------------------------- | ---------------- |
| License                         | AGPL-3.0                               | MIT                         | AGPL-3.0           | Apache-2.0                | Proprietary             | Proprietary  | AGPL-3.0                                                            | Unknown       | Unknown                                | Unknown          |
| Access                          | Public                                 | Public                      | Public             | Paid, API Key             | API Key                 | API Key      | Public                                                              | Public        | Public                                 | Public           |
| Format                          | REST                                   | Node.js Package, REST, JSON | REST               | REST                      | REST                    | REST         | JSON                                                                | JSON          | XML                                    | JSON             |
| Main Languages                  | Python, JSON, TSV                      | JavaScript, JSON            | TypeScript, SQLite | C#, MySQL, PostgreSQL     | -                       | -            | JSON                                                                | JSON          | XLSL, XML                              | PowerShell, JSON |
| Base Data                       | AOD, ARM, ATIP, FAL<br>![f:kz] ![f:oo] | ![f:ntf]                    | FAL                | ![f:al] ![f:kts] ![f:ntf] | ![f:tvdb] ![f:adb]      | ![f:tmdb]    | ![f:mal] ![f:al] ![f:adb] ![f:kts] ![f:lc] ![f:as] ![f:ap] ![f:ntf] | AOD, ALAL     | ![f:adb] ![f:tvdb] ![f:tmdb] ![f:imdb] | [aniTrakt][atrk] |
| Rate Limit                      | -                                      | -                           | -                  | -                         | 1000/day for unverified | 1000/5 mins  | Unapplicable                                                        | Unapplicable  | Unapplicable                           | Unapplicable     |
| Is Building Process Public?     | Yes                                    | No                          | No                 | No                        | -                       | -            | No                                                                  | Yes           | No                                     | Yes              |
|                                 |                                        |                             |                    |                           |                         |              |                                                                     |               |                                        |                  |
| Anime Title                     | ✔                                      | ❌                           | ❌                  | ❌                         | ✔                       | ✔            | ✔                                                                   | ❌             | ✔                                      | ✔                |
| [![f:adb] aniDB][adb]           | ✔                                      | ❌                           | ✔                  | ✔                         | ✔                       | ❌            | ✔                                                                   | ✔             | ❌                                      | ❌                |
| [![f:al] AniList][al]           | ✔                                      | ✔                           | ✔                  | ✔                         | ✔ Result Only           | ❌            | ✔                                                                   | ✔             | ❌                                      | ❌                |
| [![f:ap] Anime-Planet][ap]      | ✔                                      | ❌                           | ✔                  | ❌                         | ✔ Result Only           | ❌            | ✔                                                                   | ✔             | ❌                                      | ❌                |
| [![f:as] AniSearch][as]         | ✔                                      | ❌                           | ✔                  | ❌                         | ✔ Result Only           | ❌            | ✔                                                                   | ✔             | ❌                                      | ❌                |
| [![f:an] Annict][an]            | ✔                                      | ✔                           | ❌                  | ❌                         | ❌                       | ❌            | ❌                                                                   | ❌             | ❌                                      | ❌                |
| [![f:bgm] Bangumi][bgm]         | ❌                                      | ❌                           | ❌                  | ❌                         | ❌                       | ❌            | ❌                                                                   | ❌             | ❌                                      | ❌                |
| [![f:imdb] IMDB][imdb]          | ✔                                      | ❌                           | ✔                  | ❌                         | ✔                       | ✔            | ❌                                                                   | ✔             | ✔                                      | ❌                |
| [![f:kz] Kaize][kz]             | ✔                                      | ❌                           | ❌                  | ❌                         | ❌                       | ❌            | ❌                                                                   | ❌             | ❌                                      | ❌                |
| [![f:kts] Kitsu][kts]           | ✔                                      | ❌                           | ✔                  | ✔                         | ✔ Result Only           | ❌            | ✔                                                                   | ✔             | ❌                                      | ❌                |
| [![f:lc] LiveChart][lc]         | ✔                                      | ❌                           | ✔                  | ❌                         | ✔ Result Only           | ❌            | ✔                                                                   | ✔             | ❌                                      | ❌                |
| [![f:mal] MyAnimeList][mal]     | ✔                                      | ✔                           | ✔                  | ✔                         | ✔                       | ❌            | ✔                                                                   | ✔             | ❌                                      | ✔                |
| [![f:ntj] Nautiljon][ntj]       | ❌                                      | ❌                           | ❌                  | ❌                         | ❌                       | ❌            | ❌                                                                   | ❌             | ❌                                      | ❌                |
| [![f:ntf] Notify][ntf]          | ✔                                      | ❌                           | ✔                  | ✔                         | ❌                       | ❌            | ✔                                                                   | ✔             | ❌                                      | ❌                |
| [![f:oo] Otak Otaku][oo]        | ✔                                      | ❌                           | ❌                  | ❌                         | ❌                       | ❌            | ❌                                                                   | ❌             | ❌                                      | ❌                |
| [![f:shk] Shikimori][shk]       | ✔                                      | ✔ via MAL                   | ✔ via MAL          | ✔ via MAL                 | ✔ via MAL               | ❌            | ✔ via MAL                                                           | ✔ via MAL     | ❌                                      | ✔ via MAL        |
| [![f:shb] Shoboi Calendar][shb] | ✔                                      | ✔                           | ❌                  | ❌                         | ❌                       | ❌            | ❌                                                                   | ❌             | ❌                                      | ❌                |
| [![f:sy] SilverYasha DBTI][sy]  | ✔                                      | ❌                           | ❌                  | ❌                         | ❌                       | ❌            | ❌                                                                   | ❌             | ❌                                      | ❌                |
| [![f:smk] SIMKL][smk]           | ✔ via IMDb                             | ❌                           | ❌                  | ❌                         | ✔                       | ❌            | ❌                                                                   | ❌             | ❌                                      | ❌                |
| [![f:tmdb] TMDB][tmdb]          | ✔, only movie                          | ❌                           | ✔, only movie      | ❌                         | ✔                       | ✔            | ❌                                                                   | ✔, only movie | ✔                                      | ❌                |
| [![f:trk] Trakt][trk]           | ✔                                      | ❌                           | ❌                  | ❌                         | ❌                       | ✔            | ❌                                                                   | ❌             | ❌                                      | ✔                |
| [![f:tvdb] TVDB][tvdb]          | ❌                                      | ❌                           | ❌                  | ❌                         | ✔                       | ✔            | ❌                                                                   | ✔             | ✔                                      | ❌                |
| [![f:tvtm] TVTime][tvtm]        | ❌                                      | ❌                           | ❌                  | ❌                         | ✔ via TVDB              | ✔ via TVDB   | ❌                                                                   | ✔ via TVDB    | ✔ via TVDB                             | ❌                |

<!-- omit in toc -->
### Legends

* ALAL: [Anime-Lists/anime-lists][alal]
* AOD: [manami-project/anime-offline-database][aod]
* ARM: [kawaiioverflow/arm][arm]
* ATIP: [ryuuganime/aniTrakt-IndexParser][atip]
* BQA: [BeeeQueue/arm-server][bq]
* FAL: [Fribb/anime-lists][fal]

## Statistic

So far, AnimeAPI has indexed data from 17 databases, with details as follows:

<!-- updated -->
Last updated: 06 August 2023 05:15:07 UTC
<!-- /updated -->

<!-- counters -->
| Platform           |            ID |     Count |
| :----------------- | ------------: | --------: |
| aniDB              |       `anidb` |     12898 |
| AniList            |     `anilist` |     18969 |
| Anime-Planet       | `animeplanet` |     22993 |
| aniSearch          |   `anisearch` |     17921 |
| Annict             |      `annict` |      8922 |
| IMDb               |        `imdb` |      2256 |
| Kaize              |       `kaize` |     22958 |
| Kitsu              |       `kitsu` |     19332 |
| LiveChart          |   `livechart` |     10860 |
| MyAnimeList        | `myanimelist` |     25288 |
| Notify.moe         |      `notify` |     15835 |
| Otak Otaku         |   `otakotaku` |      2544 |
| Shikimori          |   `shikimori` |     25288 |
| Shoboi/Syobocal    |      `shoboi` |      4713 |
| Silver Yasha       | `silveryasha` |      3982 |
| The Movie Database |  `themoviedb` |       280 |
| Trakt              |       `trakt` |      4451 |
|                    |               |           |
|                    |     **Total** | **31695** |
<!-- /counters -->

## Usage

To use this API, you can access the following base URLs:

* Latest/v3:
  
  ```http
  GET https://animeapi.my.id
  ```

* v2:
  
  ```http
  GET https://aniapi.nattadasu.my.id
  ```

All requests must be `GET`, and response always will be in JSON format.

> **Warning**
>
> In `v2`, If an entry can not be found, the API will return 404 status code
> and GitHub Pages' default 404 page. This is because `v2` and earlier versions
> are hosted on GitHub Pages and API was a mock RESTful response.

### Differences between v1, v2, and v3

AnimeAPI has 3 versions, which are `v1`, `v2`, and `v3`. The differences between
each version are as follows:

|                    | v1                         | v2                               | v3                                       |
| ------------------ | -------------------------- | -------------------------------- | ---------------------------------------- |
| Base URL           | *inactive*                 | `https://aniapi.nattadasu.my.id` | `https://animeapi.my.id`                 |
| Deprecated?        | ✔                          | Maintenance                      | ❌                                        |
| Host               | -                          | GitHub Pages                     | Vercel                                   |
| Language           | PowerShell                 | Python                           | Python                                   |
| Framework          | -                          | GitHub Pages                     | Flask                                    |
| Database           | JSON                       | JSON                             | JSON                                     |
| Expected MIME Type | `application/octet-stream` | `application/octet-stream`       | `application/json`                       |
| Status Codes       | `200`, `404`               | `200`, `404`                     | `200`, `302`, `304`, `400`, `404`, `500` |
| Response Schema    | -                          | -                                | [JSON Schema](#json-schema)              |
| Documented         | ❌                          | ✔                                | ✔                                        |

### Get status and statistics

> **Note**: This endpoint is only available on v3

MIME Type: `application/json`

```http
GET /status
```

<details>
<summary>Response example</summary>

<!-- status -->
```json
{
  "mainrepo": "https://github.com/nattadasu/animeApi/tree/v3",
  "updated": {
    "timestamp": 1691298907,
    "iso": "2023-08-06T05:15:07.434318+00:00"
  },
  "contributors": [
    "nattadasu"
  ],
  "sources": [
    "manami-project/anime-offline-database",
    "kawaiioverflow/arm",
    "ryuuganime/aniTrakt-IndexParser",
    "https://db.silveryasha.web.id",
    "https://kaize.io",
    "https://otakotaku.com"
  ],
  "license": "AGPL-3.0",
  "website": "https://animeapi.my.id",
  "counts": {
    "anidb": 12898,
    "anilist": 18969,
    "animeplanet": 22993,
    "anisearch": 17921,
    "annict": 8922,
    "imdb": 2256,
    "kaize": 22958,
    "kitsu": 19332,
    "livechart": 10860,
    "myanimelist": 25288,
    "notify": 15835,
    "otakotaku": 2544,
    "shikimori": 25288,
    "shoboi": 4713,
    "silveryasha": 3982,
    "themoviedb": 280,
    "trakt": 4451,
    "total": 31695
  },
  "endpoints": {
    "$comment": "The endpoints are stated in Python regex format",
    "anidb": "/anidb/(?P<media_id>\\d+)",
    "anilist": "/anilist/(?P<media_id>\\d+)",
    "animeapi_tsv": "/anime(a|A)pi.tsv",
    "animeplanet": "/animeplanet/(?P<media_id>[\\w\\-]+)",
    "anisearch": "/anisearch/(?P<media_id>\\d+)",
    "annict": "/annict/(?P<media_id>\\d+)",
    "heartbeat": "/(heartbeat|ping)",
    "imdb": "/imdb/(?P<media_id>tt[\\d]+)",
    "kaize": "/kaize/(?P<media_id>[\\w\\-]+)",
    "kitsu": "/kitsu/(?P<media_id>\\d+)",
    "livechart": "/livechart/(?P<media_id>\\d+)",
    "myanimelist": "/myanimelist/(?P<media_id>\\d+)",
    "notify": "/notify/(?P<media_id>[\\w\\-_]+)",
    "otakotaku": "/otakotaku/(?P<media_id>\\d+)",
    "repo": "/",
    "schema": "/schema(?:.json)?",
    "shikimori": "/shikimori/(?P<media_id>\\d+)",
    "shoboi": "/shoboi/(?P<media_id>\\d+)",
    "silveryasha": "/silveryasha/(?P<media_id>\\d+)",
    "status": "/status",
    "syobocal": "/syobocal/(?P<media_id>\\d+)",
    "themoviedb": "/themoviedb/movie/(?P<media_id>\\d+)",
    "trakt": "/trakt/(?P<media_type>show|movie)(s)?/(?P<media_id>\\d+)(?:/season(s)?/(?P<season_id>\\d+))?",
    "updated": "/updated"
  }
}
```
<!-- /status -->

</details>

### Get latency report

> **Note**: This endpoint is only available on v3

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
```json
Updated on 08/06/2023 05:15:07 UTC
```
<!-- /updated-txt -->

</details>

### Get all items in Array

MIME Type: `application/json`

```http
GET /animeApi.json
```

On `v3`, you will automatically redirected to GitHub raw file URL of the
provider's JSON file. Make sure to allow `302` and `304` status code on your
application if you want to use this endpoint.

### Fetch all item as TSV (Tab Separated Values) file

> **Note**: This endpoint is only available on v3

> **Note**: Use this endpoint if you want to import the data to spreadsheet.

MIME Type: `text/tab-separated-values`

```http
GET /animeApi.tsv
```

### Get All ID in Object/Dictionary format of each provider

MIME Type: `application/json`

```http
GET /:platform.json
```

`:platform` can be one of the following:

`anidb`, `anilist`, `animeplanet`, `anisearch`, `annict`, `kaize`, `kitsu`,
`livechart`, `myanimelist`, `notify`, `otakotaku`, `shikimori`, `shoboi`,
`silveryasha`, `trakt`

Additionally, on `v3`, you can use `imdb` or `themoviedb` as `:platform` to get
ID from IMDB or TMDB respectively.

On `v3`, you will automatically redirected to GitHub raw file URL of the
provider's JSON file. Make sure to allow `302` and `304` status code on your
application if you want to use this endpoint.

### Get All ID in Array/List format of each provider

MIME Type: `application/json`

```http
GET /:platform().json
```

`:platform` can be one of the following:

`anidb`, `anilist`, `animeplanet`, `anisearch`, `annict`, `kaize`, `kitsu`,
`livechart`, `myanimelist`, `notify`, `otakotaku`, `shikimori`, `shoboi`,
`silveryasha`, `trakt`

Additionally, on `v3`, you can use `imdb` or `themoviedb` as `:platform` to get
ID from IMDB or TMDB respectively.

> **Note**: The `()` in the endpoint is not a typo, it's part of the endpoint.
> If you can't access the endpoint, try to encode the `()` to `%28%29`.

On `v3`, you will automatically redirected to GitHub raw file URL of the
provider's JSON file. Make sure to allow `302` and `304` status code on your
application if you want to use this endpoint.

### Get anime relation mapping data

MIME Type: `application/json` on `v3`, `application/octet-stream` on `v2`

```http
GET /:platform/:mediaid
```

* `:platform` can be one of the following:

  `anidb`, `anilist`, `animeplanet`, `anisearch`, `annict`, `kaize`, `kitsu`,
  `livechart`, `myanimelist`, `notify`, `otakotaku`, `shikimori`, `shoboi`,
  `silveryasha`, `trakt`

  Additionally, on `v3`, you can use `imdb` or `themoviedb` as `:platform` to
  get ID from IMDB or TMDB respectively.

* `:mediaid` is the ID of the anime in the platform.

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
  "notify": "Tk3ccKimg",
  "otakotaku": 1149,
  "shikimori": 1,
  "shoboi": 538,
  "silveryasha": 2652,
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
GET https://kitsu.io/api/edge/anime?filter[slug]=<ID>
```

For example, if you want to get anime data from Kitsu with slug `cowboy-bebop`,
you can use the following endpoint:

```http
GET https://kitsu.io/api/edge/anime?filter[slug]=cowboy-bebop
```

The response will be in JSON format, and you can get the ID from `data[0].id`

##### Shikimori

`shikimori` IDs are basically the same as `myanimelist` IDs. If you get a 404
status code, remove any alphabetical prefix from the ID and try again.

For example: `z218` → `218`

##### The Movie DB

For The Movie DB (TMDB), the ID is in the format of `:provider/:mediatype/:mediaid`
where `:mediatype` is only `movie` and `:mediaid` is the ID of the title in the
provider instead of typical `:provider/:mediaid` format.

Unfortunately, due to some issues reported in [Anime-Lists/anime-lists][alal],
the relation mapping data for TMDB is limited to `movie` only.

##### Trakt

For Trakt, the ID is in the format of `:provider/:mediatype/:mediaid` where
`:mediatype` is either `movies` or `shows` and `:mediaid` is the ID of the title
in the provider instead of typical `:provider/:mediaid` format.

An ID on Trakt must in numerical value. If your application obtained slug as ID
instead, you can resolve/convert it to ID using following Trakt API endpoint:

```http
GET https://api.trakt.tv/search/trakt/<ID>?type=<movie|show>
```

To get exact season mapping, append `/seasons/:season_inc` to the end of the ID,
where `:season_inc` is the season number of the title in the provider.

> **Warning**
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
  "notify": "Okl9YtInR",
  "otakotaku": 2305,
  "shikimori": 49784,
  "shoboi": 6489,
  "silveryasha": 3702,
  "themoviedb": null,
  "trakt": 152334,
  "trakt_type": "shows",
  "trakt_season": 3
}
```
<!-- /trakt152334 -->

</details>

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

<!-- jsonschema -->
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "JSON Schema for animeApi base, support for v2 and v3",
  "definitions": {
    "stringnull": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "$comment": "Type: string or null"
    },
    "numbernull": {
      "anyOf": [
        {
          "type": "number"
        },
        {
          "type": "null"
        }
      ],
      "$comment": "Type: number or null"
    },
    "trakttype": {
      "anyOf": [
        {
          "type": "string",
          "enum": [
            "movies",
            "shows"
          ]
        },
        {
          "type": "null"
        }
      ],
      "$comment": "Type: 'movies', 'shows', or null"
    },
    "themoviedbtype": {
      "anyOf": [
        {
          "type": "string",
          "enum": [
            "movie",
            "tv"
          ]
        },
        {
          "type": "null"
        }
      ],
      "$comment": "Type: 'movie', 'tv', or null"
    },
    "anime": {
      "$comment": "Interface: Anime",
      "type": "object",
      "properties": {
        "title": {
          "title": "Title",
          "description": "Title of the anime",
          "type": "string"
        },
        "anidb": {
          "title": "aniDB",
          "description": "aniDB ID, website: https://anidb.net/",
          "$ref": "#/definitions/numbernull"
        },
        "anilist": {
          "title": "AniList",
          "description": "AniList ID, website: https://anilist.co/",
          "$ref": "#/definitions/numbernull"
        },
        "animeplanet": {
          "title": "Anime-Planet",
          "description": "Anime-Planet slug, website: https://www.anime-planet.com/",
          "$ref": "#/definitions/stringnull",
          "pattern": "^[a-z0-9\\-]+$"
        },
        "anisearch": {
          "title": "AniSearch",
          "description": "AniSearch ID, website: https://www.anisearch.com/, https://anisearch.de, https://anisearch.it, https://anisearch.es, https://anisearch.fr, https://anisearch.jp",
          "$ref": "#/definitions/numbernull"
        },
        "annict": {
          "title": "Annict",
          "description": "Annict ID, website: https://annict.com/, https://en.annict.com/, https://annict.jp/",
          "$ref": "#/definitions/numbernull"
        },
        "imdb": {
          "title": "IMDb",
          "description": "IMDb ID, website: https://www.imdb.com/",
          "$ref": "#/definitions/stringnull",
          "pattern": "^tt[\\d]+$"
        },
        "kaize": {
          "title": "Kaize",
          "description": "Kaize slug, website: https://kaize.io/",
          "$ref": "#/definitions/stringnull",
          "pattern": "^[a-z0-9\\-]+$"
        },
        "kaize_id": {
          "title": "Kaize ID",
          "description": "Kaize ID in integer format, not recommended as some entry can't be found its ID compared to slug",
          "$ref": "#/definitions/numbernull"
        },
        "kitsu": {
          "title": "Kitsu",
          "description": "Kitsu ID in integer, slug not suppported, website: https://kitsu.io/",
          "$ref": "#/definitions/numbernull"
        },
        "livechart": {
          "title": "LiveChart",
          "description": "LiveChart ID, website: https://www.livechart.me/",
          "$ref": "#/definitions/numbernull"
        },
        "myanimelist": {
          "title": "MyAnimeList",
          "description": "MyAnimeList ID, website: https://myanimelist.net/",
          "$ref": "#/definitions/numbernull"
        },
        "notify": {
          "title": "Notify.moe",
          "description": "Notify.moe Base64 ID, website: https://notify.moe/",
          "$ref": "#/definitions/stringnull",
          "pattern": "^[a-zA-Z0-9\\-\\_]+$"
        },
        "otakotaku": {
          "title": "Otak Otaku",
          "description": "Otak Otaku ID, website: https://otakotaku.com/",
          "$ref": "#/definitions/numbernull"
        },
        "shikimori": {
          "title": "Shikimori/Шикимори",
          "description": "Shikimori ID (nonprefixed), based on MyAnimeList ID. Remove prefix if found on the ID, website: https://shikimori.one/",
          "$ref": "#/definitions/numbernull"
        },
        "shoboi": {
          "title": "Shoboi/Syobocal/しょぼいカレンダー",
          "description": "Shoboi ID, website: http://cal.syoboi.jp/",
          "$ref": "#/definitions/numbernull"
        },
        "silveryasha": {
          "title": "Silveryasha",
          "description": "Silveryasha ID, website: https://db.silveryasha.web.id/",
          "$ref": "#/definitions/numbernull"
        },
        "themoviedb": {
          "title": "The Movie Database (TMDB)",
          "description": "The Movie Database ID, website: https://www.themoviedb.org/",
          "$ref": "#/definitions/numbernull"
        },
        "themoviedb_type": {
          "title": "The Movie Database (TMDB) Type",
          "description": "The Movie Database type, either 'movies' or 'shows'",
          "$ref": "#/definitions/themoviedbtype"
        },
        "themoviedb_season": {
          "title": "The Movie Database (TMDB) Season",
          "description": "The Movie Database season number, only used if themoviedb_type is 'shows', else null",
          "$ref": "#/definitions/numbernull"
        },
        "trakt": {
          "title": "Trakt",
          "description": "Trakt ID, slug not supported, website: https://trakt.tv/",
          "$ref": "#/definitions/numbernull"
        },
        "trakt_type": {
          "title": "Trakt Type",
          "description": "Trakt type, either 'movies' or 'shows'",
          "$ref": "#/definitions/trakttype"
        },
        "trakt_season": {
          "title": "Trakt Season",
          "description": "Trakt season number, only used if trakt_type is 'shows', else null",
          "$ref": "#/definitions/numbernull"
        }
      },
      "required": [
        "title",
        "anidb",
        "anilist",
        "animeplanet",
        "anisearch",
        "annict",
        "kaize",
        "kitsu",
        "livechart",
        "myanimelist",
        "notify",
        "otakotaku",
        "shikimori",
        "shoboi",
        "silveryasha",
        "trakt",
        "trakt_type",
        "trakt_season"
      ],
      "additionalProperties": false
    }
  },
  "oneOf": [
    {
      "$comment": "Use this schema if you want to validate an array of anime",
      "type": "array",
      "items": {
        "$ref": "#/definitions/anime"
      }
    },
    {
      "$comment": "Use this schema if you want to validate an object known in each provider",
      "type": "object",
      "additionalProperties": {
        "$ref": "#/definitions/anime"
      },
      "minProperties": 1
    }
  ]
}
```
<!-- /jsonschema -->

</details>

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
    notify:            StringNull; // Base64 based
    otakotaku:         NumberNull;
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
    notify:            StringNull  # Base64 based
    otakotaku:         NumberNull
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
[bgm]: https://bangumi.tv
[bq]: https://github.com/BeeeQueue/arm-server
[fal]: https://github.com/Fribb/anime-lists
[hato]: https://github.com/Atelier-Shiori/Hato
[imdb]: https://imdb.com
[ko]: https://github.com/kawaiioverflow
[kts]: https://kitsu.io
[kz]: https://kaize.moe
[lc]: https://livechart.me
[mal]: https://myanimelist.net
[mp]: https://github.com/manami-project
[ntf]: https://notify.moe
[ntj]: https://nautiljon.com
[oo]: https://otakotaku.com
[shb]: https://cal.syoboi.jp
[shk]: https://shikimori.me
[smk]: https://simkl.com
[sy]: https://db.silveryasha.web.id
[tmdb]: https://themoviedb.org
[trk]: https://trakt.tv
[tvdb]: https://thetvdb.com
[tvtm]: https://tvtime.com
[f:adb]: https://www.google.com/s2/favicons?domain=anidb.net&sz=16
[f:al]: https://www.google.com/s2/favicons?domain=anilist.co&sz=16
[f:an]: https://www.google.com/s2/favicons?domain=annict.com&sz=16
[f:ap]: https://www.google.com/s2/favicons?domain=anime-planet.com&sz=16
[f:as]: https://www.google.com/s2/favicons?domain=anisearch.com&sz=16
[f:bgm]: https://www.google.com/s2/favicons?domain=bangumi.tv&sz=16
[f:imdb]: https://www.google.com/s2/favicons?domain=imdb.com&sz=16
[f:kts]: https://www.google.com/s2/favicons?domain=kitsu.io&sz=16
[f:kz]: https://www.google.com/s2/favicons?domain=kaize.io&sz=16
[f:lc]: https://www.google.com/s2/favicons?domain=livechart.me&sz=16
[f:mal]: https://www.google.com/s2/favicons?domain=myanimelist.net&sz=16
[f:ntf]: https://www.google.com/s2/favicons?domain=notify.moe&sz=16
[f:ntj]: https://www.google.com/s2/favicons?domain=nautiljon.com&sz=16
[f:oo]: https://www.google.com/s2/favicons?domain=otakotaku.com&sz=16
[f:shb]: https://www.google.com/s2/favicons?domain=cal.syoboi.jp&sz=16
[f:shk]: https://www.google.com/s2/favicons?domain=shikimori.me&sz=16
[f:smk]: https://www.google.com/s2/favicons?domain=simkl.com&sz=16
[f:sy]: https://www.google.com/s2/favicons?domain=db.silveryasha.web.id&sz=16
[f:tmdb]: https://www.google.com/s2/favicons?domain=themoviedb.org&sz=16
[f:trk]: https://www.google.com/s2/favicons?domain=trakt.tv&sz=16
[f:tvdb]: https://www.google.com/s2/favicons?domain=thetvdb.com&sz=16
[f:tvtm]: https://www.google.com/s2/favicons?domain=tvtime.com&sz=16
