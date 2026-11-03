import type { Metadata } from 'next';
import { SessionProvider } from '@/components/session';
import './globals.css';
import './modern.css';
import './book-conveyor.css';
import './master.css';
export const metadata: Metadata = { title: '子平 · 八字排盘与人生解读', description: '从出生资料到四柱排盘，白话阅读性格、事业、财运与感情，逐项查看命盘依据。' };
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return <html lang="zh-CN" data-scroll-behavior="smooth"><body><a href="#main-content" className="skip-link">跳到正文</a><SessionProvider>{children}</SessionProvider></body></html>;
}
