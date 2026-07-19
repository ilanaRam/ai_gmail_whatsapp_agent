# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A personal automation agent with two independent pipelines, both exposed as MCP tools:

1. **Mail → WhatsApp**: polls Gmail (IMAP) for an unread message matching a subject/sender, then forwards a notification to WhatsApp via Twilio.
2. **Voice → Calendar**: records audio from the mic, transcribes Hebrew speech with Whisper, extracts event details with Gemini, and creates the event on Google Calendar.

## Setup

- Python 3.12, dependencies installed directly into `.venv` (no `requirements.txt`/`pyproject.toml` in the repo — check `.venv/Scripts/python.exe -m pip list` for the current set: `mcp`, `google-genai`, `google-api-python-client`, `google-auth-oauthlib`, `openai-whisper`, `torch`, `sounddevice`, `soundfile`, `twilio`, `python-dotenv`, `colorama`, `pytest`, `pytest-asyncio`).
- Copy `.env.example` to `.env` and fill in real values before running anything — every module calls `load_dotenv()` and reads secrets via `os.getenv(...)`.
- **Never read or display the contents of `.env` or any `token.json` file** (root, `src/`, `test/`) — they hold live secrets and OAuth tokens. Reference `.env.example` instead when you need to know which variables exist.
- Whisper transcription requires `ffmpeg` on PATH (`winget install ffmpeg`).
- Google Calendar auth is interactive on first use: `connect_to_google_calendar()` opens a browser (`InstalledAppFlow.run_local_server`) and writes `token.json` to the working directory. Subsequent runs reuse that token until it expires. There are stray `token.json` files at repo root, `src/`, and `test/` — the one that matters is whichever directory the process is run from (`TOKEN_FILE = 'token.json'` is a relative path in `src/calendar_checker.py`).

## Running

```
# Mail → WhatsApp poller (root script, entrypoint picks direct_main or mcp_main)
python agent_mail_checker_whatsapp_sender.py

# Voice → Calendar pipeline
python calendar_updater.py

# Run the MCP server standalone (for manual tool inspection)
python -m src.mcp_server
```

Both root scripts run the MCP server in a background daemon thread (`mcp_obj.run_mcp_server()`) and then drive it by calling `mcp_obj.my_mcp_server.call_tool(name, params)` in an asyncio loop — MCP tool results always arrive as `[TextContent(...)]`; unwrap with `json.loads(result[0].text)`.

## Tests

```
pytest test/test_mcp_tools.py
```

- No `pytest.ini`/`pyproject.toml` config exists, and `pytest-asyncio` defaults to strict mode. Only the parameterized test (`test_create_google_calendar_event_tool_parameterized`) has `@pytest.mark.asyncio` and will actually execute as async; the other `async def test_*` functions in this file are missing that marker and will not run as coroutines under plain `pytest` — keep this in mind when adding new async tests, and add the marker (or an `asyncio_mode = auto` config) rather than assuming an unmarked async test runs.
- Tests call real external services (Gmail IMAP, Twilio, Google Calendar, Gemini) — there are no mocks. Running the full suite sends real WhatsApp messages and can create real Calendar events; read a test before running it.

## Architecture

**Separation of Concerns** is the deliberate design principle throughout `src/`: each integration module (`mail_checker.py`, `whatsapp_sender.py`, `calendar_checker.py`, `ai_analyzer.py`, `voice.py`) is a plain, synchronous, MCP-agnostic function library that works standalone (each has a `__main__` block for direct testing). `mcp_server.py` is the only module that knows about MCP — it imports every integration module and wraps each function in a thin `@my_mcp_server.tool()`-decorated function that adapts args/return values to dict form. Never merge tool logic into the integration modules; add new capabilities as a new integration function + a new wrapper tool in `mcp_server.py`.

Call graph for the two pipelines:

- **Mail→WhatsApp**: `agent_mail_checker_whatsapp_sender.py` → `tool_check_email` → `mail_checker.check_email()` (IMAP `UNSEEN` search, returns `(subject, sender)` or `(None, None)`) → if matched, `tool_send_whatsapp` → `whatsapp_sender.send_whatsapp()` (Twilio sandbox message).
- **Voice→Calendar**: `calendar_updater.py` → `tool_record_voice_and_convert_voice_to_text` (`voice.record_voice()` records until `SILENCE_DURATION` seconds of sub-threshold volume, then `voice.convert_voice_to_text()` runs Whisper with `language='he'`) → `tool_analyze_text` (`ai_analyzer.analyze_text()` prompts Gemini to return a fixed-schema JSON event dict) → `tool_set_google_calendar_event` (`calendar_checker.connect_to_google_calendar()` + `create_google_calendar_event()`, which runs `validity_check()` on the event dict before building the Google Calendar API payload).

Key data contract: the event dict passed between `ai_analyzer` and `calendar_checker` must have exactly these fields — `title, date (YYYY-MM-DD), time (HH:MM), duration_minutes, description, participants, my_calendar, alex_calendar, is_urgent, alert_minutes_before` — `calendar_checker.validity_check()` rejects anything missing or wrong-typed and `create_google_calendar_event()` raises `ValueError` rather than silently defaulting.

Recorded audio and transcripts are written per-run to `Results/<YYYY-MM-DD_HH-MM-SS>/` (`voice.create_results_subfolder()`), never overwritten in place.
