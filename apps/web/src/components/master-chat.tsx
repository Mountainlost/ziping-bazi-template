'use client';
import Image from 'next/image';
import Link from 'next/link';
import { useEffect, useRef, useState } from 'react';
import { ArrowRight, PaperPlaneTilt } from '@phosphor-icons/react';
import { api, type Evidence } from '@/lib/types';
import { EvidenceList } from './shared';
import { useSession } from './session';

type Answer={id?:number;question:string;answer:string;evidence:Evidence[];sources?:{title:string;url:string}[];onlineUsed?:boolean;remaining?:number;presentation?:string};
type Access={authorized:boolean;remaining:number;history:Answer[]};
const suggestions=[{label:'事业方向',question:'事业上能详细说说吗？'},{label:'情感方向',question:'我的配偶在哪个方位？'},{label:'财运方向',question:'财运上能详细说说吗？'}];
function Paragraphs({text,sections=false}:{text:string;sections?:boolean}){
  const blocks: {text:string;heading?:boolean}[]=[];
  let lines:string[]=[];
  function flush(){
    if(lines.length)blocks.push({text:lines.join('\n')});
    lines=[];
  }
  for(const line of text.split(/\r?\n/)){
    const heading=sections&&line.trim().match(/^(?:#{2,3}\s+(.+?)|\*\*([^*]+)\*\*)$/);
    if(heading){flush();blocks.push({text:heading[1]||heading[2],heading:true});}
    else if(!line.trim())flush();
    else lines.push(line);
  }
  flush();
  return <>{blocks.map((block,i)=>block.heading?<h3 key={i}>{block.text}</h3>:
    <p key={i}>{block.text.split(/(\*\*[^*]+\*\*)/g).map((part,j)=>j%2===1?<strong key={j}>{part.slice(2,-2)}</strong>:part)}</p>)}</>;
}

export function MasterChat({chartId}:{chartId:string|null}){
  const {chart}=useSession();
  const [question,setQuestion]=useState('');
  const [configured,setConfigured]=useState<boolean|null>(null);
  const [access,setAccess]=useState<Access>({authorized:false,remaining:0,history:[]});
  const [code,setCode]=useState('');
  const [pending,setPending]=useState<'question'|'rederive'|null>(null);
  const busy=pending!==null;
  const [activating,setActivating]=useState(false);
  const [error,setError]=useState('');
  const [readingError,setReadingError]=useState('');
  const [draftSaved,setDraftSaved]=useState(true);
  const input=useRef<HTMLTextAreaElement>(null);
  const passInput=useRef<HTMLInputElement>(null);
  const bottom=useRef<HTMLDivElement>(null);
  const reading=useRef<HTMLElement>(null);
  const key=`ziping-master-draft:${chartId||'example'}`;
  useEffect(()=>{
    const controller=new AbortController();
    api<{aiConfigured:boolean}>('/status',undefined,controller.signal).then(data=>setConfigured(data.aiConfigured)).catch(e=>{if(e.name!=='AbortError')setError('问答状态暂时未能读取，请稍后刷新。');});
    if(chartId) api<Access>(`/charts/${chartId}/access`,undefined,controller.signal).then(setAccess).catch(e=>{if(e.name!=='AbortError')setError(e.message);});
    queueMicrotask(()=>{if(controller.signal.aborted)return;try{setQuestion(sessionStorage.getItem(key)||'');}catch{setDraftSaved(false);}});
    return()=>controller.abort();
  },[chartId,key]);
  function update(text:string){setQuestion(text);try{sessionStorage.setItem(key,text);setDraftSaved(true);}catch{setDraftSaved(false);}}
  async function activate(event:React.FormEvent){
    event.preventDefault(); if(!chartId||activating)return;
    setActivating(true);setError('');
    try{setAccess(await api<Access>(`/charts/${chartId}/access`,{code}));setCode('');}
    catch(e){setError(e instanceof Error?e.message:'签子未能验证，请重试。');}
    finally{setActivating(false);}
  }
  async function send(event:React.FormEvent){
    event.preventDefault();
    await requestReading(question.trim(),'question');
  }
  async function requestReading(text:string,mode:'question'|'rederive'){
    if(!chartId||!configured||!access.authorized||!text||busy||access.remaining<=0)return;
    const setRequestError=mode==='rederive'?setReadingError:setError;
    setPending(mode);setRequestError('');
    try{
      const result=await api<Omit<Answer,'question'>>(`/charts/${chartId}/ask`,{question:text,mode});
      setAccess(a=>({...a,remaining:result.remaining??Math.max(0,a.remaining-1),history:[...a.history,{...result,question:text}]}));
      if(mode==='question')update('');
      requestAnimationFrame(()=> (mode==='rederive'?reading.current:bottom.current)?.scrollIntoView({block:'nearest'}));
    }catch(e){
      setRequestError(e instanceof Error?e.message:'这次解读未能完成，请稍后重试。');
      // Requests that reached the model also count toward the daily cap.
      try{const state=await api<Access>(`/charts/${chartId}/access`);setAccess(state);}catch{/* Keep the last displayed report and draft. */}
    }finally{setPending(null);}
  }
  const enabled=!!chartId&&configured===true&&access.authorized&&access.remaining>0&&!busy;
  const readingHint=!chartId?'先生成默认命盘的报告，再启用大师解盘。'
    :configured===null?'正在读取服务状态。'
    :configured===false?'大师解盘暂未启用。'
    :!access.authorized?'输入大师签后，即可按已确认的命盘重新推导。'
    :access.remaining<=0?'今日额度已用完，北京时间零点恢复。'
    :'根据已确认的排盘推导一份新解读，占用 1 次提问额度。';
  const latestReading=access.history.findLast(item=>item.presentation==='rederive');
  const questions=access.history.filter(item=>item.presentation!=='rederive');
  return <>
    <section id="ziping-reading" className="master-feature" aria-labelledby="ziping-reading-heading">
      <div className="master-feature-intro">
        <div><h2 id="ziping-reading-heading">子平解盘</h2><p>从原局看性格、事业、财运和感情，再对照大运与近年的变化。</p><small>{readingHint}</small></div>
        {chartId
          ? <button className="scan-primary" type="button" disabled={configured!==true||busy||(access.authorized&&!enabled)} onClick={()=>{if(access.authorized)void requestReading('子平解盘','rederive');else passInput.current?.focus();}}>
              {pending==='rederive'?'解盘中…':latestReading?'再次子平解盘':'开始子平解盘'} <ArrowRight size={18} aria-hidden="true"/>
            </button>
          : <Link className="scan-primary" href={chart?'/verify':'/#birth-form'}>查看基础排盘 <ArrowRight size={18} aria-hidden="true"/></Link>}
      </div>
      {pending==='rederive'&&<p className="master-answer-pending" role="status">正在推导原局、各主题和运年，请稍等…</p>}
      {readingError&&<p className="master-chat-error" role="alert">{readingError}</p>}
      {latestReading&&<article ref={reading} className="master-feature-result" aria-label="子平解盘结果">
        <span className="master-generated-note">人工智能生成解读</span>
        <div className="master-answer"><Paragraphs text={latestReading.answer} sections/></div>
        {latestReading.evidence.length>0&&<EvidenceList items={latestReading.evidence}/>}
      </article>}
    </section>
    <aside className="master-chat" aria-labelledby="master-chat-heading">
    <header><div className="master-chat-avatar"><Image src="/images/master-scholar-v2.png" alt="" width={80} height={80}/></div><div><h2 id="master-chat-heading">子平大师</h2><p>我们就从这份报告聊起。</p></div><span>{configured===null?'连接中':configured?(access.authorized?'已启用':'凭签启用'):'尚未配置'}</span></header>
    <p className="master-greeting">先聊你最关心的一件事。我会结合这份报告，把原因和接下来可以留意的地方慢慢说清楚。</p>
    <div className="master-questions">{suggestions.map(item=><button type="button" key={item.label} onClick={()=>{update(item.question);input.current?.focus();}}><span><b>{item.label}</b><small>{item.question}</small></span><ArrowRight size={18} aria-hidden="true"/></button>)}</div>
    {!chartId?<p className="master-access-note"><Link href="/#birth-form">先生成并确认自己的命盘</Link>，再凭大师签继续解读。</p>:configured===false?<p className="master-access-note">大师解盘暂未启用，仍可排盘并阅读报告。</p>:configured&&!access.authorized?<form className="master-pass-form" onSubmit={activate}><label htmlFor="master-pass">输入大师签</label><p>普通大师签首次启用后绑定当前报告，以后仍可凭原签查看。</p><div><input ref={passInput} id="master-pass" type="password" autoComplete="off" value={code} onChange={e=>setCode(e.target.value)} placeholder="粘贴完整大师签" minLength={12} maxLength={120} required/><button type="submit" disabled={activating}>{activating?'验证中…':'启用'}</button></div></form>:null}
    {questions.length>0&&<div className="master-conversation" aria-label="已保存的问答">{questions.map((item,i)=><article className="master-exchange" key={item.id??i}><p className="master-user-question">{item.question}</p><div className="master-answer"><Paragraphs text={item.answer}/>{item.evidence?.length>0&&<EvidenceList items={item.evidence}/>} {!!item.sources?.length&&<details className="master-online-sources"><summary>联网查证来源</summary><ul>{item.sources.filter(s=>/^https?:\/\//i.test(s.url)).map((s,j)=><li key={j}><a href={s.url} target="_blank" rel="noopener noreferrer">{s.title||new URL(s.url).hostname}</a></li>)}</ul></details>}</div></article>)}<div ref={bottom}/></div>}
    {pending==='question'&&<p className="master-answer-pending" role="status">正在结合命盘整理本次解读，请稍等…</p>}
    {error&&<p className="master-chat-error" role="alert">{error}</p>}
    <form className="master-chat-compose" onSubmit={send}><label htmlFor="master-question" className="sr-only">关于当前报告的问题</label><textarea id="master-question" ref={input} value={question} onChange={event=>update(event.target.value)} placeholder="把你想问的写在这里……" maxLength={1000} disabled={busy}/><div><small>{!draftSaved?'草稿未能保存，请先复制内容。':busy?'正在解读，请稍等。':enabled?'可以继续追问，每次先聊一个重点。':'问题草稿保留在当前浏览器标签页。'}</small><button type="submit" disabled={!enabled||!question.trim()} aria-label="发送问题"><PaperPlaneTilt size={22} weight="fill" aria-hidden="true"/></button></div></form>
    <p className="master-question-limit">每日问答上限 50 次，北京时间零点更新。{access.authorized?`今日还可提问 ${access.remaining} 次。`:''}</p>
    </aside>
  </>;
}
