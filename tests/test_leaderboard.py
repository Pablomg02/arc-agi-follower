import unittest
from datetime import date

from src import KaggleLeaderboard, LeaderboardEntryNotFoundError


class KaggleLeaderboardTests(unittest.TestCase):
    def setUp(self):
        self.entries = [
            {
                "teamId": "1",
                "teamName": "Alpha",
                "submissionDate": "2026-03-19 10:00:00",
                "score": "0.50",
            },
            {
                "teamId": "2",
                "teamName": "Beta",
                "submissionDate": "2026-03-21 09:30:00",
                "score": "0.49",
            },
            {
                "teamId": "3",
                "teamName": "Gamma",
                "submissionDate": "2026-03-28 08:15:00",
                "score": "0.48",
            },
            {
                "teamId": "4",
                "teamName": "Delta",
                "submissionDate": "2026-03-15 12:00:00",
                "score": "0.47",
            },
            {
                "teamId": "5",
                "teamName": "Epsilon",
                "submissionDate": "2026-03-30 18:45:00",
                "score": "0.46",
            },
        ]
        self.leaderboard = KaggleLeaderboard(self.entries)

    def test_get_entry_at_position_returns_expected_entry(self):
        entry = self.leaderboard.get_entry_at_position(1)

        self.assertEqual(entry["teamName"], "Beta")

    def test_get_entry_at_position_raises_when_position_is_missing(self):
        with self.assertRaises(LeaderboardEntryNotFoundError):
            self.leaderboard.get_entry_at_position(10)

    def test_get_top_entries_since_filters_current_top_n(self):
        entries = self.leaderboard.get_top_entries_since(date(2026, 3, 20), 3)

        self.assertEqual(
            entries,
            [
                {
                    "position": 1,
                    "rank": 2,
                    "teamId": "2",
                    "teamName": "Beta",
                    "submissionDate": "2026-03-21 09:30:00",
                    "score": "0.49",
                },
                {
                    "position": 2,
                    "rank": 3,
                    "teamId": "3",
                    "teamName": "Gamma",
                    "submissionDate": "2026-03-28 08:15:00",
                    "score": "0.48",
                },
            ],
        )


if __name__ == "__main__":
    unittest.main()
