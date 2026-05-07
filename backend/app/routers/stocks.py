from fastapi import APIRouter

router = APIRouter(prefix="/api/stocks", tags=["stocks"])


@router.get("/{ticker}/news")
async def get_stock_news(ticker: str):
    """특정 종목 뉴스 (더미)."""
    sym = ticker.upper()
    return {
        "ticker": sym,
        "items": [
            {
                "id": 1,
                "title": f"[더미] {sym} 분기 실적 시장 기대치 부합",
                "source": "DummyWire",
                "url": "https://example.com/news/1",
                "published_at": "2026-05-02T09:00:00Z",
                "snippet": "실제 데이터 연동 전 플레이스홀더 본문입니다.",
            },
            {
                "id": 2,
                "title": f"[더미] {sym} 업종 동향 리포트",
                "source": "DemoResearch",
                "url": "https://example.com/news/2",
                "published_at": "2026-05-01T15:30:00Z",
                "snippet": "추후 Serper·크롤링 등으로 교체 예정입니다.",
            },
        ],
    }
