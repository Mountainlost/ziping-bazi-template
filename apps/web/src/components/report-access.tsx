'use client';
import Link from 'next/link';
import { useRef, useState } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowUpRight, X } from '@phosphor-icons/react';
import { useSession } from './session';
import { api, type Chart } from '@/lib/types';

export function ReportAccess() {
  const dialog = useRef<HTMLDialogElement>(null);
  const { chart, setChart } = useSession();
  const router=useRouter();
  const [code,setCode]=useState('');
  const [busy,setBusy]=useState(false);
  const [error,setError]=useState('');
  function startChart(event: React.MouseEvent<HTMLAnchorElement>) {
    dialog.current?.close();
    const form = document.getElementById('birth-form');
    if (window.location.pathname === '/' && !window.location.search && form) {
      event.preventDefault();
      window.location.hash = 'birth-form';
      form.scrollIntoView();
    }
  }
  async function lookup(event:React.FormEvent){
    event.preventDefault();if(busy)return;setBusy(true);setError('');
    try{const report=await api<Chart>('/access/report',{code});setChart(report);setCode('');dialog.current?.close();router.push('/overview');}
    catch(e){setError(e instanceof Error?e.message:'未能读取报告，请重试。');}
    finally{setBusy(false);}
  }
  if (chart?.locked) return <Link className="header-report-access" href="/overview">阅读我的报告 <ArrowUpRight size={21} aria-hidden="true"/></Link>;
  return <><button className="header-report-access" type="button" aria-haspopup="dialog" onClick={() => dialog.current?.showModal()}>凭签查看报告 <ArrowUpRight size={21} aria-hidden="true"/></button><dialog ref={dialog} className="report-access-dialog" aria-labelledby="report-access-title" onClick={event => { if (event.target === event.currentTarget) dialog.current?.close(); }}><button className="report-access-close" aria-label="关闭" type="button" onClick={() => dialog.current?.close()}><X size={23} aria-hidden="true"/></button><h2 id="report-access-title">找回你的解盘报告</h2><p>输入已绑定报告的签子，即可继续阅读原来的报告。</p><form className="master-pass-form" onSubmit={lookup}><label htmlFor="report-pass">完整签子</label><input id="report-pass" type="password" autoComplete="off" value={code} onChange={e=>setCode(e.target.value)} minLength={12} maxLength={120} required/>{error&&<p role="alert" className="master-chat-error">{error}</p>}<button className="scan-primary" type="submit" disabled={busy}>{busy?'正在读取…':'查看原报告'}<ArrowUpRight size={21} aria-hidden="true"/></button></form><Link href="/#birth-form" className="scan-text-link" onClick={startChart}>第一次来？先开始排盘</Link></dialog></>;
}
