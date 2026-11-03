export type BeltState = { offset: number; velocity: number };

export function bookCopies(viewport: number, span: number, titles = 4) {
  return Math.max(2, Math.ceil((viewport + 2 * span) / (span * titles)));
}

export function bookPosition(offset: number, index: number, span: number, count: number) {
  const period = span * count;
  return ((offset + index * span + span) % period + period) % period - span;
}

export function scanCoverage(x: number, width: number, scanner: number) {
  const textWidth = Math.max(0, Math.min(width, scanner - x));
  return { textWidth, bookWidth: width - textWidth, crossing: textWidth > 0 && textWidth < width };
}

export function advanceBelt(state: BeltState, seconds: number, target: number, reduced: boolean): BeltState {
  if (reduced) return { offset: state.offset, velocity: 0 };
  const dt = Math.max(0, Math.min(seconds, 0.05));
  const velocity = state.velocity + (target - state.velocity) * (1 - Math.exp(-2.2 * dt));
  return { offset: state.offset + velocity * dt, velocity };
}
