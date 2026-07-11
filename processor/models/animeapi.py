from datetime import date, datetime
from enum import Enum
from warnings import deprecated

from pydantic_extra_types.country import CountryAlpha2
from pydantic_extra_types.ulid import ULID
from pydantic import UUID4, AliasChoices, Base64UrlStr, BaseModel, BeforeValidator, ConfigDict, Field, NonNegativeInt, PositiveInt
from typing import Annotated, Any


def convert_date_to_str(v: Any) -> Any:
    if isinstance(v, (datetime, date)):
        return v.strftime("%Y-%m-%d")
    return v


class TitleModel(BaseModel):
    model_config = ConfigDict(use_attribute_docstrings=True)
    display: str
    """Display title, usually in Romaji or localized"""
    english: str | None = None
    """English title of the release"""
    native: str | None = None
    """Native title of the release based on country of origin"""


class MediaTypeEnum(str, Enum):
    TV = "TV"
    OVA = "OVA"
    MOVIE = "MOVIE"
    SPECIAL = "SPECIAL"
    PV = "PV"
    MUSIV = "MUSIC"
    OTHER = "OTHER"


class MetaModel(BaseModel):
    model_config = ConfigDict(use_attribute_docstrings=True)
    start_date: Annotated[
        str | None,
        BeforeValidator(convert_date_to_str),
        Field(default=None, pattern=r"^\d{4}(?:-\d{2}(?:-\d{2})?)?$"),
    ] = None
    """Start date of the release, using YYYY[-MM[-DD]] format"""
    type: MediaTypeEnum | None = MediaTypeEnum.OTHER
    """Type of media released"""
    total: PositiveInt | None = None
    """Total released episodes, so far"""
    country: CountryAlpha2 | None = "JP"
    """Country of origin of the media"""


class SlugIdPair(BaseModel):
    model_config = ConfigDict(use_attribute_docstrings=True)
    id: PositiveInt | None
    """Numerical int used by platform for API requests"""
    slug: str | None
    """Human readable identifier usually placed on URL"""


class AnimeComModel(BaseModel):
    model_config = ConfigDict(use_attribute_docstrings=True)
    uuid: UUID4
    """Anime.com Unique Identifier"""
    slug: str
    """Anime.com human-readable slug"""


class KinopoiskType(str, Enum):
    SERIES = "series"
    FILM = "film"


class KinopoiskModel(BaseModel):
    model_config = ConfigDict(use_attribute_docstrings=True)
    type: KinopoiskType
    """Type of media on Kinopoisk"""
    id: PositiveInt
    """Media ID on Kinopoisk"""


class LetterboxdModel(BaseModel):
    model_config = ConfigDict(use_attribute_docstrings=True)
    lid: str | None = None
    """Letterboxd Letter ID, used for interacting official API"""
    slug: str | None = None
    """Letterboxd Slug, used for navigating to the webpage"""
    uid: PositiveInt | None = None
    """Letterboxd Unique Int ID, unknown use"""


class SeasonIdentifier(BaseModel):
    model_config = ConfigDict(use_attribute_docstrings=True)
    pos: NonNegativeInt
    """Official season number, human readable, eg shows/one-piece/seasons/1"""
    id: PositiveInt | None = None
    """Season ID used for API calls"""


class TheMovieDbType(str, Enum):
    TV = "tv"
    MOVIE = "movie"


class TheMovieDbModel(BaseModel):
    model_config = ConfigDict(use_attribute_docstrings=True)
    id: PositiveInt
    """TheMovieDB ID"""
    type: TheMovieDbType
    """TheMovieDB media type (tv or movie)"""
    may_invalid: bool = False
    """Define if the season/cour is not split and compatible with anime-oriented database. If `true`, season mapping will be nulled"""
    season: SeasonIdentifier | None = None
    """TheMovieDB season information"""


class TheTvdbType(str, Enum):
    SERIES = "series"
    MOVIES = "movies"


class TheTvdbModel(BaseModel):
    model_config = ConfigDict(use_attribute_docstrings=True)
    id: PositiveInt
    """TheTVDB ID"""
    type: TheTvdbType = TheTvdbType.SERIES
    """TheTVDB media type (series or movies)"""
    slug: str | None = None
    """TheTVDB slug identifier"""
    may_invalid: bool = False
    """Define if the season/cour is not split and compatible with anime-oriented database. If `true`, season mapping will be nulled"""
    season: SeasonIdentifier | None = None
    """TheTVDB season information"""


class TraktType(str, Enum):
    SHOWS = "shows"
    MOVIES = "movies"


