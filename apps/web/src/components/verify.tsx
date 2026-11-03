'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { api, type Chart, type Candidates } from '@/lib/types';
import { useSession } from './session';
import { EvidenceList, Pillars, Warnings, formatTime } from './shared';

export function Verification({ chart }: { chart: Chart }) {
  const { candidates, setChart, setCandidates } = useSession();
  const router = useRouter(); const [loading,setLoading] = useState(false); const [error,setError] = useState('');
  async function confirm() { setLoading(true); setError(''); try { setChart(await api<Chart>('/analyze',{chartId:chart.id})); router.push('/overview'); } catch(e) {setError(e instanceof Error ? e.message : '生成失败');} finally { setLoading(false); } }
  async function revalidate() { setLoading(true); setError(''); try { const r = await api<Candidates>(`/charts/${chart.id}/revalidate`,{});setCandidates(r.possibleCharts);setChart(r.possibleCharts[0]);}catch(e){setError(e instanceof Error ? e.message : '校验失败');}finally{setLoading(false);} }
  const time = chart.time;
  const facts = [['原始出生记录',`${chart.input.year}-${chart.input.month}-${chart.input.day} ${chart.input.time || (chart.input.shichen ? chart.input.shichen+'时范围' : '时辰未知')}`],
    ['出生地点',chart.input.province+' / '+chart.input.city+' / '+chart.input.district],['时间基准',chart.input.clockBasis === 'wall' ? '历史钟表时间 → UTC+8' : 'UTC+8 标准时间'],
    ['北京时间',formatTime(time.standardTime)],['地理经度',`${time.longitude}°E`],['中央经线','120°E'],
    ['经度修正',time.longitudeCorrectionMinutes === undefined ? '信息不足' : `${time.longitudeCorrectionMinutes.toFixed(2)} 分钟`],['均时差',time.equationOfTimeMinutes === undefined ? '信息不足' : `${time.equationOfTimeMinutes.toFixed(2)} 分钟`],
    ['真太阳时',formatTime(time.trueSolarTime)],['校正前 → 校正后',time.originalShichen ? `${time.originalShichen}时 → ${time.correctedShichen}时` : '信息不足'],['是否跨时辰',time.crossedShichen === undefined ? '信息不足' : time.crossedShichen ? '是 · 请核对' : '否'],['月令',chart.pillars.month?.branch+'月']];
  return <>
    {candidates.length > 1 && <section className="candidate-panel"><h2>出生时间涉及 {candidates.length} 个候选命盘</h2><p>第一项为默认命盘。可比较时间边界两侧，选择其他候选生成报告。</p><div className="candidate-options">{candidates.map((c,i) => <button key={c.id} aria-pressed={chart.id === c.id} onClick={() => {if(c.id!==chart.id)setChart(c);}}><b>{i===0?'默认命盘':`候选 ${i+1}`} · {c.pillars.hour ? c.pillars.hour.branch+'时' : '三柱暂定'}</b><span>{['year','month','day','hour'].map(k => {const p=c.pillars[k];return p ? p.stem+p.branch : '未知';}).join(' / ')}</span><small>{formatTime(c.candidateInterval?.from)} 至 {formatTime(c.candidateInterval?.to)}</small></button>)}</div></section>}
    <section className="paper"><div className="section-top"><h2>时间校正与四柱预览</h2><span className="status">{chart.locked ? '已锁定' : '等待你确认'}</span></div><Pillars chart={chart}/><div className="facts-grid verification-facts">{facts.map(([k,v]) => <div key={k}><small>{k}</small><p>{v}</p></div>)}</div>
      <p className="field-hint">{time.note || time.precisionNote} 年柱与月柱按北京时间的交节瞬间判断。</p>
    </section>
    <section className="paper"><h2>节气边界</h2><div className="term-line"><div><small>前一节</small><h3>{chart.calendar.previousSolarTerm.name}</h3><p>{formatTime(chart.calendar.previousSolarTerm.time)}</p></div><span className="term-dot">出生</span><div><small>后一节</small><h3>{chart.calendar.nextSolarTerm.name}</h3><p>{formatTime(chart.calendar.nextSolarTerm.time)}</p></div></div><p className={chart.calendar.isNearBoundary ? 'boundary-warning' : 'field-hint'}>距离最近交节约 {chart.calendar.distanceFromBoundary.toFixed(2)} 小时。{chart.calendar.isNearBoundary ? '不足24小时，请特别核实出生记录；近临界时需外部历书复核。' : '未进入24小时边界提醒范围。'}</p></section>
    <Warnings chart={chart}/>{error && <p className="error" role="alert">{error}</p>}
    <div className="actions"><button className="secondary" onClick={() => router.push('/paipan?edit=1#birth-form')}>修改出生资料</button>{chart.locked && <button className="secondary" disabled={loading} onClick={revalidate}>重新校验命盘</button>}<button className="primary" disabled={loading} onClick={confirm}>{loading ? '正在生成规则报告…' : chart.locked ? '查看已锁定报告 →' : '确认并开始分析 →'}</button></div>
    {chart.locked && <EvidenceList items={chart.monthCommand.evidence}/>}
  </>;
}
