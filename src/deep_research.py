"""Research helpers backed by Tavily search and Anthropic summaries."""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

import anthropic
from dotenv import dotenv_values
from tavily import TavilyClient, TavilyError
from tavily import TimeoutError as TavilyTimeoutError

DEFAULT_ANTHROPIC_MODEL = "claude-haiku-4-5-20251001"


class ResearchAgentError(RuntimeError):
    """Raised when an external research provider request fails."""


class ResearchAgent:
    """Simple interface for Tavily search and Anthropic summarization.

    Config priority:
    1. Explicit constructor arguments
    2. `TAVILY_API_KEY` / `ANTHROPIC_API_KEY` from the system environment
    3. `TAVILY_API_KEY` / `ANTHROPIC_API_KEY` from the repo `.env` file
    """

    def __init__(
        self,
        tavily_api_key: str | None = None,
        anthropic_api_key: str | None = None,
        *,
        anthropic_model: str | None = None,
        tavily_timeout: int = 60,
        summary_max_tokens: int = 1024,
    ):
        env_values = self._get_dotenv_values()
        self.tavily_api_key = (
            tavily_api_key or os.getenv("TAVILY_API_KEY") or env_values.get("TAVILY_API_KEY")
        )
        self.anthropic_api_key = (
            anthropic_api_key
            or os.getenv("ANTHROPIC_API_KEY")
            or env_values.get("ANTHROPIC_API_KEY")
        )
        self.anthropic_model = (
            anthropic_model
            or DEFAULT_ANTHROPIC_MODEL
        )
        self.summary_max_tokens = summary_max_tokens

        self.search_client = (
            TavilyClient(api_key=self.tavily_api_key, timeout=tavily_timeout)
            if self.tavily_api_key
            else None
        )
        self.summary_client = (
            anthropic.Anthropic(api_key=self.anthropic_api_key) if self.anthropic_api_key else None
        )

    def is_configured(self) -> bool:
        """Return True when both the search and summary clients are configured."""
        return self.is_search_configured() and self.is_summary_configured()

    def is_search_configured(self) -> bool:
        """Return True when the Tavily API key is available."""
        return bool(self.search_client)

    def is_summary_configured(self) -> bool:
        """Return True when the Anthropic API key is available."""
        return bool(self.summary_client)

    def _get_dotenv_values(self) -> dict[str, str]:
        """Read research settings from the repo `.env` file."""
        env_file = Path(__file__).resolve().parent.parent / ".env"
        if not env_file.exists():
            return {}

        values = dotenv_values(env_file)
        return {key: value for key, value in values.items() if value}

    def _require_search_client(self) -> TavilyClient:
        """Return the configured Tavily client or raise a helpful error."""
        if not self.search_client:
            raise ValueError(
                "Missing Tavily API key. Set TAVILY_API_KEY in your environment or .env file."
            )

        return self.search_client

    def _require_summary_client(self) -> anthropic.Anthropic:
        """Return the configured Anthropic client or raise a helpful error."""
        if not self.summary_client:
            raise ValueError(
                "Missing Anthropic API key. Set ANTHROPIC_API_KEY in your environment or .env file."
            )

        return self.summary_client

    def search(
        self,
        query: str,
        *,
        search_depth: str = "basic",
        max_results: int = 5,
        include_answer: bool = False,
        include_raw_content: bool = False,
        include_domains: list[str] | None = None,
        exclude_domains: list[str] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Run a Tavily search and return the raw response."""
        normalized_query = query.strip()
        if not normalized_query:
            raise ValueError("Search query cannot be empty.")

        client = self._require_search_client()

        try:
            return client.search(
                query=normalized_query,
                search_depth=search_depth,
                max_results=max_results,
                include_answer=include_answer,
                include_raw_content=include_raw_content,
                include_domains=include_domains,
                exclude_domains=exclude_domains,
                **kwargs,
            )
        except (TavilyError, TavilyTimeoutError) as exc:
            raise ResearchAgentError(str(exc)) from exc

    def search_news(
        self,
        query: str,
        *,
        report_end: datetime,
        report_hours: int,
        fallback_days: int,
        max_results: int = 10,
        search_depth: str = "advanced",
        include_raw_content: bool = False,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Search news with a simple timeframe-aware query."""
        if report_hours <= 0:
            raise ValueError("report_hours must be greater than 0.")
        if fallback_days <= 0:
            raise ValueError("fallback_days must be greater than 0.")

        normalized_query = self._build_timeframe_aware_news_query(
            query,
            report_hours=report_hours,
        )
        return self.search(
            normalized_query,
            search_depth=search_depth,
            max_results=max_results,
            include_answer=False,
            include_raw_content=include_raw_content,
            **kwargs,
        )

    def summarize(
        self,
        response: Any,
        target_length: str,
        language: str = "espanol",
        additional_instructions: str | None = None,
    ) -> str:
        """Summarize a search response in the requested language and length."""
        normalized_target_length = target_length.strip()
        if not normalized_target_length:
            raise ValueError("Summary target length cannot be empty.")

        normalized_language = language.strip() or "espanol"
        serialized_response = self._serialize_response(response)
        client = self._require_summary_client()
        request_payload = self._build_summary_request(
            serialized_response,
            target_length=normalized_target_length,
            language=normalized_language,
            additional_instructions=additional_instructions,
        )

        try:
            message = client.messages.create(
                model=request_payload["model"],
                max_tokens=request_payload["max_tokens"],
                temperature=request_payload["temperature"],
                system=request_payload["system"],
                messages=request_payload["messages"],
            )
        except anthropic.AnthropicError as exc:
            raise ResearchAgentError(str(exc)) from exc

        summary = self._extract_text_from_message(message)
        if not summary:
            raise ResearchAgentError("Anthropic returned an empty summary.")

        return summary

    def summarize_news(
        self,
        response: Any,
        *,
        report_end: datetime,
        report_hours: int,
        timezone_name: str,
        target_length: str,
        fallback_days: int,
        language: str = "espanol",
    ) -> str:
        """Summarize news while making the reporting window explicit to Anthropic."""
        if report_hours <= 0:
            raise ValueError("report_hours must be greater than 0.")
        if fallback_days <= 0:
            raise ValueError("fallback_days must be greater than 0.")

        additional_instructions = (
            f"La fecha y hora actual es {report_end.isoformat(sep=' ', timespec='minutes')} "
            f"en la zona {timezone_name}. Prioriza noticias de las ultimas {report_hours} horas. "
            f"Si no hay nada claramente dentro de ese rango, dilo de forma breve y usa como "
            f"contexto secundario lo mas importante de los ultimos {fallback_days} dias. "
            "Trabaja directamente con el contenido recibido; no asumas que todo resultado aplica "
            "al rango prioritario si la fecha no es clara. Devuelve el resumen en bullet points "
            "y empieza cada bullet con un emoji relevante. No escribas parrafos ni introducciones "
            "fuera de la lista."
        )

        return self.summarize(
            response,
            target_length=target_length,
            language=language,
            additional_instructions=additional_instructions,
        )

    def _build_summary_request(
        self,
        serialized_response: str,
        *,
        target_length: str,
        language: str,
        additional_instructions: str | None = None,
    ) -> dict[str, Any]:
        normalized_additional_instructions = (
            additional_instructions.strip() if additional_instructions else ""
        )

        prompt_parts = [
            f"Resume el siguiente contenido en {language} con una "
            f'longitud objetivo de "{target_length}".',
        ]
        if normalized_additional_instructions:
            prompt_parts.append(f"Instrucciones adicionales:\n{normalized_additional_instructions}")

        prompt_parts.extend(
            [
                "Prioriza ideas principales, datos concretos y limitaciones "
                "relevantes. Si faltan datos o hay ambiguedad, indicalo "
                "claramente.",
                f"Contenido a resumir:\n{serialized_response}",
            ]
        )

        return {
            "model": self.anthropic_model,
            "max_tokens": self.summary_max_tokens,
            "temperature": 0.2,
            "system": (
                "You are a careful research assistant. Summarize the provided material "
                "faithfully, avoid inventing facts, and make uncertainty explicit."
            ),
            "messages": [
                {
                    "role": "user",
                    "content": "\n\n".join(prompt_parts),
                }
            ],
        }

    def _serialize_response(self, response: Any) -> str:
        """Convert the incoming response into a plain serialized payload."""
        if isinstance(response, str):
            text = response.strip()
            if not text:
                raise ValueError("Response to summarize cannot be empty.")

            return text

        serialized = json.dumps(response, ensure_ascii=False, indent=2, default=str).strip()
        if not serialized or serialized == "null":
            raise ValueError("Response to summarize cannot be empty.")

        return serialized

    def _extract_text_from_message(self, message: Any) -> str:
        """Extract plain text blocks from an Anthropic message response."""
        parts = []
        for block in getattr(message, "content", []):
            text = getattr(block, "text", None)
            if isinstance(text, str) and text.strip():
                parts.append(text.strip())

        return "\n\n".join(parts).strip()

    def _build_timeframe_aware_news_query(
        self,
        query: str,
        *,
        report_hours: int,
    ) -> str:
        """Build a short news query aligned with the reporting window."""
        normalized_query = query.strip()
        if not normalized_query:
            raise ValueError("Search query cannot be empty.")
        if report_hours <= 0:
            raise ValueError("report_hours must be greater than 0.")

        return f"{normalized_query} in the last {report_hours} hours"
