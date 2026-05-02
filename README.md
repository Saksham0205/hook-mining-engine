# Hook Mining Engine

## Setup

From the `hook-mining-engine` folder:

```bash
cd backend && pip install -r requirements.txt
```

```bash
cp ../.env.example .env && add your GROQ_API_KEY
```

```bash
cd ../frontend && npm install
```

`SQLAlchemy` is pinned to `2.0.49` (instead of `2.0.30`) so installs work on newer Python versions; behavior is unchanged for this app.

## Run

Terminal 1:

```bash
cd hook-mining-engine/backend && uvicorn main:app --reload --port 8000
```

Terminal 2:

```bash
cd hook-mining-engine/frontend && npm run dev
```

Open http://localhost:5173
