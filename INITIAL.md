# INITIAL.md — Intelligent Entrepreneurs Support

> AI-Powered Smart Financial Guidance System for Entrepreneurs

---

## Product Vision

A virtual financial decision assistant that helps new entrepreneurs make smarter
financial and operational decisions. Beyond reporting historical data, the
platform predicts future risks, analyzes trends, forecasts stock, and recommends
actions.

## Target User

Early-stage entrepreneurs and small business founders who run a product business
(inventory + sales + expenses) and lack a dedicated finance/analytics team.

## Problem

Existing tools report the past (income, expenses, sales) but do not:
- Surface real-time financial visibility
- Alert before risks occur
- Recommend next actions
- Forecast inventory / stock trends

## Core Features (from spec)

### AI / Intelligence
1. **Predictive Financial Risk Alerts** — cash flow shortage, overspending,
   profit decline, debt warnings. Example: "Cash reserves may drop below safe
   levels in 18 days."
2. **Intelligent Recommendation Engine** — reduce expenses, stock high-demand
   items, reorder low inventory, pricing suggestions.
3. **Trend Analysis** — sales growth, seasonal demand, customer buying behavior,
   product performance.
4. **Stock Inventory Prediction** — demand forecasting, reorder point, turnover
   analysis, fast/slow movers, over/understock risk.
5. **Smart Inventory Optimization** — reorder timing, min stock levels, warehouse
   balance.
6. **Business Health Dashboard** — revenue, expenses, inventory status, profit
   margins, risk indicators.
7. **Automated Profit Forecasting** — monthly profit prediction from historical
   trends.
8. **AI Expense Categorization** — auto-classify into operations, marketing,
   inventory, salaries.
9. **Scenario Simulation** — "what happens if I increase stock by 20%?"
10. **Personalized Business Advisor Chatbot** — conversational answers grounded
    in the user's data.

## Tech Stack (per CLAUDE.md)

- **Backend:** FastAPI + Python 3.11+, SQLAlchemy, Alembic
- **Frontend:** React + TypeScript + Vite, Chakra UI or Tailwind + Framer Motion
- **Database:** PostgreSQL
- **Auth:** JWT + Google OAuth
- **AI/ML:** scikit-learn, pandas, Prophet/statsmodels for time-series;
  LLM (Claude API) for chatbot and recommendation narration
- **Infra:** Docker Compose for local dev

## Data Model (initial)

- `users` — entrepreneur accounts
- `businesses` — a user may own one or more businesses
- `products` — SKU, name, cost, price, category, reorder_point, min_stock
- `inventory_movements` — stock in/out with timestamp, reason
- `sales` — line items linked to products, quantity, unit_price, date, customer
- `expenses` — amount, category, date, description
- `forecasts` — cached model outputs (demand, profit, risk)
- `alerts` — generated risk alerts with severity, acknowledged state
- `recommendations` — generated action suggestions

## Phased Delivery

**Phase 1 — Foundation**
- Auth (JWT + Google OAuth)
- CRUD for products, sales, expenses, inventory movements
- Business Health Dashboard (descriptive analytics only)
- Docker Compose dev environment

**Phase 2 — AI Intelligence**
- Stock demand forecasting + reorder point prediction
- Cash flow / profit forecasting
- Risk alert engine (rule + model hybrid)
- Trend analysis endpoints
- Recommendation engine
- Expense auto-categorization

**Phase 3 — Advanced**
- Scenario simulation
- Advisor chatbot (Claude API, RAG over user's own data)
- Notifications (email / push)

## Non-Goals (v1)

- Multi-branch inventory (future scope)
- Mobile apps (future scope)
- Accounting software integrations (future scope)
- Voice assistant (future scope)

## Success Metrics

- Time from signup to first dashboard insight < 10 min
- Forecast MAPE < 20% for products with ≥ 90 days of sales history
- Alerts fire ≥ 7 days before a cash-flow breach in backtests

## Validation Gates

```bash
ruff check backend/ && pytest                    # backend
cd frontend && npm run lint && npm run type-check && npm test
docker-compose build
```
