'use client';
import Link from 'next/link';
import { useEffect, useRef, useState, type CSSProperties } from 'react';
import { advanceBelt, bookPosition, scanCoverage, bookCopies } from '@/lib/book-conveyor';

const books = [
  { title: '滴天髓', style: 'white', subtitle: ['五行之理', '衰旺之辨'], headline: '先看自身，再看机会。', labels: ['状态', '做法', '节奏'], rows: ['事情一多，先分清哪些值得亲自投入。', '把最擅长的一件事做好，再接下一件。', '给忙碌留点余地，做事才能持续下去。'] },
  { title: '三命通会', style: 'navy', subtitle: ['四柱 · 十神', '格局 · 行运'], headline: '把本事变成实际成果。', labels: ['事业', '合作', '收入'], rows: ['从能积累经验的工作开始，做出自己的长处。', '不用一个人包办，先把分工和责任说清。', '让能力能够重复交付，比追着机会跑更稳。'] },
  { title: '子平真诠', style: 'silver', subtitle: ['格局与取用', '方法与条理'], headline: '找到长处，也看清条件。', labels: ['长处', '配合', '取舍'], rows: ['看懂自己擅长什么，也知道哪里需要支持。', '把专业、资源和执行放在一起考虑。', '一条路能不能走通，要看具体条件是否齐备。'] },
  { title: '渊海子平', style: 'wave', subtitle: ['干支 · 五行', '十神 · 格局'], headline: '看十年，也安排好眼前。', labels: ['十年', '今年', '当下'], rows: ['先看较长阶段的重点，再理解眼前的变化。', '把一年的任务放回自己的长期计划里。', '该积累时沉下心，该调整时留出空间。'] },
];
type Spark = { x: number; y: number; vx: number; vy: number; life: number; size: number };
const clamp = (value: number, min: number, max: number) => Math.max(min, Math.min(value, max));
function hash(a: number, b: number, c: number) {
  let n = (Math.imul(a, 374761393) + Math.imul(b, 668265263) + Math.imul(c, 2147483647)) | 0;
  n = Math.imul(n ^ (n >>> 13), 1274126177);
  return ((n ^ (n >>> 16)) >>> 0) / 4294967296;
}

