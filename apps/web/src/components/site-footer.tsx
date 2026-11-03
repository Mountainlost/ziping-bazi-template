'use client';
import Link from 'next/link';
import { Compass, ArrowUpRight } from '@phosphor-icons/react';

export function SiteFooter() {
  return <section className="footer-section" aria-label="网站页尾"><div className="footer-wrapper">
    <div className="footer-left"><div className="footer-orbit" aria-hidden="true"><i/><i/><i/><span>子</span></div><Link href="/" className="footer-logo"><span className="footer-logo-mark"><Compass size={25} weight="duotone" aria-hidden="true"/></span><b>子平 <small>ZIPING</small></b></Link>
      <div className="footer-tagline">看见结构，<br/><span>也读懂自己的节奏。</span></div><div className="footer-card-bottom"><span>始于生辰，回到生活。</span><a href="#birth-form" aria-label="回到出生资料"><ArrowUpRight size={20} aria-hidden="true"/></a></div>
    </div>
    <div className="footer-right"><a className="footer-floating-seal" href="#birth-form" aria-label="回到出生资料"><span className="footer-seal-cube"><Compass size={49} weight="duotone" aria-hidden="true"/></span><small>从这里开始 ↗</small></a>
      <div className="footer-nav-cols"><div><h3>探索子平</h3><Link href="/">出生排盘</Link><Link href="/overview">命盘解读</Link><Link href="/cycles">大运流年</Link></div><div><h3>安心阅读</h3><Link href="/sources">数据与算法</Link><Link href="/conclusion">报告与依据</Link><Link href="/verify">重新校验资料</Link></div></div>
      <div className="footer-bottom"><p>子平 · 传统文化的现代阅读<br/><span>白话读结论，专业看依据。</span></p><div><small>先了解自己，再慢慢做选择。</small><a href="#birth-form" className="footer-cta">创建我的命盘 <span>↗</span></a></div></div>
    </div>
  </div><div className="footer-watermark" aria-hidden="true">ZIPING<span>子平</span></div><div className="footer-legal"><span>出生资料仅用于当前命盘</span><Link href="/sources">资料来源与开源声明</Link></div></section>;
}
