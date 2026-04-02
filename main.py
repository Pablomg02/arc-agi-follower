from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime, timedelta
from typing import Sequence
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from src import KaggleAPI, KaggleCommandError, KaggleLeaderboard, TelegramBot, TelegramBotError

COMPETITION = "arc-prize-2026-arc-agi-3"
LEADERBOARD_PAGE_SIZE = 5
DEFAULT_REPORT_TIMEZONE = "Europe/Madrid"
DEFAULT_REPORT_HOURS = 24


def build_daily_message(
    leaderboard: KaggleLeaderboard,
    *,
    report_end: datetime,
    report_hours: int = DEFAULT_REPORT_HOURS,
) -> str:
    if report_hours <= 0:
        raise ValueError("hours must be greater than 0.")

    report_start = report_end - timedelta(hours=report_hours)
    recent_top_five = leaderboard.get_top_entries_since(report_start, LEADERBOARD_PAGE_SIZE)

    sections = [
        f"ARC-AGI 3 | Resumen diario | {report_end.date().isoformat()}",
        format_top_five_movement_section(recent_top_five, report_hours=report_hours),
        format_current_top_five_section(leaderboard.entries[:LEADERBOARD_PAGE_SIZE]),
    ]
    return "\n\n".join(sections)


def format_top_five_movement_section(
    entries: list[dict[str, str | int]],
    *,
    report_hours: int,
) -> str:
    if not entries:
        return f"📌 Sin cambios en el top 5 en las ultimas {report_hours} horas."

    lines = [f"📈 Movimiento en el top 5 en las ultimas {report_hours} horas:"]
    for entry in entries:
        lines.append(f'#{entry["rank"]} {entry["teamName"]} | {entry["score"]}')

    return "\n".join(lines)


def format_current_top_five_section(entries: list[dict[str, str]]) -> str:
    lines = ["🏆 Top 5 actual:"]
    for rank, entry in enumerate(entries, start=1):
        lines.append(
            f'#{rank} {entry["teamName"]} | {entry["score"]} | {entry["submissionDate"].split()[0]}'
        )

    return "\n".join(lines)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Send ARC-AGI 3 leaderboard updates to Telegram.")
    parser.add_argument(
        "--hours",
        type=int,
        default=DEFAULT_REPORT_HOURS,
        help="Look for top 5 movement within the last N hours. Default: 24.",
    )
    args = parser.parse_args(argv)

    if args.hours <= 0:
        parser.error("--hours must be greater than 0.")

    return args


def get_report_now(*, timezone_name: str) -> datetime:
    timezone = ZoneInfo(timezone_name)
    return datetime.now(timezone).replace(tzinfo=None)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    timezone_name = os.getenv("ARC_AGI_REPORT_TIMEZONE", DEFAULT_REPORT_TIMEZONE)
    competition = os.getenv("ARC_AGI_COMPETITION", COMPETITION)

    try:
        report_end = get_report_now(timezone_name=timezone_name)
        api = KaggleAPI()
        leaderboard = KaggleLeaderboard.from_api(
            api,
            competition,
            page_size=LEADERBOARD_PAGE_SIZE,
        )

        if not leaderboard.entries:
            print("No leaderboard entries were returned by Kaggle.", file=sys.stderr)
            return 1

        message = build_daily_message(
            leaderboard,
            report_end=report_end,
            report_hours=args.hours,
        )
        print(message)

        bot = TelegramBot()
        bot.send_message(message)
        print("\nTelegram message sent.")
        return 0
    except (KaggleCommandError, TelegramBotError, ValueError, ZoneInfoNotFoundError) as error:
        print(error, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
