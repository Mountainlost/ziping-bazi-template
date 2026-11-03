'use client';
import { useState } from 'react';
import { type Chart } from '@/lib/types';
import { CycleDetail, formatTime } from './shared';
import { useSession } from './session';
import { ReadingModeSwitch } from './report-reader';

export function Cycles({ chart }: { chart: Chart }) {
  const {mode}=useSession();
  const [luckIndex,setLuckIndex] = useState(0);
  const [year,setYear] = useState(chart.metadata.referenceYear);
  const [compare,setCompare] = useState(false);
  const [otherYear,setOtherYear] = useState(chart.metadata.referenceYear+1);
  const luck = chart.luckCycles[luckIndex];
  return <>
    <section className="paper"><div className="section-top"><h2>大运时间轴</h2><span className="status">{chart.calendar.forward ? '顺排' : '逆排'} · {chart.calendar.qiyun}</span></div>
      <div className="mode-switch"><p>{mode==='plain' ? '选一个时间段，看看工作、合作和生活更需要注意什么。' : '先看原局喜忌，再看干支作用，最后理解主题。'}</p><ReadingModeSwitch/></div>
      <div className="timeline" aria-label="选择大运">{chart.luckCycles.map((l,i) => <button onClick={() => setLuckIndex(i)} aria-pressed={i === luckIndex} key={l.index}><small>{l.startAge.toFixed(1)} 岁起</small><b>{l.stem}{l.branch}</b><span>{l.startDate.slice(0,4)} — {l.endDateExclusive.slice(0,4)}</span></button>)}</div>
      <p className="field-hint">当前选择 {luck.startDate} 至 {luck.endDateExclusive}（不含）。</p><CycleDetail analysis={luck.analysis}/>
    </section>
    <section className="paper"><div className="section-top"><h2>{mode==='plain'?'每一年的重点':'流年 · 原局与大运共同分析'}</h2><label className="checkbox"><input type="checkbox" checked={compare} onChange={e => setCompare(e.target.checked)}/>比较年份</label></div>
      <div className="year-controls"><label>流年<select value={year} onChange={e => setYear(Number(e.target.value))}>{chart.annualCycles.map(a => <option key={a.year} value={a.year}>{a.year} · {a.stem}{a.branch}</option>)}</select></label>{compare && <label>对比流年<select value={otherYear} onChange={e => setOtherYear(Number(e.target.value))}>{chart.annualCycles.map(a => <option key={a.year} value={a.year}>{a.year} · {a.stem}{a.branch}</option>)}</select></label>}</div>
      <div className={compare ? 'year-comparison' : ''}>{(compare ? [year,otherYear] : [year]).map((y,i) => {const annual = chart.annualCycles.find(a => a.year === y);return annual ? <article className="annual-block" key={`${y}-${i}`}><h3>{annual.year} · {annual.stem}{annual.branch}</h3><p className="field-hint">立春 {formatTime(annual.startDate)} 起，至下一年立春。</p><p>所处大运：{annual.activeLuck || '超出已计算范围'}</p>{annual.segments.length > 1 ? annual.segments.map(s => <section className="annual-segment" key={s.from}><h4>{s.activeLuck}</h4><small>{formatTime(s.from)} 至 {formatTime(s.toExclusive)}（不含）</small><CycleDetail analysis={s.analysis}/></section>) : <CycleDetail analysis={annual.analysis}/>}</article> : <p key={`${y}-${i}`}>该年未计算，不能补算。请重新校验资料后更改参考年。</p>;})}</div>
    </section>
  </>;
}
