'use client';
import Link from 'next/link';
import { useEffect, useState } from 'react';
import type { Chart, ReportChapter } from '@/lib/types';
import { formatBirthTime } from '@/lib/types';
import { useSession } from './session';
import { EvidenceList } from './shared';
import { ChartAttachment } from './chart-attachment';
import { AiQuestions } from './ai-questions';
import { ListBullets, ChatCircleText, ArrowUpRight } from '@phosphor-icons/react';

const names: Record<number,string>={1:'排盘',2:'旺衰',3:'格局',4:'喜忌',5:'性格',6:'事业',7:'财运',8:'感情',9:'生活',10:'大运',11:'流年',12:'总断'};
export function ReadingModeSwitch() {
  const {mode,setMode}=useSession();
  return <div className="reading-mode segmented" role="group" aria-label="报告阅读版本"><button type="button" aria-pressed={mode==='plain'} onClick={()=>setMode('plain')}>白话版</button><button type="button" aria-pressed={mode==='professional'} onClick={()=>setMode('professional')}>专业版</button></div>;
}

export function ReadingChapter({ chapter, mode }: { chapter: ReportChapter; mode: 'plain'|'professional' }) {
  const text=mode==='plain' ? chapter.plain : chapter.professional;
  const paragraphs=text?.paragraphs || [mode==='plain' ? chapter.body : chapter.conclusion];
  return <article className="reading-chapter" id={`chapter-${chapter.number}`} data-chapter={chapter.number}>
    <div className="chapter-heading"><span>{String(chapter.number).padStart(2,'0')}</span><h2>{names[chapter.number] || chapter.title}</h2><small>{mode==='plain' ? '白话解读' : '专业解读'}</small></div>
    {mode==='professional' && <div className="professional-conclusion"><span>规则结论</span><strong>{chapter.conclusion}</strong><small>{chapter.stability==='disputed' ? '条件存在争议，须核实' : '基于当前规则与资料'}</small></div>}
    <div className="chapter-copy">{paragraphs.map((p,i)=><p key={i}>{p}</p>)}</div>
    {mode==='plain' && chapter.plain?.takeaway && <div className="chapter-takeaway"><span>这一节，记住一句</span><p>{chapter.plain.takeaway}</p></div>}
    <EvidenceList key={mode} items={chapter.evidence}/>
  </article>;
}

