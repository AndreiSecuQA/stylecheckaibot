# StyleCheckAIBot — Optimized Build Prompt

> Use this prompt with a capable coding LLM (e.g. GPT-4o, Claude 3.5 Sonnet, Gemini 1.5 Pro) to generate the full MVP codebase.

---

# SYSTEM ROLE

You are a senior Python backend engineer, AI product architect, and Telegram bot specialist with deep expertise in async Python, LLM integrations, and production-grade code quality.

---

# 🧩 Product Overview

Build a clean, production-ready MVP for a Telegram bot called **StyleCheckAIBot**.

StyleCheckAIBot analyzes outfit photos and provides fast, AI-powered feedback:

* Style rating
* Color matching
* Outfit fit
* Occasion appropriateness
* Actionable improvement suggestions

The bot must feel like a **concise, confident personal stylist**.

---

# 🏗️ Tech Stack (STRICT)

| Layer | Technology |
|---|---|
| Language | Python 3.11+ |
| Telegram Framework | aiogram 3.x (async) |
| Database | SQLite via SQLAlchemy 2.0 async + aiosqlite |
| AI | Google Generative AI SDK (`google-generativeai`) |
| Image Storage | Local filesystem |
| Config | python-dotenv |

---

# 📁 Project Structure (MANDATORY)

```
/app
  /bot
    handlers.py       # Telegram event handlers (NO business logic here)
    keyboards.py      # Inline/reply keyboards
  /services
    gemini_service.py # Raw Gemini API calls only
    outfit_analyzer.py # Prompt building + response parsing
  /db
    models.py         # SQLAlchemy ORM models
    database.py       # Async engine, session factory, init_db()
  /storage
    image_storage.py  # Save/delete local images
  /utils
    logger.py         # Structured logging setup
    config.py         # Env var loading + validation
  main.py             # Bot startup entrypoint
```

---

# ⚙️ Core Functionalities

## 1. /start Command

* Send welcome message
* Show reply keyboard with buttons:
  * 📸 Rate my outfit
  * 🎯 Choose occasion
  * ❓ Ask a question

---

## 2. Image Upload (MAIN FEATURE)

**Flow:**

1. User sends photo
2. Immediately reply with `"⏳ Analyzing your outfit..."` and send `ChatAction.UPLOAD_PHOTO`
3. Download highest-resolution photo variant using aiogram async API
4. Save locally to: `app/storage/images/{user_id}/{unix_timestamp}.jpg`
   * Auto-create directories
   * Use `pathlib.Path` only
   * Sanitize `user_id` (digits only) to prevent path traversal
5. Pass image path to `outfit_analyzer.py`
6. Send formatted result back to user

---

## 3. AI Outfit Analysis

### Gemini Integration Rules

* Use `google-generativeai` SDK (`genai.configure(api_key=...)`)
* Use model: `gemini-1.5-flash` (vision-capable, fast)
* Auth: API key via `GEMINI_API_KEY` env var
* Since the SDK is **synchronous**, wrap all Gemini calls with `asyncio.get_event_loop().run_in_executor(None, ...)` to avoid blocking the event loop

### analyze_outfit function signature

```python
async def analyze_outfit(image_path: str, occasion: str | None) -> str
```

### Prompt Template

```
You are a professional fashion stylist. Analyze this outfit photo and respond ONLY in this exact format, no extra text:

🔥 Style Score: X/10
🎨 Colors: <one sentence>
👕 Fit: <one sentence>
🎯 Occasion: <suitability for {occasion if occasion else 'general use'}>
💡 Suggestion: <1-2 specific actionable tips>

Be concise, direct, and confident. No greetings, no closing remarks.
```

### Response Parsing

* Parse response in `outfit_analyzer.py` using regex or line-by-line matching
* If parsing fails, return the raw response with a note: `"⚠️ Couldn't parse structured response, here's the raw analysis:\n{raw}"`
* Never crash on model output variance

---

## 4. Occasion Selection

* Options: Casual, Work, Date, Sport, Event
* Show as `InlineKeyboardMarkup`
* On selection: upsert `selected_occasion` in DB for that user
* Confirm with: `"✅ Occasion set to: {occasion}"`

---

## 5. Text Questions

* Handle plain text (non-command, non-photo)
* Detect if user is asking a fashion-related question
* Send text-only prompt to Gemini:

```
You are a professional fashion stylist. Answer this question briefly and confidently in 2-3 sentences: {user_text}
```

* Wrap Gemini call in executor (same as image analysis)

---

## 6. SQLite Database (SQLAlchemy 2.0 Async)

