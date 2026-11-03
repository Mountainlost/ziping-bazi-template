'use client';
import { type Chart, type Evidence, type Judgment, type CycleAnalysis } from '@/lib/types';
import { useSession } from './session';

const labels: Record<string,string> = { year: '年柱', month: '月柱', day: '日柱', hour: '时柱' };
export function Pillars({ chart }: { chart: Chart }) {
  return <div className="pillars">{['year','month','day','hour'].map(key => {const p = chart.pillars[key]; return <div className={`pillar ${key === 'day' ? 'day-master' : ''}`} key={key}>
    <span className="eyebrow">{labels[key]}</span><span className="ten-god">{p?.tenGod || '信息不足'}</span>
    <strong className="stem">{p?.stem || '—'}</strong><strong className="branch">{p?.branch || '—'}</strong>
    <span className="hidden-stems">{p?.hiddenStems.join(' · ') || '未知'}</span>
    <span className="hidden-gods">{p?.hiddenStemTenGods.join(' / ') || '待补全'}</span>
    {key === 'day' && <span className="day-label">日主</span>}
  </div>;})}</div>;
}

export function EvidenceList({ items, open = false }: { items: Evidence[]; open?: boolean }) {
  return <details className="evidence" open={open || undefined}><summary>查看命理依据 <span>{items.length} 条</span></summary>
    <div className="evidence-items">{items.map(e => <div key={e.id} className="evidence-item"><b>{e.factor}</b><p>{e.explanation}</p><code>{e.source} · {e.id}</code></div>)}</div>
  </details>;
}

export function JudgmentCard({ title, value, professional = false }: { title: string; value: Judgment; professional?: boolean }) {
  const stability: Record<string,string> = { high:'较稳定', medium:'条件性结论', disputed:'存在争议 / 待核实' };
  return <section className="judgment-card"><div className="section-top"><span className="eyebrow">{title}</span><span className="status">{stability[value.stability]}</span></div>
    <h3>{value.conclusion}</h3>{value.plainLanguage && <p>{value.plainLanguage}</p>}
    <EvidenceList items={value.evidence} open={professional}/>
  </section>;
}

export function Warnings({ chart }: { chart: Chart }) {
  return <details className="warnings"><summary>计算边界与阅读提示 · {chart.warnings.length} 项</summary><ul>{chart.warnings.map(w => <li key={w}>{w}</li>)}</ul></details>;
}

export function CycleDetail({ analysis }: { analysis: CycleAnalysis }) {
  const {mode}=useSession();
  if(mode==='plain') return <div className="cycle-detail plain-cycle"><h3>{analysis.plain?.headline || '看看这一段该怎样安排'}</h3>{(analysis.plain?.paragraphs || ['先把手头的任务分清轻重缓急，给合作和变化留出时间。','需要更详细的关系说明，可以切换专业版。']).map((p,i)=><p key={i}>{p}</p>)}<div className="themes-grid">{Object.entries(analysis.plain?.focus || {}).map(([key,value])=><div key={key}><small>{key}</small><p>{value}</p></div>)}</div><EvidenceList items={analysis.evidence}/></div>;
  return <div className="cycle-detail"><div className="section-top"><h3>{analysis.conclusion}</h3><span className="status">已计算的作用与条件</span></div>
    <div className="facts-grid"><div><small>天干作用</small><p>{analysis.stemEffect || '信息不足'}</p></div><div><small>原局扶抑首选</small><p>{analysis.natalUsefulGod}</p></div></div>
    <p>{analysis.branchEffect}</p>
    <div className="relation-list">{analysis.relations.length ? analysis.relations.map((r,i) => <div key={i}><b>{r.type} · {r.characters}</b><p>{r.explanation}</p></div>) : <p>未命中本版关系表；不代表现实没有变化。</p>}</div>
    {analysis.themes && <div className="themes-grid">{Object.entries(analysis.themes).map(([k,v]) => <div key={k}><small>{{career:'事业主题',finance:'财务主题',relationship:'关系主题',pressure:'压力主题'}[k]}</small><p>{v}</p></div>)}</div>}
    <EvidenceList items={analysis.evidence}/>
  </div>;
}

export function formatTime(value?: string | null) { return value ? value.replace('T',' ').replace('+08:00','').slice(0,19) : '信息不足'; }
export function PageHeading({ number, title, description }: { number: string; title: string; description: string }) {
  return <header className="page-heading"><span className="eyebrow">子平 / {number}</span><h1>{title}</h1><p>{description}</p></header>;
}
