'use client';
import Image from 'next/image';
import Link from 'next/link';
import { useState } from 'react';
import { ArrowUpRight, ArrowRight } from '@phosphor-icons/react';
import { SiteHeader } from './site-header';
import { useSession } from './session';
import { EvidenceList } from './shared';
import { MasterChat } from './master-chat';

const topics=[{name:'性格',number:5},{name:'事业',number:6},{name:'财运',number:7},{name:'感情',number:8},{name:'大运',number:10},{name:'流年',number:11}];
const examples:Record<string,{title:string;paragraphs:string[];professional:string[]}>={
  性格:{title:'看得细，也要把话说清楚。',paragraphs:['你对细节和好坏有自己的标准，也容易留意到别人没有发现的问题。把判断变成方法和作品，会比急着证明自己更有力量。','有分歧时，先把话说完整。别在情绪最顶的时候做决定。'],professional:['案例以日干象义、月令与十神主题组织性格解读，具体条件需与旺衰共同观察。']},
  事业:{title:'先把一门本事做深，再把机会接稳。',paragraphs:['你更适合在需要分析问题、表达想法和找到更好做法的工作里发挥长处。先把一项能力做深，再把它变成别人看得见的成果。','你可以掌握自己的核心能力和决定权，但不必一个人包办所有环节。有人配合、有清楚的流程，会比什么都亲自扛更省力。'],professional:['案例围绕分析、表达与专业输出的主题，解释自身条件、资源配合及事业规模之间的关系。','本节为匿名案例节选，未将示例判断写入任何个人命盘。']},
  财运:{title:'能看到机会，也要接得住。',paragraphs:['真正需要留意的是，机会一多就想同时铺开。先把手里最重要的一件事做成，再逐步扩大。','涉及共同投入、共同支出或收入分配，就提前把账和责任讲清楚。感情归感情，约定归约定。'],professional:['案例将财星主题与自身条件结合解释，不以单一财星直接推出实际收益。']},
  感情:{title:'你想明白的事，对方未必已经知道。',paragraphs:['有需求就直接说，有分歧先把各自的想法讲完整。不要让沉默、猜测或一时说重的话，代替真正的沟通。','能长期相处的人，不只是眼下合得来，也要能一起处理意见不同的时候。'],professional:['感情章节综合相处主题与已有命盘结论解释。未计算的桃花与感情方位不会自行添加。']},
  大运:{title:'把时间放长一点，看积累怎样起作用。',paragraphs:['十年背景帮助你理解较长阶段的侧重点。看机会时，也看看自己的能力、时间和身边的支持准备到了哪一步。','正式报告会按已经计算完成的起止日期展示每步大运，再结合原本的命盘解释。'],professional:['大运采用已保存的运序、起止时间与分析依据，解释界面不重新计算起运。']},
  流年:{title:'安排眼前的一年，也给变化留出空间。',paragraphs:['任务增加时，先分清哪些必须自己做，哪些可以协作。给工作与生活留一点调整空间，会更容易把事情持续做好。','遇到一年内换大运，报告会分别讲清两段时间，不把不同条件混成同一个结论。'],professional:['流年结合原局及当前大运解释；交运年份读取已经完成的分段结果。']},
};

export function MasterContent(){
  const {chart,ready,mode,setMode}=useSession();
  const [topic,setTopic]=useState('事业');
  const locked=chart?.locked?chart:null;
  const selected=topics.find(t=>t.name===topic)!;
  const chapter=locked?.report.chapters.find(ch=>ch.number===selected.number);
  const sample=examples[topic];
  const reading=chapter?(mode==='plain'?chapter.plain:chapter.professional):null;
  const paragraphs=chapter?(reading?.paragraphs||[mode==='plain'?chapter.body:chapter.conclusion]):mode==='plain'?sample.paragraphs:sample.professional;
  return <div className="modern-app scan-home-app master-app"><SiteHeader section="master"/><main id="main-content"><section className="master-hero"><div className="master-breadcrumb"><Link href="/">首页</Link><span>/</span>子平大师</div><Image className="master-portrait" src="/images/master-scholar-v2.png" alt="徐子平人物意象：蓝袍古代学者插画" width={1536} height={1024} preload sizes="75vw"/><div className="master-hero-copy"><span>子平大师</span><h1>先认识子平，<br/>再读懂你的命盘。</h1><p>徐居易，字子平，世称徐子平。<br/>他是四柱命理发展中的重要人物。<br/>以出生年月日时、五行生克推演命局的方法，<br/>后世称为“子平法”。</p><Link href="/sources#ziping-origin" className="scan-text-link">了解子平法的由来<ArrowUpRight size={19} aria-hidden="true"/></Link><div className="master-hero-actions">{locked?<a className="scan-primary" href="#master-reading">深入解读我的命盘<ArrowUpRight size={22} aria-hidden="true"/></a>:<Link className="scan-primary" href="/paipan">先生成我的命盘<ArrowUpRight size={22} aria-hidden="true"/></Link>}<a className="scan-text-link" href="#master-reading">先看解盘案例<ArrowUpRight size={20} aria-hidden="true"/></a></div><small>围绕已有命盘解读，继续问你关心的事。</small></div><p className="master-portrait-caption">徐子平 · 人物意象</p></section><section className="master-reading-section" id="master-reading"><header><h2>看懂报告，再把问题聊明白。</h2><p>{locked?'围绕你已经确认的报告，继续问你关心的事。':'先读一段匿名案例。生成自己的命盘后，这里会显示你的报告。'}</p></header><div className="master-workspace"><article className="master-report"><header><h2>{locked?'我的命盘解读':'匿名解盘案例'}</h2><button type="button" onClick={()=>setMode(mode==='plain'?'professional':'plain')}>{mode==='plain'?'看专业版':'回到白话版'}<ArrowUpRight size={17} aria-hidden="true"/></button></header><nav aria-label="解盘主题">{topics.map(t=><button type="button" key={t.name} aria-pressed={topic===t.name} onClick={()=>setTopic(t.name)}>{t.name}</button>)}</nav>{!ready?<p role="status">正在读取当前报告…</p>:<div className="master-report-copy"><h3>{chapter?(mode==='plain'?chapter.plain?.takeaway||chapter.title:chapter.conclusion):sample.title}</h3>{paragraphs.map((p,i)=><p key={i}>{p}</p>)}{chapter?<EvidenceList items={chapter.evidence}/>:<details className="master-example-basis"><summary>查看案例说明</summary><p>本节为匿名解读案例节选，用来展示阅读方式。个人报告会显示实际计算结果和同一份判断依据。</p></details>}<div className="master-next-topic"><span>{topics[(topics.findIndex(t=>t.name===topic)+1)%topics.length].name}</span><button type="button" onClick={()=>setTopic(topics[(topics.findIndex(t=>t.name===topic)+1)%topics.length].name)}>继续阅读<ArrowRight size={18} aria-hidden="true"/></button></div></div>}</article><MasterChat key={locked?.id||'example'} chartId={locked?.id||null}/></div></section><footer className="master-page-footer"><p>本页人物与案例含人工智能生成内容。传统文化解读，仅供参考，不作为医疗、投资或重大人生决定的唯一依据。</p><Link href="/sources">资料来源与开源声明</Link></footer></main></div>;
}
