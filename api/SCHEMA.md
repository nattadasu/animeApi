<!-- markdownlint-disable MD032 MD033 MD034 -->
<!-- omit in toc -->
# JSON Schema for AnimeAPI V3

* [1. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime`](#1-property-json-schema-for-animeapi-v3--oneof--array-of-anime)
  * [1.1. JSON Schema for AnimeAPI V3 \> oneOf \> Array of Anime \> Anime Schema](#11-json-schema-for-animeapi-v3--oneof--array-of-anime--anime-schema)
    * [1.1.1. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > anidb`](#111-property-json-schema-for-animeapi-v3--oneof--array-of-anime--anime-schema--anidb)
      * [1.1.1.1. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > anidb > anyOf > item 0`](#1111-property-json-schema-for-animeapi-v3--oneof--array-of-anime--anime-schema--anidb--anyof--item-0)
      * [1.1.1.2. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > anidb > anyOf > item 1`](#1112-property-json-schema-for-animeapi-v3--oneof--array-of-anime--anime-schema--anidb--anyof--item-1)
    * [1.1.2. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > anilist`](#112-property-json-schema-for-animeapi-v3--oneof--array-of-anime--anime-schema--anilist)
      * [1.1.2.1. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > anidb > anyOf > item 0`](#1121-property-json-schema-for-animeapi-v3--oneof--array-of-anime--anime-schema--anidb--anyof--item-0)
      * [1.1.2.2. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > anidb > anyOf > item 1`](#1122-property-json-schema-for-animeapi-v3--oneof--array-of-anime--anime-schema--anidb--anyof--item-1)
    * [1.1.3. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > animeplanet`](#113-property-json-schema-for-animeapi-v3--oneof--array-of-anime--anime-schema--animeplanet)
      * [1.1.3.1. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > animeplanet > anyOf > item 0`](#1131-property-json-schema-for-animeapi-v3--oneof--array-of-anime--anime-schema--animeplanet--anyof--item-0)
      * [1.1.3.2. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > animeplanet > anyOf > item 1`](#1132-property-json-schema-for-animeapi-v3--oneof--array-of-anime--anime-schema--animeplanet--anyof--item-1)
    * [1.1.4. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > anisearch`](#114-property-json-schema-for-animeapi-v3--oneof--array-of-anime--anime-schema--anisearch)
      * [1.1.4.1. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > anidb > anyOf > item 0`](#1141-property-json-schema-for-animeapi-v3--oneof--array-of-anime--anime-schema--anidb--anyof--item-0)
      * [1.1.4.2. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > anidb > anyOf > item 1`](#1142-property-json-schema-for-animeapi-v3--oneof--array-of-anime--anime-schema--anidb--anyof--item-1)
    * [1.1.5. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > annict`](#115-property-json-schema-for-animeapi-v3--oneof--array-of-anime--anime-schema--annict)
      * [1.1.5.1. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > anidb > anyOf > item 0`](#1151-property-json-schema-for-animeapi-v3--oneof--array-of-anime--anime-schema--anidb--anyof--item-0)
      * [1.1.5.2. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > anidb > anyOf > item 1`](#1152-property-json-schema-for-animeapi-v3--oneof--array-of-anime--anime-schema--anidb--anyof--item-1)
    * [1.1.6. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > imdb`](#116-property-json-schema-for-animeapi-v3--oneof--array-of-anime--anime-schema--imdb)
      * [1.1.6.1. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > animeplanet > anyOf > item 0`](#1161-property-json-schema-for-animeapi-v3--oneof--array-of-anime--anime-schema--animeplanet--anyof--item-0)
      * [1.1.6.2. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > animeplanet > anyOf > item 1`](#1162-property-json-schema-for-animeapi-v3--oneof--array-of-anime--anime-schema--animeplanet--anyof--item-1)
    * [1.1.7. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > kaize`](#117-property-json-schema-for-animeapi-v3--oneof--array-of-anime--anime-schema--kaize)
      * [1.1.7.1. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > animeplanet > anyOf > item 0`](#1171-property-json-schema-for-animeapi-v3--oneof--array-of-anime--anime-schema--animeplanet--anyof--item-0)
      * [1.1.7.2. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > animeplanet > anyOf > item 1`](#1172-property-json-schema-for-animeapi-v3--oneof--array-of-anime--anime-schema--animeplanet--anyof--item-1)
    * [1.1.8. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > kaize_id`](#118-property-json-schema-for-animeapi-v3--oneof--array-of-anime--anime-schema--kaize_id)
      * [1.1.8.1. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > anidb > anyOf > item 0`](#1181-property-json-schema-for-animeapi-v3--oneof--array-of-anime--anime-schema--anidb--anyof--item-0)
      * [1.1.8.2. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > anidb > anyOf > item 1`](#1182-property-json-schema-for-animeapi-v3--oneof--array-of-anime--anime-schema--anidb--anyof--item-1)
    * [1.1.9. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > kitsu`](#119-property-json-schema-for-animeapi-v3--oneof--array-of-anime--anime-schema--kitsu)
      * [1.1.9.1. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > anidb > anyOf > item 0`](#1191-property-json-schema-for-animeapi-v3--oneof--array-of-anime--anime-schema--anidb--anyof--item-0)
      * [1.1.9.2. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > anidb > anyOf > item 1`](#1192-property-json-schema-for-animeapi-v3--oneof--array-of-anime--anime-schema--anidb--anyof--item-1)
    * [1.1.10. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > livechart`](#1110-property-json-schema-for-animeapi-v3--oneof--array-of-anime--anime-schema--livechart)
      * [1.1.10.1. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > anidb > anyOf > item 0`](#11101-property-json-schema-for-animeapi-v3--oneof--array-of-anime--anime-schema--anidb--anyof--item-0)
      * [1.1.10.2. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > anidb > anyOf > item 1`](#11102-property-json-schema-for-animeapi-v3--oneof--array-of-anime--anime-schema--anidb--anyof--item-1)
    * [1.1.11. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > myanimelist`](#1111-property-json-schema-for-animeapi-v3--oneof--array-of-anime--anime-schema--myanimelist)
      * [1.1.11.1. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > anidb > anyOf > item 0`](#11111-property-json-schema-for-animeapi-v3--oneof--array-of-anime--anime-schema--anidb--anyof--item-0)
      * [1.1.11.2. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > anidb > anyOf > item 1`](#11112-property-json-schema-for-animeapi-v3--oneof--array-of-anime--anime-schema--anidb--anyof--item-1)
    * [1.1.12. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > nautiljon`](#1112-property-json-schema-for-animeapi-v3--oneof--array-of-anime--anime-schema--nautiljon)
      * [1.1.12.1. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > animeplanet > anyOf > item 0`](#11121-property-json-schema-for-animeapi-v3--oneof--array-of-anime--anime-schema--animeplanet--anyof--item-0)
      * [1.1.12.2. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > animeplanet > anyOf > item 1`](#11122-property-json-schema-for-animeapi-v3--oneof--array-of-anime--anime-schema--animeplanet--anyof--item-1)
    * [1.1.13. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > nautiljon_id`](#1113-property-json-schema-for-animeapi-v3--oneof--array-of-anime--anime-schema--nautiljon_id)
      * [1.1.13.1. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > anidb > anyOf > item 0`](#11131-property-json-schema-for-animeapi-v3--oneof--array-of-anime--anime-schema--anidb--anyof--item-0)
      * [1.1.13.2. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > anidb > anyOf > item 1`](#11132-property-json-schema-for-animeapi-v3--oneof--array-of-anime--anime-schema--anidb--anyof--item-1)
    * [1.1.14. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > notify`](#1114-property-json-schema-for-animeapi-v3--oneof--array-of-anime--anime-schema--notify)
      * [1.1.14.1. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > animeplanet > anyOf > item 0`](#11141-property-json-schema-for-animeapi-v3--oneof--array-of-anime--anime-schema--animeplanet--anyof--item-0)
      * [1.1.14.2. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > animeplanet > anyOf > item 1`](#11142-property-json-schema-for-animeapi-v3--oneof--array-of-anime--anime-schema--animeplanet--anyof--item-1)
    * [1.1.15. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > otakotaku`](#1115-property-json-schema-for-animeapi-v3--oneof--array-of-anime--anime-schema--otakotaku)
      * [1.1.15.1. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > anidb > anyOf > item 0`](#11151-property-json-schema-for-animeapi-v3--oneof--array-of-anime--anime-schema--anidb--anyof--item-0)
      * [1.1.15.2. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > anidb > anyOf > item 1`](#11152-property-json-schema-for-animeapi-v3--oneof--array-of-anime--anime-schema--anidb--anyof--item-1)
    * [1.1.16. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > shikimori`](#1116-property-json-schema-for-animeapi-v3--oneof--array-of-anime--anime-schema--shikimori)
      * [1.1.16.1. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > anidb > anyOf > item 0`](#11161-property-json-schema-for-animeapi-v3--oneof--array-of-anime--anime-schema--anidb--anyof--item-0)
      * [1.1.16.2. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > anidb > anyOf > item 1`](#11162-property-json-schema-for-animeapi-v3--oneof--array-of-anime--anime-schema--anidb--anyof--item-1)
    * [1.1.17. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > shoboi`](#1117-property-json-schema-for-animeapi-v3--oneof--array-of-anime--anime-schema--shoboi)
      * [1.1.17.1. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > anidb > anyOf > item 0`](#11171-property-json-schema-for-animeapi-v3--oneof--array-of-anime--anime-schema--anidb--anyof--item-0)
      * [1.1.17.2. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > anidb > anyOf > item 1`](#11172-property-json-schema-for-animeapi-v3--oneof--array-of-anime--anime-schema--anidb--anyof--item-1)
    * [1.1.18. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > silveryasha`](#1118-property-json-schema-for-animeapi-v3--oneof--array-of-anime--anime-schema--silveryasha)
      * [1.1.18.1. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > anidb > anyOf > item 0`](#11181-property-json-schema-for-animeapi-v3--oneof--array-of-anime--anime-schema--anidb--anyof--item-0)
      * [1.1.18.2. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > anidb > anyOf > item 1`](#11182-property-json-schema-for-animeapi-v3--oneof--array-of-anime--anime-schema--anidb--anyof--item-1)
    * [1.1.19. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > simkl`](#1119-property-json-schema-for-animeapi-v3--oneof--array-of-anime--anime-schema--simkl)
      * [1.1.19.1. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > anidb > anyOf > item 0`](#11191-property-json-schema-for-animeapi-v3--oneof--array-of-anime--anime-schema--anidb--anyof--item-0)
      * [1.1.19.2. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > anidb > anyOf > item 1`](#11192-property-json-schema-for-animeapi-v3--oneof--array-of-anime--anime-schema--anidb--anyof--item-1)
    * [1.1.20. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > themoviedb`](#1120-property-json-schema-for-animeapi-v3--oneof--array-of-anime--anime-schema--themoviedb)
      * [1.1.20.1. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > anidb > anyOf > item 0`](#11201-property-json-schema-for-animeapi-v3--oneof--array-of-anime--anime-schema--anidb--anyof--item-0)
      * [1.1.20.2. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > anidb > anyOf > item 1`](#11202-property-json-schema-for-animeapi-v3--oneof--array-of-anime--anime-schema--anidb--anyof--item-1)
    * [1.1.21. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > themoviedb_season`](#1121-property-json-schema-for-animeapi-v3--oneof--array-of-anime--anime-schema--themoviedb_season)
      * [1.1.21.1. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > anidb > anyOf > item 0`](#11211-property-json-schema-for-animeapi-v3--oneof--array-of-anime--anime-schema--anidb--anyof--item-0)
      * [1.1.21.2. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > anidb > anyOf > item 1`](#11212-property-json-schema-for-animeapi-v3--oneof--array-of-anime--anime-schema--anidb--anyof--item-1)
    * [1.1.22. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > themoviedb_type`](#1122-property-json-schema-for-animeapi-v3--oneof--array-of-anime--anime-schema--themoviedb_type)
      * [1.1.22.1. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > themoviedb_type > anyOf > item 0`](#11221-property-json-schema-for-animeapi-v3--oneof--array-of-anime--anime-schema--themoviedb_type--anyof--item-0)
      * [1.1.22.2. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > themoviedb_type > anyOf > item 1`](#11222-property-json-schema-for-animeapi-v3--oneof--array-of-anime--anime-schema--themoviedb_type--anyof--item-1)
    * [1.1.23. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > title`](#1123-property-json-schema-for-animeapi-v3--oneof--array-of-anime--anime-schema--title)
    * [1.1.24. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > trakt`](#1124-property-json-schema-for-animeapi-v3--oneof--array-of-anime--anime-schema--trakt)
      * [1.1.24.1. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > anidb > anyOf > item 0`](#11241-property-json-schema-for-animeapi-v3--oneof--array-of-anime--anime-schema--anidb--anyof--item-0)
      * [1.1.24.2. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > anidb > anyOf > item 1`](#11242-property-json-schema-for-animeapi-v3--oneof--array-of-anime--anime-schema--anidb--anyof--item-1)
    * [1.1.25. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > trakt_season`](#1125-property-json-schema-for-animeapi-v3--oneof--array-of-anime--anime-schema--trakt_season)
      * [1.1.25.1. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > anidb > anyOf > item 0`](#11251-property-json-schema-for-animeapi-v3--oneof--array-of-anime--anime-schema--anidb--anyof--item-0)
      * [1.1.25.2. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > anidb > anyOf > item 1`](#11252-property-json-schema-for-animeapi-v3--oneof--array-of-anime--anime-schema--anidb--anyof--item-1)
    * [1.1.26. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > trakt_type`](#1126-property-json-schema-for-animeapi-v3--oneof--array-of-anime--anime-schema--trakt_type)
      * [1.1.26.1. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > trakt_type > anyOf > item 0`](#11261-property-json-schema-for-animeapi-v3--oneof--array-of-anime--anime-schema--trakt_type--anyof--item-0)
      * [1.1.26.2. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > trakt_type > anyOf > item 1`](#11262-property-json-schema-for-animeapi-v3--oneof--array-of-anime--anime-schema--trakt_type--anyof--item-1)
* [2. Property `JSON Schema for AnimeAPI V3 > oneOf > Anime Object`](#2-property-json-schema-for-animeapi-v3--oneof--anime-object)
  * [2.1. Property `JSON Schema for AnimeAPI V3 > oneOf > Anime Object > oneOf > Anime Schema`](#21-property-json-schema-for-animeapi-v3--oneof--anime-object--oneof--anime-schema)
  * [2.2. Property `JSON Schema for AnimeAPI V3 > oneOf > Anime Object > oneOf > item 1`](#22-property-json-schema-for-animeapi-v3--oneof--anime-object--oneof--item-1)
    * [2.2.1. Property `JSON Schema for AnimeAPI V3 > oneOf > Anime Object > oneOf > item 1 > Anime Schema`](#221-property-json-schema-for-animeapi-v3--oneof--anime-object--oneof--item-1--anime-schema)

**Title:** JSON Schema for AnimeAPI V3

|                           |                  |
| ------------------------- | ---------------- |
| **Type**                  | `combining`      |
| **Required**              | No               |
| **Additional properties** | Any type allowed |

**Description:** This schema is used to validate the JSON response from AnimeAPI V3. Schema is not backward compatible with previous versions. Website: https://animeapi.my.id

| One of(Option)              |
| --------------------------- |
| [Array of Anime](#oneOf_i0) |
| [Anime Object](#oneOf_i1)   |

## <a name="oneOf_i0"></a>1. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime`

**Title:** Array of Anime

|              |         |
| ------------ | ------- |
| **Type**     | `array` |
| **Required** | No      |

**Description:** Schema for array of anime

|                      | Array restrictions |
| -------------------- | ------------------ |
| **Min items**        | N/A                |
| **Max items**        | N/A                |
| **Items unicity**    | False              |
| **Additional items** | False              |
| **Tuple validation** | See below          |

| Each item of this array must be | Description      |
| ------------------------------- | ---------------- |
| [Anime Schema](#oneOf_i0_items) | Schema for anime |

### <a name="oneOf_i0_items"></a>1.1. JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema

**Title:** Anime Schema

|                           |                     |
| ------------------------- | ------------------- |
| **Type**                  | `object`            |
| **Required**              | No                  |
| **Additional properties** | Not allowed         |
| **Defined in**            | #/definitions/anime |

**Description:** Schema for anime

| Property                                                  | Pattern | Type   | Deprecated | Definition                      | Title/Description                |
| --------------------------------------------------------- | ------- | ------ | ---------- | ------------------------------- | -------------------------------- |
| + [anidb](#oneOf_i0_items_anidb )                         | No      | object | No         | In #/definitions/numbernull     | aniDB                            |
| + [anilist](#oneOf_i0_items_anilist )                     | No      | object | No         | In #/definitions/numbernull     | AniList                          |
| + [animeplanet](#oneOf_i0_items_animeplanet )             | No      | object | No         | In #/definitions/stringnull     | Anime-Planet                     |
| + [anisearch](#oneOf_i0_items_anisearch )                 | No      | object | No         | In #/definitions/numbernull     | AniSearch                        |
| + [annict](#oneOf_i0_items_annict )                       | No      | object | No         | In #/definitions/numbernull     | Annict                           |
| + [imdb](#oneOf_i0_items_imdb )                           | No      | object | No         | In #/definitions/stringnull     | IMDb                             |
| + [kaize](#oneOf_i0_items_kaize )                         | No      | object | No         | In #/definitions/stringnull     | Kaize                            |
| + [kaize_id](#oneOf_i0_items_kaize_id )                   | No      | object | No         | In #/definitions/numbernull     | Kaize ID                         |
| + [kitsu](#oneOf_i0_items_kitsu )                         | No      | object | No         | In #/definitions/numbernull     | Kitsu                            |
| + [livechart](#oneOf_i0_items_livechart )                 | No      | object | No         | In #/definitions/numbernull     | LiveChart                        |
| + [myanimelist](#oneOf_i0_items_myanimelist )             | No      | object | No         | In #/definitions/numbernull     | MyAnimeList                      |
| + [nautiljon](#oneOf_i0_items_nautiljon )                 | No      | object | No         | In #/definitions/stringnull     | Nautiljon                        |
| + [nautiljon_id](#oneOf_i0_items_nautiljon_id )           | No      | object | No         | In #/definitions/numbernull     | Nautiljon ID                     |
| + [notify](#oneOf_i0_items_notify )                       | No      | object | No         | In #/definitions/stringnull     | Notify.moe                       |
| + [otakotaku](#oneOf_i0_items_otakotaku )                 | No      | object | No         | In #/definitions/numbernull     | Otak Otaku                       |
| + [shikimori](#oneOf_i0_items_shikimori )                 | No      | object | No         | In #/definitions/numbernull     | Shikimori/Шикимори               |
| + [shoboi](#oneOf_i0_items_shoboi )                       | No      | object | No         | In #/definitions/numbernull     | Shoboi/Syobocal/しょぼいカレンダー        |
| + [silveryasha](#oneOf_i0_items_silveryasha )             | No      | object | No         | In #/definitions/numbernull     | Silveryasha                      |
| + [simkl](#oneOf_i0_items_simkl )                         | No      | object | No         | In #/definitions/numbernull     | SIMKL                            |
| + [themoviedb](#oneOf_i0_items_themoviedb )               | No      | object | No         | In #/definitions/numbernull     | The Movie Database (TMDB)        |
| - [themoviedb_season](#oneOf_i0_items_themoviedb_season ) | No      | object | No         | In #/definitions/numbernull     | The Movie Database (TMDB) Season |
| - [themoviedb_type](#oneOf_i0_items_themoviedb_type )     | No      | object | No         | In #/definitions/themoviedbtype | The Movie Database (TMDB) Type   |
| + [title](#oneOf_i0_items_title )                         | No      | string | No         | -                               | Title                            |
| + [trakt](#oneOf_i0_items_trakt )                         | No      | object | No         | In #/definitions/numbernull     | Trakt                            |
| + [trakt_season](#oneOf_i0_items_trakt_season )           | No      | object | No         | In #/definitions/numbernull     | Trakt Season                     |
| + [trakt_type](#oneOf_i0_items_trakt_type )               | No      | object | No         | In #/definitions/trakttype      | Trakt Type                       |

#### <a name="oneOf_i0_items_anidb"></a>1.1.1. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > anidb`

**Title:** aniDB

|                           |                          |
| ------------------------- | ------------------------ |
| **Type**                  | `combining`              |
| **Required**              | Yes                      |
| **Additional properties** | Any type allowed         |
| **Default**               | `null`                   |
| **Defined in**            | #/definitions/numbernull |

**Description:** aniDB ID, website: https://anidb.net/

| Any of(Option)                           |
| ---------------------------------------- |
| [item 0](#oneOf_i0_items_anidb_anyOf_i0) |
| [item 1](#oneOf_i0_items_anidb_anyOf_i1) |

##### <a name="oneOf_i0_items_anidb_anyOf_i0"></a>1.1.1.1. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > anidb > anyOf > item 0`

|              |          |
| ------------ | -------- |
| **Type**     | `number` |
| **Required** | No       |

##### <a name="oneOf_i0_items_anidb_anyOf_i1"></a>1.1.1.2. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > anidb > anyOf > item 1`

|              |        |
| ------------ | ------ |
| **Type**     | `null` |
| **Required** | No     |

#### <a name="oneOf_i0_items_anilist"></a>1.1.2. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > anilist`

**Title:** AniList

|                           |                          |
| ------------------------- | ------------------------ |
| **Type**                  | `combining`              |
| **Required**              | Yes                      |
| **Additional properties** | Any type allowed         |
| **Default**               | `null`                   |
| **Defined in**            | #/definitions/numbernull |

**Description:** AniList ID, website: https://anilist.co/

| Any of(Option)                           |
| ---------------------------------------- |
| [item 0](#oneOf_i0_items_anidb_anyOf_i0) |
| [item 1](#oneOf_i0_items_anidb_anyOf_i1) |

##### <a name="oneOf_i0_items_anidb_anyOf_i0"></a>1.1.2.1. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > anidb > anyOf > item 0`

|              |          |
| ------------ | -------- |
| **Type**     | `number` |
| **Required** | No       |

##### <a name="oneOf_i0_items_anidb_anyOf_i1"></a>1.1.2.2. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > anidb > anyOf > item 1`

|              |        |
| ------------ | ------ |
| **Type**     | `null` |
| **Required** | No     |

#### <a name="oneOf_i0_items_animeplanet"></a>1.1.3. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > animeplanet`

**Title:** Anime-Planet

|                           |                          |
| ------------------------- | ------------------------ |
| **Type**                  | `combining`              |
| **Required**              | Yes                      |
| **Additional properties** | Any type allowed         |
| **Default**               | `null`                   |
| **Defined in**            | #/definitions/stringnull |

**Description:** Anime-Planet slug, website: https://www.anime-planet.com/

| Any of(Option)                                 |
| ---------------------------------------------- |
| [item 0](#oneOf_i0_items_animeplanet_anyOf_i0) |
| [item 1](#oneOf_i0_items_animeplanet_anyOf_i1) |

##### <a name="oneOf_i0_items_animeplanet_anyOf_i0"></a>1.1.3.1. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > animeplanet > anyOf > item 0`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |

##### <a name="oneOf_i0_items_animeplanet_anyOf_i1"></a>1.1.3.2. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > animeplanet > anyOf > item 1`

|              |        |
| ------------ | ------ |
| **Type**     | `null` |
| **Required** | No     |

| Restrictions                      |                                                                                   |
| --------------------------------- | --------------------------------------------------------------------------------- |
| **Must match regular expression** | ```^[a-z0-9\-]+$``` [Test](https://regex101.com/?regex=%5E%5Ba-z0-9%5C-%5D%2B%24) |

#### <a name="oneOf_i0_items_anisearch"></a>1.1.4. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > anisearch`

**Title:** AniSearch

|                           |                          |
| ------------------------- | ------------------------ |
| **Type**                  | `combining`              |
| **Required**              | Yes                      |
| **Additional properties** | Any type allowed         |
| **Default**               | `null`                   |
| **Defined in**            | #/definitions/numbernull |

**Description:** AniSearch ID, website: https://www.anisearch.com/, https://anisearch.de, https://anisearch.it, https://anisearch.es, https://anisearch.fr, https://anisearch.jp

| Any of(Option)                           |
| ---------------------------------------- |
| [item 0](#oneOf_i0_items_anidb_anyOf_i0) |
| [item 1](#oneOf_i0_items_anidb_anyOf_i1) |

##### <a name="oneOf_i0_items_anidb_anyOf_i0"></a>1.1.4.1. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > anidb > anyOf > item 0`

|              |          |
| ------------ | -------- |
| **Type**     | `number` |
| **Required** | No       |

##### <a name="oneOf_i0_items_anidb_anyOf_i1"></a>1.1.4.2. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > anidb > anyOf > item 1`

|              |        |
| ------------ | ------ |
| **Type**     | `null` |
| **Required** | No     |

#### <a name="oneOf_i0_items_annict"></a>1.1.5. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > annict`

**Title:** Annict

|                           |                          |
| ------------------------- | ------------------------ |
| **Type**                  | `combining`              |
| **Required**              | Yes                      |
| **Additional properties** | Any type allowed         |
| **Default**               | `null`                   |
| **Defined in**            | #/definitions/numbernull |

**Description:** Annict ID, website: https://annict.com/, https://en.annict.com/, https://annict.jp/

| Any of(Option)                           |
| ---------------------------------------- |
| [item 0](#oneOf_i0_items_anidb_anyOf_i0) |
| [item 1](#oneOf_i0_items_anidb_anyOf_i1) |

##### <a name="oneOf_i0_items_anidb_anyOf_i0"></a>1.1.5.1. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > anidb > anyOf > item 0`

|              |          |
| ------------ | -------- |
| **Type**     | `number` |
| **Required** | No       |

##### <a name="oneOf_i0_items_anidb_anyOf_i1"></a>1.1.5.2. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > anidb > anyOf > item 1`

|              |        |
| ------------ | ------ |
| **Type**     | `null` |
| **Required** | No     |

#### <a name="oneOf_i0_items_imdb"></a>1.1.6. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > imdb`

**Title:** IMDb

|                           |                          |
| ------------------------- | ------------------------ |
| **Type**                  | `combining`              |
| **Required**              | Yes                      |
| **Additional properties** | Any type allowed         |
| **Default**               | `null`                   |
| **Defined in**            | #/definitions/stringnull |

**Description:** IMDb ID, website: https://www.imdb.com/

| Any of(Option)                                 |
| ---------------------------------------------- |
| [item 0](#oneOf_i0_items_animeplanet_anyOf_i0) |
| [item 1](#oneOf_i0_items_animeplanet_anyOf_i1) |

##### <a name="oneOf_i0_items_animeplanet_anyOf_i0"></a>1.1.6.1. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > animeplanet > anyOf > item 0`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |

##### <a name="oneOf_i0_items_animeplanet_anyOf_i1"></a>1.1.6.2. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > animeplanet > anyOf > item 1`

|              |        |
| ------------ | ------ |
| **Type**     | `null` |
| **Required** | No     |

| Restrictions                      |                                                                           |
| --------------------------------- | ------------------------------------------------------------------------- |
| **Must match regular expression** | ```^tt[\d]+$``` [Test](https://regex101.com/?regex=%5Ett%5B%5Cd%5D%2B%24) |

#### <a name="oneOf_i0_items_kaize"></a>1.1.7. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > kaize`

**Title:** Kaize

|                           |                          |
| ------------------------- | ------------------------ |
| **Type**                  | `combining`              |
| **Required**              | Yes                      |
| **Additional properties** | Any type allowed         |
| **Default**               | `null`                   |
| **Defined in**            | #/definitions/stringnull |

**Description:** Kaize slug, website: https://kaize.io/

| Any of(Option)                                 |
| ---------------------------------------------- |
| [item 0](#oneOf_i0_items_animeplanet_anyOf_i0) |
| [item 1](#oneOf_i0_items_animeplanet_anyOf_i1) |

##### <a name="oneOf_i0_items_animeplanet_anyOf_i0"></a>1.1.7.1. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > animeplanet > anyOf > item 0`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |

##### <a name="oneOf_i0_items_animeplanet_anyOf_i1"></a>1.1.7.2. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > animeplanet > anyOf > item 1`

|              |        |
| ------------ | ------ |
| **Type**     | `null` |
| **Required** | No     |

| Restrictions                      |                                                                                   |
| --------------------------------- | --------------------------------------------------------------------------------- |
| **Must match regular expression** | ```^[a-z0-9\-]+$``` [Test](https://regex101.com/?regex=%5E%5Ba-z0-9%5C-%5D%2B%24) |

#### <a name="oneOf_i0_items_kaize_id"></a>1.1.8. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > kaize_id`

**Title:** Kaize ID

|                           |                          |
| ------------------------- | ------------------------ |
| **Type**                  | `combining`              |
| **Required**              | Yes                      |
| **Additional properties** | Any type allowed         |
| **Default**               | `null`                   |
| **Defined in**            | #/definitions/numbernull |

**Description:** Kaize ID in integer format, not recommended as some entry can't be found its ID compared to slug

| Any of(Option)                           |
| ---------------------------------------- |
| [item 0](#oneOf_i0_items_anidb_anyOf_i0) |
| [item 1](#oneOf_i0_items_anidb_anyOf_i1) |

##### <a name="oneOf_i0_items_anidb_anyOf_i0"></a>1.1.8.1. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > anidb > anyOf > item 0`

|              |          |
| ------------ | -------- |
| **Type**     | `number` |
| **Required** | No       |

##### <a name="oneOf_i0_items_anidb_anyOf_i1"></a>1.1.8.2. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > anidb > anyOf > item 1`

|              |        |
| ------------ | ------ |
| **Type**     | `null` |
| **Required** | No     |

#### <a name="oneOf_i0_items_kitsu"></a>1.1.9. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > kitsu`

**Title:** Kitsu

|                           |                          |
| ------------------------- | ------------------------ |
| **Type**                  | `combining`              |
| **Required**              | Yes                      |
| **Additional properties** | Any type allowed         |
| **Default**               | `null`                   |
| **Defined in**            | #/definitions/numbernull |

**Description:** Kitsu ID in integer, slug not suppported, website: https://kitsu.app/

| Any of(Option)                           |
| ---------------------------------------- |
| [item 0](#oneOf_i0_items_anidb_anyOf_i0) |
| [item 1](#oneOf_i0_items_anidb_anyOf_i1) |

##### <a name="oneOf_i0_items_anidb_anyOf_i0"></a>1.1.9.1. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > anidb > anyOf > item 0`

|              |          |
| ------------ | -------- |
| **Type**     | `number` |
| **Required** | No       |

##### <a name="oneOf_i0_items_anidb_anyOf_i1"></a>1.1.9.2. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > anidb > anyOf > item 1`

|              |        |
| ------------ | ------ |
| **Type**     | `null` |
| **Required** | No     |

#### <a name="oneOf_i0_items_livechart"></a>1.1.10. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > livechart`

**Title:** LiveChart

|                           |                          |
| ------------------------- | ------------------------ |
| **Type**                  | `combining`              |
| **Required**              | Yes                      |
| **Additional properties** | Any type allowed         |
| **Default**               | `null`                   |
| **Defined in**            | #/definitions/numbernull |

**Description:** LiveChart ID, website: https://www.livechart.me/

| Any of(Option)                           |
| ---------------------------------------- |
| [item 0](#oneOf_i0_items_anidb_anyOf_i0) |
| [item 1](#oneOf_i0_items_anidb_anyOf_i1) |

##### <a name="oneOf_i0_items_anidb_anyOf_i0"></a>1.1.10.1. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > anidb > anyOf > item 0`

|              |          |
| ------------ | -------- |
| **Type**     | `number` |
| **Required** | No       |

##### <a name="oneOf_i0_items_anidb_anyOf_i1"></a>1.1.10.2. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > anidb > anyOf > item 1`

|              |        |
| ------------ | ------ |
| **Type**     | `null` |
| **Required** | No     |

#### <a name="oneOf_i0_items_myanimelist"></a>1.1.11. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > myanimelist`

**Title:** MyAnimeList

|                           |                          |
| ------------------------- | ------------------------ |
| **Type**                  | `combining`              |
| **Required**              | Yes                      |
| **Additional properties** | Any type allowed         |
| **Default**               | `null`                   |
| **Defined in**            | #/definitions/numbernull |

**Description:** MyAnimeList ID, website: https://myanimelist.net/

| Any of(Option)                           |
| ---------------------------------------- |
| [item 0](#oneOf_i0_items_anidb_anyOf_i0) |
| [item 1](#oneOf_i0_items_anidb_anyOf_i1) |

##### <a name="oneOf_i0_items_anidb_anyOf_i0"></a>1.1.11.1. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > anidb > anyOf > item 0`

|              |          |
| ------------ | -------- |
| **Type**     | `number` |
| **Required** | No       |

##### <a name="oneOf_i0_items_anidb_anyOf_i1"></a>1.1.11.2. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > anidb > anyOf > item 1`

|              |        |
| ------------ | ------ |
| **Type**     | `null` |
| **Required** | No     |

#### <a name="oneOf_i0_items_nautiljon"></a>1.1.12. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > nautiljon`

**Title:** Nautiljon

|                           |                          |
| ------------------------- | ------------------------ |
| **Type**                  | `combining`              |
| **Required**              | Yes                      |
| **Additional properties** | Any type allowed         |
| **Default**               | `null`                   |
| **Defined in**            | #/definitions/stringnull |

**Description:** Nautiljon slug in plus, website: https://www.nautiljon.com/

| Any of(Option)                                 |
| ---------------------------------------------- |
| [item 0](#oneOf_i0_items_animeplanet_anyOf_i0) |
| [item 1](#oneOf_i0_items_animeplanet_anyOf_i1) |

##### <a name="oneOf_i0_items_animeplanet_anyOf_i0"></a>1.1.12.1. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > animeplanet > anyOf > item 0`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |

##### <a name="oneOf_i0_items_animeplanet_anyOf_i1"></a>1.1.12.2. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > animeplanet > anyOf > item 1`

|              |        |
| ------------ | ------ |
| **Type**     | `null` |
| **Required** | No     |

#### <a name="oneOf_i0_items_nautiljon_id"></a>1.1.13. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > nautiljon_id`

**Title:** Nautiljon ID

|                           |                          |
| ------------------------- | ------------------------ |
| **Type**                  | `combining`              |
| **Required**              | Yes                      |
| **Additional properties** | Any type allowed         |
| **Default**               | `null`                   |
| **Defined in**            | #/definitions/numbernull |

**Description:** Nautiljon ID in integer format, used internally

| Any of(Option)                           |
| ---------------------------------------- |
| [item 0](#oneOf_i0_items_anidb_anyOf_i0) |
| [item 1](#oneOf_i0_items_anidb_anyOf_i1) |

##### <a name="oneOf_i0_items_anidb_anyOf_i0"></a>1.1.13.1. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > anidb > anyOf > item 0`

|              |          |
| ------------ | -------- |
| **Type**     | `number` |
| **Required** | No       |

##### <a name="oneOf_i0_items_anidb_anyOf_i1"></a>1.1.13.2. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > anidb > anyOf > item 1`

|              |        |
| ------------ | ------ |
| **Type**     | `null` |
| **Required** | No     |

#### <a name="oneOf_i0_items_notify"></a>1.1.14. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > notify`

**Title:** Notify.moe

|                           |                          |
| ------------------------- | ------------------------ |
| **Type**                  | `combining`              |
| **Required**              | Yes                      |
| **Additional properties** | Any type allowed         |
| **Default**               | `null`                   |
| **Defined in**            | #/definitions/stringnull |

**Description:** Notify.moe Base64 ID, website: https://notify.moe/

| Any of(Option)                                 |
| ---------------------------------------------- |
| [item 0](#oneOf_i0_items_animeplanet_anyOf_i0) |
| [item 1](#oneOf_i0_items_animeplanet_anyOf_i1) |

##### <a name="oneOf_i0_items_animeplanet_anyOf_i0"></a>1.1.14.1. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > animeplanet > anyOf > item 0`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |

##### <a name="oneOf_i0_items_animeplanet_anyOf_i1"></a>1.1.14.2. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > animeplanet > anyOf > item 1`

|              |        |
| ------------ | ------ |
| **Type**     | `null` |
| **Required** | No     |

| Restrictions                      |                                                                                               |
| --------------------------------- | --------------------------------------------------------------------------------------------- |
| **Must match regular expression** | ```^[a-zA-Z0-9\-\_]+$``` [Test](https://regex101.com/?regex=%5E%5Ba-zA-Z0-9%5C-%5C_%5D%2B%24) |

#### <a name="oneOf_i0_items_otakotaku"></a>1.1.15. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > otakotaku`

**Title:** Otak Otaku

|                           |                          |
| ------------------------- | ------------------------ |
| **Type**                  | `combining`              |
| **Required**              | Yes                      |
| **Additional properties** | Any type allowed         |
| **Default**               | `null`                   |
| **Defined in**            | #/definitions/numbernull |

**Description:** Otak Otaku ID, website: https://otakotaku.com/

| Any of(Option)                           |
| ---------------------------------------- |
| [item 0](#oneOf_i0_items_anidb_anyOf_i0) |
| [item 1](#oneOf_i0_items_anidb_anyOf_i1) |

##### <a name="oneOf_i0_items_anidb_anyOf_i0"></a>1.1.15.1. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > anidb > anyOf > item 0`

|              |          |
| ------------ | -------- |
| **Type**     | `number` |
| **Required** | No       |

##### <a name="oneOf_i0_items_anidb_anyOf_i1"></a>1.1.15.2. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > anidb > anyOf > item 1`

|              |        |
| ------------ | ------ |
| **Type**     | `null` |
| **Required** | No     |

#### <a name="oneOf_i0_items_shikimori"></a>1.1.16. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > shikimori`

**Title:** Shikimori/Шикимори

|                           |                          |
| ------------------------- | ------------------------ |
| **Type**                  | `combining`              |
| **Required**              | Yes                      |
| **Additional properties** | Any type allowed         |
| **Default**               | `null`                   |
| **Defined in**            | #/definitions/numbernull |

**Description:** Shikimori ID (nonprefixed), based on MyAnimeList ID. Remove prefix if found on the ID, website: https://shikimori.one/

| Any of(Option)                           |
| ---------------------------------------- |
| [item 0](#oneOf_i0_items_anidb_anyOf_i0) |
| [item 1](#oneOf_i0_items_anidb_anyOf_i1) |

##### <a name="oneOf_i0_items_anidb_anyOf_i0"></a>1.1.16.1. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > anidb > anyOf > item 0`

|              |          |
| ------------ | -------- |
| **Type**     | `number` |
| **Required** | No       |

##### <a name="oneOf_i0_items_anidb_anyOf_i1"></a>1.1.16.2. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > anidb > anyOf > item 1`

|              |        |
| ------------ | ------ |
| **Type**     | `null` |
| **Required** | No     |

#### <a name="oneOf_i0_items_shoboi"></a>1.1.17. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > shoboi`

**Title:** Shoboi/Syobocal/しょぼいカレンダー

|                           |                          |
| ------------------------- | ------------------------ |
| **Type**                  | `combining`              |
| **Required**              | Yes                      |
| **Additional properties** | Any type allowed         |
| **Default**               | `null`                   |
| **Defined in**            | #/definitions/numbernull |

**Description:** Shoboi ID, website: http://cal.syoboi.jp/

| Any of(Option)                           |
| ---------------------------------------- |
| [item 0](#oneOf_i0_items_anidb_anyOf_i0) |
| [item 1](#oneOf_i0_items_anidb_anyOf_i1) |

##### <a name="oneOf_i0_items_anidb_anyOf_i0"></a>1.1.17.1. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > anidb > anyOf > item 0`

|              |          |
| ------------ | -------- |
| **Type**     | `number` |
| **Required** | No       |

##### <a name="oneOf_i0_items_anidb_anyOf_i1"></a>1.1.17.2. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > anidb > anyOf > item 1`

|              |        |
| ------------ | ------ |
| **Type**     | `null` |
| **Required** | No     |

#### <a name="oneOf_i0_items_silveryasha"></a>1.1.18. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > silveryasha`

**Title:** Silveryasha

|                           |                          |
| ------------------------- | ------------------------ |
| **Type**                  | `combining`              |
| **Required**              | Yes                      |
| **Additional properties** | Any type allowed         |
| **Default**               | `null`                   |
| **Defined in**            | #/definitions/numbernull |

**Description:** Silveryasha ID, website: https://db.silveryasha.id/

| Any of(Option)                           |
| ---------------------------------------- |
| [item 0](#oneOf_i0_items_anidb_anyOf_i0) |
| [item 1](#oneOf_i0_items_anidb_anyOf_i1) |

##### <a name="oneOf_i0_items_anidb_anyOf_i0"></a>1.1.18.1. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > anidb > anyOf > item 0`

|              |          |
| ------------ | -------- |
| **Type**     | `number` |
| **Required** | No       |

##### <a name="oneOf_i0_items_anidb_anyOf_i1"></a>1.1.18.2. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > anidb > anyOf > item 1`

|              |        |
| ------------ | ------ |
| **Type**     | `null` |
| **Required** | No     |

#### <a name="oneOf_i0_items_simkl"></a>1.1.19. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > simkl`

**Title:** SIMKL

|                           |                          |
| ------------------------- | ------------------------ |
| **Type**                  | `combining`              |
| **Required**              | Yes                      |
| **Additional properties** | Any type allowed         |
| **Default**               | `null`                   |
| **Defined in**            | #/definitions/numbernull |

**Description:** SIMKL ID, website: https://simkl.com/

| Any of(Option)                           |
| ---------------------------------------- |
| [item 0](#oneOf_i0_items_anidb_anyOf_i0) |
| [item 1](#oneOf_i0_items_anidb_anyOf_i1) |

##### <a name="oneOf_i0_items_anidb_anyOf_i0"></a>1.1.19.1. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > anidb > anyOf > item 0`

|              |          |
| ------------ | -------- |
| **Type**     | `number` |
| **Required** | No       |

##### <a name="oneOf_i0_items_anidb_anyOf_i1"></a>1.1.19.2. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > anidb > anyOf > item 1`

|              |        |
| ------------ | ------ |
| **Type**     | `null` |
| **Required** | No     |

#### <a name="oneOf_i0_items_themoviedb"></a>1.1.20. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > themoviedb`

**Title:** The Movie Database (TMDB)

|                           |                          |
| ------------------------- | ------------------------ |
| **Type**                  | `combining`              |
| **Required**              | Yes                      |
| **Additional properties** | Any type allowed         |
| **Default**               | `null`                   |
| **Defined in**            | #/definitions/numbernull |

**Description:** The Movie Database ID, website: https://www.themoviedb.org/

| Any of(Option)                           |
| ---------------------------------------- |
| [item 0](#oneOf_i0_items_anidb_anyOf_i0) |
| [item 1](#oneOf_i0_items_anidb_anyOf_i1) |

##### <a name="oneOf_i0_items_anidb_anyOf_i0"></a>1.1.20.1. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > anidb > anyOf > item 0`

|              |          |
| ------------ | -------- |
| **Type**     | `number` |
| **Required** | No       |

##### <a name="oneOf_i0_items_anidb_anyOf_i1"></a>1.1.20.2. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > anidb > anyOf > item 1`

|              |        |
| ------------ | ------ |
| **Type**     | `null` |
| **Required** | No     |

#### <a name="oneOf_i0_items_themoviedb_season"></a>1.1.21. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > themoviedb_season`

**Title:** The Movie Database (TMDB) Season

|                           |                          |
| ------------------------- | ------------------------ |
| **Type**                  | `combining`              |
| **Required**              | No                       |
| **Additional properties** | Any type allowed         |
| **Default**               | `null`                   |
| **Defined in**            | #/definitions/numbernull |

**Description:** The Movie Database season number, only used if themoviedb_type is 'shows', else null

| Any of(Option)                           |
| ---------------------------------------- |
| [item 0](#oneOf_i0_items_anidb_anyOf_i0) |
| [item 1](#oneOf_i0_items_anidb_anyOf_i1) |

##### <a name="oneOf_i0_items_anidb_anyOf_i0"></a>1.1.21.1. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > anidb > anyOf > item 0`

|              |          |
| ------------ | -------- |
| **Type**     | `number` |
| **Required** | No       |

##### <a name="oneOf_i0_items_anidb_anyOf_i1"></a>1.1.21.2. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > anidb > anyOf > item 1`

|              |        |
| ------------ | ------ |
| **Type**     | `null` |
| **Required** | No     |

#### <a name="oneOf_i0_items_themoviedb_type"></a>1.1.22. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > themoviedb_type`

**Title:** The Movie Database (TMDB) Type

|                           |                              |
| ------------------------- | ---------------------------- |
| **Type**                  | `combining`                  |
| **Required**              | No                           |
| **Additional properties** | Any type allowed             |
| **Default**               | `null`                       |
| **Defined in**            | #/definitions/themoviedbtype |

**Description:** The Movie Database type, either 'movie' or 'tv'

| Any of(Option)                                     |
| -------------------------------------------------- |
| [item 0](#oneOf_i0_items_themoviedb_type_anyOf_i0) |
| [item 1](#oneOf_i0_items_themoviedb_type_anyOf_i1) |

##### <a name="oneOf_i0_items_themoviedb_type_anyOf_i0"></a>1.1.22.1. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > themoviedb_type > anyOf > item 0`

|              |                    |
| ------------ | ------------------ |
| **Type**     | `enum (of string)` |
| **Required** | No                 |

Must be one of:
* "movie"
* "tv"

##### <a name="oneOf_i0_items_themoviedb_type_anyOf_i1"></a>1.1.22.2. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > themoviedb_type > anyOf > item 1`

|              |        |
| ------------ | ------ |
| **Type**     | `null` |
| **Required** | No     |

#### <a name="oneOf_i0_items_title"></a>1.1.23. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > title`

**Title:** Title

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |

**Description:** Title of the anime

#### <a name="oneOf_i0_items_trakt"></a>1.1.24. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > trakt`

**Title:** Trakt

|                           |                          |
| ------------------------- | ------------------------ |
| **Type**                  | `combining`              |
| **Required**              | Yes                      |
| **Additional properties** | Any type allowed         |
| **Default**               | `null`                   |
| **Defined in**            | #/definitions/numbernull |

**Description:** Trakt ID, slug not supported, website: https://trakt.tv/

| Any of(Option)                           |
| ---------------------------------------- |
| [item 0](#oneOf_i0_items_anidb_anyOf_i0) |
| [item 1](#oneOf_i0_items_anidb_anyOf_i1) |

##### <a name="oneOf_i0_items_anidb_anyOf_i0"></a>1.1.24.1. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > anidb > anyOf > item 0`

|              |          |
| ------------ | -------- |
| **Type**     | `number` |
| **Required** | No       |

##### <a name="oneOf_i0_items_anidb_anyOf_i1"></a>1.1.24.2. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > anidb > anyOf > item 1`

|              |        |
| ------------ | ------ |
| **Type**     | `null` |
| **Required** | No     |

#### <a name="oneOf_i0_items_trakt_season"></a>1.1.25. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > trakt_season`

**Title:** Trakt Season

|                           |                          |
| ------------------------- | ------------------------ |
| **Type**                  | `combining`              |
| **Required**              | Yes                      |
| **Additional properties** | Any type allowed         |
| **Default**               | `null`                   |
| **Defined in**            | #/definitions/numbernull |

**Description:** Trakt season number, only used if trakt_type is 'shows', else null

| Any of(Option)                           |
| ---------------------------------------- |
| [item 0](#oneOf_i0_items_anidb_anyOf_i0) |
| [item 1](#oneOf_i0_items_anidb_anyOf_i1) |

##### <a name="oneOf_i0_items_anidb_anyOf_i0"></a>1.1.25.1. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > anidb > anyOf > item 0`

|              |          |
| ------------ | -------- |
| **Type**     | `number` |
| **Required** | No       |

##### <a name="oneOf_i0_items_anidb_anyOf_i1"></a>1.1.25.2. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > anidb > anyOf > item 1`

|              |        |
| ------------ | ------ |
| **Type**     | `null` |
| **Required** | No     |

#### <a name="oneOf_i0_items_trakt_type"></a>1.1.26. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > trakt_type`

**Title:** Trakt Type

|                           |                         |
| ------------------------- | ----------------------- |
| **Type**                  | `combining`             |
| **Required**              | Yes                     |
| **Additional properties** | Any type allowed        |
| **Default**               | `null`                  |
| **Defined in**            | #/definitions/trakttype |

**Description:** Trakt type, either 'movies' or 'shows'

| Any of(Option)                                |
| --------------------------------------------- |
| [item 0](#oneOf_i0_items_trakt_type_anyOf_i0) |
| [item 1](#oneOf_i0_items_trakt_type_anyOf_i1) |

##### <a name="oneOf_i0_items_trakt_type_anyOf_i0"></a>1.1.26.1. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > trakt_type > anyOf > item 0`

|              |                    |
| ------------ | ------------------ |
| **Type**     | `enum (of string)` |
| **Required** | No                 |

Must be one of:
* "movies"
* "shows"

##### <a name="oneOf_i0_items_trakt_type_anyOf_i1"></a>1.1.26.2. Property `JSON Schema for AnimeAPI V3 > oneOf > Array of Anime > Anime Schema > trakt_type > anyOf > item 1`

|              |        |
| ------------ | ------ |
| **Type**     | `null` |
| **Required** | No     |

## <a name="oneOf_i1"></a>2. Property `JSON Schema for AnimeAPI V3 > oneOf > Anime Object`

**Title:** Anime Object

|                           |                  |
| ------------------------- | ---------------- |
| **Type**                  | `combining`      |
| **Required**              | No               |
| **Additional properties** | Any type allowed |

**Description:** Schema for anime object

| One of(Option)                     |
| ---------------------------------- |
| [Anime Schema](#oneOf_i1_oneOf_i0) |
| [item 1](#oneOf_i1_oneOf_i1)       |

### <a name="oneOf_i1_oneOf_i0"></a>2.1. Property `JSON Schema for AnimeAPI V3 > oneOf > Anime Object > oneOf > Anime Schema`

**Title:** Anime Schema

|                           |                                 |
| ------------------------- | ------------------------------- |
| **Type**                  | `object`                        |
| **Required**              | No                              |
| **Additional properties** | Not allowed                     |
| **Same definition as**    | [Anime Schema](#oneOf_i0_items) |

**Description:** Schema for anime

### <a name="oneOf_i1_oneOf_i1"></a>2.2. Property `JSON Schema for AnimeAPI V3 > oneOf > Anime Object > oneOf > item 1`

|                           |                                                                                                |
| ------------------------- | ---------------------------------------------------------------------------------------------- |
| **Type**                  | `object`                                                                                       |
| **Required**              | No                                                                                             |
| **Additional properties** | [Each additional property must conform to the schema](#oneOf_i1_oneOf_i1_additionalProperties) |

| Property                                       | Pattern | Type   | Deprecated | Definition                               | Title/Description |
| ---------------------------------------------- | ------- | ------ | ---------- | ---------------------------------------- | ----------------- |
| - [](#oneOf_i1_oneOf_i1_additionalProperties ) | No      | object | No         | Same as [Anime Schema](#oneOf_i0_items ) | Anime Schema      |

#### <a name="oneOf_i1_oneOf_i1_additionalProperties"></a>2.2.1. Property `JSON Schema for AnimeAPI V3 > oneOf > Anime Object > oneOf > item 1 > Anime Schema`

**Title:** Anime Schema

|                           |                                 |
| ------------------------- | ------------------------------- |
| **Type**                  | `object`                        |
| **Required**              | No                              |
| **Additional properties** | Not allowed                     |
| **Same definition as**    | [Anime Schema](#oneOf_i0_items) |

**Description:** Schema for anime

----------------------------------------------------------------------------------------------------------------------------
Generated using [json-schema-for-humans](https://github.com/coveooss/json-schema-for-humans) on 2025-03-19 at 13:44:55 +0700
