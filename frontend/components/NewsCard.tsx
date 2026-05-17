import type { NewsItem } from "@/lib/api";

type Props = {
  item: NewsItem;
};

function displayTitle(item: NewsItem): string {
  return item.title_ko?.trim() || item.title;
}

function displaySnippet(item: NewsItem): string {
  return item.snippet_ko?.trim() || item.snippet;
}

function newsHref(item: NewsItem): string {
  if (item.url?.trim()) {
    return item.url.trim();
  }
  return `https://www.google.com/search?q=${encodeURIComponent(item.title)}`;
}

export function NewsCard({ item }: Props) {
  const href = newsHref(item);
  const external = Boolean(item.url?.trim());
  const title = displayTitle(item);
  const snippet = displaySnippet(item);
  const showOriginal =
    Boolean(item.title_original) || Boolean(item.snippet_original);

  return (
    <li>
      <a
        href={href}
        target="_blank"
        rel="noopener noreferrer"
        className="group block rounded-xl border border-zinc-200 bg-white p-5 shadow-sm transition hover:border-blue-300 hover:shadow-md dark:border-zinc-800 dark:bg-zinc-950 dark:hover:border-blue-700"
      >
        <div className="flex items-start justify-between gap-3">
          <h2 className="text-lg font-semibold text-zinc-900 group-hover:text-blue-600 dark:text-zinc-50 dark:group-hover:text-blue-400">
            {title}
          </h2>
          <span className="shrink-0 rounded-full bg-blue-50 px-2.5 py-1 text-xs font-medium text-blue-700 dark:bg-blue-950 dark:text-blue-300">
            {external ? "기사 열기 ↗" : "검색 ↗"}
          </span>
        </div>
        {item.title_original ? (
          <p className="mt-1 line-clamp-2 text-xs text-zinc-400 dark:text-zinc-500">
            원문: {item.title_original}
          </p>
        ) : null}
        <p className="mt-2 text-xs text-zinc-500 dark:text-zinc-400">
          {item.source || "출처 미상"} · {item.published_at}
          {showOriginal ? " · 번역됨" : null}
        </p>
        {snippet ? (
          <p className="mt-3 text-sm leading-relaxed text-zinc-600 dark:text-zinc-300">
            {snippet}
          </p>
        ) : null}
        {item.snippet_original ? (
          <p className="mt-2 line-clamp-3 text-xs text-zinc-400 dark:text-zinc-500">
            원문: {item.snippet_original}
          </p>
        ) : null}
      </a>
    </li>
  );
}
