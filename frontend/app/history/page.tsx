import Link from "next/link";
import { getRecommendationHistory } from "@/lib/api";

export default async function HistoryPage() {
  let data;
  let error: string | null = null;
  try {
    data = await getRecommendationHistory();
  } catch (e) {
    error = e instanceof Error ? e.message : "히스토리를 불러오지 못했습니다.";
    data = { items: [] };
  }

  return (
    <div className="mx-auto flex min-h-screen max-w-4xl flex-col gap-8 px-4 py-10 sm:px-6">
      <header className="flex flex-col gap-2 border-b border-zinc-200 pb-6 dark:border-zinc-800">
        <Link
          href="/"
          className="text-sm text-zinc-500 hover:text-zinc-800 dark:text-zinc-400 dark:hover:text-zinc-200"
        >
          ← 대시보드
        </Link>
        <h1 className="text-3xl font-semibold tracking-tight text-zinc-900 dark:text-zinc-50">
          추천 히스토리
        </h1>
        <p className="text-sm text-zinc-600 dark:text-zinc-400">
          과거 추천 기록입니다.
        </p>
      </header>

      {error ? (
        <div className="rounded-lg border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-800 dark:border-rose-900 dark:bg-rose-950/40 dark:text-rose-200">
          {error}
        </div>
      ) : null}

      <div className="overflow-hidden rounded-xl border border-zinc-200 dark:border-zinc-800">
        <table className="w-full text-left text-sm">
          <thead className="bg-zinc-50 text-xs uppercase text-zinc-500 dark:bg-zinc-900 dark:text-zinc-400">
            <tr>
              <th className="px-4 py-3 font-medium">날짜</th>
              <th className="px-4 py-3 font-medium">티커</th>
              <th className="px-4 py-3 font-medium">확신도</th>
              <th className="px-4 py-3 font-medium">리스크</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-zinc-100 bg-white dark:divide-zinc-800 dark:bg-zinc-950">
            {data.items.map((row) => (
              <tr key={row.id}>
                <td className="whitespace-nowrap px-4 py-3 text-zinc-600 dark:text-zinc-300">
                  {row.date}
                </td>
                <td className="px-4 py-3 font-medium text-zinc-900 dark:text-zinc-50">
                  <Link
                    href={`/stock/${encodeURIComponent(row.ticker)}`}
                    className="hover:underline"
                  >
                    {row.ticker}
                  </Link>
                </td>
                <td className="px-4 py-3 text-zinc-600 dark:text-zinc-300">
                  {(row.confidence * 100).toFixed(0)}%
                </td>
                <td className="px-4 py-3 text-zinc-600 dark:text-zinc-300">
                  {row.risk_level}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {data.items.length === 0 && !error ? (
        <p className="text-center text-sm text-zinc-500 dark:text-zinc-400">
          기록이 없습니다.
        </p>
      ) : null}
    </div>
  );
}
