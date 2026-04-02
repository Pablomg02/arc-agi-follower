# arc-agi-follower

`arc-agi-follower` is a small utility for monitoring the ARC-AGI 3 Kaggle leaderboard, enriching the report with a short external-news summary, and sending the result to Telegram.

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
3. Searches for recent ARC-AGI 3 / ARC Prize news with Tavily.
4. Summarizes the retrieved news with Anthropic, prioritizing the last `N` hours and falling back to the last few days when needed.
5. Builds a summary message that includes leaderboard movement, the current top 5, and the optional news section.
6. Prints the message to stdout.
7. Sends the message to a Telegram chat.

If the research step fails or is not configured, the script still sends the leaderboard report without the news section.

## Installation

Install the project dependencies with:

```bash
uv sync
```

This installs the Python dependencies as well as the Kaggle CLI used by the project. The current dependency set also includes the Tavily and Anthropic clients used by the news-research flow.

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
TAVILY_API_KEY=PASTE_YOUR_TAVILY_API_KEY_HERE
ANTHROPIC_API_KEY=PASTE_YOUR_ANTHROPIC_API_KEY_HERE
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

### `TAVILY_API_KEY`

Create an API key in your Tavily account and store it as `TAVILY_API_KEY`.

This key is used to search for recent ARC-AGI 3 / ARC Prize coverage before generating the Telegram summary.

### `ANTHROPIC_API_KEY`

Create an Anthropic API key and store it as `ANTHROPIC_API_KEY`.

This key is used to summarize the raw Tavily search response into the short Spanish news block included in the report.

### Configuration Priority for Research Keys

`ResearchAgent` resolves research credentials in this order:

1. Explicit constructor arguments.
2. System environment variables.
3. The local repo `.env` file.

This means local debugging can rely on `.env`, while CI can inject secrets directly through the environment.

### About `ANTHROPIC_MODEL`

`.env.example` currently includes an `ANTHROPIC_MODEL` placeholder, but the current code path does not read that environment variable yet. The model is currently chosen inside `src/deep_research.py`.

## Usage

There are currently three practical ways to use the project.

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
- try to fetch and summarize recent external news,
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

Under `Secrets`, create at least:

- `KAGGLE_API_TOKEN`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

To enable the news-research section as well, also create:

- `TAVILY_API_KEY`
- `ANTHROPIC_API_KEY`

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
- use GitHub Actions when you want continuous automated tracking,
- use `debug_news_flow.py` when you want to inspect only the Tavily -> Anthropic news pipeline.

At this stage, the repository should be understood as a practical ARC-AGI 3 utility rather than a reusable framework, a polished Telegram bot, or a generic Kaggle competition monitoring platform.

## Optional Configuration

The code already supports a few optional settings:

- `ARC_AGI_REPORT_TIMEZONE`: timezone used to evaluate the report window. Default: `Europe/Madrid`.
- `ARC_AGI_COMPETITION`: Kaggle competition slug. Default: `arc-prize-2026-arc-agi-3`.
- `--hours`: CLI argument used to limit the top-5 movement window. Default: `24` for manual execution.
- `debug_news_flow.py --query "...":` override the default Tavily query for news debugging.
- `debug_news_flow.py --skip-claude`: print the Anthropic request payload without actually calling Anthropic.
- `debug_news_flow.py --max-results N`: control how many Tavily results are fetched during debugging.
- `debug_news_flow.py --report-end 2026-04-02T09:00:00`: reproduce a specific reporting window while debugging.

Again, the existence of `ARC_AGI_COMPETITION` does not change the current scope of the project. For now, this repository is specifically about tracking ARC-AGI 3.

## Debugging the Deep Research Flow

If you want to inspect the news pipeline without hitting Telegram, run:

```bash
uv run debug_news_flow.py --hours 24
```

This script prints:

- the final search query,
- the raw Tavily response,
- the payload sent to Anthropic,
- and, unless `--skip-claude` is used, the resulting summary.

It is useful when tuning the query, checking date-window behavior, or understanding why the news block did or did not appear in the final Telegram report.
