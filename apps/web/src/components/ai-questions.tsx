'use client';
import Link from 'next/link';
import { ChatCircleText, ArrowUpRight } from '@phosphor-icons/react';

export function AiQuestions() {
  return <section id="ai-questions" data-chapter="13" className="ai-questions"><div className="ai-question-heading"><span className="ai-question-symbol"><ChatCircleText size={29} weight="duotone" aria-hidden="true"/></span><div><h2>大师解盘</h2><p>读完基础报告，再看整盘推导。</p></div></div><p>用已确认的排盘，从原局主线重新讲到性格、事业、财运、感情和运年。</p><Link className="primary" href="/master#ziping-reading">查看子平解盘 <ArrowUpRight size={18} aria-hidden="true"/></Link></section>;
}
