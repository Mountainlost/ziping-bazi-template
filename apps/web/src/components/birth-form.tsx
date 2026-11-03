'use client';
import { useEffect, useState, type FormEvent } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { api, type Birth, type Candidates, type Chart, type Location } from '@/lib/types';
import { useSession } from './session';

const clockOptions = (count: number) => Array.from({length:count},(_,i)=>String(i).padStart(2,'0'));
const hours = clockOptions(24);
const minutes = clockOptions(60);

export function BirthForm() {
  const editing = useSearchParams().get('edit') === '1';
  const { chart } = useSession();
  const previous = editing ? chart : null;
  return <BirthFormFields key={previous?.id ?? 'new'} initial={previous?.input}/>;
}

function BirthFormFields({ initial }: { initial?: Birth }) {
  const router = useRouter();
  const { setChart, setCandidates } = useSession();
  const [locations, setLocations] = useState<Location[]>([]);
  const [accuracy, setAccuracy] = useState(initial?.accuracy || 'exact');
  const [calendar, setCalendar] = useState(initial?.calendar || 'solar');
  const [place, setPlace] = useState({province:initial?.province || '',city:initial?.city || '',district:initial?.district || ''});
  const [locationError, setLocationError] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [initialHour, initialMinute] = (initial?.time || '').split(':');
  useEffect(() => {
    if (window.location.hash === '#birth-form') {
      document.getElementById('birth-form')?.scrollIntoView();
    }
  }, []);
  useEffect(() => { const abort=new AbortController(); api<{ locations: Location[] }>('/locations',undefined,abort.signal).then(r => setLocations(r.locations)).catch(e => {if(e.name!=='AbortError')setLocationError('地点资料未能读取，请刷新页面重试。');}); return ()=>abort.abort(); }, []);
  const provinces=[...new Set(locations.map(l=>l.province))].sort((a,b)=>a.localeCompare(b,'zh-CN'));
  const cities=[...new Set(locations.filter(l=>l.province===place.province).map(l=>l.city))].sort((a,b)=>a.localeCompare(b,'zh-CN'));
  const cityLocations=locations.filter(l=>l.province===place.province&&l.city===place.city);
  const cityCenter=cityLocations.find(l=>!l.district);
  const location=cityLocations.find(l=>l.district===place.district) || null;
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setError(''); setLoading(true);
    if(!location){setError('请先选择出生省、市和区县，系统会自动匹配地点坐标。');setLoading(false);return;}
    const fields = new FormData(event.currentTarget);
    const birth: Birth = {name:String(fields.get('name') || ''),calendar, year:Number(fields.get('year')),month:Number(fields.get('month')),day:Number(fields.get('day')),
      leapMonth:calendar === 'lunar' && fields.get('leapMonth') === 'on', time:accuracy === 'unknown' || accuracy === 'shichen' ? null : `${fields.get('hour')}:${fields.get('minute')}`,
      accuracy, shichen:accuracy === 'shichen' ? String(fields.get('shichen')) : null,sex:String(fields.get('sex')),
      province:location.province,city:location.city,district:location.district,longitude:location.longitude,latitude:location.latitude,clockBasis:String(fields.get('clockBasis')),referenceYear:new Date().getFullYear()};
    try {
      const result = await api<Candidates>('/chart',birth);
      const selected = result.possibleCharts[0];
      const report = await api<Chart>('/analyze',{chartId:selected.id});
      setCandidates(result.possibleCharts);
      setChart(report);
      router.push('/overview');
    }
    catch(e) { setError(e instanceof Error ? e.message : '排盘失败，请检查输入。'); }
    finally { setLoading(false); }
  }
  return <form onSubmit={submit} className="birth-form" id="birth-form" autoComplete="off">
    <div className="form-heading"><div><span className="eyebrow">YOUR PERSONAL CHART</span><h2>从出生资料开始</h2></div><span className="form-step">01 <i>/</i> 03</span></div>
    <div className="form-grid personal-fields"><label>称呼（可选）<input name="name" defaultValue={initial?.name || ''} placeholder="报告中如何称呼你" maxLength={30}/></label><label>性别（用于传统大运顺逆）<select name="sex" defaultValue={initial?.sex || ''} required><option value="">请选择性别</option><option>男</option><option>女</option></select></label></div>
    <fieldset><legend>01 · 历法与日期</legend><div className="segmented" role="group" aria-label="出生历法">
      <button type="button" aria-pressed={calendar === 'solar'} onClick={() => setCalendar('solar')}>公历</button><button type="button" aria-pressed={calendar === 'lunar'} onClick={() => setCalendar('lunar')}>农历</button></div>
      <div className="date-fields"><label>出生年<input name="year" type="number" defaultValue={initial?.year} min="1901" max="2098" required/></label><label>月<input name="month" type="number" defaultValue={initial?.month} min="1" max="12" required/></label><label>日<input name="day" type="number" defaultValue={initial?.day} min="1" max="31" required/></label></div>
      {calendar === 'lunar' && <label className="checkbox"><input type="checkbox" name="leapMonth" defaultChecked={initial?.leapMonth}/> 闰月（仅农历）</label>}
    </fieldset>
    <fieldset><legend>02 · 出生时间</legend><div className="form-grid">
      <label>时间准确程度<select value={accuracy} onChange={e => setAccuracy(e.target.value)} name="accuracy"><option value="exact">准确</option><option value="10">大约 ±10 分钟</option><option value="30">大约 ±30 分钟</option><option value="60">大约 ±1 小时</option><option value="shichen">只知道时辰</option><option value="unknown">完全不知道</option></select></label>
      {accuracy === 'shichen' ? <label>已知钟表时辰<select name="shichen" defaultValue={initial?.shichen || '子'}>{Array.from('子丑寅卯辰巳午未申酉戌亥').map(c => <option key={c}>{c}</option>)}</select></label> : (
        <div role="group" aria-labelledby="birth-clock-label" className="birth-clock">
          <span id="birth-clock-label">出生时间（24小时制）</span>
          <div className="form-grid">
            <select name="hour" aria-label="出生小时" defaultValue={initialHour} required disabled={accuracy==='unknown'}>
              <option value="">小时</option>{hours.map(hour=><option key={hour} value={hour}>{hour} 时</option>)}
            </select>
            <select name="minute" aria-label="出生分钟" defaultValue={initialMinute} required disabled={accuracy==='unknown'}>
              <option value="">分钟</option>{minutes.map(minute=><option key={minute} value={minute}>{minute} 分</option>)}
            </select>
          </div>
        </div>
      )}
    </div><label className="wide-label">时间基准<select name="clockBasis" defaultValue={initial?.clockBasis || 'standard'}><option value="standard">UTC+8 标准时间（已还原夏令时）</option><option value="wall">当年钟表时间（系统还原中国历史夏令时）</option></select></label>
    <p className="field-hint">{accuracy === 'unknown' ? '继续三柱排盘；时柱及相关判断标记为信息不足。' : '按出生地点校正真太阳时；时间范围跨边界时，分别生成候选命盘。'}</p></fieldset>
    <fieldset><legend>03 · 出生地点</legend>
      <div className="location-fields"><label>省 / 直辖市<select name="province" value={place.province} onChange={e=>setPlace({province:e.target.value,city:'',district:''})} required disabled={!locations.length}><option value="">请选择省份</option>{provinces.map(p=><option key={p}>{p}</option>)}</select></label><label>市<select name="city" value={place.city} onChange={e=>setPlace(p=>({...p,city:e.target.value,district:''}))} required disabled={!place.province}><option value="">请选择城市</option>{cities.map(c=><option key={c}>{c}</option>)}</select></label><label>区县<select name="district" value={place.district} onChange={e=>setPlace(p=>({...p,district:e.target.value}))} required={!cityCenter} disabled={!place.city}><option value="">{cityCenter?'不确定区县，使用市中心':'请选择区县'}</option>{cityLocations.filter(l=>l.district).map(l=><option key={l.district}>{l.district}</option>)}</select></label></div>
      <p className="field-hint location-match" aria-live="polite">{locationError || (location ? `已自动匹配${location.city}${location.district}中心点，用于真太阳时校正。` : locations.length ? '选择出生地点后，系统会自动带出经纬度。' : '正在读取本地省市区资料…')}</p>
      {location&&<details className="coordinate-settings"><summary>查看自动匹配的坐标 <span>无需手填</span></summary><div className="form-grid"><label>地理经度（°E）<output className="coordinate-value" aria-label="地理经度">{location.longitude.toFixed(5)}</output></label><label>地理纬度（°N）<output className="coordinate-value" aria-label="地理纬度">{location.latitude.toFixed(5)}</output></label></div><p className="field-hint">使用区县或城市的近似中心位置，坐标制式为 WGS84。</p></details>}
    </fieldset>
    {error && <p className="error" role="alert">{error}</p>}
    {loading && <div className="calculation-motion" role="status"><span>历法校准中</span><div>{Array.from('甲乙丙丁戊己庚辛壬癸').map(g=><i key={g}>{g}</i>)}</div><small>正在计算，不显示假定结果</small></div>}
    <button className="primary full" type="submit" disabled={loading || !location}>{loading ? '正在排盘并生成报告…' : accuracy === 'unknown' ? '生成三柱报告 →' : '排盘并生成报告 →'}</button>
    <p className="form-footnote">提交后用默认命盘生成报告，可在排盘校验查看其他候选。</p>
  </form>;
}
