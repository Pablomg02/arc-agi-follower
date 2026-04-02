from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime

from main import (
    COMPETITION,
    DEFAULT_NEWS_FALLBACK_DAYS,
    DEFAULT_REPORT_TIMEZONE,
    NEWS_MAX_RESULTS,
    get_report_now,
)
from src import ResearchAgent, ResearchAgentError


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Debug the ARC-AGI news search -> filter -> Claude summary flow."
    )
    parser.add_argument("--hours", type=int, default=24, help="Priority window in hours.")
    parser.add_argument(
        "--timezone",
        default=DEFAULT_REPORT_TIMEZONE,
        help=f"Timezone used for report context. Default: {DEFAULT_REPORT_TIMEZONE}.",
    )
    parser.add_argument(
        "--query",
        default=None,
        help="Optional Tavily query override.",
    )
    parser.add_argument(
        "--report-end",
        default=None,
        help="Optional naive datetime in ISO format, e.g. 2026-04-02T09:00:00.",
    )
    parser.add_argument(
        "--max-results",
        type=int,
        default=NEWS_MAX_RESULTS,
        help=f"Max Tavily results. Default: {NEWS_MAX_RESULTS}.",
    )
    parser.add_argument(
        "--skip-claude",
        action="store_true",
        help="Stop after printing the Anthropic request payload.",
    )
    return parser.parse_args()


def dump(label: str, payload: object) -> None:
    print(f"\n=== {label} ===")
    print(json.dumps(payload, ensure_ascii=False, indent=2, default=str))


def build_news_summary_request(
    agent: ResearchAgent,
    response_to_summarize: object,
    *,
    report_end: datetime,
    report_hours: int,
    timezone_name: str,
    fallback_days: int,
) -> dict[str, object]:
    additional_instructions = (
        f"La fecha y hora actual es {report_end.isoformat(sep=' ', timespec='minutes')} "
        f"en la zona {timezone_name}. Prioriza noticias de las ultimas {report_hours} horas. "
        f"Si no hay nada claramente dentro de ese rango, dilo de forma breve y usa como "
        f"contexto secundario lo mas importante de los ultimos {fallback_days} dias. "
        "Trabaja directamente con el contenido recibido; no asumas que todo resultado aplica "
        "al rango prioritario si la fecha no es clara."
    )
    serialized_response = agent._serialize_response(response_to_summarize)
    return agent._build_summary_request(
        serialized_response,
        target_length="maximo 50 palabras, salvo que haya una noticia realmente clave",
        language="espanol",
        additional_instructions=additional_instructions,
    )


def main() -> int:
    args = parse_args()
    if args.hours <= 0:
        raise ValueError("--hours must be greater than 0.")
    if args.max_results <= 0:
        raise ValueError("--max-results must be greater than 0.")

    report_end = (
        datetime.fromisoformat(args.report_end)
        if args.report_end
        else get_report_now(timezone_name=args.timezone)
    )
    fallback_days = max(DEFAULT_NEWS_FALLBACK_DAYS, (args.hours + 23) // 24)
    agent = ResearchAgent()
    search_query = args.query or (
        f'"{COMPETITION}" OR "ARC-AGI 3" OR "ARC Prize 2026" '
        f'Kaggle latest updates news results in the last {args.hours} hours'
    )

    print(f"Report end: {report_end.isoformat(sep=' ', timespec='seconds')}")
    print(f"Timezone: {args.timezone}")
    print(f"Hours window: {args.hours}")
    print(f"Fallback days: {fallback_days}")
    print(f"Search query: {search_query}")

    try:
        search_response = agent.search(
            search_query,
            search_depth="advanced",
            max_results=args.max_results,
            include_raw_content=True,
            chunks_per_source=3,
        )
        dump("Tavily raw search response", search_response)

        results = search_response.get("results")
        if not isinstance(results, list) or not results:
            print("\nNo Tavily results returned.")
            return 0

        dump("Payload passed to summarize_news", search_response)

        anthropic_request = build_news_summary_request(
            agent,
            search_response,
            report_end=report_end,
            report_hours=args.hours,
            timezone_name=args.timezone,
            fallback_days=fallback_days,
        )
        dump("Anthropic request payload", anthropic_request)

        if args.skip_claude:
            return 0

        summary = agent.summarize_news(
            search_response,
            report_end=report_end,
            report_hours=args.hours,
            timezone_name=args.timezone,
            target_length="maximo 50 palabras, salvo que haya una noticia realmente clave",
            fallback_days=fallback_days,
        )
        print("\n=== Claude summary ===")
        print(summary)
        return 0
    except (ResearchAgentError, ValueError) as exc:
        print(f"\nError: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
