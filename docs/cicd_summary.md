# CI/CD Pipeline — Summary for ai_gmail_whatsapp_agent Project

## What is CI/CD?

**CI = Continuous Integration**
> Every time you push code → tests run automatically

**CD = Continuous Deployment**
> If tests pass → new version/tag created automatically

---

## The Pipeline Flow

```
You push code to GitHub, to the dev or main branch (from your Windows laptop)
         ↓
GitHub receives your code
         ↓
GitHub spins up a fresh Ubuntu virtual machine in the cloud
         ↓
Installs Python 3.12 and all your libraries
         ↓
Runs your tests on Linux
         ↓
All tests pass ✅
         ↓
Was this a push to main?
    ↙            ↘
  YES             NO (push to dev)
   ↓               ↓
GitHub creates   No tag — just the
a new version    green test result
tag (e.g.
v2026.07.22.1430)
         ↓
Virtual machine is destroyed
         ↓
Done! 🎉
```

---

## Why Each Step Exists

### Step 1 — Checkout code
```
Why: The Ubuntu virtual machine starts completely empty.
     It has no files at all — not even your project!
     This step downloads your code from GitHub onto the machine.
```

### Step 2 — Set up Python
```
Why: The Ubuntu machine has no Python installed by default.
     This step installs Python 3.12 — same version you use locally.
     Ensures tests run on the same Python version everywhere.
```

### Step 3 — Install Python dependencies + system dependencies
```
Why: All your Python libraries need to be installed.
     The fresh Ubuntu machine has none of them.
     pip installs everything your project needs to run.

     Some Python libraries also need system-level tools to work.
     sounddevice needs PortAudio — a system audio library.
     pip cannot install system libraries — we use apt-get instead.

Libraries installed:
- mcp                      ← MCP server
- google-generativeai      ← old/deprecated Gemini package (unused, safe to drop)
- google-genai             ← Gemini AI (the one actually used)
- google-api-python-client ← Google Calendar
- google-auth-httplib2, google-auth-oauthlib ← Google auth support
- twilio                   ← WhatsApp
- python-dotenv            ← .env file reading
- colorama                 ← used by mail_checker.py for colored console output
- pytest pytest-asyncio    ← running tests
- openai-whisper           ← voice transcription (also pulls in torch)
- sounddevice soundfile    ← audio recording

System package installed:
Command: sudo apt-get install -y portaudio19-dev
```

### Step 4 — Run tests
```
Why: This is the HEART of CI/CD!
     Automatically verifies your code works correctly.
     If any test fails → pipeline stops → no version tag created.
     Protects you from pushing broken code!

Command: pytest test/test_mcp_tools.py -v

Note: tests need GOOGLE_GMAIL and GEMINI_API_KEY to be set, otherwise
the code's own guard-clause checks raise an error before the mocks in
test/conftest.py ever get a chance to run. Since everything is mocked,
these don't need to be real credentials — just non-empty placeholder
values, set directly in the workflow:
    GOOGLE_GMAIL: test@example.com
    GEMINI_API_KEY: dummy-key-for-ci
```

### Step 5 — Create version tag
```
Why: Only runs if ALL tests passed, AND only on the main branch!
     Creates a permanent marker in GitHub showing:
     "This version of the code was tested and works!"

     Tests run on every push to dev or main (fast feedback while you
     work), but a tag is only created when code lands on main — so
     tags represent actual releases, not every small dev commit.

Tag format: v2026.07.27.1430
             ↑    ↑  ↑  ↑
           year month day time

Note: this step needs `permissions: contents: write` at the workflow
level, since GitHub's default token is read-only and can't push tags
without it.
```

---

## CI/CD Decision Flow

```
Push to dev or main branch
         ↓
    Tests pass?
    ↙         ↘
  YES          NO
   ↓            ↓
Is this        Pipeline
main?          stops ❌
↙    ↘         No tag created
YES   NO       Fix your code
 ↓     ↓       and push again
Tag   No tag
 ✅    (dev push)
```

---

## What Happens if Tests Fail

