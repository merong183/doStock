import json
import os
import re
from datetime import date, datetime, timedelta, timezone

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.news import News
from app.models.recommendation import Recommendation
from app.models.stock import Stock
from app.services.rules_analyzer import analyze_with_rules

RECENT_NEWS_DAYS = 7
MAX_SNIPPETS = 12


def _anthropic_api_key() -> str | None:
    key = os.getenv("ANTHROPIC_API_KEY", "").strip()
    return key or None


def _ai_provider() -> str:
    """auto | rules | anthropic | ollama"""
    explicit = os.getenv("AI_PROVIDER", "auto").strip().lower()
    if explicit != "auto":
        return explicit
    if _anthropic_api_key():
        return "anthropic"
    return "rules"


def _anthropic_model() -> str:
    return os.getenv("ANTHROPIC_MODEL", "claude-3-5-haiku-latest")


def _ollama_base_url() -> str:
    return os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")


def _ollama_model() -> str:
    return os.getenv("OLLAMA_MODEL", "llama3.2")


def _parse_json_response(text: str) -> dict:
    cleaned = text.strip()
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", cleaned)
    if fence:
        cleaned = fence.group(1).strip()
    return json.loads(cleaned)


def _normalize_analysis(data: dict) -> dict:
    confidence = float(data.get("confidence", 0))
    confidence = max(0.0, min(1.0, confidence))

    risk = str(data.get("risk_level", "mid")).lower()
    if risk not in ("low", "mid", "high"):
        risk = "mid"

    return {
        "reason": str(data.get("reason", "")).strip() or "분석 결과 없음",
        "confidence": confidence,
        "risk_level": risk,
        "recommend": bool(data.get("recommend", confidence >= 0.5)),
    }


async def _analyze_anthropic(stock: Stock, snippets: list[str]) -> dict:
    api_key = _anthropic_api_key()
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY가 설정되지 않았습니다.")

    from anthropic import AsyncAnthropic

    client = AsyncAnthropic(api_key=api_key)
    news_block = "\n".join(f"- {s}" for s in snippets[:MAX_SNIPPETS])

    prompt = f"""You are a stock analyst. Based ONLY on the news snippets below for {stock.name} ({stock.ticker}, market {stock.market}), output a JSON object with:
- "reason": string, 2-4 sentences in Korean explaining the investment view
- "confidence": float 0.0-1.0 (how strong the signal is)
- "risk_level": one of "low", "mid", "high"
- "recommend": boolean, true if worth highlighting today

News:
{news_block}

Respond with ONLY valid JSON, no markdown."""

    message = await client.messages.create(
        model=_anthropic_model(),
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = message.content[0].text if message.content else "{}"
    return _normalize_analysis(_parse_json_response(raw))


async def _analyze_ollama(stock: Stock, snippets: list[str]) -> dict:
    news_block = "\n".join(f"- {s}" for s in snippets[:MAX_SNIPPETS])
    prompt = f"""Analyze {stock.name} ({stock.ticker}) news and reply ONLY with JSON:
{{"reason":"...", "confidence":0.0-1.0, "risk_level":"low|mid|high", "recommend":true/false}}

News:
{news_block}"""

    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            f"{_ollama_base_url()}/api/chat",
            json={
                "model": _ollama_model(),
                "messages": [{"role": "user", "content": prompt}],
                "stream": False,
            },
        )
        response.raise_for_status()
        raw = response.json()["message"]["content"]

    return _normalize_analysis(_parse_json_response(raw))


async def analyze_for_recommendation(
    stock: Stock,
    snippets: list[str],
) -> dict:
    if not snippets:
        return {
            "reason": "최근 뉴스가 없어 분석을 건너뜁니다.",
            "confidence": 0.0,
            "risk_level": "high",
            "recommend": False,
        }

    provider = _ai_provider()
    if provider == "anthropic":
        try:
            return await _analyze_anthropic(stock, snippets)
        except Exception:
            return analyze_with_rules(stock, snippets)
    if provider == "ollama":
        try:
            return await _analyze_ollama(stock, snippets)
        except Exception:
            return analyze_with_rules(stock, snippets)
    return analyze_with_rules(stock, snippets)


async def _recent_news_snippets(
    session: AsyncSession,
    ticker: str,
) -> list[str]:
    since = datetime.now(timezone.utc) - timedelta(days=RECENT_NEWS_DAYS)
    result = await session.execute(
        select(News)
        .where(News.ticker == ticker, News.fetched_at >= since)
        .order_by(News.fetched_at.desc())
        .limit(MAX_SNIPPETS)
    )
    rows = list(result.scalars().all())
    snippets: list[str] = []
    for row in rows:
        text = row.title
        if row.content:
            text = f"{row.title}: {row.content[:300]}"
        snippets.append(text)
    return snippets


async def _upsert_recommendation(
    session: AsyncSession,
    stock: Stock,
    today: date,
    analysis: dict,
) -> bool:
    result = await session.execute(
        select(Recommendation).where(
            Recommendation.ticker == stock.ticker,
            Recommendation.date == today,
        )
    )
    row = result.scalar_one_or_none()

    if not analysis.get("recommend") and analysis.get("confidence", 0) < 0.4:
        if row:
            await session.delete(row)
            await session.commit()
        return False

    if row:
        row.reason = analysis["reason"]
        row.confidence = analysis["confidence"]
        row.risk_level = analysis["risk_level"]
    else:
        session.add(
            Recommendation(
                ticker=stock.ticker,
                date=today,
                reason=analysis["reason"],
                confidence=analysis["confidence"],
                risk_level=analysis["risk_level"],
            )
        )

    await session.commit()
    return True


async def generate_recommendations_for_all_stocks(session: AsyncSession) -> dict:
    today = date.today()
    provider = _ai_provider()
    result = await session.execute(select(Stock).order_by(Stock.ticker))
    stocks = list(result.scalars().all())

    analyzed = 0
    saved = 0
    errors: list[str] = []
    for stock in stocks:
        try:
            snippets = await _recent_news_snippets(session, stock.ticker)
            if not snippets:
                continue
            analysis = await analyze_for_recommendation(stock, snippets)
            analyzed += 1
            if await _upsert_recommendation(session, stock, today, analysis):
                saved += 1
        except Exception as e:
            errors.append(f"{stock.ticker}: {e}")

    return {
        "provider": provider,
        "analyzed": analyzed,
        "saved": saved,
        "stocks": len(stocks),
        "errors": errors,
    }
