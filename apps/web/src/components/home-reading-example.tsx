'use client';
import { useState } from 'react';

const sections = [
  { title: '事业', plain: ['你更适合在需要分析问题、表达想法和找到更好做法的工作里发挥长处。比起长期机械重复，更值得找能积累经验、体现判断和做出成果的事情。', '先把一项能力做深，再把它变成别人看得见的成果。你可以掌握自己的核心能力和决定权，同时借团队、平台和清楚的合作方式把事情做大。'], professional: ['案例从日干、月令与十神主题出发，围绕分析、表达及专业输出组织事业解读。', '本节为匿名案例的阅读节选。正式报告中的格局、旺衰及喜用，以用户确认后保存的命盘与对应依据为准。'] },
  { title: '财运', plain: ['你不是看不到机会，真正要留意的是机会一多，就想同时铺开。先把手里最重要的一件事做成，再逐步扩大，会更容易把机会留在自己手里。', '只要涉及共同投入、共同支出或收入分配，就提前把账和责任讲清楚。感情归感情，约定归约定，后面的合作会轻松得多。'], professional: ['案例围绕财星主题与自身条件的关系，解释机会、投入规模和合作责任。', '见财星不直接等于获得财富。具体解读需要结合原局、大运及流年已经计算完成的结果。'] },
  { title: '感情', plain: ['你观察细，对相处中的细节有自己的标准。但自己已经想明白的事，对方未必已经知道。你不说，对方就很难准确知道你在意什么。', '有需求就直接说，有分歧先把各自的想法讲完整。能长期相处的人，不只是眼下合得来，也要能一起处理意见不同的时候。'], professional: ['案例在感情主题中解释表达方式、相处需求与共同责任。', '桃花、夫妻星、夫妻宫及相关方位，只有在系统实际计算并保留依据后，才会进入个人报告。'] },
];

export function HomeReadingExample() {
  const [professional, setProfessional] = useState(false);
  return <section className="home-reading-example" id="reading-example" aria-labelledby="example-heading"><header><div><span>解盘案例 · 姓名与出生资料已隐去</span><h2 id="example-heading">先练本事，再把机会接稳。</h2></div><div className="example-mode" role="group" aria-label="案例阅读版本"><button type="button" aria-pressed={!professional} onClick={() => setProfessional(false)}>白话版</button><button type="button" aria-pressed={professional} onClick={() => setProfessional(true)}>专业版</button></div></header><div className="home-example-body">{sections.map(section => <article key={section.title}><h3>{section.title}</h3><div>{(professional ? section.professional : section.plain).map(text => <p key={text}>{text}</p>)}</div></article>)}</div><p className="home-example-note">本案例为解读节选，含人工智能生成内容。传统文化解读，仅供参考。</p></section>;
}
