# arc-agi-follower

`arc-agi-follower` is a small utility for monitoring the ARC-AGI 3 Kaggle leaderboard and sending periodic summaries to Telegram.

Its current purpose is intentionally narrow: this repository exists to track ARC-AGI 3. While it could later be adapted into a more general tool for other Kaggle competitions, that is not the current goal. Even though a small amount of configuration already points in that direction, the project is documented and maintained specifically for ARC-AGI 3 for now.

## Current Status

The project is functional, but still fairly pragmatic and rough around the edges.

- `main.py` currently holds too much logic and is the least polished part of the codebase.
- The Telegram message format is designed around the immediate use case rather than long-term flexibility.
- The current message content is still quite ad hoc, and the reporting text is in Spanish.
- If the project becomes worth expanding, sensible next steps would include cleaning up the structure, separating message generation more clearly, improving message handling, and optionally providing an English version of the report.

## What It Does

When executed, the script:

1. Fetches the ARC-AGI 3 leaderboard from Kaggle.
2. Detects whether there has been movement in the top 5 during the last `N` hours.
3. Builds a summary message.
4. Prints the message to stdout.
5. Sends the message to a Telegram chat.

## Installation

Install the project dependencies with:

```bash
uv sync
```

This installs the Python dependencies as well as the Kaggle CLI used by the project.

Then create your local environment file:

```bash
cp .env.example .env
```

## Environment Variables

Secrets are expected to live in a local `.env` file, which is ignored by Git.

Start from `.env.example` and provide your own values:

```dotenv
KAGGLE_API_TOKEN=PASTE_YOUR_KAGGLE_API_TOKEN_HERE
TELEGRAM_BOT_TOKEN=PASTE_YOUR_TELEGRAM_BOT_TOKEN_HERE
TELEGRAM_CHAT_ID=PASTE_YOUR_TELEGRAM_CHAT_ID_HERE
```

### `KAGGLE_API_TOKEN`

Create a Kaggle API token from your account settings at `https://www.kaggle.com/settings`, then place it in `KAGGLE_API_TOKEN`.

The code first checks the system environment for `KAGGLE_API_TOKEN` and, if it is not present, falls back to the local `.env` file.

### `TELEGRAM_BOT_TOKEN`

1. Open Telegram and start a conversation with `@BotFather`.
2. Run `/newbot`.
3. Follow the instructions to create a bot.
4. Copy the token returned by BotFather.
5. Store it in `.env` as `TELEGRAM_BOT_TOKEN`.

### `TELEGRAM_CHAT_ID`

1. Open a chat with your bot and send any message.
2. Open the following URL in your browser, replacing `TOKEN` with the real bot token:

```text
https://api.telegram.org/botTOKEN/getUpdates
```

3. Find the `chat` object in the JSON response.
4. Copy the value of `chat.id`.
5. Store it in `.env` as `TELEGRAM_CHAT_ID`.

Example:

```json
"chat": {
  "id": 805431716,
  "type": "private"
}
```

In that case:

```dotenv
TELEGRAM_CHAT_ID=805431716
```

If you want to send messages to a group instead of a private chat, add the bot to the group, send a message there, and call `getUpdates` again. Group chat IDs are usually negative numbers.

## Usage

There are currently two intended ways to use the project.

### Option 1: Run It Manually with `main.py`

This is the simplest way to test the workflow locally, validate credentials, or trigger a one-off report.

```bash
uv run main.py
```

By default, the script checks the last `24` hours. To change the reporting window:

```bash
uv run main.py --hours 12
```

This will:

- load `.env` automatically when needed,
- fetch the leaderboard,
- generate the summary,
- print it to the console,
- and send it to Telegram.

This is the expected workflow when you want to run the report manually or experiment locally.

### Option 2: Run It Automatically with GitHub Actions

This is the expected day-to-day setup if you want the report to run on a schedule without manual intervention.

The workflow lives at `.github/workflows/arc-agi-report.yml` and runs:

```bash
uv run main.py --hours 12
```

It is scheduled to run twice per day, at `09:00` and `21:00` in the `Europe/Madrid` timezone.

Because GitHub Actions schedules are defined in UTC, the workflow includes multiple candidate cron entries and then skips the runs that do not match the target local hours.

It can also be launched manually from the Actions tab using `workflow_dispatch`.

### Configuring GitHub Actions

In GitHub, go to `Settings` -> `Secrets and variables` -> `Actions`.

Under `Secrets`, create:

- `KAGGLE_API_TOKEN`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

Under `Variables`, you may optionally create:

- `ARC_AGI_REPORT_HOURS`
- `ARC_AGI_COMPETITION`

If those optional variables are not defined:

- the workflow uses a default reporting window of `12` hours,
- the default competition is `arc-prize-2026-arc-agi-3`.

Although `ARC_AGI_COMPETITION` exists as a technical override, it should not be read as a sign that the repository is already intended as a general-purpose leaderboard follower. The project remains focused on ARC-AGI 3.

## Expected Workflow

The intended usage is straightforward:

- use `main.py` when you want to test locally or trigger a report manually,
- use GitHub Actions when you want continuous automated tracking.

At this stage, the repository should be understood as a practical ARC-AGI 3 utility rather than a reusable framework, a polished Telegram bot, or a generic Kaggle competition monitoring platform.

## Optional Configuration

The code already supports a few optional settings:

- `ARC_AGI_REPORT_TIMEZONE`: timezone used to evaluate the report window. Default: `Europe/Madrid`.
- `ARC_AGI_COMPETITION`: Kaggle competition slug. Default: `arc-prize-2026-arc-agi-3`.
- `--hours`: CLI argument used to limit the top-5 movement window. Default: `24` for manual execution.

Again, the existence of `ARC_AGI_COMPETITION` does not change the current scope of the project. For now, this repository is specifically about tracking ARC-AGI 3.
