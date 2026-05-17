"""기본 추적 종목 (시드용)."""

DEFAULT_STOCKS: list[dict[str, str]] = [
    {"ticker": "005930", "name": "삼성전자", "market": "KR"},
    {"ticker": "000660", "name": "SK하이닉스", "market": "KR"},
    {"ticker": "035420", "name": "NAVER", "market": "KR"},
    {"ticker": "035720", "name": "카카오", "market": "KR"},
    {"ticker": "AAPL", "name": "Apple Inc.", "market": "US"},
    {"ticker": "MSFT", "name": "Microsoft", "market": "US"},
    {"ticker": "NVDA", "name": "NVIDIA", "market": "US"},
    {"ticker": "GOOGL", "name": "Alphabet", "market": "US"},
    {"ticker": "TSLA", "name": "Tesla", "market": "US"},
]
