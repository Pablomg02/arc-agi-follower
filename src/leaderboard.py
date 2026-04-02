"""Helpers to inspect Kaggle leaderboard data."""

from datetime import date, datetime, time
from typing import Sequence

from .kaggle_api import KaggleAPI


class LeaderboardEntryNotFoundError(IndexError):
    """Raised when the requested leaderboard position is not available."""


class KaggleLeaderboard:
    """Query helpers built from the output of `KaggleAPI.get_leaderboard`."""

    def __init__(self, entries: Sequence[dict[str, str]]):
        self.entries = [dict(entry) for entry in entries]

    @classmethod
    def from_api(
        cls,
        kaggle_api: KaggleAPI,
        competition: str,
        *,
        page_size: int | None = None,
    ) -> "KaggleLeaderboard":
        """Build the helper from a live Kaggle leaderboard request."""
        entries = kaggle_api.get_leaderboard(competition, page_size=page_size)
        return cls(entries)

    def get_entry_at_position(self, position: int) -> dict[str, str]:
        """Return the leaderboard entry at a zero-based position."""
        if position < 0:
            raise ValueError("Position must be 0 or greater.")

        if position >= len(self.entries):
            raise LeaderboardEntryNotFoundError(
                f"No leaderboard data found at position {position}. "
                f"Only {len(self.entries)} participants were loaded."
            )

        return dict(self.entries[position])

    def get_top_entries_since(
        self,
        since: str | date | datetime,
        top_n: int,
    ) -> list[dict[str, str | int]]:
        """Return current top-N entries whose submission date is after `since`."""
        if top_n <= 0:
            raise ValueError("top_n must be greater than 0.")

        since_datetime = self._normalize_since(since)
        recent_entries: list[dict[str, str | int]] = []

        for index, entry in enumerate(self.entries[:top_n]):
            submission_datetime = self._parse_submission_datetime(entry)
            if submission_datetime > since_datetime:
                recent_entries.append(
                    {
                        "position": index,
                        "rank": index + 1,
                        **entry,
                    }
                )

        return recent_entries

    def _parse_submission_datetime(self, entry: dict[str, str]) -> datetime:
        submission_date = entry.get("submissionDate")
        if not submission_date:
            team_name = entry.get("teamName", "<unknown team>")
            raise ValueError(f"Missing submissionDate for leaderboard entry {team_name}.")

        return datetime.fromisoformat(submission_date)

    def _normalize_since(self, since: str | date | datetime) -> datetime:
        if isinstance(since, datetime):
            return since
        if isinstance(since, date):
            return datetime.combine(since, time.min)
        if isinstance(since, str):
            return datetime.fromisoformat(since)

        raise TypeError("since must be a str, date, or datetime.")
