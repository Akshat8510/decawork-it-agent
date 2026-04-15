# 🤖 IT Support AI Agent

An AI agent that takes natural-language IT support requests and executes them autonomously on a mock IT admin panel — navigating like a human using **browser-use** (Playwright + Claude).

---

## 📁 Project Structure

```
it-agent/
├── agent/
│   ├── __init__.py        # Package exports
│   ├── agent.py           # CLI entry point + demo menu
│   ├── browser_agent.py   # browser-use integration (Playwright + Claude)
│   └── prompts.py         # System prompt & task templates
├── app/
│   ├── main.py            # Flask admin panel (3 pages, full CRUD)
│   └── templates/
│       ├── index.html     # Dashboard
│       ├── users.html     # User management
│       └── licenses.html  # License management
├── run.py                 # One-shot launcher (Flask + Agent)
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🚀 Quick Start

### 1. Clone & install

```bash
git clone https://github.com/YOUR_USERNAME/it-agent.git
cd it-agent

python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate

pip install -r requirements.txt
playwright install chromium
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

### 3. Run the admin panel (standalone)

```bash
cd app
flask --app main run --port 5000
# Open http://localhost:5000
```

### 4. Run the agent

```bash
# Interactive demo menu
python run.py --demo

# Direct task
python run.py "reset password for alice@company.com"
python run.py "create user Jane Doe jane@company.com role Engineer then assign Slack Pro"

# Headless (no visible browser)
python run.py --headless "disable account for bob@company.com"
```

---

## 🏗 Architecture

```
User (CLI/natural language)
        │
        ▼
  agent/agent.py          ← parses CLI args, provides demo menu
        │
        ▼
agent/browser_agent.py    ← browser-use Agent
        │  Uses: Claude claude-opus-4-5 via LangChain
        │  Uses: Playwright (real Chromium browser)
        │
        ▼
  Flask Admin Panel        ← http://localhost:5000
  (app/main.py)
  ┌──────────────────────┐
  │  /           Dashboard│
  │  /users   User Mgmt   │
  │  /licenses Licenses   │
  │  /api/*  JSON helpers │
  └──────────────────────┘
        │
        ▼
  In-memory store (dict)   ← resets on restart; swap for SQLite/Postgres
```

### Key Design Decisions

| Decision | Choice | Why |
|---|---|---|
| Browser automation | `browser-use` | Playwright + LLM vision — no DOM shortcuts |
| LLM | Claude claude-opus-4-5 | Best reasoning for multi-step tasks |
| Admin panel | Flask | Fast to build, zero boilerplate |
| State | In-memory dict | Keeps demo simple; swap for DB in production |
| Screenshots | Enabled | Agent can "see" flash messages to verify success |

---

## 🎯 Supported Tasks

| Task | Example |
|---|---|
| Reset password | `"reset password for alice@company.com"` |
| Create user | `"create user Jane Doe jane@company.com role Engineer"` |
| Disable account | `"disable account for bob@company.com"` |
| Enable account | `"enable account for bob@company.com"` |
| Assign license | `"assign Microsoft 365 to alice@company.com"` |
| Revoke license | `"revoke license from bob@company.com"` |
| **Conditional (bonus)** | `"check if carol@company.com exists; if not, create her then assign Slack Pro"` |

---

## 🧠 How the Agent Works

1. **Receives task** in plain English
2. **Navigates to admin panel** root URL
3. **Reads page content + screenshot** to understand current state
4. **Clicks navigation**, fills forms, submits them — exactly like a human
5. **Reads flash messages** to verify success/failure
6. **Retries** with corrected inputs if an error flash appears
7. **Returns a summary** of actions taken

The agent uses **no DOM selectors**, **no API shortcuts**, and **no JavaScript injection** — it only interacts through visible UI elements.

---

## ✨ Bonus Features Implemented

- **Conditional multi-step logic** — "check if user exists, if not create them, then assign license"
- **Audit log** — every action is logged with timestamp on the dashboard
- **JSON API** — `/api/users`, `/api/user/<email>`, `/api/licenses` for agent state checks

---

## 🔧 Extending

**Add a new panel page:**
1. Add route + template in `app/main.py`
2. Add nav link in all 3 HTML templates
3. Describe it in `agent/prompts.py` SYSTEM_PROMPT

**Use a different LLM:**
```python
# browser_agent.py — swap ChatAnthropic for any LangChain-compatible model
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model="gpt-4o", ...)
```

**Trigger from Slack (bonus):**
```python
# In a Slack Bolt app:
@app.message(re.compile(r"^/it (.+)"))
def handle_it_request(message, say):
    task = message["text"].replace("/it ", "")
    result = run(task, headless=True)
    say(result)
```

---

## 📋 Requirements

- Python 3.11+
- Anthropic API key
- Chromium (installed via `playwright install chromium`)