import Link from "next/link";
import { NewsCard } from "@/components/NewsCard";
import { getStockNews } from "@/lib/api";

type Props = {
  params: { ticker: string };
};

export default async function StockDetailPage({ params }: Props) {
  const ticker = decodeURIComponent(params.ticker);
  let news;
  let error: string | null = null;
  try {
    news = await getStockNews(ticker);
  } catch (e) {
    error = e instanceof Error ? e.message : "뉴스를 불러오지 못했습니다.";
    news = { ticker, items: [] };
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
          {news.ticker}
        </h1>
        <p className="text-sm text-zinc-600 dark:text-zinc-400">
          종목 관련 뉴스
        </p>
      </header>

      {error ? (
        <div className="rounded-lg border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-800 dark:border-rose-900 dark:bg-rose-950/40 dark:text-rose-200">
          {error}
        </div>
      ) : null}

      <ul className="flex flex-col gap-4">
        {news.items.map((n) => (
          <NewsCard key={n.id} item={n} />
        ))}
      </ul>

      {news.items.length === 0 && !error ? (
        <p className="text-center text-sm text-zinc-500 dark:text-zinc-400">
          표시할 뉴스가 없습니다.
        </p>
      ) : null}
    </div>
  );
}
