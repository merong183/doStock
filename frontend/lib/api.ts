const API_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function fetchJson<T>(path: string): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error(`API ${path} failed: ${res.status}`);
  }
  return res.json() as Promise<T>;
}

export type TodayRecommendationItem = {
  ticker: string;
  name: string;
  market: string;
  confidence: number;
  risk_level: string;
  reason: string;
};

export type TodayRecommendationsResponse = {
  date: string;
  items: TodayRecommendationItem[];
};

export type HistoryItem = {
  id: number;
  ticker: string;
  date: string;
  confidence: number;
  risk_level: string;
  reason: string;
};

export type HistoryResponse = {
  items: HistoryItem[];
};

export type NewsItem = {
  id: number;
  title: string;
  source: string;
  url: string;
  published_at: string;
  snippet: string;
};

export type StockNewsResponse = {
  ticker: string;
  items: NewsItem[];
};

export function getTodayRecommendations() {
  return fetchJson<TodayRecommendationsResponse>(
    "/api/recommendations/today",
  );
}

export function getRecommendationHistory() {
  return fetchJson<HistoryResponse>("/api/recommendations/history");
}

export function getStockNews(ticker: string) {
  const encoded = encodeURIComponent(ticker);
  return fetchJson<StockNewsResponse>(`/api/stocks/${encoded}/news`);
}

export function triggerSchedulerRun() {
  return fetch(`${API_URL}/api/scheduler/run`, { method: "POST" }).then(
    async (res) => {
      if (!res.ok) throw new Error(`Scheduler trigger failed: ${res.status}`);
      return res.json() as Promise<{ ok: boolean; message: string }>;
    },
  );
}