### Setup

* Use `create_async_engine("sqlite+aiosqlite:///app/db/stylecheck.db")`
* Enable WAL mode on startup:
  ```python
  async with engine.connect() as conn:
      await conn.execute(text("PRAGMA journal_mode=WAL"))
  ```
* Use `async_sessionmaker` for session factory
* All DB operations must use `async with session:` context managers

### Table: `users`

| Column | Type | Notes |
|---|---|---|
| id | Integer PK | autoincrement |
| telegram_user_id | BigInteger | unique, indexed |
| selected_occasion | String | nullable |
| created_at | DateTime | UTC, server_default |

### Table: `outfit_checks`

| Column | Type | Notes |
|---|---|---|
| id | Integer PK | autoincrement |
| user_id | Integer FK | → users.id, cascade delete |
| image_path | String | local path |
| result_text | Text | full AI response |
| created_at | DateTime | UTC, server_default |

### Retention Rule

After each new `outfit_check` insert for a user, **in the same transaction**:

1. Query all outfit checks for user ordered by `created_at DESC`
2. Delete any beyond the 3rd one
3. Also delete the corresponding image files from disk

---

## 💾 Image Storage (`image_storage.py`)

```python
async def save_image(user_id: int, image_bytes: bytes) -> str:
    # Returns absolute path string
    # Uses pathlib.Path
    # Sanitizes user_id
    # Auto-creates directories
    # Writes atomically (write to .tmp then rename)

async def delete_image(image_path: str) -> None:
    # Silently ignores missing files
    # Logs deletion
```

---

## ⚡ UX Rules

* Always send `ChatAction.TYPING` or `ChatAction.UPLOAD_PHOTO` before slow operations
* Acknowledge image receipt **immediately** before processing
* Target response time: best-effort under 10s (5s is aspirational)

---

## 🧪 Error Handling (MANDATORY)

| Error Scenario | User Message |
|---|---|
| Non-photo file sent | `"📎 Please send a photo, not a file."` |
| Image too large (>10MB) | `"📏 Photo is too large. Please send a smaller image."` |
| Gemini API failure | `"😔 AI service is temporarily unavailable. Try again in a moment."` |
| Missing API key on startup | Raise `RuntimeError` with clear message, exit immediately |
| DB error | `"⚠️ Something went wrong on our end. Please try again."` |
| Unknown input | `"🤔 I didn't understand that. Use the menu buttons or send a photo."` |

* Log all errors with full traceback at `ERROR` level
* Never expose internal errors or stack traces to users

---

## 🔐 Environment Variables

**`.env.example`:**

```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
GEMINI_API_KEY=your_google_gemini_api_key_here
```

**`config.py` must:**

* Load vars with `python-dotenv`
* Validate on startup: if any required var is missing → raise `RuntimeError` with the missing var name
* Expose typed constants (not raw strings)

---

## ⭐ Bonus Features (implement if straightforward)

### Daily Rate Limiting

* Add column `daily_check_count: Integer` and `last_check_date: Date` to `users` table
* On each outfit check:
  * If `last_check_date != today`: reset count to 0
  * If count `>= 3`: reply `"⏰ You've reached your 3 outfit checks for today. Come back tomorrow!"`
  * Otherwise: increment count and proceed

---

## 🧼 Code Quality Rules (NON-NEGOTIABLE)

* Type hints on **every** function signature
* `async/await` used correctly — no sync blocking in async context
* All Gemini SDK calls wrapped in `run_in_executor`
* No business logic inside `handlers.py` — handlers only call services
* Structured logging via `logging` module (not `print`)
* `pathlib.Path` for all file paths (no `os.path`)
* Constants in `config.py`, never hardcoded inline

---

## 📦 Deliverables (ALL REQUIRED)

Generate in order:

1. `requirements.txt`
2. `.env.example`
3. `app/utils/config.py`
4. `app/utils/logger.py`
5. `app/db/models.py`
6. `app/db/database.py`
7. `app/storage/image_storage.py`
8. `app/services/gemini_service.py`
9. `app/services/outfit_analyzer.py`
10. `app/bot/keyboards.py`
11. `app/bot/handlers.py`
12. `app/main.py`
13. `README.md`

---

## 🚀 Run Instructions

Project must run with:

```bash
pip install -r requirements.txt
python app/main.py
```

---

## ⚠️ Final Constraints

* MVP only — no overengineering
* No authentication system (Telegram `user_id` is identity)
* No external storage (no S3, no cloud)
* No Docker required
* Deliver **complete, runnable code** — no placeholders, no `# TODO`, no `...` stubs

