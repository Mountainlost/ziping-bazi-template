'use client';
import Link from 'next/link';
import { useSession } from './session';
import { HomeContent } from './home';
import { ReportReader, ReadingModeSwitch } from './report-reader';
import { Verification } from './verify';
import { Analysis } from './analysis';
import { Cycles } from './cycles';
import { Conclusion } from './conclusion';
import { PageHeading } from './shared';
import { Compass, CalendarDots, BookOpenText, ChartLineUp, ShieldCheck, ChatCircleText } from '@phosphor-icons/react';
import { SiteHeader } from './site-header';

const navIcons=[CalendarDots,ShieldCheck,BookOpenText,Compass,ChartLineUp,ChatCircleText];

const navigation = [
  {stage:'birth',path:'/',name:'出生资料',note:'输入生辰与地点'},
  {stage:'verify',path:'/verify',name:'排盘校验',note:'校准时间与历法'},
  {stage:'overview',path:'/overview',name:'解读报告',note:'白话与专业解读'},
  {stage:'analysis',path:'/analysis',name:'旺衰与取用',note:'结论背后的依据'},
  {stage:'cycles',path:'/cycles',name:'大运与流年',note:'在时间中看变化'},
  {stage:'conclusion',path:'/conclusion',name:'复核与追问',note:'完整报告及复核'},
];
const headings: Record<string,[string,string]> = {
  verify:['先核对，再解读。','确认出生资料、真太阳时与节气边界。选择一个候选后，生成完整规则报告。'],
  overview:['一局四柱，循证而读。','排盘事实由程序计算。传统解释附有依据，未确认的条件会明确保留。'],
  analysis:['每个判断，都有来处。','由月令、根气、透干到生克制化，理解规则如何得出结论。'],
  cycles:['看变化，也看条件。','原局是基础，大运是背景，流年须放在两者之中理解。'],
  conclusion:['读到结论，也看到边界。','十二章节报告、程序一致性复核，以及围绕已有证据的只读追问。'],
};

export function Workspace({ stage }: { stage: string }) {
  const { chart, ready, error } = useSession();
  const isBirth = stage === 'birth';
  const current = navigation.findIndex(n => n.stage === stage);
  return <div className={`app-shell modern-app ${isBirth ? 'home-app scan-home-app' : 'report-app'}`} data-motion="on">
    <SiteHeader section={isBirth?'home':'report'} stage={stage}/>
    <div className="main-area">
      {!isBirth && <div className="workspace-bar"><nav aria-label="命盘导航">{navigation.map((n,i)=>{const Icon=navIcons[i];return <Link href={n.path} key={n.stage} aria-current={stage===n.stage?'page':undefined}><Icon size={20} weight="duotone" aria-hidden="true"/>{n.name}</Link>;})}</nav></div>}
      <main id="main-content" className={isBirth?'home-main':stage==='overview'?'reader-main':'workspace-main'}>
        {!ready ? <div className="empty-state" role="status">正在读取命盘…</div> : isBirth ? <HomeContent/> : <>
          {stage!=='overview' && <div className="workspace-heading"><PageHeading number={String(current+1).padStart(2,'0')} title={headings[stage]?.[0] || '命盘'} description={headings[stage]?.[1] || ''}/>{stage==='analysis'&&<ReadingModeSwitch/>}</div>}
          {error && <p role="alert" className="error">{error}</p>}
          {!chart || (stage !== 'verify' && !chart.locked) ? <div className="empty-state"><span className="eyebrow">尚未生成报告</span><h2>{chart ? '请先确认当前排盘' : '从出生资料开始'}</h2><p>{chart ? '核对时间和四柱，确认后才能读取完整报告。' : '没有示例命盘代替你的资料。填写生辰后，系统会进行确定性计算。'}</p><Link className="primary" href={chart ? '/verify' : '/'}>{chart ? '核对排盘 →' : '填写出生资料 →'}</Link></div> : <>
            {stage === 'verify' && <Verification key={chart.id} chart={chart}/>}
            {stage === 'overview' && <ReportReader chart={chart}/>}
            {stage === 'analysis' && <Analysis chart={chart}/>}
            {stage === 'cycles' && <Cycles key={chart.id} chart={chart}/>}
            {stage === 'conclusion' && <Conclusion key={chart.id} chart={chart}/>}
          </>}
        </>}
      </main>{!isBirth&&<footer className="site-footer"><span>ZIPING 子平 · 每个判断，都有来处</span><span>个人命盘报告</span></footer>}
    </div>
  </div>;
}
