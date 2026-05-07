import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import news, recommendations, stocks

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
    """개발용 수동 트리거 (더미)."""
    return {"ok": True, "message": "스케줄러 파이프라인은 아직 연결되지 않았습니다."}
