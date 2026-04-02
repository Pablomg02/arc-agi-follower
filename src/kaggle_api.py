"""Small wrapper around the Kaggle CLI."""

import csv
import io
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from dotenv import dotenv_values


@dataclass
class KaggleCommandResult:
    """Result of running a Kaggle CLI command."""

    command: list[str]
    returncode: int
    stdout: str
    stderr: str


class KaggleCommandError(RuntimeError):
    """Raised when a Kaggle CLI command finishes with an error."""

    def __init__(self, result: KaggleCommandResult):
        self.result = result
        error_message = result.stderr.strip() or result.stdout.strip() or "Kaggle command failed."
        super().__init__(error_message)


class KaggleAPI:
    """Simple interface to call Kaggle commands from Python.

    Token priority:
    1. Explicit `api_key` argument
    2. `KAGGLE_API_TOKEN` from the system environment
    3. `KAGGLE_API_TOKEN` from the repo `.env` file via `python-dotenv`
    """

    def __init__(self, api_key: str | None = None):
        """Load the Kaggle token from the argument, environment, or local `.env`."""
        self.api_key = api_key or os.getenv("KAGGLE_API_TOKEN") or self._get_dotenv_token()
        if not self.api_key:
            raise ValueError(
                "Missing Kaggle API token. Set KAGGLE_API_TOKEN in your environment or .env file."
            )

    def is_configured(self) -> bool:
        """Return True when the API token is available."""
        return bool(self.api_key)

    def _get_dotenv_token(self) -> str | None:
        """Read `KAGGLE_API_TOKEN` from the repo `.env` file using `python-dotenv`."""
        env_file = Path(__file__).resolve().parent.parent / ".env"
        if not env_file.exists():
            return None

        token = dotenv_values(env_file).get("KAGGLE_API_TOKEN")
        return token if token else None

    def _normalize_competition_ref(self, competition: str) -> str:
        """Accept either a Kaggle competition URL or its URL suffix."""
        normalized = competition.strip().rstrip("/")
        marker = "/competitions/"
        if marker in normalized:
            return normalized.split(marker, maxsplit=1)[1]

        return normalized

    def run_cli(
        self,
        args: Sequence[str],
        *,
        check: bool = True,
        timeout: float | None = 30,
    ) -> KaggleCommandResult:
        """Run a Kaggle CLI command with the current token."""
        kaggle_binary = Path(sys.executable).with_name("kaggle")
        command = [str(kaggle_binary if kaggle_binary.exists() else "kaggle"), *args]
        env = os.environ.copy()
        env["KAGGLE_API_TOKEN"] = self.api_key

        # We call the CLI directly and capture everything so the caller
        # can decide what to do with the output.
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            env=env,
            check=False,
            timeout=timeout,
        )

        result = KaggleCommandResult(
            command=command,
            returncode=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
        )

        if check and completed.returncode != 0:
            raise KaggleCommandError(result)

        return result

    def list_competitions(
        self,
        *,
        search: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> list[dict[str, str]]:
        """Return competitions from `kaggle competitions list` as dictionaries."""
        args = ["competitions", "list", "--csv"]

        if search:
            args.extend(["--search", search])
        if page is not None:
            args.extend(["--page", str(page)])
        if page_size is not None:
            args.extend(["--page-size", str(page_size)])

        result = self.run_cli(args)
        output = result.stdout.strip()
        if not output:
            return []

        # Kaggle returns CSV here, so we parse it into a Python-friendly shape.
        competitions = list(csv.DictReader(io.StringIO(output)))
        if page_size is not None:
            return competitions[:page_size]

        return competitions

    def get_leaderboard(
        self,
        competition: str,
        *,
        page_size: int | None = None,
    ) -> list[dict[str, str]]:
        """Return one leaderboard page from `kaggle competitions leaderboard`."""
        args = [
            "competitions",
            "leaderboard",
            self._normalize_competition_ref(competition),
            "--show",
            "--csv",
        ]

        if page_size is not None:
            args.extend(["--page-size", str(page_size)])

        result = self.run_cli(args)
        output = result.stdout.strip()
        if not output:
            return []

        lines = output.splitlines()
        if lines and lines[0].startswith("Next Page Token = "):
            lines = lines[1:]

        if not lines:
            return []

        return list(csv.DictReader(io.StringIO("\n".join(lines))))
