"""Advisor chatbot — grounds Gemini responses in the user's business data.

Uses Google Gemini's free API tier. Get a free key at:
    https://aistudio.google.com/app/apikey

Set GEMINI_API_KEY in backend/.env. If unset, the chatbot returns the raw
snapshot so the UI still works offline.
"""
from __future__ import annotations

import json

import httpx
from sqlalchemy.orm import Session

from app.ai.recommendations import generate_recommendations
from app.ai.risk import generate_risk_signals
from app.ai.trends import revenue_growth_pct, top_products
from app.config import settings
from app.services.dashboard import build_dashboard


GEMINI_MODEL = "gemini-1.5-flash-latest"
GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    f"{GEMINI_MODEL}:generateContent"
)

SYSTEM_PROMPT = (
    "You are an AI business advisor for an entrepreneur. Answer briefly and "
    "concretely, using ONLY the data in the provided business context. If the "
    "context does not contain enough information, say so. Prefer specific "
    "numbers over generalities."
)


def _context_snapshot(db: Session, business_id: int) -> dict:
    dash = build_dashboard(db, business_id)
    return {
        "revenue_30d": dash.revenue_30d,
        "expenses_30d": dash.expenses_30d,
        "profit_30d": dash.profit_30d,
        "margin_pct": dash.profit_margin_pct,
        "inventory_value": dash.inventory_value,
        "low_stock_count": dash.low_stock_count,
        "revenue_growth_mom_pct": revenue_growth_pct(db, business_id),
        "top_products_30d": top_products(db, business_id, limit=5),
        "open_risks": [s.message for s in generate_risk_signals(db, business_id)],
        "recommendations": [
            {"title": r.title, "rationale": r.rationale, "action": r.action}
            for r in generate_recommendations(db, business_id)
        ],
    }


def ask(db: Session, business_id: int, question: str) -> str:
    snapshot = _context_snapshot(db, business_id)

    if not settings.GEMINI_API_KEY:
        return (
            "Chatbot disabled: no GEMINI_API_KEY configured. Get a free key at "
            "https://aistudio.google.com/app/apikey and set it in backend/.env. "
            f"Current snapshot: {json.dumps(snapshot, default=str)}"
        )

    user_prompt = (
        f"Business context (JSON):\n{json.dumps(snapshot, default=str)}\n\n"
        f"Question: {question}"
    )

    payload = {
        "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
        "generationConfig": {"temperature": 0.2, "maxOutputTokens": 600},
    }

    try:
        response = httpx.post(
            GEMINI_URL,
            params={"key": settings.GEMINI_API_KEY},
            json=payload,
            timeout=30.0,
        )
        response.raise_for_status()
        data = response.json()
        candidates = data.get("candidates", [])
        if not candidates:
            return "No response from model."
        parts = candidates[0].get("content", {}).get("parts", [])
        text = "".join(p.get("text", "") for p in parts).strip()
        return text or "No response."
    except httpx.HTTPError as exc:
        return f"Chatbot error: {exc}"
