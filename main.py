from __future__ import annotations

import os
import sys
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from src.leaderboard import KaggleLeaderboard

COMPETITION = "arc-prize-2026-arc-agi-3"
LEADERBOARD_PAGE_SIZE = 5
DEFAULT_REPORT_TIMEZONE = "Europe/Madrid"
REPORT_WINDOW_HOURS = 12


def build_daily_message(
    leaderboard: KaggleLeaderboard,
    *,
    report_end: datetime,
) -> str:
    report_start = report_end - timedelta(hours=REPORT_WINDOW_HOURS)
    recent_top_five = leaderboard.get_top_entries_since(report_start, LEADERBOARD_PAGE_SIZE)

    sections = [
        f"ARC-AGI 3 | Resumen diario | {report_end.date().isoformat()}",
        format_top_five_movement_section(recent_top_five),
        format_current_top_five_section(leaderboard.entries[:LEADERBOARD_PAGE_SIZE]),
    ]
    return "\n\n".join(sections)


def format_top_five_movement_section(entries: list[dict[str, str | int]]) -> str:
    if not entries:
        return f"Sin cambios en el top 5 en las ultimas {REPORT_WINDOW_HOURS} horas."

    lines = [f"Cambios en el top 5 en las ultimas {REPORT_WINDOW_HOURS} horas:"]
    for entry in entries:
        lines.append(f'#{entry["rank"]} {entry["teamName"]} | {entry["score"]}')

    return "\n".join(lines)


def format_current_top_five_section(entries: list[dict[str, str]]) -> str:
    lines = ["Top 5 actual:"]
    for rank, entry in enumerate(entries, start=1):
        lines.append(
            f'#{rank} {entry["teamName"]} | {entry["score"]} | {_format_submission_date(entry)}'
        )

    return "\n".join(lines)


def _format_submission_date(entry: dict[str, str]) -> str:
    submission_date = entry.get("submissionDate")
    if not submission_date:
        return "fecha desconocida"

    return submission_date.split()[0]


def get_report_now(*, timezone_name: str) -> datetime:
    try:
        timezone_info = ZoneInfo(timezone_name)
        return datetime.now(timezone_info).replace(tzinfo=None)
    except ZoneInfoNotFoundError:
        if timezone_name != DEFAULT_REPORT_TIMEZONE:
            raise

        # Windows can lack the IANA tz database, so keep Europe/Madrid working
        # without requiring tzdata for local runs.
        utc_now = datetime.now(timezone.utc)
        return _get_europe_madrid_now_from_utc(utc_now)


def _get_europe_madrid_now_from_utc(utc_now: datetime) -> datetime:
    normalized_utc = utc_now.astimezone(timezone.utc)
    offset_hours = 2 if _is_europe_madrid_dst(normalized_utc) else 1
    return (normalized_utc + timedelta(hours=offset_hours)).replace(tzinfo=None)


def _is_europe_madrid_dst(utc_now: datetime) -> bool:
    year = utc_now.year
    dst_start_day = _last_sunday(year, 3)
    dst_end_day = _last_sunday(year, 10)
    dst_start = datetime(year, 3, dst_start_day, 1, 0, tzinfo=timezone.utc)
    dst_end = datetime(year, 10, dst_end_day, 1, 0, tzinfo=timezone.utc)
    return dst_start <= utc_now < dst_end


def _last_sunday(year: int, month: int) -> int:
    if month == 12:
        next_month = datetime(year + 1, 1, 1)
    else:
        next_month = datetime(year, month + 1, 1)

    last_day = next_month - timedelta(days=1)
    days_since_sunday = (last_day.weekday() + 1) % 7
    return last_day.day - days_since_sunday


def main() -> int:
    from src.kaggle_api import KaggleAPI, KaggleCommandError
    from src.telegram_bot import TelegramBot, TelegramBotError

    timezone_name = os.getenv("ARC_AGI_REPORT_TIMEZONE", DEFAULT_REPORT_TIMEZONE)
    competition = os.getenv("ARC_AGI_COMPETITION", COMPETITION)

    try:
        report_end = get_report_now(timezone_name=timezone_name)
        api = KaggleAPI()
        leaderboard = KaggleLeaderboard.from_api(api, competition, page_size=LEADERBOARD_PAGE_SIZE)

        if not leaderboard.entries:
            print("No leaderboard entries were returned by Kaggle.", file=sys.stderr)
            return 1

        message = build_daily_message(leaderboard, report_end=report_end)
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
