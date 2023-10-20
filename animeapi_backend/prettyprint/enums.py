from enum import Enum

class Platform(Enum):
    """Platform color to be used for pretty printing."""
    ALLCINEMA = 0xEC0A0A
    ANIDB = 0x2A2F46
    ANILIST = 0x2F80ED
    ANIMEPLANET = 0xE75448
    ANISEARCH = 0xFDA37C
    ANIMENEWSNETWORK = 0x2D50A7
    ANNICT = 0xF65B73
    FRIBB = 0x212121
    IMDB = 0xF5C518
    KAIZE = 0x692FC2
    KITSU = 0xF85235
    LIVECHART = 0x67A427
    MYANIMELIST = 0x2F51A3
    NAUTILJON = 0x3C5891
    NOTIFY = 0xDEA99E
    OTAKOTAKU = 0xBE2222
    SHIKIMORI = 0x2E2E2E
    SHOBOI = 0xE3F0FD
    SILVERYASHA = 0x0172BB
    SIMKL = 0x0B0F10
    SYOBOI = 0xE3F0FD
    TMDB = 0x09B4E2
    TVDB = 0x6CD491
    TVTIME = 0xFBD737
    SYSTEM = 0x000000
    ARM = 0x222222
    ANITRAKT = 0xED1C24

class Status(Enum):
    """
    Status color to be used for pretty printing.

    Supported status:
        - Pass
        - Fail
        - Err
        - Warn
        - Info
        - Debug
        - Notice
        - Log
        - Ready
        - Assert
    """
    # Use Hex color codes instead of ANSI color codes
    PASS = 0x2ECC71
    FAIL = 0xE74C3C
    ERR = 0xFF0000
    WARN = 0xFFA500
    INFO = 0x3498DB
    DEBUG = 0xBFBFBF
    LOG = 0x1A1A1A
    READY = 0x228B22
    NOTICE = 0x1E90FF
    ASSERT = 0x808080
    BUILD = 0x4B0082
