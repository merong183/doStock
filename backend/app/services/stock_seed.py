from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.data.default_stocks import DEFAULT_STOCKS
from app.models.stock import Stock


async def ensure_stocks_seeded(session: AsyncSession) -> int:
    """종목이 없으면 기본 목록을 삽입. 추가된 개수 반환."""
    result = await session.execute(select(Stock.ticker))
    existing = {row[0] for row in result.all()}
    added = 0
    for item in DEFAULT_STOCKS:
        if item["ticker"] in existing:
            continue
        session.add(
            Stock(
                ticker=item["ticker"],
                name=item["name"],
                market=item["market"],
            )
        )
        added += 1
    if added:
        await session.commit()
    return added
