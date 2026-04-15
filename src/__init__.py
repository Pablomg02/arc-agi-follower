from __future__ import annotations

from importlib import import_module

__all__ = [
    "KaggleAPI",
    "KaggleCommandError",
    "KaggleCommandResult",
    "KaggleLeaderboard",
    "LeaderboardEntryNotFoundError",
    "ResearchAgent",
    "ResearchAgentError",
    "TelegramBot",
    "TelegramBotError",
]

_MODULE_EXPORTS = {
    "KaggleAPI": "src.kaggle_api",
    "KaggleCommandError": "src.kaggle_api",
    "KaggleCommandResult": "src.kaggle_api",
    "KaggleLeaderboard": "src.leaderboard",
    "LeaderboardEntryNotFoundError": "src.leaderboard",
    "ResearchAgent": "src.deep_research",
    "ResearchAgentError": "src.deep_research",
    "TelegramBot": "src.telegram_bot",
    "TelegramBotError": "src.telegram_bot",
}


def __getattr__(name: str):
    module_name = _MODULE_EXPORTS.get(name)
    if module_name is None:
        raise AttributeError(f"module 'src' has no attribute {name!r}")

    value = getattr(import_module(module_name), name)
    globals()[name] = value
    return value
