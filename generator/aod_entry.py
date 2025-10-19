# SPDX-License-Identifier: AGPL-3.0-only AND MIT

from dataclasses import dataclass, field
from typing import Any, Optional, Set


@dataclass
class AodEntry:
    """
    Smart dataclass for AOD entries with automatic ID extraction from sources
    """

    title: str
    sources: list[str]
    anidb: Optional[int] = None
    anilist: Optional[int] = None
    animenewsnetwork: Optional[int] = None
    animeplanet: Optional[str] = None
    anisearch: Optional[int] = None
    kitsu: Optional[int] = None
    livechart: Optional[int] = None
    myanimelist: Optional[int] = None
    notify: Optional[str] = None
    simkl: Optional[int] = None

    # Track all extracted IDs for comparison
    id_set: Set[str] = field(default_factory=set, init=False)

    def __post_init__(self):
        """Extract IDs from sources and populate id_set"""
        self._extract_ids_from_sources()
        self.populate_id_set()

    def _extract_ids_from_sources(self):
        """
        Parse sources array and extract IDs.

        Note: Sources come from anime-offline-database, a trusted curated dataset.
        URL substring matching is used for ID extraction, not security validation.
        """
        for source in self.sources:
            if "anidb.net/anime/" in source:
                self.anidb = int(source.split("/")[-1])
            elif "anilist.co/anime/" in source:
                self.anilist = int(source.split("/")[-1])
            elif "anime-planet.com/anime/" in source:
                self.animeplanet = source.split("/")[-1]
            elif "anisearch.com/anime/" in source:
                self.anisearch = int(source.split("/")[-1])
            elif "kitsu.io/anime/" in source or "kitsu.app/anime/" in source:
                self.kitsu = int(source.split("/")[-1])
            elif "livechart.me/anime/" in source:
                self.livechart = int(source.split("/")[-1])
            elif "myanimelist.net/anime/" in source:
                self.myanimelist = int(source.split("/")[-1])
            elif "notify.moe/anime/" in source:
                self.notify = source.split("/")[-1]
            elif "simkl.com/anime/" in source:
                self.simkl = int(source.split("/")[-1])
            elif "animenewsnetwork.com/" in source and "id=" in source:
                self.animenewsnetwork = int(source.split("id=")[-1])

    def populate_id_set(self):
        """
        Create a set of all non-null IDs for comparison.

        This method clears and rebuilds the id_set from current ID values.
        It's called during initialization but can also be called after
        manual ID assignment to refresh the id_set.
        """
        self.id_set.clear()
        if self.anidb:
            self.id_set.add(f"anidb:{self.anidb}")
        if self.anilist:
            self.id_set.add(f"anilist:{self.anilist}")
        if self.animenewsnetwork:
            self.id_set.add(f"ann:{self.animenewsnetwork}")
        if self.animeplanet:
            self.id_set.add(f"ap:{self.animeplanet}")
        if self.anisearch:
            self.id_set.add(f"as:{self.anisearch}")
        if self.kitsu:
            self.id_set.add(f"kitsu:{self.kitsu}")
        if self.livechart:
            self.id_set.add(f"lc:{self.livechart}")
        if self.myanimelist:
            self.id_set.add(f"mal:{self.myanimelist}")
        if self.notify:
            self.id_set.add(f"notify:{self.notify}")
        if self.simkl:
            self.id_set.add(f"simkl:{self.simkl}")

    def has_overlapping_ids(self, other: "AodEntry") -> bool:
        """
        Check if two entries have overlapping IDs (indicating they're the same anime)

        :param other: Another AodEntry to compare with
        :return: True if there are overlapping IDs
        """
        return bool(self.id_set & other.id_set)

    def id_count(self) -> int:
        """Return the number of IDs this entry has"""
        return len(self.id_set)

    @classmethod
    def from_aod_dict(cls, aod_dict: dict[str, Any]) -> "AodEntry":
        """
        Create an AodEntry from AOD dictionary format

        :param aod_dict: Dictionary from anime-offline-database
        :return: AodEntry instance
        """
        return cls(title=aod_dict["title"], sources=aod_dict["sources"])

    def to_simplified_dict(self) -> dict[str, Any]:
        """
        Convert to simplified format used in the rest of the code

        :return: Dictionary with simplified structure
        """
        return {
            "title": self.title,
            "anidb": self.anidb,
            "anilist": self.anilist,
            "animenewsnetwork": self.animenewsnetwork,
            "animeplanet": self.animeplanet,
            "anisearch": self.anisearch,
            "kitsu": self.kitsu,
            "livechart": self.livechart,
            "myanimelist": self.myanimelist,
            "notify": self.notify,
            "shikimori": self.myanimelist,  # Shikimori uses same ID as MAL
            "simkl": self.simkl,
        }


def merge_aod_entries_if_compatible(
    entry1: AodEntry, entry2: AodEntry
) -> Optional[AodEntry]:
    """
    Merge two AOD entries if they represent different anime (no overlapping IDs).

    The function checks if entries have overlapping IDs:
    - If they have overlapping IDs: They are the SAME anime and should NOT be merged.
      Returns None to indicate incompatibility.
    - If they have NO overlapping IDs: They are DIFFERENT anime and CAN be merged.
      Returns a merged entry combining all IDs from both.

    This is used during AOD data parsing to handle duplicate titles that
    represent different anime (e.g., "Everyday Host" with different IDs).

    :param entry1: First AodEntry
    :param entry2: Second AodEntry
    :return: Merged AodEntry if compatible (no overlapping IDs), None otherwise
    """
    if entry1.has_overlapping_ids(entry2):
        # Entries have overlapping IDs, they're the same anime
        # Return None to indicate they should NOT be merged
        return None

    # Merge by combining all IDs
    merged = AodEntry(
        title=entry1.title, sources=list(set(entry1.sources + entry2.sources))
    )

    # Manually set IDs from both entries
    merged.anidb = entry1.anidb or entry2.anidb
    merged.anilist = entry1.anilist or entry2.anilist
    merged.animenewsnetwork = entry1.animenewsnetwork or entry2.animenewsnetwork
    merged.animeplanet = entry1.animeplanet or entry2.animeplanet
    merged.anisearch = entry1.anisearch or entry2.anisearch
    merged.kitsu = entry1.kitsu or entry2.kitsu
    merged.livechart = entry1.livechart or entry2.livechart
    merged.myanimelist = entry1.myanimelist or entry2.myanimelist
    merged.notify = entry1.notify or entry2.notify
    merged.simkl = entry1.simkl or entry2.simkl

    # Rebuild id_set with the new IDs
    merged.populate_id_set()

    return merged
