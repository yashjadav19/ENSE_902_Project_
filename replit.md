# TalentFlow AI Agent System

A Python-based multi-agent HR intelligence system that uses Anthropic Claude AI to provide proactive HR analytics for small to medium enterprises (SMEs). Built as a master's research project (ENSE 902, University of Regina).

## Run & Operate

- `cd TalentFlow && python3 -m streamlit run app.py --server.port 5000` — launch the Streamlit dashboard
- `cd TalentFlow && python3 run_system.py` — run the full agent pipeline (generates results.json)
- `cd TalentFlow && python3 server.py` — run the Flask API on port 3001

## Stack

- Python 3.11
- LLM: Anthropic Claude (`claude-sonnet-4-20250514`)
- UI: Streamlit (dashboard)
- Backend API: Flask
- Storage: JSON files (no database)
- Environment: python-dotenv

## Where things live

```
TalentFlow/
├── data/employees.json       # 15 synthetic employee profiles
├── memory/store.json         # agent memory (longitudinal observations)
├── agents/
│   ├── employee_agent.py     # Layer 1 — per-employee Claude agent
│   └── manager_agent.py      # Layer 2 — department synthesis agent
├── app.py                    # Streamlit dashboard UI
├── server.py                 # Flask REST API
├── run_system.py             # Full pipeline runner → results.json
└── results.json              # Output of the latest full run
```

## Architecture decisions

- Two-layer agent design: employee agents analyze individuals; manager agents synthesize department-wide patterns
- JSON memory store keyed by employee ID keeps the last 10 observations per employee for longitudinal trend detection
- Agents receive memory history in their prompts, enabling deteriorating/improving trend labeling
- Flask API is separate from the Streamlit UI so the backend can be demoed independently
- No database — pure JSON for portability and simplicity

## Product

- Run Full Agent System button triggers all 15 employee agents + 3 manager agents via Claude API
- Dashboard shows urgent/monitor/healthy counts with expandable per-employee insight cards
- Manager tab shows department health scores, critical issues, team patterns, and top 3 weekly actions
- Memory tab shows longitudinal observation history and trend changes across runs

## User preferences

- Python only (no Node.js for TalentFlow)
- Model: claude-sonnet-4-20250514
- JSON-only storage, no database

## Gotchas

- First run has no memory history; trend = "insufficient_data" — run again to see trend detection
- The full system run takes 60-90 seconds (15 employee agents + 3 manager agents)
- The Streamlit workflow runs on port 5000

## Pointers

- See the `pnpm-workspace` skill for the existing Node.js monorepo structure (api-server, mockup-sandbox)
- TalentFlow lives in `TalentFlow/` at the workspace root, separate from the Node.js artifacts