class TraktModel(BaseModel):
    model_config = ConfigDict(use_attribute_docstrings=True)
    id: PositiveInt
    """Trakt ID"""
    type: TraktType
    """Trakt media type (shows or movies)"""
    slug: str | None = None
    """Trakt slug identifier"""
    may_invalid: bool = False
    """Define if the season/cour is not split and compatible with anime-oriented database. If `true`, season mapping will be nulled"""
    season: SeasonIdentifier | None = None
    """Trakt season information"""


class MappingsModel(BaseModel):
    model_config = ConfigDict(use_attribute_docstrings=True)
    anidb: PositiveInt | None = None
    """AniDB ID (https://anidb.net)"""
    anilist: PositiveInt | None = None
    """AniList ID (https://anilist.co)"""
    animecom: AnimeComModel | None = None
    """Anime.com model mappings (https://anime.com)"""
    animeoshi: SlugIdPair | None = None
    """AnimeOshi mappings (https://animeoshi.com)"""
    animeplanet: SlugIdPair | None = None
    """Anime-Planet mappings (https://www.anime-planet.com)"""
    anisearch: PositiveInt | None = None
    """aniSearch ID (https://www.anisearch.com)"""
    animenewsnetwork: Annotated[
        PositiveInt | None, Field(validation_alias=AliasChoices("animenewsnetwork", "ann"))
    ] = None
    """Anime News Network ID (https://www.animenewsnetwork.com)"""
    annict: PositiveInt | None = None
    """Annict ID (https://annict.com)"""
    bangumi: Annotated[
        PositiveInt | None, Field(validation_alias=AliasChoices("bangumi", "bgm"))
    ] = None
    """Bangumi ID (https://bgm.tv)"""
    douban: PositiveInt | None = None
    """Douban ID (https://movie.douban.com)"""
    hikka: str | None = None
    """Hikka ID or slug (https://hikka.io)"""
    imdb: str | None = None
    """IMDb ID (https://www.imdb.com)"""
    kaize: SlugIdPair | None = None
    """Kaize mappings (https://kaize.io)"""
    kinopoisk: KinopoiskModel | None = None
    """Kinopoisk model mappings (https://www.kinopoisk.ru)"""
    kitsu: SlugIdPair | None = None
    """Kitsu mappings (https://kitsu.io)"""
    letterboxd: LetterboxdModel | None = None
    """Letterboxd model mappings (https://letterboxd.com)"""
    livechart: PositiveInt | None = None
    """LiveChart ID (https://www.livechart.me)"""
    myanimelist: PositiveInt | None = None
    """MyAnimeList ID (https://myanimelist.net)"""
    notify: Annotated[
        Base64UrlStr | None, Field(validation_alias=AliasChoices("notify", "notifymoe"))
    ] = None
    """Notify.moe ID (https://notify.moe)"""
    otakotaku: PositiveInt | None = None
    """Otakotaku ID (https://otakotaku.com)"""
    syoboi: Annotated[
        PositiveInt | None,
        Field(
            validation_alias=AliasChoices(
                "syoboi",
                "shoboi",
                "syobocal",
                "shobocal",
                "syoboicalendar",
                "shoboicalendar",
            )
        ),
    ] = None
    """Syoboi Calendar ID (https://cal.syoboi.jp)"""
    themoviedb: Annotated[
        TheMovieDbModel | None,
        Field(validation_alias=AliasChoices("themoviedb", "tmdb")),
    ] = None
    """TheMovieDB (TMDB) model mappings (https://www.themoviedb.org)"""
    thetvdb: Annotated[
        TheTvdbModel | None, Field(validation_alias=AliasChoices("thetvdb", "tvdb"))
    ] = None
    """TheTVDB model mappings (https://thetvdb.com)"""
    trakt: TraktModel | None = None
    """Trakt model mappings (https://trakt.tv)"""
    worldarts: PositiveInt | None = None
    """World Art ID (http://www.world-art.ru)"""


