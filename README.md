# 🔥 StyleCheckAIBot

AI-powered Telegram bot that analyzes your outfit photos and gives instant, professional style feedback.

## Features

- **📸 Outfit Analysis** — Send a photo and get a style score, color feedback, fit evaluation, occasion suitability, and actionable suggestions
- **🎯 Occasion Selection** — Set context (Casual, Work, Date, Sport, Event) for smarter analysis
- **❓ Fashion Q&A** — Ask any fashion-related question and get a concise answer
- **⏰ Daily Limit** — 3 free outfit checks per day per user
- **💾 History** — Last 3 analyses stored per user with automatic cleanup

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.11+ |
| Telegram | aiogram 3.x (async) |
| Database | SQLite + SQLAlchemy 2.0 async + aiosqlite |
| AI | Google Gemini 1.5 Flash (Vision) |
| Image Storage | Local filesystem |
| Config | python-dotenv |

## Project Structure

```
/app
  /bot
    handlers.py         # Telegram event handlers
    keyboards.py        # Reply & inline keyboards
  /services
    gemini_service.py   # Raw Gemini API calls (sync wrapped in executor)
    outfit_analyzer.py  # Prompt building + response parsing
  /db
    models.py           # SQLAlchemy ORM models
    database.py         # Async engine, session, DB operations
  /storage
    image_storage.py    # Atomic save/delete for local images
  /utils
    logger.py           # Structured logging setup
    config.py           # Env var loading + validation
  main.py               # Bot entrypoint
```

## Quick Start

### 1. Clone the repo

```bash
git clone <your-repo-url>
cd stylecheckaibot
```

### 2. Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` and set:

| Variable | Description |
|---|---|
| `TELEGRAM_BOT_TOKEN` | Get from [@BotFather](https://t.me/BotFather) |
| `GEMINI_API_KEY` | Get from [Google AI Studio](https://aistudio.google.com/app/apikey) |

### 5. Run the bot

```bash
python -m app.main
```

Or:

```bash
cd stylecheckaibot
python app/main.py
```

## How It Works

1. User sends a photo → bot downloads the highest-resolution version
2. Image is saved locally to `app/storage/images/{user_id}/{timestamp}.jpg`
3. Image + prompt are sent to Gemini 1.5 Flash Vision API
4. Structured response is parsed and returned:

```
🔥 Style Score: 8/10
🎨 Colors: Great earth-tone palette with complementary navy accents.
👕 Fit: Well-fitted blazer, pants could be slightly tapered.
🎯 Occasion: Perfect for a smart-casual work environment.
💡 Suggestion: Swap the sneakers for loafers and add a leather belt to tie it together.
```

## Architecture Notes

- **No business logic in handlers** — handlers delegate to services
- **All Gemini calls are non-blocking** — sync SDK wrapped with `run_in_executor`
- **SQLite WAL mode** — enabled on startup for better concurrent read performance
- **Atomic image writes** — write to `.tmp` then rename to prevent corruption
- **Retention enforcement** — only the last 3 outfit checks per user are kept; older images are deleted from disk automatically
- **Structured logging** — all operations logged via Python `logging` module

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `TELEGRAM_BOT_TOKEN` | ✅ | Telegram Bot API token |
| `GEMINI_API_KEY` | ✅ | Google Generative AI API key |

## Limits

| Limit | Value |
|---|---|
| Max outfit checks per day | 3 |
| Max stored checks per user | 3 |
| Max image upload size | 10 MB |

## License

MIT

