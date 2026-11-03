'use client';
import { Suspense } from 'react';
import { BirthForm } from './birth-form';
import Link from 'next/link';
import { ArrowUpRight } from '@phosphor-icons/react';
import { BookConveyor } from './book-conveyor';
import { HomeReadingExample } from './home-reading-example';
import { SiteFooter } from './site-footer';

export function HomeContent() {
  return <>
    <section className="scan-hero" aria-labelledby="scan-heading">
      <div className="scan-hero-intro"><h1 id="scan-heading">推演有据，<br/>解读有温度<span>。</span></h1><div className="scan-hero-action"><p>先核对四柱，再理清格局与喜忌。<br/>把事业、财运、感情与时间变化，<br/>讲成你听得懂的话。</p><a href="#birth-form" className="scan-primary">开始排盘 <ArrowUpRight size={23} aria-hidden="true"/></a></div></div>
      <BookConveyor/>
    </section>
    <div className="scan-home-content">
      <section className="home-birth-layout" aria-labelledby="birth-intro-heading"><div className="home-birth-intro"><h2 id="birth-intro-heading">从你的生辰开始。</h2><p>先把时间与地点核对好，再慢慢读你的报告。</p><ol><li><b>填写出生资料</b><span>支持公历、农历，也可以填写大致时间。</span></li><li><b>查看排盘依据</b><span>按默认命盘生成报告，也可以查看真太阳时和其他候选。</span></li><li><b>读完整解盘</b><span>先看白话结论，想弄明白时再展开依据。</span></li></ol></div><Suspense><BirthForm/></Suspense></section>
      <HomeReadingExample/>
      <section id="master-preview" className="home-master"><div><span className="home-master-name">子平大师</span><h2>读完报告，<br/>还有哪里想聊明白？</h2><p>围绕这份报告，继续问工作、赚钱、相处，或某一年的变化。</p></div><div className="home-master-detail"><p>在完整报告里看依据，也可以把想问的先记下来。</p><Link className="scan-text-link" href="/master">进入子平大师<ArrowUpRight size={21} aria-hidden="true"/></Link></div></section>
      <SiteFooter/>
    </div>
  </>;
}
