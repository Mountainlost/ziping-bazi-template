'use client';
import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { api, type Chart } from '@/lib/types';

type Session = { chart: Chart | null; candidates: Chart[]; ready: boolean; error: string;
  mode: 'plain' | 'professional'; setMode: (mode: 'plain' | 'professional') => void; motion: boolean; setMotion: (motion: boolean) => void;
  setChart: (chart: Chart) => void; setCandidates: (charts: Chart[]) => void };
const Context = createContext<Session | null>(null);

export function SessionProvider({ children }: { children: React.ReactNode }) {
  const [chart, updateChart] = useState<Chart | null>(null);
  const [candidates, updateCandidates] = useState<Chart[]>([]);
  const [ready, setReady] = useState(false);
  const [error, setError] = useState('');
  const [mode,setMode] = useState<'plain'|'professional'>('plain');
  const [motion,setMotion] = useState(true);
  const setChart = useCallback((item: Chart) => { updateChart(item); sessionStorage.setItem('ziping-current', item.id); }, []);
  const setCandidates = useCallback((items: Chart[]) => { updateCandidates(items); sessionStorage.setItem('ziping-candidates', JSON.stringify(items.map(c => c.id))); }, []);
  useEffect(() => {
    const abort = new AbortController();
    const id = sessionStorage.getItem('ziping-current');
    let ids: string[] = [];
    try { const stored: unknown = JSON.parse(sessionStorage.getItem('ziping-candidates') || '[]');
      if (Array.isArray(stored)) ids = stored.filter((v): v is string => typeof v === 'string' && /^[0-9a-f-]{36}$/.test(v));
    } catch { sessionStorage.removeItem('ziping-candidates'); }
    Promise.all([id ? api<Chart>(`/charts/${encodeURIComponent(id)}`, undefined, abort.signal) : Promise.resolve(null),
      Promise.all(ids.slice(0, 10).map(i => api<Chart>(`/charts/${encodeURIComponent(i)}`, undefined, abort.signal)))])
      .then(([current, options]) => { updateChart(current); updateCandidates(options); setReady(true); })
      .catch(e => { if (e.name !== 'AbortError') { setError('上次命盘未能读取，请重新填写资料。'); setReady(true); } });
    return () => abort.abort();
  }, []);
  return <Context.Provider value={{ chart, candidates, ready, error, setChart, setCandidates, mode, setMode, motion, setMotion }}>{children}</Context.Provider>;
}

export function useSession() { const value = useContext(Context); if (!value) throw new Error('Session missing'); return value; }