class AnimeApiV4Data(BaseModel):
    model_config = ConfigDict(use_attribute_docstrings=True)
    ulid: ULID
    """Unique ULID of the record"""
    title: TitleModel
    """Title details of the release"""
    meta: MetaModel
    """Metadata details (dates, format types, total episodes, country)"""
    mappings: MappingsModel
    """Platform database ID/slug mapping relationships"""

    def to_v3(self) -> "AnimeApiV3Data":
        m = self.mappings
        return AnimeApiV3Data(
            title=self.title.display,
            anidb=m.anidb,
            anilist=m.anilist,
            animecom_slug=m.animecom.slug if m.animecom else None,
            animecom_uuid=m.animecom.uuid if m.animecom else None,
            animenewsnetwork=m.animenewsnetwork,
            animeoshi=m.animeoshi.slug if m.animeoshi else None,
            animeoshi_id=m.animeoshi.id if m.animeoshi else None,
            animeplanet=m.animeplanet.slug if m.animeplanet else None,
            animeplanet_id=m.animeplanet.id if m.animeplanet else None,
            anisearch=m.anisearch,
            annict=m.annict,
            bangumi=m.bangumi,
            douban=m.douban,
            hikka=m.hikka,
            imdb=m.imdb,
            kaize=m.kaize.slug if m.kaize else None,
            kaize_id=m.kaize.id if m.kaize else None,
            kinopoisk_id=m.kinopoisk.id if m.kinopoisk else None,
            kinopoisk_type=m.kinopoisk.type if m.kinopoisk else None,
            kitsu=m.kitsu.id if m.kitsu else None,
            kitsu_slug=m.kitsu.slug if m.kitsu else None,
            letterboxd_lid=m.letterboxd.lid if m.letterboxd else None,
            letterboxd_slug=m.letterboxd.slug if m.letterboxd else None,
            letterboxd_uid=m.letterboxd.uid if m.letterboxd else None,
            livechart=m.livechart,
            myanimelist=m.myanimelist,
            notify=m.notify,
            otakotaku=m.otakotaku,
            shoboi=m.syoboi,
            themoviedb=m.themoviedb.id if m.themoviedb else None,
            themoviedb_season=m.themoviedb.season.pos if m.themoviedb and m.themoviedb.season else None,
            themoviedb_season_id=m.themoviedb.season.id if m.themoviedb and m.themoviedb.season else None,
            themoviedb_type=m.themoviedb.type if m.themoviedb else None,
            thetvdb=m.thetvdb.id if m.thetvdb else None,
            thetvdb_season=m.thetvdb.season.pos if m.thetvdb and m.thetvdb.season else None,
            thetvdb_season_id=m.thetvdb.season.id if m.thetvdb and m.thetvdb.season else None,
            thetvdb_slug=m.thetvdb.slug if m.thetvdb else None,
            thetvdb_type=m.thetvdb.type if m.thetvdb else None,
            trakt=m.trakt.id if m.trakt else None,
            trakt_season=m.trakt.season.pos if m.trakt and m.trakt.season else None,
            trakt_season_id=m.trakt.season.id if m.trakt and m.trakt.season else None,
            trakt_slug=m.trakt.slug if m.trakt else None,
            trakt_type=m.trakt.type if m.trakt else None,
            worldarts=m.worldarts,
        )


