'use client';
import type { CSSProperties } from 'react';
import { useSession } from './session';
import { Compass } from '@phosphor-icons/react';

export function CalendarMotion() {
  const {motion,setMotion}=useSession();
  return <div className="calendar-motion" aria-label="历法演示动画，不代表真实命盘结果"><div className="calendar-motion-top"><span>十干 · 十二支</span><button type="button" onClick={() => setMotion(!motion)} aria-pressed={!motion}>{motion ? '暂停动效' : '开启动效'}</button></div><div className="calendar-wheel" aria-hidden="true"><div className="wheel-orbit"/>
    <div className="wheel-labels">{Array.from('子丑寅卯辰巳午未申酉戌亥').map((b,i)=><span key={b} style={{'--angle':`${i*30}deg`} as CSSProperties}>{b}</span>)}</div><div className="wheel-center"><Compass size={31} weight="duotone" color="#3d5dbb" aria-hidden="true"/><small>历法有序</small></div><i className="wheel-pointer"/></div>
    <div className="calendar-pillars">{['年','月','日','时'].map((b,i)=><div key={b} style={{'--delay':`${i*.16}s`} as CSSProperties}><b>{b}</b><span>柱</span></div>)}</div><small className="calendar-caption">历法演示 · 实际命盘由出生资料计算</small></div>;
}
