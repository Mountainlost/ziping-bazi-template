'use client';
import Image from 'next/image';
import { useState } from 'react';
import type { Chart } from '@/lib/types';
import { Pillars } from './shared';
import { FileImage, CaretDown, CaretUp, ArrowUpRight } from '@phosphor-icons/react';

export function ChartAttachment({ chart }: { chart: Chart }) {
  const [open,setOpen] = useState(false);
  const [format,setFormat] = useState<'image'|'text'>('image');
  return <section className={`chart-attachment ${open ? 'is-open' : ''}`}>
    <button className="attachment-toggle" type="button" aria-expanded={open} aria-controls="chart-attachment-body" onClick={() => setOpen(!open)}>
      <span className="attachment-icon" aria-hidden="true"><FileImage size={25} weight="duotone"/></span><span><b>排盘附件</b><small>命盘图或文字 · 可选查看</small></span><span className="attachment-meta">1 项附件</span><span className="attachment-arrow" aria-hidden="true">{open ? <CaretUp size={20}/> : <CaretDown size={20}/>}</span>
    </button>
    {open && <div id="chart-attachment-body" className="attachment-body"><div className="attachment-toolbar"><div className="segmented"><button type="button" onClick={() => setFormat('image')} aria-pressed={format==='image'}>图片</button><button type="button" onClick={() => setFormat('text')} aria-pressed={format==='text'}>文字</button></div><a href={`/api/v1/charts/${chart.id}/image.svg`} target="_blank" rel="noreferrer" className="inline-link">打开排盘图 <ArrowUpRight size={18} aria-hidden="true"/></a></div>
      {format==='image' ? <Image className="chart-attachment-image" src={`/api/v1/charts/${chart.id}/image.svg`} alt="根据当前锁定命盘生成的四柱、藏干与大运图" width={1060} height={940} unoptimized/> : <Pillars chart={chart}/>}
      <p className="field-hint">附件由当前锁定事实生成，未计算的项目不补写；完整解读与证据见正文。</p></div>}
  </section>;
}
