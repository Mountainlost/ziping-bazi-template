'use client';
import Link from 'next/link';
import { type Chart } from '@/lib/types';
import { ChartAttachment } from './chart-attachment';
import { AiQuestions } from './ai-questions';
import { DownloadSimple } from '@phosphor-icons/react';

const checks: Record<string,string> = {pillars:'四柱未改变',tenGods:'十神与藏干对应',strengthConsistency:'旺衰前后一致',patternConsistency:'格局与原局一致',usefulGodConsistency:'喜用与旺衰一致',luckCycleConsistency:'大运引用原局喜忌',annualCycleConsistency:'流年结合当前大运',hourCompleteness:'时柱资料完整性'};
export function Conclusion({ chart }: { chart: Chart }) {
  function download() { const url = URL.createObjectURL(new Blob([JSON.stringify(chart,null,2)],{type:'application/json;charset=utf-8'}));const anchor = document.createElement('a');anchor.href=url;anchor.download=`子平命盘-${chart.id}.json`;anchor.click();setTimeout(() => URL.revokeObjectURL(url),1000); }
  return <>
    <section className="paper report-archive"><span className="eyebrow">YOUR LOCKED REPORT</span><h2>一份报告，两种读法，同一组依据。</h2><p>{chart.report.overview?.headline || chart.finalConclusion.conclusion}</p><div className="actions"><Link href="/overview" className="primary">阅读完整解读 ↗</Link><button className="secondary" onClick={download}><DownloadSimple size={20} aria-hidden="true"/>导出报告数据</button></div></section><ChartAttachment chart={chart}/>
    <section className="paper"><div className="section-top"><h2>自我复核</h2><span className="status">{(chart.selfReview.issues as string[]).length ? '存在问题' : '一致性检查通过'}</span></div><div className="review-grid">{Object.entries(checks).map(([key,label]) => <div key={key}><span>{label}</span><b>{chart.selfReview[key] === 'pass' || chart.selfReview[key] === 'complete' ? '通过' : chart.selfReview[key] === 'insufficient' ? '信息不足' : '需复核'}</b></div>)}</div><p className="field-hint">{chart.selfReview.scope}</p><Link className="inline-link" href="/verify">重新校验命盘 →</Link></section>
    <AiQuestions/>
  </>;
}