export function BookConveyor() {
  const [copies, setCopies] = useState(3);
  const beltBooks = Array.from({ length: copies }, () => books).flat();
  const rootRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const root = rootRef.current;
    const canvas = canvasRef.current;
    if (!root || !canvas) return;
    const covers = Array.from(root.querySelectorAll<HTMLElement>('.conveyor-book'));
    const readings = Array.from(root.querySelectorAll<HTMLElement>('.conveyor-reading'));
    const ctx = canvas.getContext('2d');
    const media = matchMedia('(prefers-reduced-motion: reduce)');
    let width = 0, bookWidth = 0, bookHeight = 0, height = 0, span = 0;
    let state = { offset: 0, velocity: 0 };
    let reduced = media.matches, hovered = false, focused = false, dragging = false;
    let visible = true, alive = true, frame = 0, previous = 0, lastFx = 0;
    let pointerX = 0, pointerTime = 0;
    let sparks: Spark[] = [];
    const positions = new Array<number>(beltBooks.length).fill(0);

    function paintFx(now: number, dt: number) {
      if (!ctx) return;
      const scanner = width / 2;
      const top = 44;
      ctx.clearRect(0, 0, width, height);
      const tick = reduced ? 0 : Math.floor(now / 110);
      for (let i = 0; i < positions.length; i++) {
        const x = positions[i];
        if (!scanCoverage(x, bookWidth, scanner).crossing) continue;
        const reach = Math.min(115, x + bookWidth - scanner);
        if (reach <= 0) continue;
        const haze = ctx.createLinearGradient(scanner - 22, 0, scanner + reach, 0);
        haze.addColorStop(0, '#4b79ff18'); haze.addColorStop(0.25, '#6493ff32'); haze.addColorStop(1, '#6992ff00');
        ctx.fillStyle = haze; ctx.fillRect(scanner - 22, top - 12, reach + 22, bookHeight + 24);
        const start = Math.floor((scanner - x - 95) / 4);
        const end = Math.ceil((scanner - x + reach) / 4);
        for (let col = start; col < end; col++) {
          const sx = x + col * 4;
          const distance = sx - scanner;
          const chance = distance < 0 ? Math.pow(1 + distance / 100, 1.6) * 0.68 : Math.pow(1 - distance / 118, 1.7) * 0.88;
          for (let row = -4; row < Math.ceil(bookHeight / 4) + 4; row++) {
            const density = row < 0 || row * 4 > bookHeight ? 0.15 : 1;
            if (hash(col, row, i) > chance * density || hash(col, row, tick + 97) < 0.14) continue;
            const tone = hash(row, col, i + 31);
            ctx.globalAlpha = 0.42 + tone * 0.56;
            ctx.fillStyle = ['#315df2', '#5c84ff', '#8eacff', '#c5d8ff', '#f5f9ff'][Math.floor(tone * 5)];
            const size = 1.8 + tone * 3.1;
            ctx.fillRect(sx + (hash(col, row, 2) - 0.5) * 2, top + row * 4, size, size);
          }
        }
        if (!reduced && sparks.length < 70) {
          for (let j = 0; j < 2; j++) {
            const seed = Math.floor(now * 10) + j;
            sparks.push({ x: scanner + hash(seed, j, 1) * 20, y: top + hash(seed, j, 2) * bookHeight, vx: -30 - hash(seed, j, 3) * 65 + state.velocity * 0.25, vy: (hash(seed, j, 4) - 0.5) * 32, life: 0.4 + hash(seed, j, 5) * 0.6, size: 1 + hash(seed, j, 6) * 2 });
          }
        }
      }
      if (!reduced) {
        sparks = sparks.filter(spark => (spark.life -= dt) > 0);
        for (const spark of sparks) {
          spark.x += spark.vx * dt; spark.y += spark.vy * dt;
          ctx.globalAlpha = Math.min(0.75, spark.life);
          ctx.fillStyle = '#5783ff'; ctx.fillRect(spark.x, spark.y, spark.size, spark.size);
        }
      }
      ctx.globalAlpha = 1;
    }

    function draw(now: number, dt: number, force = false) {
      for (let i = 0; i < covers.length; i++) {
        const x = bookPosition(state.offset, i, span, covers.length);
        positions[i] = x;
        const { textWidth, bookWidth: remaining } = scanCoverage(x, bookWidth, width / 2);
        const transform = `translate3d(${x}px,0,0)`;
        covers[i].style.transform = transform;
        covers[i].style.clipPath = `inset(-16px -20px -30px ${textWidth}px)`;
        covers[i].style.maskImage = textWidth > 0 ? `linear-gradient(90deg, transparent ${textWidth}px, #000 ${textWidth + 25}px)` : 'none';
        covers[i].style.visibility = remaining > 0 && x < width && x + bookWidth > 0 ? 'visible' : 'hidden';
        readings[i].style.transform = transform;
        readings[i].style.clipPath = `inset(0 ${remaining}px 0 0)`;
        readings[i].style.visibility = textWidth > 0 && x + bookWidth > 0 ? 'visible' : 'hidden';
        readings[i].style.opacity = String(Math.pow(textWidth / bookWidth, 3));
      }
      if (force || now - lastFx >= 32) { paintFx(now, Math.min(0.05, dt * 2)); lastFx = now; }
    }

    function animate(now: number) {
      const dt = previous ? Math.min((now - previous) / 1000, 0.05) : 0;
      previous = now;
      if (!dragging) state = advanceBelt(state, dt, focused ? 0 : -width * 0.045 * (hovered ? 0.35 : 1), reduced);
      draw(now, dt);
      if (alive && visible && !document.hidden && !reduced) frame = requestAnimationFrame(animate);
    }

    function restart() {
      cancelAnimationFrame(frame); previous = 0;
      root!.dataset.motion = reduced ? 'reduced' : !visible || document.hidden ? 'resting' : 'running';
      if (!alive || !width) return;
      if (reduced) { state.velocity = 0; sparks = []; draw(performance.now(), 0, true); }
      else if (visible && !document.hidden) frame = requestAnimationFrame(animate);
    }

    function measure() {
      const oldSpan = span;
      width = root!.clientWidth;
      bookWidth = clamp(width * 0.225, 265, 365);
      bookHeight = bookWidth * 1.33;
      span = bookWidth + clamp(width * 0.033, 38, 58);
      const needed = bookCopies(width, span, books.length);
      if (needed !== copies) { setCopies(needed); return; }
      height = bookHeight + 90;
      state.offset = oldSpan ? state.offset * span / oldSpan : width / 2 - bookWidth * 0.40;
      root!.style.setProperty('--book-width', `${bookWidth}px`);
      root!.style.setProperty('--book-height', `${bookHeight}px`);
      root!.style.setProperty('--belt-height', `${height}px`);
      const dpr = Math.min(devicePixelRatio || 1, 1.5);
      canvas!.width = Math.round(width * dpr); canvas!.height = Math.round(height * dpr);
      ctx?.setTransform(dpr, 0, 0, dpr, 0, 0);
      draw(performance.now(), 0, true);
      root!.dataset.ready = 'true'; restart();
    }

    function enter() { hovered = true; }
    function leave() { hovered = false; }
    function focus() { focused = root!.matches(':focus-visible'); }
    function blur() { focused = false; }
    function down(event: PointerEvent) {
      if (event.button !== 0 || !event.isPrimary) return;
      dragging = true; focused = false; pointerX = event.clientX; pointerTime = event.timeStamp; state.velocity = 0;
      root!.dataset.dragging = 'true'; root!.setPointerCapture(event.pointerId);
    }
    function move(event: PointerEvent) {
      if (!dragging) return;
      const dx = event.clientX - pointerX;
      state.offset += dx;
      state.velocity = dx / Math.max(8, event.timeStamp - pointerTime) * 800 + state.velocity * 0.2;
      pointerX = event.clientX; pointerTime = event.timeStamp;
      if (reduced) draw(performance.now(), 0, true);
    }
    function up(event: PointerEvent) {
      dragging = false; root!.dataset.dragging = 'false';
      if (event.timeStamp - pointerTime > 100) state.velocity = 0;
      if (root!.hasPointerCapture(event.pointerId)) root!.releasePointerCapture(event.pointerId);
      if (reduced) state.velocity = 0;
    }
    function cancel() { if (dragging) { dragging = false; state.velocity = 0; root!.dataset.dragging = 'false'; } }
    function wheel(event: WheelEvent) {
      if (Math.abs(event.deltaX) <= Math.abs(event.deltaY)) return;
      event.preventDefault(); state.offset -= event.deltaX; state.velocity -= event.deltaX * 2;
      if (reduced) { state.velocity = 0; draw(performance.now(), 0, true); }
    }
    function key(event: KeyboardEvent) {
      if (event.key !== 'ArrowLeft' && event.key !== 'ArrowRight') return;
      event.preventDefault(); focused = true;
      state.offset += (event.key === 'ArrowRight' ? -1 : 1) * span * 0.6; state.velocity = 0;
      draw(performance.now(), 0, true);
    }
    function preference() { reduced = media.matches; restart(); }
    const resize = new ResizeObserver(measure);
    const visibility = new IntersectionObserver(entries => { visible = entries[0]?.isIntersecting ?? false; restart(); }, { rootMargin: '120px' });
    resize.observe(root); visibility.observe(root);
    media.addEventListener('change', preference); document.addEventListener('visibilitychange', restart);
    root.addEventListener('pointerenter', enter); root.addEventListener('pointerleave', leave);
    root.addEventListener('focus', focus); root.addEventListener('blur', blur);
    root.addEventListener('pointerdown', down); root.addEventListener('pointermove', move);
    root.addEventListener('pointerup', up); root.addEventListener('pointercancel', cancel); root.addEventListener('lostpointercapture', cancel);
    root.addEventListener('wheel', wheel, { passive: false }); root.addEventListener('keydown', key);
    measure();
    return () => {
      alive = false; cancelAnimationFrame(frame); resize.disconnect(); visibility.disconnect();
      media.removeEventListener('change', preference); document.removeEventListener('visibilitychange', restart);
      root.removeEventListener('pointerenter', enter); root.removeEventListener('pointerleave', leave);
      root.removeEventListener('focus', focus); root.removeEventListener('blur', blur);
      root.removeEventListener('pointerdown', down); root.removeEventListener('pointermove', move);
      root.removeEventListener('pointerup', up); root.removeEventListener('pointercancel', cancel); root.removeEventListener('lostpointercapture', cancel);
      root.removeEventListener('wheel', wheel); root.removeEventListener('keydown', key);
    };
  }, [copies, beltBooks.length]);

  return <figure className="book-conveyor-figure">
    <div className="conveyor-caption">从命盘依据，到白话解读</div>
    <div ref={rootRef} className="book-conveyor" tabIndex={0} role="group" aria-label="子平典籍与解读展示。可拖动，或使用左右方向键查看；键盘聚焦时自动停留。">
      <div className="conveyor-visual" aria-hidden="true">
        <div className="conveyor-readings">{beltBooks.map((book, i) => <div className="conveyor-reading" key={i} style={{ '--book-index': i } as CSSProperties}><small>白话解读</small><h2>{book.headline}</h2><dl>{book.rows.map((text, j) => <div key={j}><dt>{book.labels[j]}</dt><dd>{text}</dd></div>)}</dl></div>)}</div>
        <div className="conveyor-covers">{beltBooks.map((book, i) => <div className={`conveyor-book book-${book.style}`} key={i} style={{ '--book-index': i } as CSSProperties}><div className="book-page-edge"/><div className="book-cover"><span className="book-series">子平典籍</span><h3>{book.title}</h3><div className="book-cover-art"><i/><i/><i/></div><p>{book.subtitle.map(line => <span key={line}>{line}</span>)}</p><div className="book-spine"/></div></div>)}</div>
        <canvas ref={canvasRef} className="conveyor-fx"/>
        <div className="conveyor-scanner"><i/></div>
      </div>
      <span className="sr-only">《滴天髓》《三命通会》《子平真诠》《渊海子平》。左侧为案例白话节选，书籍与文字的转化为视觉演示，不代表即时计算结果或古籍原文。</span>
    </div>
    <figcaption><span/><Link href="/sources#traditional-methods">子平典籍 · 方法与出处</Link><span/></figcaption>
  </figure>;
}
