> [!WARNING]
>
> This branch is work in progress. Stable release of this branch may or may not be a final product for public use.

# nattadasu's RESTful AnimeAPI v4

AnimeAPI is a RESTful API that provides anime relation mapping across multiple anime databases. It mainly focuses on providing relations between anime titles from different databases.

## Why use AnimeAPI?

Compared to other relation mapping API, AnimeAPI provides more databases yet
it's still easy to use. It also provides more data than other relation mapping
API, such as the anime title itself.

Below is the comparison between AnimeAPI and other relation mapping API.

<!-- markdownlint-disable MD013 MD060 -->

| Project | License | Access & Rate Limits | Formats | Basic metadata | Supported Platforms |
| :--- | :--- | :--- | :--- | :---: | :---: |
| **AnimeAPI** | MIT[^1] | Public / No limits | REST, JSON, TSV, SQLite | ✔ | ![f:adb] ![f:al] ![f:an] ![f:ap] ![f:as] ![f:ac] ![f:hka] ![f:imdb] ![f:kz] ![f:kts] ![f:krz] ![f:lbx] ![f:lc] ![f:mal] ![f:ntj] ![f:ntf] ![f:oo] ![f:shk] ![f:shb] ![f:sy] ![f:smk] ![f:tmdb] ![f:trk] ![f:tvdb] ![f:tvtm] <br> *(All 22+ platforms)* |
| **[manami-project/anime-offline-database][aod]** | ODbL, DbCL | Public Dump | JSON | ✔ | ![f:mal] ![f:al] ![f:adb] ![f:kts] ![f:lc] ![f:as] ![f:ap] ![f:smk] ![f:an] |
| **[kawaiioverflow/arm][arm]** | MIT | Public / No limits | Node Package, REST, JSON | ❌ | ![f:mal] ![f:al] ![f:ac] ![f:shb] |
| **[Fribb/anime-lists][fal]** | Unknown | Public Dump | JSON | ❌ | ![f:mal] ![f:al] ![f:adb] ![f:kts] ![f:lc] ![f:as] ![f:ap] ![f:smk] ![f:an] ![f:ntf] ![f:shk] ![f:tmdb] ![f:tvdb] ![f:imdb] |
| **[beeequeue/arm-server][bq]** | AGPL-3.0 | Public / No limits | REST | ❌ | ![f:adb] ![f:al] ![f:ap] ![f:as] ![f:imdb] ![f:kts] ![f:lc] ![f:mal] ![f:ntf] ![f:shk] ![f:tmdb] [^2] ![f:tvdb] |
| **[Atelier-Shiori/Hato][hato]** | Apache-2.0 | Paid (API Key) / No limits | REST | ❌ | ![f:al] ![f:kts] ![f:mal] ![f:ntf] ![f:adb] |
| **[SIMKL][smk]** | Proprietary | API Key / 1k reqs/day | REST | ✔ | ![f:mal] ![f:tmdb] ![f:tvdb] ![f:imdb] ![f:adb] ![f:trk] <br> *Result-only:* ![f:al] ![f:an] ![f:ap] ![f:as] ![f:kts] ![f:lc] |
| **[Trakt][trk]** | Proprietary | API Key / 1k reqs/5 mins | REST | ✔ | ![f:tmdb] ![f:tvdb] ![f:imdb] |
| **[Anime-Lists/anime-lists][alal]** | Unknown | Public / No limits | XML, XLSX | ❌ | ![f:adb] ![f:tvdb] ![f:tmdb] [^2] ![f:imdb] |
| **[rensetsu/db.trakt.extended-anitrakt][atip]** | MIT | Public Dump | JSON | ✔ | ![f:trk] ![f:tmdb] ![f:tvdb] ![f:lbx] ![f:imdb] |

[^1]: Unless otherwise stated, usually due to dump requirement imposed by 1st party or 3rd party provider, AnimeAPI is generally MIT-licensed. Read more about it on [Licensing](#licensing)
[^2]: *Movie only*

<!-- markdownlint-enable MD013 MD060 -->

## Licensing

AnimeAPI is generally licensed under [MIT License](LICENSE). Dump data provided by 1st party or 3rd party may impose different licensing and attribution requirement. Please read following exclusion list to learn more about:

* *Currently none*

## Limitation

Because AnimeAPI uses a flat, 1-to-1 mapping model (allowing only a single ID per provider per entry), it cannot natively represent **1-to-many** or **many-to-many** relationships across different databases.

This leads to mapping discrepancies in several common scenarios:

* **Specials, OVAs, and Movies:** Side stories or prequel films may be cataloged as special episodes within a main entry on one platform (like AniDB or TVDB), but split into standalone entries on others. By default, AnimeAPI conforms to MyAnimeList's entry structure to achieve compatibility across different databases.
* **Split-cours:** Shows broadcast in two separate parts may be merged under one entry or split depending on the database's moderation policies.

## Featured on

Do you want to integrate AnimeAPI into your project? Or do you want to see how AnimeAPI is used in other projects and their use cases? Check out the list below!

> [!TIP]
>
> If you want to add your project to this list, please open a pull request adding your project to the table below. Please make sure to add a short description of your project and a link to your project's homepage.

| Name | Type | Language | Homepage | Description |
| :--- | :--: | :------- | :------- | :---------- |


## Supported Platforms and Aliases

AnimeAPI supported following sites for media lookup. You can use this as an alias cheatsheet as well.

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
|        `kurozora` ![f:krz] | `kr`  | `krz`, `kurozora.app`                                                                           |
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
[krz]: https://kurozora.app
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
