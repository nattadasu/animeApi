from datetime import date
from enum import Enum
from typing import Annotated, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
)


class SeasonEnum(Enum):
    SPRING = "SPRING"
    SUMMER = "SUMMER"
    FALL = "FALL"
    WINTER = "WINTER"
    UNDEFINED = "UNDEFINED"


class AnimeSeasonData(BaseModel):
    model_config = ConfigDict(use_attribute_docstrings=True)
    season: SeasonEnum = SeasonEnum.UNDEFINED
    """Season in which the first release occurred"""
    year: Annotated[int | None, Field(ge=1907)] = None
    """Year of first release"""


class AnimeDurationData(BaseModel):
    model_config = ConfigDict(use_attribute_docstrings=True)
    value: int = 0
    """Duration in seconds"""
    unit: Literal["SECONDS"] = "SECONDS"
    """For (de)serialization this value is always ``SECONDS``"""


class AnimeScoreData(BaseModel):
    model_config = ConfigDict(use_attribute_docstrings=True)
    arithmeticGeometricMean: float = 0.0
    """Arithmetic–geometric mean based on all available scores from all metadata providers"""
    arithmeticMean: float = 0.0
    """Arithmetic mean based on all available scores from all metadata providers"""
    median: float = 0.0
    """Median based on all available scores from all metadata providers"""


class AnimeTypeEnum(Enum):
    TV = "TV"
    MOVIE = "MOVIE"
    OVA = "OVA"
    ONA = "ONA"
    SPECIAL = "SPECIAL"
    UNKNOWN = "UNKNOWN"


class AnimeStatusEnum(Enum):
    FINISHED = "FINISHED"
    ONGOING = "ONGOING"
    UPCOMING = "UPCOMING"
    UNKNOWN = "UNKNOWN"


class AnimeData(BaseModel):
    model_config = ConfigDict(use_attribute_docstrings=True)
    sources: list[HttpUrl]
    """URLs to the pages of the metadata providers for this anime"""
    title: str
    """Main title"""
    type: AnimeTypeEnum
    """Distribution type"""
    episodes: int
    """Number of episodes, movies, or parts"""
    status: AnimeStatusEnum
    """Status of distribution"""
    animeSeason: AnimeSeasonData
    """Data on when the anime was first distributed"""
    picture: HttpUrl
    """URL of a picture which represents the anime"""
    thumbnail: HttpUrl
    """URL of a smaller version of the picture"""
    duration: AnimeDurationData | None = None
    """Duration. Normally this is per episode"""
    score: AnimeScoreData | None = None
    """Score calculated using all available scores from metadata providers.
    Original scores are rescaled if necessary"""
    synonyms: list[str] = []
    """Alternative titles and spellings under which the anime is also known.
    Duplicate free (case-sensitive). Doesn't contain the ``title``"""
    studios: list[str] = []
    """Lower case studio names. In general a duplicate free list,
    but might contain duplicates for different writings"""
    producers: list[str] = []
    """Lower case producers names. Companies only. In general a duplicate free list,
    but might contain duplicates for different writings"""
    relatedAnime: list[HttpUrl] = []
    """URLs to the metadata providers for anime that are somehow related to this anime"""
    tags: list[str] = []
    """A non-curated list of tags and genres which describe the anime.
    All entries are lower case"""


class AodLicenseData(BaseModel):
    model_config = ConfigDict(use_attribute_docstrings=True)
    name: str
    """Name of the license"""
    url: HttpUrl
    """URL to the license file"""


class AodScoreRangeData(BaseModel):
    minInclusive: float
    """Minimum value that a score can take."""
    maxInclusive: float
    """Maximum value that a score can take."""


class AnimeOfflineDatabase(BaseModel):
    license: AodLicenseData | None = Field(None)
    """Information about the license of the dataset"""
    repository: HttpUrl = Field(...)
    """URL of this github repository which is the source of the dataset"""
    lastUpdate: Annotated[date, Field(gt=date(2017, 9, 21))] = Field(...)
    """The date on which the file was updated"""
    scoreRange: AodScoreRangeData | None = Field(None)
    """Describes the upper and lower boundaries of a score"""
    data: list[AnimeData] = []
    """List of all anime"""
