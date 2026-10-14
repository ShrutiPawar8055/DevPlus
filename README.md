# LLD Practice Platform

A focused practice platform for **Low-Level Design (LLD)**. Learners pick a problem, design a solution (prose + code), submit it, and receive structured, explainable feedback — then iterate.

## ✨ Features

- **4 seed LLD problems**: Parking Lot, Elevator System, Vending Machine, Snake Game — each with requirements, hints, and evaluation criteria.
- **Submission format**: free-text design description + code snippets (classes/interfaces).
- **Two evaluators** with automatic fallback:
  - **LLM evaluator** (OpenAI-compatible API) — qualitative, specific feedback.
  - **Rule-based evaluator** — deterministic, transparent scoring across 5 categories.
- **Attempt history** — every submission is stored, so learners can track improvement.
- **Structured feedback** — overall score, strengths, improvements, and per-category scores.

## 🏗️ Architecture

```
frontend/  (React + TypeScript + Vite)
  └── calls  /api/*  (proxied to backend)

backend/   (FastAPI + SQLAlchemy + SQLite)
  app/
  ├── models/          # SQLAlchemy ORM (Problem, Attempt)
  ├── schemas/         # Pydantic API contracts
  ├── repositories/    # Data access (ProblemRepository, AttemptRepository)
  ├── services/
  │   ├── attempt_service.py          # Orchestrates create → evaluate → store
  │   └── evaluator/
  │       ├── base.py                 # FeedbackEvaluator interface
  │       ├── llm_evaluator.py        # LLM (OpenAI-compatible) implementation
  │       ├── rule_based_evaluator.py # Deterministic fallback
  │       └── factory.py              # Picks evaluator + fallback logic
  ├── api/             # FastAPI route handlers
  ├── seed.py          # Seed problems
  ├── config.py        # Environment configuration
  └── main.py          # App entry point
  tests/               # pytest suite (20 tests)
```

### Key Design Decisions

| Concern | Approach |
|---|---|
| **Domain model** | `Problem` and `Attempt` as the core aggregates. Feedback is stored as JSON on `Attempt` so it can evolve without migrations. |
| **Evaluation abstraction** | `FeedbackEvaluator` interface with one method `evaluate()`. Adding a new evaluator (e.g., a different LLM, a diagram parser) requires only a new implementation — no changes to the service or API. |
| **LLM + deterministic split** | Deterministic: requirement keyword coverage, class/interface counts, SOLID vocabulary. LLM: qualitative assessment, specific trade-off feedback, natural-language suggestions. If the LLM fails, the rule-based engine takes over automatically. |
| **Failure handling** | Attempts have a `status` field (`pending → evaluating → completed/failed`). If evaluation fails, the attempt is marked `failed` with the error stored. The rule-based fallback prevents total failure when the LLM is unavailable. |
| **Persistence** | SQLite via SQLAlchemy. A simple monolith — no microservices, no message queues. |

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+

### 1. Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
cp .env.example .env          # optional: set LLM_API_KEY to enable AI feedback
uvicorn app.main:app --reload
```

The backend runs on `http://localhost:8000`. The database and seed problems are created automatically on first start.

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend runs on `http://localhost:5173` and proxies `/api` requests to the backend.

### 3. (Optional) Enable LLM Feedback

Set your OpenAI-compatible API key in `backend/.env`:

```env
LLM_API_KEY=sk-your-key-here
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4o-mini
```

If no key is set, the platform uses the **rule-based evaluator** automatically — the app still works end-to-end.

## 🧪 Running Tests

```bash
cd backend
pytest tests/ -v
```

20 tests cover: evaluator scoring logic, LLM response parsing (including malformed/edge cases), API routes (404s, validation, history ordering, feedback structure), and failure paths.

## 🎨 Design & Colors

- **Font**: Jost (Medium weight)
- **Palette**:
  - `#2A7C13` — primary dark green
  - `#76C457` — accent light green
  - `#FFF8CF` — cream background
  - `#FBE6C2` — beige cards

## 📋 API Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/health` | Health check + LLM status |
| `GET` | `/api/problems` | List all problems |
| `GET` | `/api/problems/{id}` | Get problem details |
| `POST` | `/api/problems/{id}/attempts` | Submit a solution → returns feedback |
| `GET` | `/api/problems/{id}/attempts` | Attempt history for a problem |
| `GET` | `/api/attempts/{id}` | Get a single attempt with feedback |

## ⚠️ Limitations

- Evaluation is synchronous (blocking). For high load or slow LLMs, move evaluation to a background worker and poll the attempt status.
- No user authentication — attempts are not tied to users in this MVP.
- The rule-based evaluator uses simple heuristics; it's transparent but not as nuanced as an LLM.
- No diagram-based submissions yet (the abstraction supports adding one).

## 📄 Additional Docs

- [AI_USAGE.md](./AI_USAGE.md) — meaningful AI-assisted decisions during development.
