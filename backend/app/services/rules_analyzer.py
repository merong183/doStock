"""API 비용 없이 뉴스 키워드로 추천 점수를 계산 (무료 폴백)."""

from app.models.stock import Stock

POSITIVE = (
    "상승",
    "호실적",
    "성장",
    "수주",
    "신고가",
    "급등",
    "흑자",
    "매수",
    "beat",
    "growth",
    "profit",
    "rally",
    "upgrade",
    "surge",
    "record high",
    "outperform",
)

NEGATIVE = (
    "하락",
    "적자",
    "소송",
    "리콜",
    "급락",
    "매도",
    "우려",
    "miss",
    "loss",
    "decline",
    "downgrade",
    "warning",
    "lawsuit",
    "recall",
    "slump",
)

RISK_HIGH = ("급락", "적자", "소송", "리콜", "lawsuit", "recall", "bankruptcy", "부도")


def analyze_with_rules(stock: Stock, snippets: list[str]) -> dict:
    if not snippets:
        return {
            "reason": "최근 뉴스가 없어 분석을 건너뜁니다.",
            "confidence": 0.0,
            "risk_level": "high",
            "recommend": False,
        }

    text = " ".join(snippets).lower()
    pos = sum(1 for w in POSITIVE if w.lower() in text)
    neg = sum(1 for w in NEGATIVE if w.lower() in text)
    score = pos - neg

    if score >= 2:
        sentiment = "긍정"
        recommend = True
        confidence = min(0.85, 0.45 + score * 0.08 + min(len(snippets), 8) * 0.02)
    elif score <= -2:
        sentiment = "부정"
        recommend = False
        confidence = min(0.75, 0.35 + abs(score) * 0.08)
    else:
        sentiment = "중립"
        recommend = score >= 0 and len(snippets) >= 3
        confidence = 0.4 + min(len(snippets), 6) * 0.03

    risk = "mid"
    if any(w.lower() in text for w in RISK_HIGH):
        risk = "high"
    elif sentiment == "긍정" and score >= 3:
        risk = "low"

    sample = snippets[0][:80] + ("…" if len(snippets[0]) > 80 else "")
    reason = (
        f"[무료 키워드 분석] {stock.name}({stock.ticker}) 최근 뉴스 {len(snippets)}건 기준 "
        f"톤은 {sentiment}입니다(긍정 신호 {pos}·부정 신호 {neg}). "
        f"대표 헤드라인: {sample}"
    )

    return {
        "reason": reason,
        "confidence": round(confidence, 2),
        "risk_level": risk,
        "recommend": recommend,
    }
