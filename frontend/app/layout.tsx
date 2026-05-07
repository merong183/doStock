import type { Metadata } from "next";
import Link from "next/link";
import localFont from "next/font/local";
import "./globals.css";

const geistSans = localFont({
  src: "./fonts/GeistVF.woff",
  variable: "--font-geist-sans",
  weight: "100 900",
});
const geistMono = localFont({
  src: "./fonts/GeistMonoVF.woff",
  variable: "--font-geist-mono",
  weight: "100 900",
});

export const metadata: Metadata = {
  title: "doStock · 종목 추천",
  description: "추천 종목 대시보드와 뉴스",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ko">
      <body
        className={`${geistSans.variable} ${geistMono.variable} min-h-screen bg-zinc-50 font-sans antialiased dark:bg-zinc-950`}
      >
        <nav className="sticky top-0 z-10 border-b border-zinc-200 bg-white/90 backdrop-blur dark:border-zinc-800 dark:bg-zinc-950/90">
          <div className="mx-auto flex max-w-4xl items-center gap-6 px-4 py-3 sm:px-6">
            <Link
              href="/"
              className="text-sm font-semibold text-zinc-900 dark:text-zinc-50"
            >
              doStock
            </Link>
            <Link
              href="/"
              className="text-sm text-zinc-600 hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-zinc-100"
            >
              대시보드
            </Link>
            <Link
              href="/history"
              className="text-sm text-zinc-600 hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-zinc-100"
            >
              히스토리
            </Link>
          </div>
        </nav>
        {children}
      </body>
    </html>
  );
}
