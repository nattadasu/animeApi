# nattadasu's Mock REST API for Anime (AnimeAPI)

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
- [x] [Trakt](https://trakt.tv/)

## Returned Value

```ts
type StringNull = string | null;
type NumberNull = number | null;
type TraktType = "movies" | "shows";

interface Anime = {
    title:            string;
    anidb:        NumberNull;
    anilist:      NumberNull;
    animeplanet:  StringNull;
    anisearch:    NumberNull;
    annict:       NumberNull;
    kaize:        StringNull;
    kitsu:        NumberNull;
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

<!-- markdownlint-disable MD033 -->
<details><summary>Example of <code>myanimelist/1</code></summary><pre>{
  "title": "Cowboy Bebop",
  "anidb": 23,
  "anilist": 1,
  "animeplanet": "cowboy-bebop",
  "anisearch": 1572,
  "kaize": "cowboy-bebop",
  "kitsu": 1,
  "livechart": 3418,
  "myanimelist": 1,
  "notify": "Tk3ccKimg",
  "silveryasha": 2652
}</pre></details>
<!-- markdownlint-enable MD033 -->

## Usage

To use this API, you can access the following endpoints:

```http
GET https://aniapi.nattadasu.com/
```

All requests must be `GET`, and response always will be in JSON format.

> **Warning**
>
> If an entry can not be found, the API will return `404` status code and GitHub
> Pages' default 404 page.

### Get all items in Array

```http
/animeApi.json
```

### Get All ID in Object/Dictionary format of each provider

> **Notes**
>
> Use this endpoint as "cache"-like for your application, so you don't have to
> query the API for every title you want to get the ID, which is useful for
> offline indexer that already have the ID from supported providers.

```http
/<PROVIDER>.json
```

`<PROVIDER>` can be one of the following:

`anidb`, `anilist`, `animeplanet`, `anisearch`, `annict`, `kaize`, `kitsu`,
`livechart`, `myanimelist`, `notify`, `otakotaku`, `shikimori`,
`shoboi`, `silveryasha`, `trakt`

### Get All ID in Array/List format of each provider

```http
/<PROVIDER>().json
```

`<PROVIDER>` can be one of the following:

`anidb`, `anilist`, `animeplanet`, `anisearch`, `annict`, `kaize`, `kitsu`,
`livechart`, `myanimelist`, `notify`, `otakotaku`, `shikimori`,
`shoboi`, `silveryasha`, `trakt`

If your application unable to reach the endpoint, replace `()` to `%28%29`.

### Get a relation of ID to title

```http
/<PROVIDER>/<ID>
```

`<PROVIDER>` can be one of the following:

`anidb`, `anilist`, `animeplanet`, `anisearch`, `annict`, `kaize`, `kitsu`,
`livechart`, `myanimelist`, `notify`, `otakotaku`, `shikimori`,
`shoboi`, `silveryasha`, `trakt`

`<ID>` is the ID of the title in the provider.

#### Provider exclusive rules

##### Shikimori

`shikimori` IDs are basically the same as `myanimelist` IDs. If you get a
`404` status code, remove any alphabetical prefix from the ID and try again.

For example: `z218` -> `218`

##### Trakt

For `trakt` provider, the ID is in the format of `<TYPE>/<ID>` where `<TYPE>`
is either `movies` or `shows` and `<ID>` is the ID of the title in the provider.

An ID on Trakt must in numerical value. If your application obtained slug as ID
instead, you can resolve/convert it to ID using following Trakt API endpoint:

```https
GET https://api.trakt.tv/search/trakt/<ID>?type=<movie|show>
```

To get exact season mapping, append `/season/<SEASON>` to the end of the ID,
where `<SEASON>` is the season number of the title in the provider.

For example, to get the ID of `Mairimashita Iruma-kun` Season 3, you can use:

```http
GET https://aniapi.nattadasu.com/trakt/shows/152334/seasons/3
```

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
