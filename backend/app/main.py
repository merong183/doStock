import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import news, recommendations, stocks
from app.services.pipeline import run_daily_pipeline

load_dotenv()


def _cors_allow_origins() -> list[str]:
    """로컬 기본값 + CORS_ORIGINS(쉼표 구분) 병합."""
    defaults = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
    extra = os.getenv("CORS_ORIGINS", "")
    merged: list[str] = list(defaults)
    for part in extra.split(","):
        o = part.strip()
        if o and o not in merged:
            merged.append(o)
    return merged


@asynccontextmanager
async def lifespan(_app: FastAPI):
    yield


app = FastAPI(title="doStock API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_allow_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(recommendations.router)
app.include_router(stocks.router)
app.include_router(news.router)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/api/scheduler/run")
async def run_scheduler_manual():
    """개발용 수동 트리거: 뉴스 수집 → AI 추천 생성."""
    summary = await run_daily_pipeline()
    message = "파이프라인 완료"
    if summary.get("errors"):
        message = f"파이프라인 완료 (경고 {len(summary['errors'])}건)"
    return {"message": message, **summary}
