import Link from "next/link";
import type { TodayRecommendationItem } from "@/lib/api";

type Props = {
  item: TodayRecommendationItem;
  riskBadgeClass: (level: string) => string;
};

function latestNewsHref(item: TodayRecommendationItem): string | null {
  const url = item.latest_news_url?.trim();
  if (url) return url;
  if (item.latest_news_title?.trim()) {
    return `https://www.google.com/search?q=${encodeURIComponent(item.latest_news_title)}`;
  }
  return null;
}

export function RecommendationCard({ item, riskBadgeClass }: Props) {
  const newsHref = latestNewsHref(item);
  const stockHref = `/stock/${encodeURIComponent(item.ticker)}`;

  return (
    <li className="rounded-xl border border-zinc-200 bg-white shadow-sm dark:border-zinc-800 dark:bg-zinc-950">
      <div className="p-5">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <Link
              href={stockHref}
              className="text-lg font-semibold text-zinc-900 hover:text-blue-600 dark:text-zinc-50 dark:hover:text-blue-400"
            >
              {item.name}{" "}
              <span className="font-normal text-zinc-500 dark:text-zinc-400">
                {item.ticker}
              </span>
            </Link>
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
        {item.reason_original ? (
          <p className="mt-2 line-clamp-2 text-xs text-zinc-400 dark:text-zinc-500">
            원문: {item.reason_original}
          </p>
        ) : null}
        <div className="mt-4 flex flex-wrap gap-2 border-t border-zinc-100 pt-4 dark:border-zinc-800">
          {newsHref ? (
            <a
              href={newsHref}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center rounded-lg bg-blue-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-blue-700"
            >
              최신 뉴스 열기 ↗
            </a>
          ) : null}
          <Link
            href={stockHref}
            className="inline-flex items-center rounded-lg border border-zinc-200 px-3 py-1.5 text-sm font-medium text-zinc-700 hover:bg-zinc-50 dark:border-zinc-700 dark:text-zinc-200 dark:hover:bg-zinc-900"
          >
            뉴스 목록 보기
          </Link>
        </div>
      </div>
    </li>
  );
}
