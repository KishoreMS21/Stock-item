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
