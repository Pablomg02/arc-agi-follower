import unittest
from datetime import datetime

from main import build_daily_message, parse_args
from src import KaggleLeaderboard


class DailyMessageTests(unittest.TestCase):
    def test_build_daily_message_reports_top_five_movement_and_current_top_five(self):
        leaderboard = KaggleLeaderboard(
            [
                {
                    "teamId": "1",
                    "teamName": "Alpha",
                    "submissionDate": "2026-04-01 08:00:00",
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
                            "📈 Movimiento en el top 5 en las ultimas 24 horas:",
                            "#1 Alpha | 58.10",
                            "#3 Gamma | 57.50",
                            "#4 Delta | 57.10",
                        ]
                    ),
                    "\n".join(
                        [
                            "🏆 Top 5 actual:",
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
                    "submissionDate": "2026-04-01 09:00:00",
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
                            "📈 Movimiento en el top 5 en las ultimas 24 horas:",
                            "#5 Epsilon | 56.80",
                        ]
                    ),
                    "\n".join(
                        [
                            "🏆 Top 5 actual:",
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
                    "📌 Sin cambios en el top 5 en las ultimas 24 horas.",
                    "\n".join(
                        [
                            "🏆 Top 5 actual:",
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

    def test_build_daily_message_uses_custom_hour_window(self):
        leaderboard = KaggleLeaderboard(
            [
                {
                    "teamId": "1",
                    "teamName": "Alpha",
                    "submissionDate": "2026-04-01 19:30:00",
                    "score": "58.10",
                },
                {
                    "teamId": "2",
                    "teamName": "Beta",
                    "submissionDate": "2026-04-01 17:45:00",
                    "score": "57.90",
                },
                {
                    "teamId": "3",
                    "teamName": "Gamma",
                    "submissionDate": "2026-04-01 16:00:00",
                    "score": "57.50",
                },
                {
                    "teamId": "4",
                    "teamName": "Delta",
                    "submissionDate": "2026-04-01 21:15:00",
                    "score": "57.10",
                },
                {
                    "teamId": "5",
                    "teamName": "Epsilon",
                    "submissionDate": "2026-04-01 10:00:00",
                    "score": "56.80",
                },
            ]
        )

        message = build_daily_message(
            leaderboard,
            report_end=datetime(2026, 4, 2, 0, 0, 0),
            report_hours=6,
        )

        self.assertEqual(
            message,
            "\n\n".join(
                [
                    "ARC-AGI 3 | Resumen diario | 2026-04-02",
                    "\n".join(
                        [
                            "📈 Movimiento en el top 5 en las ultimas 6 horas:",
                            "#1 Alpha | 58.10",
                            "#4 Delta | 57.10",
                        ]
                    ),
                    "\n".join(
                        [
                            "🏆 Top 5 actual:",
                            "#1 Alpha | 58.10 | 2026-04-01",
                            "#2 Beta | 57.90 | 2026-04-01",
                            "#3 Gamma | 57.50 | 2026-04-01",
                            "#4 Delta | 57.10 | 2026-04-01",
                            "#5 Epsilon | 56.80 | 2026-04-01",
                        ]
                    ),
                ]
            ),
        )

    def test_parse_args_defaults_to_24_hours(self):
        args = parse_args([])

        self.assertEqual(args.hours, 24)

    def test_parse_args_accepts_custom_hours(self):
        args = parse_args(["--hours", "6"])

        self.assertEqual(args.hours, 6)


if __name__ == "__main__":
    unittest.main()
