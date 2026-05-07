"""주기 작업(APScheduler) 자리 — 앱 기동 시 자동 실행하지 않음."""

from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()


def setup_scheduler() -> None:
    """추후 일 배치 등록 시 사용."""
    pass