```
❌ Run tests FAILED
         ↓
⬜ Create version tag — SKIPPED automatically
         ↓
You get email notification from GitHub
         ↓
Fix the failing tests
         ↓
Push again → pipeline runs again
```

---

## Benefits of This Pipeline

| Benefit | Explanation |
|---------|-------------|
| **Automatic** | No manual testing needed after every push |
| **Consistent** | Same tests run the same way every time |
| **Protected** | Broken code never gets a version tag |
| **Cross-platform** | Your Windows code tested on Linux too |
| **Historical** | Every version tag = working snapshot of code |

---

## Why Ubuntu (Linux)?

GitHub Actions provides virtual machines to run your pipeline.
You choose the operating system:

| Option | OS |
|--------|----|
| `ubuntu-latest` | Linux Ubuntu ← we use this |
| `windows-latest` | Windows |
| `macos-latest` | Mac OS |

**Why we chose `ubuntu-latest`:**
- ✅ **Free** — Ubuntu runners are free on GitHub
- ✅ **Fast** — Linux machines start quickly
- ✅ **Standard** — most CI/CD pipelines use Linux
- ✅ **Clean** — every push gets a brand new machine, no leftovers from previous runs
- ✅ **Cross-platform testing** — your code runs on Windows locally but tested on Linux too, catches bugs you might miss!

---

## The Tool We Use: GitHub Actions

- ✅ Built into GitHub — no extra tools needed
- ✅ Free for public repos
- ✅ Simple YAML file to configure
- ✅ Industry standard

---

## Project File Structure

```
ai_gmail_whatsapp_agent\
└── .github\
    └── workflows\
        └── ci.yml    ← the pipeline configuration file
```

---

## The Pipeline File — ci.yml

```yaml
name: CI/CD Pipeline

on:
  push:
    branches:
      - dev
      - main

permissions:
  contents: write

jobs:
  test-and-tag:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          pip install mcp
          pip install google-generativeai
          pip install google-genai
          pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
          pip install twilio
          pip install python-dotenv
          pip install colorama
          pip install pytest pytest-asyncio
          pip install openai-whisper
          pip install sounddevice soundfile
          sudo apt-get update
          sudo apt-get install -y portaudio19-dev

      - name: Run tests
        env:
          GOOGLE_GMAIL: test@example.com
          GEMINI_API_KEY: dummy-key-for-ci
        run: |
          pytest test/test_mcp_tools.py -v

      - name: Create version tag
        if: success() && github.ref == 'refs/heads/main'
        run: |
          git config user.name "github-actions"
          git config user.email "github-actions@github.com"
          git tag v$(date +'%Y.%m.%d.%H%M')
          git push origin --tags
```

---

## What Each Section Does

| Section | Meaning |
|---------|---------|
| `on: push: branches: dev, main` | triggers when you push to `dev` or `main` branch |
| `permissions: contents: write` | lets the workflow push a tag back to the repo |
| `runs-on: ubuntu-latest` | runs on GitHub's free Linux server |
| `Checkout code` | downloads your code onto the virtual machine |
| `Set up Python` | installs Python 3.12 on the virtual machine |
| `Install dependencies` | installs all your project libraries + the PortAudio system package |
| `Run tests` (with `env:`) | runs `pytest test/test_mcp_tools.py -v`, with placeholder `GOOGLE_GMAIL`/`GEMINI_API_KEY` values so guard-clause checks don't fail |
| `Create version tag` | only runs **if tests pass AND the branch is `main`** — creates tag like `v2026.07.22.1430` |

---

## How to Trigger the Pipeline

Push to `dev` (your everyday work — runs tests, no tag) or `main` (your release branch — runs tests AND creates a tag if they pass):

```bash
git add .
git commit -m "your commit message"
git push origin dev
```

---

## How to Watch the Pipeline Run

1. Go to your repo: `https://github.com/ilanaRam/ai_gmail_whatsapp_agent`
2. Click **"Actions"** tab at the top
3. Watch your pipeline running in real time!

---

## Version Tag Format

When tests pass, a tag is created automatically:
```
v2026.07.22.1430
  ↑    ↑  ↑  ↑
year month day time
```

You can see all tags in GitHub under **"Tags"** or **"Releases"** section.
