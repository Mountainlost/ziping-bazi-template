'use client';
import { type Chart } from '@/lib/types';
import { JudgmentCard, EvidenceList } from './shared';
import { useSession } from './session';
import { ReadingChapter } from './report-reader';

export function Analysis({ chart }: { chart: Chart }) {
  const {mode}=useSession();
  const professional=mode==='professional';
  if(!professional) return <div className="analysis-reading">{chart.report.chapters.filter(c=>[2,3,4].includes(c.number)).map(ch=><ReadingChapter key={ch.number} chapter={ch} mode="plain"/>)}</div>;
  return <><div className="mode-switch"><span>专业版 · 规则结论与证据</span></div>
    <JudgmentCard title="01 / 身强身弱" value={chart.strength} professional={professional}/>
    <details className="paper"><summary>旺衰的替代解释与成立条件</summary>{chart.strength.alternativeInterpretations.map(a => <div key={a.conclusion}><h3>{a.conclusion}</h3><p>{a.reason}</p><ul>{a.conditions.map(c => <li key={c}>{c}</li>)}</ul></div>)}<p>{chart.strength.method}</p></details>
    <JudgmentCard title="02 / 格局" value={chart.pattern} professional={professional}/>
    <section className="paper"><h3>常格与从格 · 分别核实条件</h3><div className="comparison">{chart.pattern.alternativePatterns.map(p => <div key={p.name}><h4>{p.name}</h4><p>{p.current}</p><ul>{p.conditions.map(c => <li key={c}>{c}</li>)}</ul></div>)}</div><details><summary>本版未采用的推断</summary><ul>{chart.pattern.rejectedConditions.map(c => <li key={c}>{c}</li>)}</ul></details></section>
    <JudgmentCard title="03 / 喜忌用神" value={chart.usefulGod} professional={professional}/>
    <section className="paper"><div className="facts-grid"><div><small>扶抑首选</small><h3>{chart.usefulGod.primaryUsefulGod}</h3></div><div><small>辅助有利元素</small><h3>{chart.usefulGod.supportingFavorableElements.join('、') || '暂不独定'}</h3></div><div><small>需谨慎的元素</small><p>{chart.usefulGod.unfavorableElements.join('、') || '暂不独定'}</p></div><div><small>调候参考</small><h3>{chart.usefulGod.climate.element}</h3></div></div><p>扶抑与调候解决的问题不同，并不一定矛盾。{chart.usefulGod.climate.scope}。</p><details><summary>通关条件</summary>{chart.usefulGod.mediation.length ? chart.usefulGod.mediation.map(m => <p key={m.between.join('')}>{m.between.join('与')}之间以{m.element}通关：{m.status}</p>) : <p>未识别透干相克组合，不额外补判通关用神。</p>}</details></section>
    <section className="paper"><h2>原局刑冲合害</h2>{chart.relations.length ? chart.relations.map((r,i) => <div className="relation-row" key={i}><b>{r.type} · {r.characters}</b><p>{r.explanation}</p></div>) : <p>未命中本版关系表。</p>}<EvidenceList items={chart.strength.evidence.filter(e => e.factor === '刑冲合会')}/></section>
  </>;
}
