from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.news import News
from app.models.recommendation import Recommendation
from app.models.stock import Stock
from app.services.translator import bilingual

router = APIRouter(prefix="/api/recommendations", tags=["recommendations"])


@router.get("/today")
async def get_today_recommendations(db: AsyncSession = Depends(get_db)):
    today = date.today()
    result = await db.execute(
        select(Recommendation, Stock)
        .join(Stock, Stock.ticker == Recommendation.ticker)
        .where(Recommendation.date == today)
        .order_by(Recommendation.confidence.desc().nullslast())
    )
    rows = result.all()
    tickers = [rec.ticker for rec, _ in rows]
    latest_news: dict[str, dict[str, str]] = {}
    if tickers:
        news_result = await db.execute(
            select(News)
            .where(News.ticker.in_(tickers))
            .order_by(News.ticker, News.fetched_at.desc())
        )
        for article in news_result.scalars().all():
            if article.ticker not in latest_news:
                latest_news[article.ticker] = {
                    "title": article.title,
                    "url": article.url or "",
                }

    items = []
    for rec, stock in rows:
        news = latest_news.get(rec.ticker, {})
        reason_ko, reason_orig = await bilingual(rec.reason or "")
        news_title = news.get("title", "")
        news_title_ko, news_title_orig = (
            await bilingual(news_title) if news_title else ("", None)
        )

        items.append(
            {
                "ticker": rec.ticker,
                "name": stock.name,
                "market": stock.market,
                "confidence": rec.confidence or 0.0,
                "risk_level": rec.risk_level or "mid",
                "reason": reason_ko,
                "reason_original": reason_orig,
                "latest_news_title": news_title_ko or news_title,
                "latest_news_title_original": news_title_orig,
                "latest_news_url": news.get("url", ""),
            }
        )

    return {"date": today.isoformat(), "items": items}


@router.get("/history")
async def get_recommendation_history(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Recommendation)
        .order_by(Recommendation.date.desc(), Recommendation.confidence.desc().nullslast())
        .limit(100)
    )
    rows = list(result.scalars().all())

    items = []
    for row in rows:
        reason_ko, reason_orig = await bilingual(row.reason or "")
        items.append(
            {
                "id": row.id,
                "ticker": row.ticker,
                "date": row.date.isoformat(),
                "confidence": row.confidence or 0.0,
                "risk_level": row.risk_level or "mid",
                "reason": reason_ko,
                "reason_original": reason_orig,
            }
        )

    return {"items": items}