@deprecated("Use V4")
class AnimeApiV3Data(BaseModel):
    model_config = ConfigDict(use_attribute_docstrings=True)
    title: str
    """Main title of the anime"""
    anidb: PositiveInt | None = None
    """AniDB ID (https://anidb.net)"""
    anilist: PositiveInt | None = None
    """AniList ID (https://anilist.co)"""
    animecom_slug: str | None = None
    """Anime.com slug (https://anime.com)"""
    animecom_uuid: UUID4 | None = None
    """Anime.com UUID (https://anime.com)"""
    animenewsnetwork: Annotated[
        PositiveInt | None, Field(validation_alias=AliasChoices("animenewsnetwork", "ann"))
    ] = None
    """Anime News Network ID (https://www.animenewsnetwork.com)"""
    animeoshi: str | None = None
    """AnimeOshi slug (https://animeoshi.com)"""
    animeoshi_id: PositiveInt | None = None
    """AnimeOshi ID (https://animeoshi.com)"""
    animeplanet: str | None = None
    """Anime-Planet slug (https://www.anime-planet.com)"""
    animeplanet_id: PositiveInt | None = None
    """Anime-Planet ID (https://www.anime-planet.com)"""
    anisearch: PositiveInt | None = None
    """aniSearch ID (https://www.anisearch.com)"""
    annict: PositiveInt | None = None
    """Annict ID (https://annict.com)"""
    bangumi: Annotated[
        PositiveInt | None, Field(validation_alias=AliasChoices("bangumi", "bgm"))
    ] = None
    """Bangumi ID (https://bgm.tv)"""
    douban: PositiveInt | None = None
    """Douban ID (https://movie.douban.com)"""
    hikka: str | None = None
    """Hikka ID or slug (https://hikka.io)"""
    imdb: str | None = None
    """IMDb ID (https://www.imdb.com)"""
    kaize: str | None = None
    """Kaize slug (https://kaize.io)"""
    kaize_id: PositiveInt | None = None
    """Kaize ID (https://kaize.io)"""
    kinopoisk_id: PositiveInt | None = None
    """Kinopoisk ID (https://www.kinopoisk.ru)"""
    kinopoisk_type: KinopoiskType | None = None
    """Kinopoisk media type (https://www.kinopoisk.ru)"""
    kitsu: PositiveInt | None = None
    """Kitsu ID (https://kitsu.io)"""
    kitsu_slug: str | None = None
    """Kitsu slug (https://kitsu.io)"""
    letterboxd_lid: str | None = None
    """Letterboxd Letter ID (https://letterboxd.com)"""
    letterboxd_slug: str | None = None
    """Letterboxd slug (https://letterboxd.com)"""
    letterboxd_uid: PositiveInt | None = None
    """Letterboxd unique integer ID (https://letterboxd.com)"""
    livechart: PositiveInt | None = None
    """LiveChart ID (https://www.livechart.me)"""
    myanimelist: PositiveInt | None = None
    """MyAnimeList ID (https://myanimelist.net)"""
    nautiljon: str | None = None
    """Nautiljon slug (https://www.nautiljon.com)"""
    nautiljon_id: PositiveInt | None = None
    """Nautiljon ID (https://www.nautiljon.com)"""
    notify: Annotated[
        Base64UrlStr | None, Field(validation_alias=AliasChoices("notify", "notifymoe"))
    ] = None
    """Notify.moe ID (https://notify.moe)"""
    otakotaku: PositiveInt | None = None
    """Otakotaku ID (https://otakotaku.com)"""
    shikimori: PositiveInt | None = None
    """Shikimori ID (https://shikimori.one)"""
    shoboi: Annotated[
        PositiveInt | None,
        Field(
            validation_alias=AliasChoices(
                "shoboi",
                "syoboi",
                "syobocal",
                "shobocal",
                "syoboicalendar",
                "shoboicalendar",
            )
        ),
    ] = None
    """Syoboi Calendar ID (https://cal.syoboi.jp)"""
    silveryasha: PositiveInt | None = None
    """SilverYasha ID (https://db.silveryasha.id)"""
    simkl: PositiveInt | None = None
    """Simkl ID (https://simkl.com)"""
    themoviedb: Annotated[
        PositiveInt | None, Field(validation_alias=AliasChoices("themoviedb", "tmdb"))
    ] = None
    """TheMovieDB (TMDB) ID (https://www.themoviedb.org)"""
    themoviedb_season: Annotated[
        NonNegativeInt | None, Field(validation_alias=AliasChoices("themoviedb_season", "tmdb_season"))
    ] = None
    """TheMovieDB season number (https://www.themoviedb.org)"""
    themoviedb_season_id: Annotated[
        PositiveInt | None, Field(validation_alias=AliasChoices("themoviedb_season_id", "tmdb_season_id"))
    ] = None
    """TheMovieDB season ID (https://www.themoviedb.org)"""
    themoviedb_type: Annotated[
        TheMovieDbType | None, Field(validation_alias=AliasChoices("themoviedb_type", "tmdb_type"))
    ] = None
    """TheMovieDB media type (tv/movie) (https://www.themoviedb.org)"""
    thetvdb: Annotated[
        PositiveInt | None, Field(validation_alias=AliasChoices("thetvdb", "tvdb"))
    ] = None
    """TheTVDB ID (https://thetvdb.com)"""
    thetvdb_season: Annotated[
        NonNegativeInt | None, Field(validation_alias=AliasChoices("thetvdb_season", "tvdb_season"))
    ] = None
    """TheTVDB season number (https://thetvdb.com)"""
    thetvdb_season_id: Annotated[
        PositiveInt | None, Field(validation_alias=AliasChoices("thetvdb_season_id", "tvdb_season_id"))
    ] = None
    """TheTVDB season ID (https://thetvdb.com)"""
    thetvdb_slug: Annotated[
        str | None, Field(validation_alias=AliasChoices("thetvdb_slug", "tvdb_slug"))
    ] = None
    """TheTVDB slug (https://thetvdb.com)"""
    thetvdb_type: Annotated[
        TheTvdbType | None, Field(validation_alias=AliasChoices("thetvdb_type", "tvdb_type"))
    ] = None
    """TheTVDB media type (https://thetvdb.com)"""
    trakt: PositiveInt | None = None
    """Trakt ID (https://trakt.tv)"""
    trakt_may_invalid: bool | None = None
    """Flag indicating Trakt mapping status (https://trakt.tv)"""
    trakt_season: NonNegativeInt | None = None
    """Trakt season number (https://trakt.tv)"""
    trakt_season_id: PositiveInt | None = None
    """Trakt season ID (https://trakt.tv)"""
    trakt_slug: str | None = None
    """Trakt slug (https://trakt.tv)"""
    trakt_type: TraktType | None = None
    """Trakt media type (https://trakt.tv)"""
    worldarts: PositiveInt | None = None
    """World Art ID (http://www.world-art.ru)"""