export function ReportReader({ chart }: { chart: Chart }) {
  const {mode}=useSession(); const [active,setActive]=useState(1);
  const overview=chart.report.overview;
  useEffect(()=>{const observer=new IntersectionObserver(entries=>{const item=entries.find(e=>e.isIntersecting);if(item)setActive(Number((item.target as HTMLElement).dataset.chapter));},{rootMargin:'-165px 0px -55% 0px'});document.querySelectorAll('[data-chapter]').forEach(e=>observer.observe(e));return()=>observer.disconnect();},[chart.id]);
  return <div className="report-layout"><aside className="report-rail"><div className="report-rail-inner"><div className="report-rail-title"><ListBullets size={21} aria-hidden="true"/><span>目录</span></div><nav aria-label="阅读目录">{chart.report.chapters.map(ch=><a href={`#chapter-${ch.number}`} key={ch.number} className={active===ch.number?'selected':''} aria-current={active===ch.number?'location':undefined}><span>{names[ch.number] || ch.title}</span></a>)}<a href="#ai-questions" className={`toc-ai ${active===13?'selected':''}`}><ChatCircleText size={19} aria-hidden="true"/>大师解盘</a></nav></div></aside>
    <div className="report-document"><header className="report-header"><div><span className="eyebrow">PERSONAL READING · 个人命盘解读</span><h1>{chart.input.name ? `${chart.input.name}的命盘解读` : '你的命盘解读'}</h1><p>{chart.calendar.solarDate} · {formatBirthTime(chart.input)} · {chart.input.city}{chart.input.district} · {chart.input.sex}</p></div><span className="report-edition">子平 / REPORT<br/><b>{chart.metadata.referenceYear}</b></span></header>
      <div className="report-summary"><div className="summary-topline"><span>先看重点</span><span>{mode==='plain'?'根据你的出生资料':'基于已锁定命盘'} · {mode==='plain'?'白话版':'专业版'}</span></div><h2>{mode==='plain' ? overview?.headline || chart.strength.plainLanguage : chart.finalConclusion.conclusion}</h2>{(mode==='plain' ? overview?.paragraphs || [chart.finalConclusion.plainLanguage || chart.finalConclusion.conclusion] : [chart.finalConclusion.conclusion]).map((p,i)=><p key={i}>{p}</p>)}
        <div className="summary-keywords">{mode==='plain' ? (overview?.plainTags || ['先读解读，再看依据']).map(tag=><span key={tag}>{tag}</span>) : <><span>{chart.dayMaster.stem}{chart.dayMaster.element}日主</span><span>{chart.strength.conclusion}</span><span>{chart.pillars.month?.branch}月</span><span>扶抑 · {chart.usefulGod.primaryUsefulGod}</span></>}</div>
      </div>
      <div className="report-context-strip"><Link href="/cycles"><small>这十年的重点</small><strong>{mode==='plain' ? overview?.currentLuck.map(c=>c.from.slice(0,4)+'—'+c.toExclusive.slice(0,4)).join(' / ') || '查看时间段' : overview?.currentLuck.map(c=>c.stem+c.branch).join(' / ') || '查看大运'}</strong><span>{mode==='plain' ? overview?.currentLuck[0]?.plainTheme || '查看这段时间该注意什么' : overview?.currentLuck[0]?.theme} <ArrowUpRight size={17} aria-hidden="true"/></span></Link><Link href="/cycles"><small>{chart.metadata.referenceYear} 年的重点</small><strong>{mode==='plain' ? '看看怎样安排' : overview?.currentAnnual ? overview.currentAnnual.stem+overview.currentAnnual.branch : '查看流年'}</strong><span>{mode==='plain' ? overview?.currentAnnual?.plainTheme || '看看这一年的变化' : overview?.currentAnnual?.theme} <ArrowUpRight size={17} aria-hidden="true"/></span></Link><div><small>怎么读这份报告</small><strong>先读白话，再看依据</strong><span>有疑问，直接看对应的章节</span></div></div>
      <ChartAttachment chart={chart}/>
      <div className="report-reading-toolbar"><div><b>展开看你的命盘</b><p>{mode==='plain' ? '先把术语放在一边，从你关心的事情开始。' : '结论、成立条件与原始依据逐项对照。'}</p></div><ReadingModeSwitch/></div>
      {!chart.report.overview && <p className="legacy-report-note">这是旧版锁定报告。旧结论保持不变；<Link href="/verify">重新校验并确认</Link>后可生成新版分层解读。</p>}
      <div className="report-article-body">{chart.report.chapters.map(ch=><ReadingChapter key={ch.number} chapter={ch} mode={mode}/>)}</div>
      <div className="reading-end"><span>读到这里，回到生活。</span><h2>报告是理解的起点，<br/>选择仍然在你手中。</h2><Link href="/conclusion" className="primary">查看复核与追问 <span>↗</span></Link></div>
      <AiQuestions/>
      <details className="coverage-note"><summary>报告内容与数据说明</summary><p>{chart.report.coverage?.available.join('、') || '本版提供十二章节规则报告。'}</p><ul>{(chart.report.coverage?.unavailable || ['未计算的内容不会添加到报告']).map(item=><li key={item}>{item}</li>)}</ul><Link href="/sources">数据与算法说明 ↗</Link></details>
      <p className="report-disclaimer">{chart.report.disclaimer || '以上为传统文化解读，仅供参考，不作为医疗、投资或重大人生决定的唯一依据。'}</p>
    </div>
  </div>;
}
