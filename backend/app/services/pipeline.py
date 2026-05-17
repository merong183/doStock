from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.services import ai_analyzer, news_fetcher, stock_seed


async def run_daily_pipeline() -> dict:
    """뉴스 수집 → AI 추천 생성 일일 파이프라인."""
    from app.services.ai_analyzer import _ai_provider
    from app.services.news_fetcher import _news_provider

    summary: dict = {
        "ok": True,
        "mode": {
            "news": _news_provider(),
            "ai": _ai_provider(),
        },
        "stocks_seeded": 0,
        "news": {},
        "recommendations": {},
        "errors": [],
    }

    async with AsyncSessionLocal() as session:
        try:
            summary["stocks_seeded"] = await stock_seed.ensure_stocks_seeded(session)
        except Exception as e:
            summary["errors"].append(f"seed: {e}")

        try:
            summary["news"] = await news_fetcher.fetch_news_for_all_stocks(session)
            summary["errors"].extend(summary["news"].get("errors", []))
        except Exception as e:
            summary["ok"] = False
            summary["errors"].append(f"news: {e}")

        try:
            summary["recommendations"] = await ai_analyzer.generate_recommendations_for_all_stocks(
                session
            )
            summary["errors"].extend(summary["recommendations"].get("errors", []))
        except Exception as e:
            summary["ok"] = False
            summary["errors"].append(f"recommendations: {e}")

    if summary["errors"]:
        summary["ok"] = False

    return summary
