import os
import unittest
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import patch

from src.deep_research import DEFAULT_ANTHROPIC_MODEL, ResearchAgent


class ResearchAgentTests(unittest.TestCase):
    @patch.dict(os.environ, {}, clear=True)
    @patch.object(ResearchAgent, "_get_dotenv_values", return_value={})
    @patch("src.deep_research.anthropic.Anthropic")
    @patch("src.deep_research.TavilyClient")
    def test_search_uses_tavily_with_expected_arguments(
        self,
        tavily_client_class,
        anthropic_client_class,
        _get_dotenv_values,
    ):
        tavily_client = tavily_client_class.return_value
        tavily_client.search.return_value = {"results": []}

        agent = ResearchAgent(tavily_api_key="tavily-token", anthropic_api_key="anthropic-token")

        result = agent.search(
            "  latest ARC-AGI 3 news  ",
            search_depth="advanced",
            max_results=7,
            include_answer=False,
            include_domains=["kaggle.com"],
        )

        self.assertEqual(result, {"results": []})
        tavily_client_class.assert_called_once_with(api_key="tavily-token", timeout=60)
        anthropic_client_class.assert_called_once_with(api_key="anthropic-token")
        tavily_client.search.assert_called_once_with(
            query="latest ARC-AGI 3 news",
            search_depth="advanced",
            max_results=7,
            include_answer=False,
            include_raw_content=False,
            include_domains=["kaggle.com"],
            exclude_domains=None,
        )

    @patch.dict(os.environ, {}, clear=True)
    @patch.object(ResearchAgent, "_get_dotenv_values", return_value={})
    @patch("src.deep_research.anthropic.Anthropic")
    @patch("src.deep_research.TavilyClient")
    def test_summarize_builds_prompt_and_returns_text_response(
        self,
        tavily_client_class,
        anthropic_client_class,
        _get_dotenv_values,
    ):
        anthropic_client = anthropic_client_class.return_value
        anthropic_client.messages.create.return_value = SimpleNamespace(
            content=[
                SimpleNamespace(type="text", text="Resumen final."),
                SimpleNamespace(type="tool_use"),
            ]
        )

        agent = ResearchAgent(tavily_api_key="tavily-token", anthropic_api_key="anthropic-token")
        summary = agent.summarize(
            {
                "query": "ARC-AGI 3 leaderboard",
                "answer": "There was movement in the top 5.",
                "results": [
                    {
                        "title": "ARC-AGI 3 Competition",
                        "url": "https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3",
                        "content": "A new submission changed the top 5 positions.",
                    }
                ],
            },
            target_length="120 palabras",
            additional_instructions="La fecha actual es 2026-04-02 12:00.",
        )

        self.assertEqual(summary, "Resumen final.")
        anthropic_request = anthropic_client.messages.create.call_args.kwargs
        self.assertEqual(anthropic_request["model"], DEFAULT_ANTHROPIC_MODEL)
        self.assertEqual(anthropic_request["max_tokens"], 1024)
        self.assertEqual(anthropic_request["temperature"], 0.2)
        self.assertIn("espanol", anthropic_request["messages"][0]["content"])
        self.assertIn('"120 palabras"', anthropic_request["messages"][0]["content"])
        self.assertIn(
            "La fecha actual es 2026-04-02 12:00.",
            anthropic_request["messages"][0]["content"],
        )
        self.assertIn('"query": "ARC-AGI 3 leaderboard"', anthropic_request["messages"][0]["content"])
        self.assertIn(
            '"answer": "There was movement in the top 5."',
            anthropic_request["messages"][0]["content"],
        )
        tavily_client_class.assert_called_once_with(api_key="tavily-token", timeout=60)

    @patch.dict(os.environ, {}, clear=True)
    @patch.object(ResearchAgent, "_get_dotenv_values", return_value={})
    @patch("src.deep_research.anthropic.Anthropic")
    @patch("src.deep_research.TavilyClient")
    def test_search_news_makes_reporting_window_explicit(
        self,
        tavily_client_class,
        anthropic_client_class,
        _get_dotenv_values,
    ):
        tavily_client = tavily_client_class.return_value
        tavily_client.search.return_value = {"results": []}
        agent = ResearchAgent(tavily_api_key="tavily-token", anthropic_api_key="anthropic-token")

        result = agent.search_news(
            "ARC-AGI-3 updates, latest news and best results",
            report_end=datetime(2026, 4, 2, 12, 0, 0),
            report_hours=6,
            fallback_days=3,
            chunks_per_source=3,
        )

        self.assertEqual(result, {"results": []})
        tavily_client.search.assert_called_once_with(
            query="ARC-AGI-3 updates, latest news and best results in the last 6 hours",
            search_depth="advanced",
            max_results=10,
            include_answer=False,
            include_raw_content=False,
            include_domains=None,
            exclude_domains=None,
            chunks_per_source=3,
        )
        self.assertLess(len(tavily_client.search.call_args.kwargs["query"]), 400)

    @patch.dict(os.environ, {}, clear=True)
    @patch.object(ResearchAgent, "_get_dotenv_values", return_value={})
    @patch("src.deep_research.anthropic.Anthropic")
    @patch("src.deep_research.TavilyClient")
    def test_summarize_news_mentions_priority_window(
        self,
        tavily_client_class,
        anthropic_client_class,
        _get_dotenv_values,
    ):
        anthropic_client = anthropic_client_class.return_value
        anthropic_client.messages.create.return_value = SimpleNamespace(
            content=[SimpleNamespace(type="text", text="Resumen breve.")]
        )
        agent = ResearchAgent(tavily_api_key="tavily-token", anthropic_api_key="anthropic-token")

        summary = agent.summarize_news(
            {"results": [{"title": "News", "content": "Update"}]},
            report_end=datetime(2026, 4, 2, 12, 0, 0),
            report_hours=6,
            timezone_name="Europe/Madrid",
            target_length="maximo 50 palabras",
            fallback_days=3,
        )

        self.assertEqual(summary, "Resumen breve.")
        anthropic_request = anthropic_client.messages.create.call_args.kwargs
        self.assertIn("ultimas 6 horas", anthropic_request["messages"][0]["content"])
        self.assertIn("2026-04-02 12:00", anthropic_request["messages"][0]["content"])
        self.assertIn("ultimos 3 dias", anthropic_request["messages"][0]["content"])
        self.assertIn("bullet points", anthropic_request["messages"][0]["content"])
        self.assertIn("emoji relevante", anthropic_request["messages"][0]["content"])

    @patch.dict(os.environ, {}, clear=True)
    @patch.object(ResearchAgent, "_get_dotenv_values", return_value={})
    @patch("src.deep_research.anthropic.Anthropic")
    @patch("src.deep_research.TavilyClient")
    def test_search_raises_when_tavily_is_not_configured(
        self,
        tavily_client_class,
        anthropic_client_class,
        _get_dotenv_values,
    ):
        agent = ResearchAgent(anthropic_api_key="anthropic-token")

        with self.assertRaisesRegex(ValueError, "Missing Tavily API key"):
            agent.search("arc-agi")

        tavily_client_class.assert_not_called()
        anthropic_client_class.assert_called_once_with(api_key="anthropic-token")

    @patch.dict(os.environ, {}, clear=True)
    @patch.object(ResearchAgent, "_get_dotenv_values", return_value={})
    @patch("src.deep_research.anthropic.Anthropic")
    @patch("src.deep_research.TavilyClient")
    def test_summarize_raises_when_anthropic_is_not_configured(
        self,
        tavily_client_class,
        anthropic_client_class,
        _get_dotenv_values,
    ):
        agent = ResearchAgent(tavily_api_key="tavily-token")

        with self.assertRaisesRegex(ValueError, "Missing Anthropic API key"):
            agent.summarize("contenido", target_length="breve")

        tavily_client_class.assert_called_once_with(api_key="tavily-token", timeout=60)
        anthropic_client_class.assert_not_called()


if __name__ == "__main__":
    unittest.main()
