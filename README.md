# Pixii Hook Mining Engine

Full-stack app to **discover viral-style hooks from the web**, **manage a hook library**, and **generate Pixii-style posts** with Groq. The UI is a React (Vite) SPA; the API is FastAPI with automatic OpenAPI docs.

## Stack

| Layer | Tech |
|--------|------|
| API | FastAPI, Uvicorn, SQLAlchemy 2.x (async), Groq SDK |
| DB | SQLite by default (`backend/hook_engine.db`); optional Postgres via `DATABASE_URL` |
| UI | React 18, Vite 5 |

## Prerequisites

- **Python 3.12** (see `.python-version`)
- **Node.js** (current LTS is fine) for the frontend

## Setup

### Backend

From the repository root:

```bash
cd backend
pip install -r requirements.txt
```

Create `backend/.env` (this file is loaded automatically). At minimum:

```env
GROQ_API_KEY=your_groq_api_key
```

Optional:

```env
# Default: SQLite file under backend/
# DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Comma-separated allowlist; default is http://localhost:5173
# CORS_ORIGINS=https://your-frontend.example,http://localhost:5173

# Optional regex for dynamic origins (e.g. preview deployments)
# CORS_ORIGIN_REGEX=https://.*\.vercel\.app
```

Without `GROQ_API_KEY`, AI-backed routes return **503** until you add a key (the app still starts).

`SQLAlchemy` is pinned to **2.0.49** so installs work cleanly on newer Python; behavior for this app matches the previous pin.

### Frontend

```bash
cd frontend
npm install
```

Local dev needs **no** `VITE_*` variables: Vite proxies `/api` to `http://localhost:8000`. See `frontend/.env.example` for production / Vercel notes.

## Run locally

**Terminal 1 — API** (from repo root):

```bash
cd backend
uvicorn main:app --reload --port 8000
```

**Terminal 2 — UI**:

```bash
cd frontend
npm run dev
```

Open [http://localhost:5173](http://localhost:5173). The header shows connectivity and hook count from `GET /api/health`.

Interactive API docs: [http://localhost:8000/docs](http://localhost:8000/docs).

## API overview

| Method | Path | Purpose |
|--------|------|--------|
| GET | `/` | Service metadata and doc links |
| GET | `/api/ping` | Lightweight ping (no DB) |
| GET | `/api/health` | Health + hook count in DB |
| POST | `/api/crawl` | Crawl / ingest |
| GET | `/api/hooks` | List hooks |
| GET | `/api/hooks/stats` | Aggregate stats |
| DELETE | `/api/hooks/{hook_id}` | Remove a hook |
| POST | `/api/generate` | Generate content |

A weekly scheduler runs when `GROQ_API_KEY` is set (see `backend/scheduler.py`).

## Project layout

```
backend/    # FastAPI app (main.py, routers/, models, mining, scraper, …)
frontend/   # Vite + React SPA (Mine / Library / Generate tabs)
```

## Deployment notes

The frontend is set up so **Vercel** can proxy `/api` to a hosted backend (e.g. Render) same-origin, avoiding browser CORS issues. For details see `frontend/vercel.json`, `frontend/src/apiConfig.js`, and comments in `frontend/.env.example`.
