# Twitch Stream Tracker

[Русский](README.md) · **English**

A Telegram bot that tells users when a Twitch channel goes live or ends a stream. Users can add channels by URL, view their current status, and remove channels from their watchlist. Free accounts can follow one channel.

The `/admin` menu supports usage statistics, subscription pricing, manual subscription grants, bans, and broadcasts. The bot has a YooMoney subscription flow with a button to check payment status.

## Setup

You need Python 3.10+, a Telegram bot, and an app registered in the Twitch Developer Console. [BotFather](https://t.me/BotFather) · [Register a Twitch app](https://dev.twitch.tv/docs/authentication/register-app/)

```bash
git clone https://github.com/deco9er/twich-tracker.git
cd twich-tracker
```

**Windows (Command Prompt)**

```cmd
python -m venv .venv
.venv\Scripts\python.exe -m pip install "aiogram>=3.7,<4" "SQLAlchemy[asyncio]>=2,<3" aiosqlite requests
```

**Linux**

```bash
python3 -m venv .venv
.venv/bin/python -m pip install 'aiogram>=3.7,<4' 'SQLAlchemy[asyncio]>=2,<3' aiosqlite requests
```

Edit the existing `config.py` in your local checkout. Keep real credentials and the SQLite database out of commits.

| Setting | Value |
| --- | --- |
| `BOT_TOKEN` | Telegram bot token from BotFather. |
| `ADMIN_ID` | A list of numeric Telegram user IDs, such as `[123456789]`. |
| `TWITCH_CLIENT_ID`, `TWITCH_ACCESS_TOKEN` | Your Twitch app's client ID and OAuth app access token from the client credentials flow. Generate a new token and restart the bot when it expires. |
| `SUPPORT_URL`, `BOT_URL` | Your support link and the bot link used to return after checkout. |
| `DB_LITE` | SQLite connection URL. The default is ready to use. |
| `YOOMONEY_WALLET_ID`, `YOOMONEY_ACCESS_TOKEN` | Wallet number and a token with access to operation history, if subscriptions will be sold. |

[Get a Twitch access token](https://dev.twitch.tv/docs/authentication/getting-tokens-oauth/#client-credentials-grant-flow)

Start the bot from the project directory.

```cmd
.venv\Scripts\python.exe app.py
```

```bash
.venv/bin/python app.py
```

The bot creates the SQLite tables on startup. Send it `/start` in a private chat and add a channel URL such as `https://www.twitch.tv/username`. To verify notifications, use a channel where you can start and end a stream.

## Project layout

- `app.py` starts aiogram, registers the handlers, and launches the background monitor.
- `handlers/` handles commands, subscriptions, and administrator actions.
- `services/` calls Twitch Helix and YooMoney. The monitor checks channels from the database, notifies users on status changes, and waits 10 seconds before the next pass.
- `database/` stores users, channels, and subscriptions using SQLAlchemy and SQLite.
