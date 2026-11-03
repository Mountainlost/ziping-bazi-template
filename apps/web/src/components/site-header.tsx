'use client';
import Link from 'next/link';
import { Compass, ArrowUpRight } from '@phosphor-icons/react';
import { useSession } from './session';
import { ReportAccess } from './report-access';

export function SiteHeader({ section='home', stage='' }: { section?: 'home'|'master'|'examples'|'report'; stage?: string }) {
  const { chart }=useSession();
  const report=section==='report';
  return <header className="site-header"><Link className="brand" href="/" aria-label="子平首页">{report?<span className="brand-symbol"><Compass size={29} weight="duotone" aria-hidden="true"/></span>:<span className="scan-brand-symbol" aria-hidden="true"><i/><i/></span>}<b>子平</b>{report&&<small>ZIPING</small>}</Link><nav className="site-nav" aria-label="主导航">{report?<><Link href="/paipan" aria-current={stage==='paipan'?'page':undefined}>生辰排盘</Link><Link href="/overview" aria-current={stage==='overview'?'page':undefined}>我的解读</Link><Link href="/cycles" aria-current={stage==='cycles'?'page':undefined}>大运流年</Link><Link href="/master">子平大师</Link></>:<><Link href="/paipan" aria-current={stage==='paipan'?'page':undefined}>生辰排盘</Link><Link href="/examples" aria-current={section==='examples'?'page':undefined}>解盘案例</Link><Link href="/master" aria-current={section==='master'?'page':undefined}>子平大师</Link></>}</nav><div className="header-tools">{report?<Link href={chart?.locked?'/overview':'/paipan'} className="header-cta">{chart?.locked?'阅读我的报告':'创建我的命盘'}<ArrowUpRight size={19} aria-hidden="true"/></Link>:<ReportAccess/>}</div></header>;
}
