<!-- markdownlint-disable MD028 MD033 -->
<!-- omit in toc -->
# nattadasu's RESTful AnimeAPI

AnimeAPI (also known as aniApi) is a RESTful API that provides anime relation
mapping across multiple anime databases. It mainly focuses on providing
relations between anime titles from different databases.

This project is mainly derived on [anime-offline-database][aod] by [manami-project][mp]
and [arm] by [kawaiioverflow][ko], while adding support for more databases.

> [!IMPORTANT]
>
> **AnimeAPI** *in general* **is dual-licensed:**
> * **Software Code** (Server & Scrapers): [MIT License](LICENSE)
> * **Database & Data**: [ODbL v1.0](LICENSE-ODbL) + [DbCL v1.0](LICENSE-DbCL)
>
> For full usage and attribution terms, see [Licensing](#licensing).


<!-- omit in toc -->
## Table of Contents

<details>
<summary>Click to expand</summary>

* [Why use AnimeAPI?](#why-use-animeapi)
* [Licensing](#licensing)
* [Limitation](#limitation)
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
* [Acknowledgements](#acknowledgements)

</details>

## Why use AnimeAPI?

Compared to other relation mapping API, AnimeAPI provides more databases yet
it's still easy to use. It also provides more data than other relation mapping
API, such as the anime title itself.

Below is the comparison between AnimeAPI and other relation mapping API.

<!-- markdownlint-disable MD013 MD060 -->

| Project | License | Access & Rate Limits | Formats | Title | Supported Platforms |
| :--- | :--- | :--- | :--- | :---: | :---: |
| **AnimeAPI** | MIT, ODbL, DbCL, CC0 | Public / No limits | REST, JSON, TSV | ✔ | ![f:adb] ![f:al] ![f:an] ![f:ap] ![f:as] ![f:ac] ![f:hka] ![f:imdb] ![f:kz] ![f:kts] ![f:lbx] ![f:lc] ![f:mal] ![f:ntj] ![f:ntf] ![f:oo] ![f:shk] ![f:shb] ![f:sy] ![f:smk] ![f:tmdb] ![f:trk] ![f:tvdb] ![f:tvtm] <br> *(All 22+ platforms)* |
| **[manami-project/anime-offline-database][aod]** | ODbL, DbCL | Public Dump | JSON | ✔ | ![f:mal] ![f:al] ![f:adb] ![f:kts] ![f:lc] ![f:as] ![f:ap] ![f:smk] ![f:an] |
| **[kawaiioverflow/arm][arm]** | MIT | Public / No limits | Node Package, REST, JSON | ❌ | ![f:mal] ![f:al] ![f:ac] ![f:shb] |
| **[Fribb/anime-lists][fal]** | Unknown | Public Dump | JSON | ❌ | ![f:mal] ![f:al] ![f:adb] ![f:kts] ![f:lc] ![f:as] ![f:ap] ![f:smk] ![f:an] ![f:ntf] ![f:shk] ![f:tmdb] ![f:tvdb] ![f:imdb] |
| **[beeequeue/arm-server][bq]** | AGPL-3.0 | Public / No limits | REST | ❌ | ![f:adb] ![f:al] ![f:ap] ![f:as] ![f:imdb] ![f:kts] ![f:lc] ![f:mal] ![f:ntf] ![f:shk] ![f:tmdb] [^1] ![f:tvdb] |
| **[Atelier-Shiori/Hato][hato]** | Apache-2.0 | Paid (API Key) / No limits | REST | ❌ | ![f:al] ![f:kts] ![f:mal] ![f:ntf] ![f:adb] |
| **[SIMKL][smk]** | Proprietary | API Key / 1k reqs/day | REST | ✔ | ![f:mal] ![f:tmdb] ![f:tvdb] ![f:imdb] ![f:adb] ![f:trk] <br> *Result-only:* ![f:al] ![f:an] ![f:ap] ![f:as] ![f:kts] ![f:lc] |
| **[Trakt][trk]** | Proprietary | API Key / 1k reqs/5 mins | REST | ✔ | ![f:tmdb] ![f:tvdb] ![f:imdb] |
| **[Anime-Lists/anime-lists][alal]** | Unknown | Public / No limits | XML, XLSX | ✔ | ![f:adb] ![f:tvdb] ![f:tmdb] [^1] ![f:imdb] |
| **[rensetsu/db.trakt.extended-anitrakt][atip]** | MIT | Public Dump | JSON | ✔ | ![f:trk] ![f:tmdb] ![f:tvdb] ![f:lbx] ![f:imdb] |

[^1]: *Movie only*

<!-- markdownlint-enable MD013 MD060 -->

## Licensing

This project uses a dual-licensing structure to separate the database data from
the software code:

### Software Code (API Server & Generators)

The codebase (including the REST API server and scraper/generator scripts) is
licensed under the **MIT License** (see [LICENSE](LICENSE)).

You are free to use, modify, and distribute this software for any purpose.

### Database/Compiled Data

The generated relation mapping database (found in `database/`) is licensed under
the **Open Database License (ODbL) v1.0** (see [LICENSE-ODbL](LICENSE-ODbL))
and the **Database Contents License (DbCL) v1.0** (see [LICENSE-DbCL](LICENSE-DbCL)).

In short, you must:

* **Share-Alike:** Under the ODbL, if you publicly use or distribute a modified
  version of this database, or another database derived from it, you must also
  release that database under the ODbL.
* **Credits:** If you use this database in your projects, you must attribute
  the source (AnimeAPI and Anime Offline Database).

### Public Domain Scraped Data (CC0-1.0)

The raw JSON files generated by the scrapers for **Kaize**, **Nautiljon**,
**Otak-Otaku**, and **SilverYasha** (found under [`database/raw/`](database/raw/))
are dedicated to the public domain under the **CC0-1.0** license (see
[LICENSE-CC0](LICENSE-CC0)). This allows you to build your own databases using
these specific raw relation mappings without database-license restrictions.

For a detailed list of these files, refer to [`database/raw/README.md`](database/raw/README.md).

## Limitation

Because AnimeAPI uses a flat, 1-to-1 mapping model (allowing only a single ID
per provider per entry), it cannot natively represent **1-to-many** or
**many-to-many** relationships across different databases.

This leads to mapping discrepancies in several common scenarios:

* **Specials, OVAs, and Movies:** Side stories or prequel films may be
  cataloged as special episodes within a main entry on one platform (like AniDB
  or TVDB), but split into standalone entries on others. By default, AnimeAPI
  conforms to MyAnimeList's entry structure to achieve compatibility across
  different databases.
* **Split-cours:** Shows broadcast in two separate parts may be merged under one
  entry or split depending on the database's moderation policies.

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

| Name                  | Language           | Homepage                                                  | Description                                                                                 |
| :-------------------- | :----------------- | :-------------------------------------------------------- | :------------------------------------------------------------------------------------------ |
| animeManga-autoBackup | Powershell, Python | [GitHub](https://github.com/bokusu/animeManga-autoBackup) | A script that uses AnimeAPI to get info one of your anime/manga lists and save it to a file |
| Bokusu                | Python             | [GitHub](https://github.com/bokusu/bokusu)                | Rewrite of animeManga-autoBackup in Python                                                  |
| Ryuuzaki Ryuusei      | Python             | [GitHub](https://github.com/nattadasu/ryuuRyuusei)        | A Discord bot that uses AnimeAPI to fetch anime maps                                        |
| TsukiHime             | -                  | [Webpage](https://tsukihime.org/)                         | Modern Anime Tracking & Releases                                                            |

## Supported Platforms and Aliases

AnimeAPI supported following sites for media lookup. You can use this as an
alias cheatsheet as well.

> [!IMPORTANT]
>
> * The aliases are case-insensitive. You can use any of the aliases to get the
>   data you want.
> * 2K is the two-letter abbreviation for the platform.

|                   Platform |  2K   | Aliases                                                                                         |
| -------------------------: | :---: | ----------------------------------------------------------------------------------------------- |
|           `anidb` ![f:adb] | `ad`  | `adb`, `anidb.net`                                                                              |
|          `anilist` ![f:al] | `al`  | `anilist.co`                                                                                    |
| `animenewsnetwork` ![f:an] | `an`  | `ann`, `animenewsnetwork.com`                                                                   |
|      `animeplanet` ![f:ap] | `ap`  | `anime-planet.com`, `anime-planet`, `animeplanet.com`                                           |
|        `anisearch` ![f:as] | `as`  | `anisearch.com`, `anisearch.de`, `anisearch.it`, `anisearch.es`, `anisearch.fr`, `anisearch.jp` |
|           `annict` ![f:ac] | `ac`  | `anc`, `act`, `annict.com`, `annict.jp`, `en.annict.com`                                        |
|           `hikka` ![f:hka] | `hk`  | `hka`, `hikka.io`                                                                               |
|           `imdb` ![f:imdb] | `im`  | `imdb.com`                                                                                      |
|            `kaize` ![f:kz] | `kz`  | `kaize.io`                                                                                      |
|           `kitsu` ![f:kts] | `kt`  | `kts`, `kitsu.io`, `kitsu.app`                                                                  |
|      `letterboxd` ![f:lbx] | `lb`  | `lx`, `letterboxd.com`                                                                          |
|        `livechart` ![f:lc] | `lc`  | `livechart.me`                                                                                  |
|     `myanimelist` ![f:mal] | `ma`  | `mal`, `myanimelist.net`                                                                        |
|       `nautiljon` ![f:ntj] | `nj`  | `ntj`, `nautiljon.com`                                                                          |
|          `notify` ![f:ntf] | `nf`  | `ntf`, `ntm`, `notifymoe`, `notify.moe`                                                         |
|        `otakotaku` ![f:oo] | `oo`  | `otakotaku.com`                                                                                 |
|       `shikimori` ![f:shk] | `sh`  | `shiki`, `shk`, `shiki.one`, `shikimori.io`, `shikimori.me`, `shikimori.one`, `shikimori.org`   |
|          `shoboi` ![f:shb] | `sb`  | `shb`, `syb`, `shobocal`, `syoboi`, `syobocal`, `cal.syoboi.jp`                                 |
|      `silveryasha` ![f:sy] | `sy`  | `dbti`, `db.silveryasha.id`, `db.silveryasha.web.id`                                            |
|           `simkl` ![f:smk] | `sm`  | `smk`, `simkl.com`, `animecountdown`, `animecountdown.com`                                      |
|     `themoviedb` ![f:tmdb] | `tm`  | `tmdb`, `themoviedb.org`                                                                        |
|        `thetvdb` ![f:tvdb] | `tv`  | `tvdb`, `thetvdb.com`, `thetvdb`, `tvtime`, `tt`, `tvtime.com`                                  |
|           `trakt` ![f:trk] | `tr`  | `trk`, `trakt.tv`                                                                               |

<!-- markdownlint-enable MD034 MD013 -->

## Statistic

So far, AnimeAPI has indexed data from 22 databases, with details as follows:

<!-- updated -->
Last updated: 27 June 2026 07:58:17 UTC
<!-- /updated -->

<!-- counters -->
| Platform           |     Count |
| :----------------- | --------: |
| aniDB              |     14430 |
| AniList            |     22460 |
| Anime News Network |     12284 |
| Anime-Planet       |     26642 |
| aniSearch          |     20699 |
| Annict             |     12801 |
| Hikka              |     28646 |
| IMDb               |      7591 |
| Kaize              |     24596 |
| Kitsu              |     21970 |
| Letterboxd         |      1879 |
| LiveChart          |     12226 |
| MyAnimeList        |     30588 |
| Nautiljon          |      9237 |
| Notify.moe         |     16965 |
| Otak Otaku         |      3045 |
| Shikimori          |     30588 |
| Shoboi/Syobocal    |      5993 |
| Silver Yasha       |      5312 |
| SIMKL              |     14356 |
| The Movie Database |      8925 |
| The TVDB           |      5421 |
| Trakt              |      7346 |
|                    |           |
| **Total**          | **40223** |
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
    "timestamp": 1782547097,
    "iso": "2026-06-27T07:58:17.024702+00:00"
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
    "https://otakotaku.com",
    "https://livechart.me",
    "https://shikimori.one",
    "https://geckyzz.my.id",
    "https://anilist.co",
    "https://kitsu.app"
  ],
  "license": "MIT AND ODbL-1.0 AND DbCL-1.0 AND CC0-1.0",
  "website": "https://animeapi.my.id",
  "counts": {
    "anidb": 14430,
    "anilist": 22460,
    "animenewsnetwork": 12284,
    "animeplanet": 26642,
    "anisearch": 20699,
    "annict": 12801,
    "hikka": 28646,
    "imdb": 7591,
    "kaize": 24596,
    "kitsu": 21970,
    "letterboxd": 1879,
    "livechart": 12226,
    "myanimelist": 30588,
    "nautiljon": 9237,
    "notify": 16965,
    "otakotaku": 3045,
    "shikimori": 30588,
    "shoboi": 5993,
    "silveryasha": 5312,
    "simkl": 14356,
    "themoviedb": 8925,
    "thetvdb": 5421,
    "trakt": 7346,
    "total": 40223
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
Updated on 06/27/2026 07:58:17 UTC
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
  "animenewsnetwork": 13,
  "animeplanet": "cowboy-bebop",
  "anisearch": 1572,
  "annict": 360,
  "hikka": "cowboy-bebop-d572ee",
  "imdb": "tt0213338",
  "kaize": "cowboy-bebop",
  "kaize_id": 265,
  "kitsu": 1,
  "letterboxd_lid": null,
  "letterboxd_slug": null,
  "letterboxd_uid": null,
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
  "themoviedb": 30991,
  "themoviedb_season_id": 42587,
  "themoviedb_type": "tv",
  "thetvdb": 76885,
  "thetvdb_season_id": 11636,
  "trakt": 30857,
  "trakt_may_invalid": false,
  "trakt_season": 1,
  "trakt_season_id": 43328,
  "trakt_slug": "cowboy-bebop",
  "trakt_type": "shows"
}
```
<!-- /sample -->

</details>

#### Provider exclusive rules

##### Kitsu

`kitsu` IDs must be numerical. If your application only store the id as slug,
you can convert it to the numerical ID using the Kitsu API:

* **Endpoint:** `GET https://kitsu.app/api/edge/anime?filter[slug]=<SLUG>`
* **Example:** `GET https://kitsu.app/api/edge/anime?filter[slug]=cowboy-bebop`
* **Parsing:** The numerical ID is found at `data[0].id` in the JSON response.

##### Letterboxd

`letterboxd` supports multiple ID formats with priority-based lookup.
The API automatically tries these formats in order:

1. **Slug** (`letterboxd_slug`) — Primary format (e.g., `your-name`)
2. **Letter ID** (`letterboxd_lid`) — Fallback format (e.g., `cUqs`),
   useful if you iterate from Letterboxd's official API directly.
3. **Unique ID** (`letterboxd_uid`) — Alternative fallback (e.g., `307684`),
   used internally by Letterboxd (not available/accessible publicly).

**Supported endpoints:**

```http
GET https://animeapi.my.id/letterboxd/your-name      # Slug lookup
GET https://animeapi.my.id/letterboxd/cUqs           # Letter ID lookup
GET https://animeapi.my.id/letterboxd/307684         # Unique ID lookup
```

##### SIMKL

> [!NOTE]
> Also applicable to AnimeCountdown.

`simkl` ID is only applicable for media entries in the Anime category.

##### Shikimori

`shikimori` IDs are identical to `myanimelist` IDs.

If you encounter a `404` error:

* Remove any alphabetical prefix from the ID.
* **Example:** Convert `z218` to `218` and retry the query.

##### The Movie DB

For The Movie DB (TMDB), the path format requires the media type:
`:provider/:mediatype/:mediaid` (where `:mediatype` is either `movie` or `tv`).

For TV shows, you can also specify a season:
`:provider/:mediatype/:mediaid/seasons/:seasonid` (supports Trakt season index
or TMDB internal season ID).

**Supported endpoints:**

```http
GET https://animeapi.my.id/themoviedb/tv/30991                # TV show
GET https://animeapi.my.id/themoviedb/movie/60669             # Movie
GET https://animeapi.my.id/themoviedb/tv/30991/seasons/1      # TV show with season
```

##### The TVDB

For The TVDB, the path format requires the `series` prefix:
`:provider/series/:mediaid` or `:provider/series/:mediaid/seasons/:season_id`.

When querying season data, you can use either the season number (`trakt_season`)
or the TVDB season ID (`thetvdb_season_id`). Season 1 entries can also be accessed
using the base series URL.

**Supported endpoints:**

```http
GET https://animeapi.my.id/thetvdb/series/12345
GET https://animeapi.my.id/thetvdb/series/12345/seasons/2
GET https://animeapi.my.id/thetvdb/series/12345/seasons/789012
```

##### Trakt

For Trakt, the path format is `:provider/:mediatype/:mediaid`
(where `:mediatype` is either `movies` or `shows`). The `:mediaid` can be a
**numeric ID** or a **slug**.

**Supported endpoints:**

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
> better compatibility. If you need to convert a slug to numeric ID externally,
> you can use the Trakt API:
>
> ```http
> GET https://api.trakt.tv/search/trakt/<ID>?type=<movie|show>
> ```
>
> Note: Trakt API requires an API key to access this endpoint.

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
{
  "title": "Mairimashita! Iruma-kun 3rd Season",
  "anidb": 16627,
  "anilist": 139092,
  "animenewsnetwork": 24018,
  "animeplanet": "welcome-to-demon-school-iruma-kun-3",
  "anisearch": 16582,
  "annict": 8883,
  "hikka": "mairimashita-iruma-kun-3rd-season-bad2d0",
  "imdb": "tt11034066",
  "kaize": "mairimashita-iruma-kun-3rd-season",
  "kaize_id": 4989,
  "kitsu": 45154,
  "letterboxd_lid": null,
  "letterboxd_slug": null,
  "letterboxd_uid": null,
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
  "themoviedb": 91801,
  "themoviedb_season_id": 306624,
  "themoviedb_type": "tv",
  "thetvdb": 369144,
  "thetvdb_season_id": 1955315,
  "trakt": 152334,
  "trakt_may_invalid": false,
  "trakt_season": 3,
  "trakt_season_id": 303584,
  "trakt_slug": "welcome-to-demon-school-iruma-kun",
  "trakt_type": "shows"
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

  |            Platform |  2K   | Aliases               | Additional Notes                           |
  | ------------------: | :---: | --------------------- | :----------------------------------------- |
  | `kurozora` ![f:krz] | `kr`  | `krz`, `kurozora.app` | Requires Kurozora+ subscription and MAL ID |
  |  `myanili` ![f:mya] | `my`  | `myani.li`            | Requires MAL ID; a web app to manage list  |

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

</details>

## Acknowledgements

This project uses multiple sources to compile the data, including:

* [gh:kawaiioverflow/arm][arm]
* [gh:manami-project/anime-offline-database][aod]
* [gh:rensetsu/db.trakt.extended-anitrakt][atip], which an automatic parser of
  [AniTrakt][atrk] index page.
* [gh:Fribb/anime-lists][fal]
* [Annict][ac]
* [AniList][al]
* [Kitsu][kts]
* [geckyzz][gkz]'s AnimeAPI data extension
* [Hikka][hka]
* [LiveChart][lc]
* [Nautiljon][ntj]
* [Notify.moe][ntf] through Rensetsu's data dump
* [Kaize][kz]
* [Otak Otaku][oo]
* [Shikimori][shk]
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
[gkz]: https://geckyzz.my.id
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
[f:krz]: https://favicone.com/kurozora.app
[f:kz]: https://www.google.com/s2/favicons?domain=kaize.io&sz=16
[f:lbx]: https://www.google.com/s2/favicons?domain=letterboxd.com&sz=16
[f:lc]: https://www.google.com/s2/favicons?domain=livechart.me&sz=16
[f:mal]: https://www.google.com/s2/favicons?domain=myanimelist.net&sz=16
[f:mya]: https://www.google.com/s2/favicons?domain=myani.li&sz=16
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
