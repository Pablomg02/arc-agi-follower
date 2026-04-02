"""Minimal Telegram bot client built on top of pyTelegramBotAPI."""

import os
from pathlib import Path

from dotenv import dotenv_values
from telebot import TeleBot, apihelper
from telebot.types import Message


class TelegramBotError(RuntimeError):
    """Raised when a Telegram Bot API request fails."""


class TelegramBot:
    """Simple interface to send messages through the Telegram Bot API.

    Config priority:
    1. Explicit `token` / `chat_id` arguments
    2. `TELEGRAM_BOT_TOKEN` / `TELEGRAM_CHAT_ID` from the system environment
    3. `TELEGRAM_BOT_TOKEN` / `TELEGRAM_CHAT_ID` from the repo `.env` file
    """

    def __init__(
        self,
        token: str | None = None,
        chat_id: str | None = None,
        *,
        timeout: int = 10,
    ):
        env_values = self._get_dotenv_values()
        self.token = token or os.getenv("TELEGRAM_BOT_TOKEN") or env_values.get("TELEGRAM_BOT_TOKEN")
        self.chat_id = (
            chat_id or os.getenv("TELEGRAM_CHAT_ID") or env_values.get("TELEGRAM_CHAT_ID")
        )
        self.timeout = timeout

        if not self.token:
            raise ValueError(
                "Missing Telegram bot token. Set TELEGRAM_BOT_TOKEN in your environment or .env file."
            )
        if not self.chat_id:
            raise ValueError(
                "Missing Telegram chat ID. Set TELEGRAM_CHAT_ID in your environment or .env file."
            )

        self.client = TeleBot(self.token)

    def is_configured(self) -> bool:
        """Return True when both required Telegram settings are available."""
        return bool(self.token and self.chat_id)

    def _get_dotenv_values(self) -> dict[str, str]:
        """Read Telegram settings from the repo `.env` file."""
        env_file = Path(__file__).resolve().parent.parent / ".env"
        if not env_file.exists():
            return {}

        values = dotenv_values(env_file)
        return {key: value for key, value in values.items() if value}

    def send_message(self, message: str) -> Message:
        """Send a plain-text message to the configured Telegram chat."""
        if not message.strip():
            raise ValueError("Telegram message cannot be empty.")

        try:
            return self.client.send_message(self.chat_id, message, timeout=self.timeout)
        except apihelper.ApiException as exc:
            raise TelegramBotError(str(exc)) from exc
