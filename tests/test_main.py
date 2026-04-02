import unittest
from datetime import datetime
from unittest.mock import Mock

from main import build_daily_message, build_recent_news_summary, parse_args
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

    def test_build_daily_message_includes_news_summary_when_available(self):
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
            news_summary="Sin grandes cambios fuera del leaderboard.",
        )

        self.assertIn(
            "📰 Noticias recientes (prioridad: ultimas 24 horas):\n"
            "Sin grandes cambios fuera del leaderboard.",
            message,
        )
        self.assertLess(
            message.index("🏆 Top 5 actual:"),
            message.index("📰 Noticias recientes (prioridad: ultimas 24 horas):"),
        )

    def test_build_recent_news_summary_prioritizes_last_hours(self):
        research_agent = Mock()
        research_agent.search.return_value = {
            "results": [
                {
                    "title": "ARC-AGI 3: nueva submission entra en el top 5",
                    "url": "https://example.com/recent",
                    "content": "Una nueva submission de ARC-AGI 3 cambió el top 5.",
                    "published_date": "2026-04-02T10:30:00+02:00",
                },
                {
                    "title": "ARC Prize 2026 resumen de hace dos dias",
                    "url": "https://example.com/older",
                    "content": "Analisis general del estado de la competicion ARC-AGI 3.",
                    "published_date": "2026-03-31T09:00:00+02:00",
                },
            ]
        }
        research_agent.summarize_news.return_value = "Nueva submission destacada en el top 5."

        summary = build_recent_news_summary(
            report_end=datetime(2026, 4, 2, 12, 0, 0),
            report_hours=6,
            timezone_name="Europe/Madrid",
            competition="arc-prize-2026-arc-agi-3",
            research_agent=research_agent,
        )

        self.assertEqual(summary, "Nueva submission destacada en el top 5.")
        search_kwargs = research_agent.search.call_args.kwargs
        self.assertEqual(search_kwargs["search_depth"], "advanced")
        self.assertEqual(search_kwargs["max_results"], 10)
        self.assertTrue(search_kwargs["include_raw_content"])
        self.assertEqual(
            research_agent.search.call_args.args[0],
            '"arc-prize-2026-arc-agi-3" OR "ARC-AGI 3" OR "ARC Prize 2026" '
            "Kaggle latest updates news results in the last 6 hours",
        )

        summarize_kwargs = research_agent.summarize_news.call_args.kwargs
        summarized_response = research_agent.summarize_news.call_args.args[0]
        self.assertEqual(len(summarized_response["results"]), 2)
        self.assertEqual(
            [result["url"] for result in summarized_response["results"]],
            ["https://example.com/recent", "https://example.com/older"],
        )
        self.assertEqual(summarize_kwargs["report_hours"], 6)
        self.assertEqual(summarize_kwargs["timezone_name"], "Europe/Madrid")
        self.assertEqual(summarize_kwargs["fallback_days"], 3)

    def test_build_recent_news_summary_falls_back_to_last_days(self):
        research_agent = Mock()
        research_agent.search.return_value = {
            "results": [
                {
                    "title": "ARC-AGI 3 analisis del fin de semana",
                    "url": "https://example.com/weekend",
                    "content": "Hubo varios cambios graduales en la competicion ARC-AGI 3.",
                    "published_date": "2026-03-31T09:00:00+02:00",
                }
            ]
        }
        research_agent.summarize_news.return_value = "Sin noticias claras en 6 horas; en los ultimos dias hubo cambios graduales."

        summary = build_recent_news_summary(
            report_end=datetime(2026, 4, 2, 12, 0, 0),
            report_hours=6,
            timezone_name="Europe/Madrid",
            competition="arc-prize-2026-arc-agi-3",
            research_agent=research_agent,
        )

        self.assertEqual(
            summary,
            "Sin noticias claras en 6 horas; en los ultimos dias hubo cambios graduales.",
        )
        summarize_kwargs = research_agent.summarize_news.call_args.kwargs
        summarized_response = research_agent.summarize_news.call_args.args[0]
        self.assertEqual(len(summarized_response["results"]), 1)
        self.assertEqual(summarize_kwargs["fallback_days"], 3)

    def test_build_recent_news_summary_sends_unrelated_results_to_claude_without_filtering(self):
        research_agent = Mock()
        research_agent.search.return_value = {
            "results": [
                {
                    "title": "General ARC benchmark update",
                    "url": "https://example.com/general-arc",
                    "content": "This talks about ARC benchmarks in general only.",
                    "published_date": "2026-04-02T10:30:00+02:00",
                }
            ]
        }
        research_agent.summarize_news.return_value = "Claude decide que no hay noticias relevantes."

        summary = build_recent_news_summary(
            report_end=datetime(2026, 4, 2, 12, 0, 0),
            report_hours=6,
            timezone_name="Europe/Madrid",
            competition="arc-prize-2026-arc-agi-3",
            research_agent=research_agent,
        )

        self.assertEqual(summary, "Claude decide que no hay noticias relevantes.")
        summarized_response = research_agent.summarize_news.call_args.args[0]
        self.assertEqual(len(summarized_response["results"]), 1)
        self.assertEqual(
            summarized_response["results"][0]["url"],
            "https://example.com/general-arc",
        )

    def test_build_recent_news_summary_sends_undated_matches_to_summary(self):
        research_agent = Mock()
        research_agent.search.return_value = {
            "results": [
                {
                    "title": "ARC-AGI 3 mention without date",
                    "url": "https://example.com/arc-agi-3",
                    "content": "ARC-AGI 3 leaderboard discussion.",
                }
            ]
        }
        research_agent.summarize_news.return_value = "Hay conversacion reciente, pero sin fecha clara."

        summary = build_recent_news_summary(
            report_end=datetime(2026, 4, 2, 12, 0, 0),
            report_hours=6,
            timezone_name="Europe/Madrid",
            competition="arc-prize-2026-arc-agi-3",
            research_agent=research_agent,
        )

        self.assertEqual(summary, "Hay conversacion reciente, pero sin fecha clara.")
        summarized_response = research_agent.summarize_news.call_args.args[0]
        self.assertEqual(len(summarized_response["results"]), 1)
        self.assertEqual(
            summarized_response["results"][0]["url"],
            "https://example.com/arc-agi-3",
        )

    def test_parse_args_defaults_to_24_hours(self):
        args = parse_args([])

        self.assertEqual(args.hours, 24)

    def test_parse_args_accepts_custom_hours(self):
        args = parse_args(["--hours", "6"])

        self.assertEqual(args.hours, 6)


if __name__ == "__main__":
    unittest.main()
