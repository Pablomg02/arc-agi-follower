import unittest
from datetime import datetime, timezone

from main import REPORT_WINDOW_HOURS, _get_europe_madrid_now_from_utc, build_daily_message
from src.leaderboard import KaggleLeaderboard


class DailyMessageTests(unittest.TestCase):
    def test_build_daily_message_reports_top_five_movement_and_current_top_five(self):
        leaderboard = KaggleLeaderboard(
            [
                {
                    "teamId": "1",
                    "teamName": "Alpha",
                    "submissionDate": "2026-04-01 18:30:00",
                    "score": "58.10",
                },
                {
                    "teamId": "2",
                    "teamName": "Beta",
                    "submissionDate": "2026-03-29 12:00:00",
                    "score": "57.90",
                },
                {
                    "teamId": "3",
                    "teamName": "Gamma",
                    "submissionDate": "2026-04-01 15:30:00",
                    "score": "57.50",
                },
                {
                    "teamId": "4",
                    "teamName": "Delta",
                    "submissionDate": "2026-04-01 20:45:00",
                    "score": "57.10",
                },
                {
                    "teamId": "5",
                    "teamName": "Epsilon",
                    "submissionDate": "2026-03-28 09:00:00",
                    "score": "56.80",
                },
            ]
        )

        message = build_daily_message(
            leaderboard,
            report_end=datetime(2026, 4, 2, 0, 0, 0),
        )

        self.assertEqual(
            message,
            "\n\n".join(
                [
                    "ARC-AGI 3 | Resumen diario | 2026-04-02",
                    "\n".join(
                        [
                            "Cambios en el top 5 en las ultimas 12 horas:",
                            "#1 Alpha | 58.10",
                            "#3 Gamma | 57.50",
                            "#4 Delta | 57.10",
                        ]
                    ),
                    "\n".join(
                        [
                            "Top 5 actual:",
                            "#1 Alpha | 58.10 | 2026-04-01",
                            "#2 Beta | 57.90 | 2026-03-29",
                            "#3 Gamma | 57.50 | 2026-04-01",
                            "#4 Delta | 57.10 | 2026-04-01",
                            "#5 Epsilon | 56.80 | 2026-03-28",
                        ]
                    ),
                ]
            ),
        )

    def test_build_daily_message_reports_single_top_five_change_and_current_top_five(self):
        leaderboard = KaggleLeaderboard(
            [
                {
                    "teamId": "1",
                    "teamName": "Alpha",
                    "submissionDate": "2026-03-29 08:00:00",
                    "score": "58.10",
                },
                {
                    "teamId": "2",
                    "teamName": "Beta",
                    "submissionDate": "2026-03-28 12:00:00",
                    "score": "57.90",
                },
                {
                    "teamId": "3",
                    "teamName": "Gamma",
                    "submissionDate": "2026-03-27 15:30:00",
                    "score": "57.50",
                },
                {
                    "teamId": "4",
                    "teamName": "Delta",
                    "submissionDate": "2026-03-26 20:45:00",
                    "score": "57.10",
                },
                {
                    "teamId": "5",
                    "teamName": "Epsilon",
                    "submissionDate": "2026-04-01 13:00:00",
                    "score": "56.80",
                },
            ]
        )

        message = build_daily_message(
            leaderboard,
            report_end=datetime(2026, 4, 2, 0, 0, 0),
        )

        self.assertEqual(
            message,
            "\n\n".join(
                [
                    "ARC-AGI 3 | Resumen diario | 2026-04-02",
                    "\n".join(
                        [
                            "Cambios en el top 5 en las ultimas 12 horas:",
                            "#5 Epsilon | 56.80",
                        ]
                    ),
                    "\n".join(
                        [
                            "Top 5 actual:",
                            "#1 Alpha | 58.10 | 2026-03-29",
                            "#2 Beta | 57.90 | 2026-03-28",
                            "#3 Gamma | 57.50 | 2026-03-27",
                            "#4 Delta | 57.10 | 2026-03-26",
                            "#5 Epsilon | 56.80 | 2026-04-01",
                        ]
                    ),
                ]
            ),
        )

    def test_build_daily_message_reports_no_top_five_changes_and_current_top_five(self):
        leaderboard = KaggleLeaderboard(
            [
                {
                    "teamId": "1",
                    "teamName": "Alpha",
                    "submissionDate": "2026-03-29 08:00:00",
                    "score": "58.10",
                },
                {
                    "teamId": "2",
                    "teamName": "Beta",
                    "submissionDate": "2026-03-28 12:00:00",
                    "score": "57.90",
                },
                {
                    "teamId": "3",
                    "teamName": "Gamma",
                    "submissionDate": "2026-03-27 15:30:00",
                    "score": "57.50",
                },
                {
                    "teamId": "4",
                    "teamName": "Delta",
                    "submissionDate": "2026-03-26 20:45:00",
                    "score": "57.10",
                },
                {
                    "teamId": "5",
                    "teamName": "Epsilon",
                    "submissionDate": "2026-03-25 09:00:00",
                    "score": "56.80",
                },
            ]
        )

        message = build_daily_message(
            leaderboard,
            report_end=datetime(2026, 4, 2, 0, 0, 0),
        )

        self.assertEqual(
            message,
            "\n\n".join(
                [
                    "ARC-AGI 3 | Resumen diario | 2026-04-02",
                    "Sin cambios en el top 5 en las ultimas 12 horas.",
                    "\n".join(
                        [
                            "Top 5 actual:",
                            "#1 Alpha | 58.10 | 2026-03-29",
                            "#2 Beta | 57.90 | 2026-03-28",
                            "#3 Gamma | 57.50 | 2026-03-27",
                            "#4 Delta | 57.10 | 2026-03-26",
                            "#5 Epsilon | 56.80 | 2026-03-25",
                        ]
                    ),
                ]
            ),
        )

    def test_report_window_is_fixed_to_12_hours(self):
        self.assertEqual(REPORT_WINDOW_HOURS, 12)

    def test_europe_madrid_fallback_uses_cet_in_winter(self):
        madrid_now = _get_europe_madrid_now_from_utc(
            datetime(2026, 1, 15, 12, 0, tzinfo=timezone.utc)
        )

        self.assertEqual(madrid_now, datetime(2026, 1, 15, 13, 0))

    def test_europe_madrid_fallback_uses_cest_in_summer(self):
        madrid_now = _get_europe_madrid_now_from_utc(
            datetime(2026, 7, 15, 12, 0, tzinfo=timezone.utc)
        )

        self.assertEqual(madrid_now, datetime(2026, 7, 15, 14, 0))


if __name__ == "__main__":
    unittest.main()
