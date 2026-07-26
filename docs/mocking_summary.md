# Mocking in Python — Summary for ai_gmail_whatsapp_agent Project

## What is Mocking?

Mocking = replacing a real object/function with a fake one during testing,
so tests never touch the real outside world.

**Why we mock:**
- No real WhatsApp messages sent during tests
- No real Google Calendar events created
- No real Gmail emails marked as read
- No real Gemini API quota used
- Tests run fast and reliably every time

---

## Tools Used

```python
from unittest.mock import patch, MagicMock  # built-in Python, no installation needed
import pytest
```

- `patch()` — temporarily replaces a real class/function with a fake
- `MagicMock()` — a fake object that responds to any method call automatically
- `pytest.fixture` — setup function that runs **before** tests — the test itself never knows it is using a fake object instead of a real one
- `autouse=True` — runs fixture automatically for every test, no need to request it

---

## Project Mock Fixtures — conftest.py

All fixtures live in `test/conftest.py`.
Pytest finds this file automatically — no imports needed in test files.

---

### 1. Gmail IMAP Mock (`mock_gmail_IMAP`)

**Real code patched:**
```python
# in mail_checker.py
mail_gmail_server = imaplib.IMAP4_SSL(IMAP_SERVER)
mail_gmail_server.login(...)    # not mocked - return value not used
mail_gmail_server.select(...)   # not mocked - return value not used
status, mails_respond = mail_gmail_server.search(None, search_criteria)
_, data = mail_gmail_server.fetch(email_id, '(RFC822)')
```

**Why we mock:** `.fetch()` marks real emails as READ in Gmail — side effect!

**Mock chain:**
```python
with patch('src.mail_checker.imaplib.IMAP4_SSL') as fake_gmail_imap_ssl:
    fake_imap_server = MagicMock()
    fake_imap_server.search.return_value = ('OK', [b'1'])
    fake_imap_server.fetch.return_value = ('OK', [(b'', b'From: ilanaaprilloriram@gmail.com\r\nSubject: RRR\r\n\r\nTest body')])
    fake_gmail_imap_ssl.return_value = fake_imap_server
    yield
```

---

### 2. Twilio WhatsApp Mock (`mock_gmail_to_whatsapp`)

**Real code patched:**
```python
# in whatsapp_sender.py
client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
message = client.messages.create(body=..., from_=..., to=...)
print(message.sid)
```

**Why we mock:** Prevents real WhatsApp messages being sent during tests.

**Mock chain:**
```python
with patch('src.whatsapp_sender.Client') as fake_twilio_client:
    fake_whatsapp_client = MagicMock()
    fake_whatsapp_client.messages.create.return_value.sid = "WHATSAPP_MSG_ID_000"
    fake_twilio_client.return_value = fake_whatsapp_client
    yield
```

---

### 3. Google Calendar Mock (`mock_voice_to_calendar`)

**Real code patched:**
```python
# in calendar_checker.py
service = connect_to_google_calendar()
created_event = service.events().insert(calendarId=..., body=...).execute()
print(created_event.get('htmlLink'))
```

**Why we mock:** Prevents real Google Calendar events being created during tests.

**Mock chain:**
```python
with patch('src.calendar_checker.connect_to_google_calendar') as fake_connect:
    fake_service = MagicMock()
    fake_service.events.return_value.insert.return_value.execute.return_value = {
        "htmlLink": "https://calendar.google.com/mock-event-link"
    }
    fake_connect.return_value = fake_service
    yield
```

---

### 4. Gemini AI Mock (`mock_gmini_ai_analyzer`)

**Real code patched:**
```python
# in ai_analyzer.py
client = genai.Client(api_key=gemini_api_key)
model = client.models.generate_content(model=GEMINI_MODEL, contents=my_prompt)
response = model.text
```

**Why we mock:** Prevents real Gemini API quota being used. Tests run fast and deterministically.

**Mock chain:**
```python
with patch('src.ai_analyzer.genai.Client') as fake_gemini:
    fake_client = MagicMock()
    fake_client.models.generate_content.return_value.text = '''{
        "title": "פגישה עם אלכס",
        "date": "2026-06-02",
        "time": "15:00",
        "duration_minutes": 60,
        "description": "לדון בפרויקט",
        "participants": ["אלכס"],
        "my_calendar": true,
        "alex_calendar": true,
        "is_urgent": false,
        "alert_minutes_before": 30
    }'''
    fake_gemini.return_value = fake_client
    yield
```

---

## How the Mocking Mechanism Works

### Step by step for each test:

```
pytest starts
    ↓
finds conftest.py automatically (special pytest file)
    ↓
runs all 4 autouse=True fixtures BEFORE each test:
    - imaplib.IMAP4_SSL      → replaced by fake ✅
    - twilio Client           → replaced by fake ✅
    - connect_to_google_calendar → replaced by fake ✅
    - genai.Client            → replaced by fake ✅
    ↓
your test runs — all real services are fake!
    ↓
test finishes
    ↓
all 4 fixtures teardown — real services restored ✅
    ↓
next test starts — same process again
```

---

## Key Rules to Remember

| Rule | Explanation |
|------|-------------|
| Patch the **class**, not the instance | `patch('src.module.ClassName')` not the variable |
| Match the **exact call chain** | `client.messages.create()` → `.messages.create.return_value` |
| Each `()` in real code = `.return_value` in mock | `.events().insert().execute()` → `.events.return_value.insert.return_value.execute.return_value` |
| No `()` = no `.return_value` | `.messages` has no `()` so just `.messages` in mock |
| `yield` keeps patch active during test | Without `yield` patch closes before test runs! |
| `autouse=True` = no need to add fixture to test | Pytest applies it automatically to every test |

---

## Project File Structure

```
ai_gmail_whatsapp_agent\
├── test\
│   ├── conftest.py        ← all mock fixtures here
│   └── test_mcp_tools.py  ← all test functions here
├── src\
│   ├── mail_checker.py    ← Gmail IMAP (mocked)
│   ├── whatsapp_sender.py ← Twilio WhatsApp (mocked)
│   ├── calendar_checker.py← Google Calendar (mocked)
│   ├── ai_analyzer.py     ← Gemini AI (mocked)
│   └── mcp_server.py      ← MCP tools wrapper
```

---

## Running Tests

```bash
# run all tests
pytest test/test_mcp_tools.py -v

# run specific test
pytest test/test_mcp_tools.py::test_check_email_tool -v

# run with output printed
pytest test/test_mcp_tools.py -v -s
```
