"""외국어 텍스트를 한국어로 번역 (무료 Google Translate 경유)."""

import asyncio
import os
import re
from functools import lru_cache

_KOREAN_RE = re.compile(r"[\uac00-\ud7a3]")
_LATIN_RE = re.compile(r"[A-Za-z]{3,}")


def translation_enabled() -> bool:
    return os.getenv("ENABLE_TRANSLATION", "true").lower() in ("1", "true", "yes")


def needs_korean_translation(text: str) -> bool:
    if not text or not text.strip():
        return False
    if _KOREAN_RE.search(text):
        return False
    return bool(_LATIN_RE.search(text))


@lru_cache(maxsize=512)
def _translate_sync(text: str) -> str:
    from deep_translator import GoogleTranslator

    chunk = text.strip()[:4500]
    if not chunk:
        return text
    return GoogleTranslator(source="auto", target="ko").translate(chunk)


async def translate_to_korean(text: str) -> str:
    if not translation_enabled() or not needs_korean_translation(text):
        return text
    try:
        return await asyncio.to_thread(_translate_sync, text)
    except Exception:
        return text


async def bilingual(text: str) -> tuple[str, str | None]:
    """(표시용 한글, 원문 또는 None)"""
    if not text:
        return "", None
    if not needs_korean_translation(text):
        return text, None
    translated = await translate_to_korean(text)
    if translated == text:
        return text, None
    return translated, text
