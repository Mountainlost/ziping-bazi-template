import type { Metadata } from 'next';
import { SiteHeader } from '@/components/site-header';
import { HomeReadingExample } from '@/components/home-reading-example';
export const metadata: Metadata={title:'解盘案例 · 子平'};
export default function ExamplesPage(){return <div className="modern-app scan-home-app examples-app"><SiteHeader section="examples"/><main id="main-content" className="examples-main"><h1>先读一份解盘案例。</h1><p>看看事业、财运和感情，怎样从专业判断讲成日常的话。</p><HomeReadingExample/></main></div>;}
