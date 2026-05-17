import asyncio
import os
from urllib.parse import quote_plus

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.news import News
from app.models.stock import Stock

SERPER_NEWS_URL = "https://google.serper.dev/news"
NEWS_PER_TICKER = 8
GOOGLE_NEWS_RSS = "https://news.google.com/rss/search?q={query}&hl=ko&gl=KR&ceid=KR:ko"


def _serper_api_key() -> str | None:
    key = os.getenv("SERPER_API_KEY", "").strip()
    return key or None


def _news_provider() -> str:
    """auto | yfinance | serper | google_rss"""
    explicit = os.getenv("NEWS_PROVIDER", "auto").strip().lower()
    if explicit != "auto":
        return explicit
    if _serper_api_key():
        return "serper"
    try:
        import yfinance  # noqa: F401
        return "yfinance"
    except ImportError:
        return "google_rss"


def _yfinance_symbol(stock: Stock) -> str:
    if stock.market == "US":
        return stock.ticker
    return f"{stock.ticker}.KS"


def _search_query(stock: Stock) -> str:
    if stock.market == "KR":
        return f"{stock.name} {stock.ticker} 주식"
    return f"{stock.name} {stock.ticker} stock"


def _normalize_yfinance_item(item: dict) -> dict:
    content = item.get("content") or item
    title = (content.get("title") or "").strip()
    summary = (content.get("summary") or content.get("description") or "").strip()
    url = ""
    for key in ("canonicalUrl", "clickThroughUrl"):
        block = content.get(key)
        if isinstance(block, dict) and block.get("url"):
            url = block["url"]
            break
    provider = ""
    prov = content.get("provider")
    if isinstance(prov, dict):
        provider = (prov.get("displayName") or "").strip()
    return {
        "title": title,
        "snippet": summary,
        "link": url,
        "source": provider,
    }


def _fetch_from_yfinance_sync(symbol: str) -> list[dict]:
    try:
        import yfinance as yf
    except ImportError as e:
        raise RuntimeError(
            "yfinance가 설치되지 않았습니다. pip install yfinance 또는 NEWS_PROVIDER=google_rss"
        ) from e
    raw = yf.Ticker(symbol).news or []
    items: list[dict] = []
    for row in raw[:NEWS_PER_TICKER]:
        normalized = _normalize_yfinance_item(row)
        if normalized["title"]:
            items.append(normalized)
    return items


async def _fetch_from_yfinance(stock: Stock) -> list[dict]:
    symbol = _yfinance_symbol(stock)
    return await asyncio.to_thread(_fetch_from_yfinance_sync, symbol)


async def _fetch_from_serper(query: str) -> list[dict]:
    api_key = _serper_api_key()
    if not api_key:
        raise ValueError("SERPER_API_KEY가 설정되지 않았습니다.")

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            SERPER_NEWS_URL,
            headers={"X-API-KEY": api_key, "Content-Type": "application/json"},
            json={"q": query, "num": NEWS_PER_TICKER},
        )
        response.raise_for_status()
        data = response.json()

    items: list[dict] = []
    for row in data.get("news") or []:
        items.append(
            {
                "title": (row.get("title") or "").strip(),
                "snippet": (row.get("snippet") or "").strip(),
                "link": (row.get("link") or "").strip(),
                "source": (row.get("source") or "").strip(),
            }
        )
    return items


async def _fetch_from_google_rss(query: str) -> list[dict]:
    url = GOOGLE_NEWS_RSS.format(query=quote_plus(query))
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        response = await client.get(url)
        response.raise_for_status()
        xml = response.text

    items: list[dict] = []
    parts = xml.split("<item>")
    for block in parts[1 : NEWS_PER_TICKER + 1]:
        title = _rss_tag(block, "title")
        link = _rss_tag(block, "link")
        source = _rss_tag(block, "source")
        pub = _rss_tag(block, "pubDate")
        snippet = f"게시: {pub}" if pub else ""
        if title:
            items.append(
                {
                    "title": title,
                    "snippet": snippet,
                    "link": link,
                    "source": source,
                }
            )
    return items


def _rss_tag(block: str, tag: str) -> str:
    open_tag = f"<{tag}"
    close_tag = f"</{tag}>"
    start = block.find(open_tag)
    if start == -1:
        return ""
    start = block.find(">", start)
    if start == -1:
        return ""
    end = block.find(close_tag, start)
    if end == -1:
        return ""
    text = block[start + 1 : end].strip()
    if text.startswith("<![CDATA[") and text.endswith("]]>"):
        text = text[9:-3].strip()
    return text


async def _fetch_news_items(stock: Stock) -> tuple[str, list[dict]]:
    provider = _news_provider()
    query = _search_query(stock)

    if provider == "serper":
        return provider, await _fetch_from_serper(query)
    if provider == "google_rss":
        return provider, await _fetch_from_google_rss(query)
    if provider == "yfinance":
        return provider, await _fetch_from_yfinance(stock)

    raise ValueError(f"지원하지 않는 NEWS_PROVIDER: {provider}")


async def _url_exists(session: AsyncSession, url: str) -> bool:
    if not url:
        return False
    result = await session.execute(select(News.id).where(News.url == url).limit(1))
    return result.scalar_one_or_none() is not None


async def fetch_and_store_news_for_stock(
    session: AsyncSession,
    stock: Stock,
) -> tuple[int, int]:
    """뉴스 검색 후 DB 저장. (조회 수, 신규 삽입 수) 반환."""
    _, items = await _fetch_news_items(stock)
    inserted = 0

    for item in items:
        url = (item.get("link") or "").strip()
        title = (item.get("title") or "").strip()
        if not title:
            continue
        if url and await _url_exists(session, url):
            continue

        session.add(
            News(
                ticker=stock.ticker,
                title=title[:512],
                content=(item.get("snippet") or "")[:8000] or None,
                source=(item.get("source") or "")[:255] or None,
                url=url[:1024] if url else None,
                published_at=None,
            )
        )
        inserted += 1

    if inserted:
        await session.commit()

    return len(items), inserted


async def fetch_news_for_all_stocks(session: AsyncSession) -> dict:
    provider = _news_provider()
    result = await session.execute(select(Stock).order_by(Stock.ticker))
    stocks = list(result.scalars().all())

    fetched = 0
    inserted = 0
    errors: list[str] = []
    for stock in stocks:
        try:
            n_fetched, n_inserted = await fetch_and_store_news_for_stock(session, stock)
            fetched += n_fetched
            inserted += n_inserted
        except Exception as e:
            errors.append(f"{stock.ticker}: {e}")

    return {
        "provider": provider,
        "fetched": fetched,
        "inserted": inserted,
        "stocks": len(stocks),
        "errors": errors,
    }
