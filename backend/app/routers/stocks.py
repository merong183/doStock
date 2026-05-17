from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.news import News
from app.services.translator import bilingual

router = APIRouter(prefix="/api/stocks", tags=["stocks"])


@router.get("/{ticker}/news")
async def get_stock_news(ticker: str, db: AsyncSession = Depends(get_db)):
    sym = ticker.upper()
    result = await db.execute(
        select(News)
        .where(News.ticker == sym)
        .order_by(News.fetched_at.desc())
        .limit(30)
    )
    rows = list(result.scalars().all())

    items = []
    for row in rows:
        snippet_raw = (row.content or "")[:500]
        title_ko, title_orig = await bilingual(row.title)
        snippet_ko, snippet_orig = await bilingual(snippet_raw) if snippet_raw else ("", None)

        items.append(
            {
                "id": row.id,
                "title": row.title,
                "title_ko": title_ko,
                "title_original": title_orig,
                "source": row.source or "",
                "url": row.url or "",
                "published_at": (
                    row.published_at.isoformat()
                    if row.published_at
                    else row.fetched_at.isoformat()
                ),
                "snippet": snippet_raw,
                "snippet_ko": snippet_ko,
                "snippet_original": snippet_orig,
            }
        )

    return {"ticker": sym, "items": items}
