# Intelligent Entrepreneurs Support (stock-items)

AI-powered smart financial guidance system for entrepreneurs. See `INITIAL.md`
for the full product brief.

## Quick start

```bash
# 1. Start Postgres + backend via Docker
docker-compose up --build

# 2. Frontend
cd frontend
cp .env.example .env
npm install
npm run dev
```

- Backend: http://localhost:8000 (docs at `/docs`)
- Frontend: http://localhost:5173

## Local dev without Docker

```bash
cd backend
cp .env.example .env
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Layout

```
stock-items/
├── backend/      FastAPI + SQLAlchemy + AI forecasting (Phase 2)
├── frontend/     React + TS + Vite + Tailwind + Recharts
├── docker-compose.yml
└── INITIAL.md    Product brief
```

## Deploy (free)

**Stack:** Vercel (frontend) + Render (backend, Docker) + Neon (Postgres).

1. **Neon** — https://neon.tech → new project → copy the connection string.
2. **Render** — New → Blueprint → point at this repo. `render.yaml` is included.
   Set env vars in the dashboard:
   - `DATABASE_URL` — Neon connection string (the `postgres://` prefix auto-normalizes)
   - `GEMINI_API_KEY` — free key from https://aistudio.google.com/app/apikey
   - `CORS_ORIGINS` — `https://your-app.vercel.app` (comma-separated if multiple)
3. **Vercel** — Import repo → root directory `frontend/` → env var
   `VITE_API_URL=https://your-render-service.onrender.com`.

Note: Render's free tier sleeps after 15 min of inactivity; first request after
idle takes ~30s to wake.

## Phase status

- [x] Phase 1 — auth, models, CRUD, dashboard, docker
- [x] Phase 2 — AI forecasting, risk alerts, recommendations, trends, simulation, chatbot, expense auto-categorization
- [ ] Phase 3 — notifications, Google OAuth, advanced scenario UI

## AI endpoints

| Endpoint | Purpose |
|---|---|
| `GET /api/ai/alerts` | Predictive risk alerts (cash flow, profit decline, overspend, stockout) |
| `GET /api/ai/recommendations` | Actionable suggestions |
| `GET /api/ai/forecast/stock` | Per-product demand + stockout ETA |
| `GET /api/ai/forecast/profit` | 30-day profit projection |
| `GET /api/ai/trends` | MoM revenue growth, top products, weekday seasonality |
| `POST /api/ai/simulate` | Scenario "what if stock +N%?" |
| `POST /api/ai/chat` | Gemini-powered advisor (needs free `GEMINI_API_KEY` from https://aistudio.google.com/app/apikey) |
