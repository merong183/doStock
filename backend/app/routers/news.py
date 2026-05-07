from fastapi import APIRouter

router = APIRouter(prefix="/api/news", tags=["news"])

# 향후: 종목 무관 글로벌 뉴스 피드 등
