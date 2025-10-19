# anime-api

- [1. Property `anime-api > data`](#data)
  - [1.1. anime-api > data > Anime](#data_items)
    - [1.1.1. Property `anime-api > data > Anime > anidb`](#data_items_anidb)
    - [1.1.2. Property `anime-api > data > Anime > anilist`](#data_items_anilist)
    - [1.1.3. Property `anime-api > data > Anime > animenewsnetwork`](#data_items_animenewsnetwork)
    - [1.1.4. Property `anime-api > data > Anime > animeplanet`](#data_items_animeplanet)
    - [1.1.5. Property `anime-api > data > Anime > anisearch`](#data_items_anisearch)
    - [1.1.6. Property `anime-api > data > Anime > annict`](#data_items_annict)
    - [1.1.7. Property `anime-api > data > Anime > imdb`](#data_items_imdb)
    - [1.1.8. Property `anime-api > data > Anime > kaize`](#data_items_kaize)
    - [1.1.9. Property `anime-api > data > Anime > kaize_id`](#data_items_kaize_id)
    - [1.1.10. Property `anime-api > data > Anime > kitsu`](#data_items_kitsu)
    - [1.1.11. Property `anime-api > data > Anime > letterboxd`](#data_items_letterboxd)
    - [1.1.12. Property `anime-api > data > Anime > letterboxd_lid`](#data_items_letterboxd_lid)
    - [1.1.13. Property `anime-api > data > Anime > letterboxd_uid`](#data_items_letterboxd_uid)
    - [1.1.14. Property `anime-api > data > Anime > livechart`](#data_items_livechart)
    - [1.1.15. Property `anime-api > data > Anime > myanimelist`](#data_items_myanimelist)
    - [1.1.16. Property `anime-api > data > Anime > nautiljon`](#data_items_nautiljon)
    - [1.1.17. Property `anime-api > data > Anime > notify`](#data_items_notify)
    - [1.1.18. Property `anime-api > data > Anime > otakotaku`](#data_items_otakotaku)
    - [1.1.19. Property `anime-api > data > Anime > shikimori`](#data_items_shikimori)
    - [1.1.20. Property `anime-api > data > Anime > shoboi`](#data_items_shoboi)
    - [1.1.21. Property `anime-api > data > Anime > silveryasha`](#data_items_silveryasha)
    - [1.1.22. Property `anime-api > data > Anime > simkl`](#data_items_simkl)
    - [1.1.23. Property `anime-api > data > Anime > themoviedb`](#data_items_themoviedb)
    - [1.1.24. Property `anime-api > data > Anime > themoviedb_season`](#data_items_themoviedb_season)
    - [1.1.25. Property `anime-api > data > Anime > themoviedb_type`](#data_items_themoviedb_type)
    - [1.1.26. Property `anime-api > data > Anime > thetvdb`](#data_items_thetvdb)
    - [1.1.27. Property `anime-api > data > Anime > thetvdb_season_id`](#data_items_thetvdb_season_id)
    - [1.1.28. Property `anime-api > data > Anime > title`](#data_items_title)
    - [1.1.29. Property `anime-api > data > Anime > trakt`](#data_items_trakt)
    - [1.1.30. Property `anime-api > data > Anime > trakt_season`](#data_items_trakt_season)
    - [1.1.31. Property `anime-api > data > Anime > trakt_type`](#data_items_trakt_type)
    - [1.1.32. Property `anime-api > data > Anime > type`](#data_items_type)

**Title:** anime-api

|                           |                  |
| ------------------------- | ---------------- |
| **Type**                  | `object`         |
| **Required**              | No               |
| **Additional properties** | Any type allowed |

| Property         | Pattern | Type  | Deprecated | Definition | Title/Description |
| ---------------- | ------- | ----- | ---------- | ---------- | ----------------- |
| - [data](#data ) | No      | array | No         | -          | -                 |

## <a name="data"></a>1. Property `anime-api > data`

|              |         |
| ------------ | ------- |
| **Type**     | `array` |
| **Required** | No      |

|                      | Array restrictions |
| -------------------- | ------------------ |
| **Min items**        | N/A                |
| **Max items**        | N/A                |
| **Items unicity**    | False              |
| **Additional items** | False              |
| **Tuple validation** | See below          |

| Each item of this array must be | Description      |
| ------------------------------- | ---------------- |
| [Anime](#data_items)            | Schema for anime |

### <a name="data_items"></a>1.1. anime-api > data > Anime

**Title:** Anime

|                           |                     |
| ------------------------- | ------------------- |
| **Type**                  | `object`            |
| **Required**              | No                  |
| **Additional properties** | Not allowed         |
| **Defined in**            | #/definitions/anime |

**Description:** Schema for anime

| Property                                              | Pattern | Type             | Deprecated | Definition                  | Title/Description         |
| ----------------------------------------------------- | ------- | ---------------- | ---------- | --------------------------- | ------------------------- |
| - [anidb](#data_items_anidb )                         | No      | number or null   | No         | In #/definitions/numbernull | aniDB                     |
| - [anilist](#data_items_anilist )                     | No      | number or null   | No         | In #/definitions/numbernull | AniList                   |
| - [animenewsnetwork](#data_items_animenewsnetwork )   | No      | number or null   | No         | In #/definitions/numbernull | Anime News Network        |
| - [animeplanet](#data_items_animeplanet )             | No      | string or null   | No         | In #/definitions/stringnull | Anime-Planet              |
| - [anisearch](#data_items_anisearch )                 | No      | number or null   | No         | In #/definitions/numbernull | AniSearch                 |
| - [annict](#data_items_annict )                       | No      | number or null   | No         | In #/definitions/numbernull | Annict                    |
| - [imdb](#data_items_imdb )                           | No      | string or null   | No         | In #/definitions/stringnull | IMDb                      |
| - [kaize](#data_items_kaize )                         | No      | string or null   | No         | In #/definitions/stringnull | Kaize                     |
| - [kaize_id](#data_items_kaize_id )                   | No      | number or null   | No         | In #/definitions/numbernull | Kaize ID                  |
| - [kitsu](#data_items_kitsu )                         | No      | number or null   | No         | In #/definitions/numbernull | Kitsu                     |
| - [letterboxd](#data_items_letterboxd )               | No      | string or null   | No         | In #/definitions/stringnull | Letterboxd                |
| - [letterboxd_lid](#data_items_letterboxd_lid )       | No      | number or null   | No         | In #/definitions/numbernull | Letterboxd ID             |
| - [letterboxd_uid](#data_items_letterboxd_uid )       | No      | string or null   | No         | In #/definitions/stringnull | Letterboxd General ID     |
| - [livechart](#data_items_livechart )                 | No      | number or null   | No         | In #/definitions/numbernull | LiveChart                 |
| - [myanimelist](#data_items_myanimelist )             | No      | number or null   | No         | In #/definitions/numbernull | MyAnimeList               |
| - [nautiljon](#data_items_nautiljon )                 | No      | string or null   | No         | In #/definitions/stringnull | Nautiljon                 |
| - [notify](#data_items_notify )                       | No      | string or null   | No         | In #/definitions/stringnull | Notify.moe                |
| - [otakotaku](#data_items_otakotaku )                 | No      | string or null   | No         | In #/definitions/stringnull | Otak Otaku                |
| - [shikimori](#data_items_shikimori )                 | No      | number or null   | No         | In #/definitions/numbernull | Shikimori                 |
| - [shoboi](#data_items_shoboi )                       | No      | number or null   | No         | In #/definitions/numbernull | Shoboi/Syobocal           |
| - [silveryasha](#data_items_silveryasha )             | No      | string or null   | No         | In #/definitions/stringnull | Silver Yasha              |
| - [simkl](#data_items_simkl )                         | No      | number or null   | No         | In #/definitions/numbernull | SIMKL                     |
| - [themoviedb](#data_items_themoviedb )               | No      | number or null   | No         | In #/definitions/numbernull | The Movie Database        |
| - [themoviedb_season](#data_items_themoviedb_season ) | No      | number or null   | No         | In #/definitions/numbernull | The Movie Database season |
| - [themoviedb_type](#data_items_themoviedb_type )     | No      | enum (of string) | No         | In #/definitions/stringnull | The Movie Database type   |
| - [thetvdb](#data_items_thetvdb )                     | No      | string or null   | No         | In #/definitions/stringnull | The TVDB                  |
| - [thetvdb_season_id](#data_items_thetvdb_season_id ) | No      | number or null   | No         | In #/definitions/numbernull | The TVDB season ID        |
| + [title](#data_items_title )                         | No      | string           | No         | -                           | Title                     |
| - [trakt](#data_items_trakt )                         | No      | number or null   | No         | In #/definitions/numbernull | Trakt                     |
| - [trakt_season](#data_items_trakt_season )           | No      | number or null   | No         | In #/definitions/numbernull | Trakt season              |
| - [trakt_type](#data_items_trakt_type )               | No      | enum (of string) | No         | In #/definitions/stringnull | Trakt type                |
| + [type](#data_items_type )                           | No      | enum (of string) | No         | In #/definitions/stringnull | Type                      |

#### <a name="data_items_anidb"></a>1.1.1. Property `anime-api > data > Anime > anidb`

**Title:** aniDB

|                |                          |
| -------------- | ------------------------ |
| **Type**       | `number or null`         |
| **Required**   | No                       |
| **Defined in** | #/definitions/numbernull |

**Description:** aniDB ID, website: https://anidb.net/

#### <a name="data_items_anilist"></a>1.1.2. Property `anime-api > data > Anime > anilist`

**Title:** AniList

|                |                          |
| -------------- | ------------------------ |
| **Type**       | `number or null`         |
| **Required**   | No                       |
| **Defined in** | #/definitions/numbernull |

**Description:** AniList ID, website: https://anilist.co/

#### <a name="data_items_animenewsnetwork"></a>1.1.3. Property `anime-api > data > Anime > animenewsnetwork`

**Title:** Anime News Network

|                |                          |
| -------------- | ------------------------ |
| **Type**       | `number or null`         |
| **Required**   | No                       |
| **Defined in** | #/definitions/numbernull |

**Description:** Anime News Network, website: https://animenewsnetwork.com

#### <a name="data_items_animeplanet"></a>1.1.4. Property `anime-api > data > Anime > animeplanet`

**Title:** Anime-Planet

|                |                          |
| -------------- | ------------------------ |
| **Type**       | `string or null`         |
| **Required**   | No                       |
| **Defined in** | #/definitions/stringnull |

**Description:** Anime-Planet slug, website: https://www.anime-planet.com/

| Restrictions                      |                                                                                   |
| --------------------------------- | --------------------------------------------------------------------------------- |
| **Must match regular expression** | ```^[a-z0-9\-]+$``` [Test](https://regex101.com/?regex=%5E%5Ba-z0-9%5C-%5D%2B%24) |

#### <a name="data_items_anisearch"></a>1.1.5. Property `anime-api > data > Anime > anisearch`

**Title:** AniSearch

|                |                          |
| -------------- | ------------------------ |
| **Type**       | `number or null`         |
| **Required**   | No                       |
| **Defined in** | #/definitions/numbernull |

**Description:** AniSearch ID, website: https://www.anisearch.com/, https://anisearch.de, https://anisearch.it, https://anisearch.es, https://anisearch.fr, https://anisearch.jp

#### <a name="data_items_annict"></a>1.1.6. Property `anime-api > data > Anime > annict`

**Title:** Annict

|                |                          |
| -------------- | ------------------------ |
| **Type**       | `number or null`         |
| **Required**   | No                       |
| **Defined in** | #/definitions/numbernull |

**Description:** Annict ID, website: https://annict.com/, https://en.annict.com/, https://annict.jp/

#### <a name="data_items_imdb"></a>1.1.7. Property `anime-api > data > Anime > imdb`

**Title:** IMDb

|                |                          |
| -------------- | ------------------------ |
| **Type**       | `string or null`         |
| **Required**   | No                       |
| **Defined in** | #/definitions/stringnull |

**Description:** IMDb ID, website: https://www.imdb.com/

| Restrictions                      |                                                                           |
| --------------------------------- | ------------------------------------------------------------------------- |
| **Must match regular expression** | ```^tt[\d]+$``` [Test](https://regex101.com/?regex=%5Ett%5B%5Cd%5D%2B%24) |

#### <a name="data_items_kaize"></a>1.1.8. Property `anime-api > data > Anime > kaize`

**Title:** Kaize

|                |                          |
| -------------- | ------------------------ |
| **Type**       | `string or null`         |
| **Required**   | No                       |
| **Defined in** | #/definitions/stringnull |

**Description:** Kaize slug, website: https://kaize.io/

| Restrictions                      |                                                                                   |
| --------------------------------- | --------------------------------------------------------------------------------- |
| **Must match regular expression** | ```^[a-z0-9\-]+$``` [Test](https://regex101.com/?regex=%5E%5Ba-z0-9%5C-%5D%2B%24) |

#### <a name="data_items_kaize_id"></a>1.1.9. Property `anime-api > data > Anime > kaize_id`

**Title:** Kaize ID

|                |                          |
| -------------- | ------------------------ |
| **Type**       | `number or null`         |
| **Required**   | No                       |
| **Defined in** | #/definitions/numbernull |

**Description:** Kaize ID in integer format, not recommended as some entry can't be found its ID compared to slug

#### <a name="data_items_kitsu"></a>1.1.10. Property `anime-api > data > Anime > kitsu`

**Title:** Kitsu

|                |                          |
| -------------- | ------------------------ |
| **Type**       | `number or null`         |
| **Required**   | No                       |
| **Defined in** | #/definitions/numbernull |

**Description:** Kitsu ID in integer, slug not suppported, website: https://kitsu.app/

#### <a name="data_items_letterboxd"></a>1.1.11. Property `anime-api > data > Anime > letterboxd`

**Title:** Letterboxd

|                |                          |
| -------------- | ------------------------ |
| **Type**       | `string or null`         |
| **Required**   | No                       |
| **Defined in** | #/definitions/stringnull |

**Description:** Letterboxd slug, website: https://letterboxd.com/

| Restrictions                      |                                                                                   |
| --------------------------------- | --------------------------------------------------------------------------------- |
| **Must match regular expression** | ```^[a-z0-9\-]+$``` [Test](https://regex101.com/?regex=%5E%5Ba-z0-9%5C-%5D%2B%24) |

#### <a name="data_items_letterboxd_lid"></a>1.1.12. Property `anime-api > data > Anime > letterboxd_lid`

**Title:** Letterboxd ID

|                |                          |
| -------------- | ------------------------ |
| **Type**       | `number or null`         |
| **Required**   | No                       |
| **Defined in** | #/definitions/numbernull |

**Description:** Letterboxd Letter ID, only being used on 1st party API requests

#### <a name="data_items_letterboxd_uid"></a>1.1.13. Property `anime-api > data > Anime > letterboxd_uid`

**Title:** Letterboxd General ID

|                |                          |
| -------------- | ------------------------ |
| **Type**       | `string or null`         |
| **Required**   | No                       |
| **Defined in** | #/definitions/stringnull |

**Description:** Letterboxd General ID, internally used

#### <a name="data_items_livechart"></a>1.1.14. Property `anime-api > data > Anime > livechart`

**Title:** LiveChart

|                |                          |
| -------------- | ------------------------ |
| **Type**       | `number or null`         |
| **Required**   | No                       |
| **Defined in** | #/definitions/numbernull |

**Description:** LiveChart ID, website: https://www.livechart.me/

#### <a name="data_items_myanimelist"></a>1.1.15. Property `anime-api > data > Anime > myanimelist`

**Title:** MyAnimeList

|                |                          |
| -------------- | ------------------------ |
| **Type**       | `number or null`         |
| **Required**   | No                       |
| **Defined in** | #/definitions/numbernull |

**Description:** MyAnimeList ID, website: https://myanimelist.net/

#### <a name="data_items_nautiljon"></a>1.1.16. Property `anime-api > data > Anime > nautiljon`

**Title:** Nautiljon

|                |                          |
| -------------- | ------------------------ |
| **Type**       | `string or null`         |
| **Required**   | No                       |
| **Defined in** | #/definitions/stringnull |

**Description:** Nautiljon slug, website: https://www.nautiljon.com/

| Restrictions                      |                                                                                   |
| --------------------------------- | --------------------------------------------------------------------------------- |
| **Must match regular expression** | ```^[a-z0-9\-]+$``` [Test](https://regex101.com/?regex=%5E%5Ba-z0-9%5C-%5D%2B%24) |

#### <a name="data_items_notify"></a>1.1.17. Property `anime-api > data > Anime > notify`

**Title:** Notify.moe

|                |                          |
| -------------- | ------------------------ |
| **Type**       | `string or null`         |
| **Required**   | No                       |
| **Defined in** | #/definitions/stringnull |

**Description:** Notify.moe slug, website: https://notify.moe/

| Restrictions                      |                                                                                   |
| --------------------------------- | --------------------------------------------------------------------------------- |
| **Must match regular expression** | ```^[a-zA-Z0-9]+$``` [Test](https://regex101.com/?regex=%5E%5Ba-zA-Z0-9%5D%2B%24) |

#### <a name="data_items_otakotaku"></a>1.1.18. Property `anime-api > data > Anime > otakotaku`

**Title:** Otak Otaku

|                |                          |
| -------------- | ------------------------ |
| **Type**       | `string or null`         |
| **Required**   | No                       |
| **Defined in** | #/definitions/stringnull |

**Description:** Otak Otaku slug, website: https://otakotaku.com/

| Restrictions                      |                                                                                   |
| --------------------------------- | --------------------------------------------------------------------------------- |
| **Must match regular expression** | ```^[a-z0-9\-]+$``` [Test](https://regex101.com/?regex=%5E%5Ba-z0-9%5C-%5D%2B%24) |

#### <a name="data_items_shikimori"></a>1.1.19. Property `anime-api > data > Anime > shikimori`

**Title:** Shikimori

|                |                          |
| -------------- | ------------------------ |
| **Type**       | `number or null`         |
| **Required**   | No                       |
| **Defined in** | #/definitions/numbernull |

**Description:** Shikimori ID, website: https://shikimori.one/

#### <a name="data_items_shoboi"></a>1.1.20. Property `anime-api > data > Anime > shoboi`

**Title:** Shoboi/Syobocal

|                |                          |
| -------------- | ------------------------ |
| **Type**       | `number or null`         |
| **Required**   | No                       |
| **Defined in** | #/definitions/numbernull |

**Description:** Shoboi/Syobocal ID, website: http://cal.syoboi.jp/

#### <a name="data_items_silveryasha"></a>1.1.21. Property `anime-api > data > Anime > silveryasha`

**Title:** Silver Yasha

|                |                          |
| -------------- | ------------------------ |
| **Type**       | `string or null`         |
| **Required**   | No                       |
| **Defined in** | #/definitions/stringnull |

**Description:** Silver Yasha slug, website: https://silveryasha.com/

| Restrictions                      |                                                                                   |
| --------------------------------- | --------------------------------------------------------------------------------- |
| **Must match regular expression** | ```^[a-z0-9\-]+$``` [Test](https://regex101.com/?regex=%5E%5Ba-z0-9%5C-%5D%2B%24) |

#### <a name="data_items_simkl"></a>1.1.22. Property `anime-api > data > Anime > simkl`

**Title:** SIMKL

|                |                          |
| -------------- | ------------------------ |
| **Type**       | `number or null`         |
| **Required**   | No                       |
| **Defined in** | #/definitions/numbernull |

**Description:** SIMKL ID, website: https://simkl.com/

#### <a name="data_items_themoviedb"></a>1.1.23. Property `anime-api > data > Anime > themoviedb`

**Title:** The Movie Database

|                |                          |
| -------------- | ------------------------ |
| **Type**       | `number or null`         |
| **Required**   | No                       |
| **Defined in** | #/definitions/numbernull |

**Description:** The Movie Database ID, can be used for movie or tv, website: https://www.themoviedb.org/

#### <a name="data_items_themoviedb_season"></a>1.1.24. Property `anime-api > data > Anime > themoviedb_season`

**Title:** The Movie Database season

|                |                          |
| -------------- | ------------------------ |
| **Type**       | `number or null`         |
| **Required**   | No                       |
| **Defined in** | #/definitions/numbernull |

**Description:** The Movie Database season number, only available for TV shows

#### <a name="data_items_themoviedb_type"></a>1.1.25. Property `anime-api > data > Anime > themoviedb_type`

**Title:** The Movie Database type

|                |                          |
| -------------- | ------------------------ |
| **Type**       | `enum (of string)`       |
| **Required**   | No                       |
| **Defined in** | #/definitions/stringnull |

**Description:** The Movie Database media type, can be movie or tv

Must be one of:
* "movie"
* "tv"

#### <a name="data_items_thetvdb"></a>1.1.26. Property `anime-api > data > Anime > thetvdb`

**Title:** The TVDB

|                |                          |
| -------------- | ------------------------ |
| **Type**       | `string or null`         |
| **Required**   | No                       |
| **Defined in** | #/definitions/stringnull |

**Description:** The TVDB ID, website: https://thetvdb.com/, can be prefixed with series/ or movie/ to deep link

#### <a name="data_items_thetvdb_season_id"></a>1.1.27. Property `anime-api > data > Anime > thetvdb_season_id`

**Title:** The TVDB season ID

|                |                          |
| -------------- | ------------------------ |
| **Type**       | `number or null`         |
| **Required**   | No                       |
| **Defined in** | #/definitions/numbernull |

**Description:** The TVDB season ID, can be used to build URL

#### <a name="data_items_title"></a>1.1.28. Property `anime-api > data > Anime > title`

**Title:** Title

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |

**Description:** Title of the anime in English or Romaji

#### <a name="data_items_trakt"></a>1.1.29. Property `anime-api > data > Anime > trakt`

**Title:** Trakt

|                |                          |
| -------------- | ------------------------ |
| **Type**       | `number or null`         |
| **Required**   | No                       |
| **Defined in** | #/definitions/numbernull |

**Description:** Trakt ID, can be used for movie or show, website: https://trakt.tv/

#### <a name="data_items_trakt_season"></a>1.1.30. Property `anime-api > data > Anime > trakt_season`

**Title:** Trakt season

|                |                          |
| -------------- | ------------------------ |
| **Type**       | `number or null`         |
| **Required**   | No                       |
| **Defined in** | #/definitions/numbernull |

**Description:** Trakt season number, only available for shows

#### <a name="data_items_trakt_type"></a>1.1.31. Property `anime-api > data > Anime > trakt_type`

**Title:** Trakt type

|                |                          |
| -------------- | ------------------------ |
| **Type**       | `enum (of string)`       |
| **Required**   | No                       |
| **Defined in** | #/definitions/stringnull |

**Description:** Trakt media type, can be movie or show

Must be one of:
* "movie"
* "show"

#### <a name="data_items_type"></a>1.1.32. Property `anime-api > data > Anime > type`

**Title:** Type

|                |                          |
| -------------- | ------------------------ |
| **Type**       | `enum (of string)`       |
| **Required**   | Yes                      |
| **Defined in** | #/definitions/stringnull |

**Description:** Type of the anime

Must be one of:
* "TV"
* "OVA"
* "ONA"
* "MOVIE"
* "SPECIAL"
* "UNKNOWN"

----------------------------------------------------------------------------------------------------------------------------
Generated using [json-schema-for-humans](https://github.com/coveooss/json-schema-for-humans) on 2025-10-19 at 13:10:23 +0700
