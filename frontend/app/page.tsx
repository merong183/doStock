import Link from "next/link";
import { getTodayRecommendations } from "@/lib/api";

function riskBadgeClass(level: string) {
  switch (level) {
    case "low":
      return "bg-emerald-500/15 text-emerald-700 dark:text-emerald-300";
    case "high":
      return "bg-rose-500/15 text-rose-700 dark:text-rose-300";
    default:
      return "bg-amber-500/15 text-amber-800 dark:text-amber-200";
  }
}

export default async function HomePage() {
  let data;
  let error: string | null = null;
  try {
    data = await getTodayRecommendations();
  } catch (e) {
    error = e instanceof Error ? e.message : "데이터를 불러오지 못했습니다.";
    data = { date: "", items: [] };
  }

  return (
    <div className="mx-auto flex min-h-screen max-w-4xl flex-col gap-8 px-4 py-10 sm:px-6">
      <header className="flex flex-col gap-2 border-b border-zinc-200 pb-6 dark:border-zinc-800">
        <p className="text-sm font-medium text-zinc-500 dark:text-zinc-400">
          오늘의 픽
        </p>
        <h1 className="text-3xl font-semibold tracking-tight text-zinc-900 dark:text-zinc-50">
          추천 종목 대시보드
        </h1>
        {data.date ? (
          <p className="text-sm text-zinc-600 dark:text-zinc-400">
            기준일 {data.date}
          </p>
        ) : null}
      </header>

      {error ? (
        <div className="rounded-lg border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-800 dark:border-rose-900 dark:bg-rose-950/40 dark:text-rose-200">
          백엔드 연결 확인: <code>NEXT_PUBLIC_API_URL</code> · {error}
        </div>
      ) : null}

      <ul className="flex flex-col gap-4">
        {data.items.map((item) => (
          <li key={`${item.ticker}-${item.market}`}>
            <Link
              href={`/stock/${encodeURIComponent(item.ticker)}`}
              className="block rounded-xl border border-zinc-200 bg-white p-5 shadow-sm transition hover:border-zinc-300 hover:shadow-md dark:border-zinc-800 dark:bg-zinc-950 dark:hover:border-zinc-700"
            >
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <p className="text-lg font-semibold text-zinc-900 dark:text-zinc-50">
                    {item.name}{" "}
                    <span className="font-normal text-zinc-500 dark:text-zinc-400">
                      {item.ticker}
                    </span>
                  </p>
                  <p className="mt-1 text-xs uppercase tracking-wide text-zinc-500 dark:text-zinc-400">
                    {item.market}
                  </p>
                </div>
                <div className="flex flex-wrap items-center gap-2">
                  <span
                    className={`rounded-full px-3 py-1 text-xs font-medium ${riskBadgeClass(item.risk_level)}`}
                  >
                    리스크 {item.risk_level}
                  </span>
                  <span className="rounded-full bg-zinc-100 px-3 py-1 text-xs font-medium text-zinc-700 dark:bg-zinc-800 dark:text-zinc-200">
                    확신도 {(item.confidence * 100).toFixed(0)}%
                  </span>
                </div>
              </div>
              <p className="mt-4 text-sm leading-relaxed text-zinc-600 dark:text-zinc-300">
                {item.reason}
              </p>
            </Link>
          </li>
        ))}
      </ul>

      {data.items.length === 0 && !error ? (
        <p className="text-center text-sm text-zinc-500 dark:text-zinc-400">
          표시할 추천이 없습니다.
        </p>
      ) : null}
    </div>
  );
}
