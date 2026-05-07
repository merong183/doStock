from datetime import date

from fastapi import APIRouter

router = APIRouter(prefix="/api/recommendations", tags=["recommendations"])


@router.get("/today")
async def get_today_recommendations():
    """오늘 추천 종목 (더미)."""
    return {
        "date": date.today().isoformat(),
        "items": [
            {
                "ticker": "005930",
                "name": "삼성전자",
                "market": "KR",
                "confidence": 0.82,
                "risk_level": "mid",
                "reason": "더미: 단기 모멘텀과 반도체 업황 개선 기대.",
            },
            {
                "ticker": "AAPL",
                "name": "Apple Inc.",
                "market": "US",
                "confidence": 0.71,
                "risk_level": "low",
                "reason": "더미: 서비스 매출 성장 및 현금흐름 안정.",
            },
        ],
    }


@router.get("/history")
async def get_recommendation_history():
    """추천 히스토리 (더미)."""
    return {
        "items": [
            {
                "id": 1,
                "ticker": "005930",
                "date": "2026-05-01",
                "confidence": 0.79,
                "risk_level": "mid",
                "reason": "더미 과거 추천 근거.",
            },
            {
                "id": 2,
                "ticker": "NVDA",
                "date": "2026-05-02",
                "confidence": 0.68,
                "risk_level": "high",
                "reason": "더미 변동성 높은 성장주 관점.",
            },
        ]
    }
