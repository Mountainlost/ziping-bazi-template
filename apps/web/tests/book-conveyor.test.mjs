import test from 'node:test';
import assert from 'node:assert/strict';
import { bookPosition, scanCoverage, advanceBelt, bookCopies } from '../src/lib/book-conveyor.ts';

test('超宽桌面回收位置始终在视口以外', () => {
  const width = 3840, book = 365, span = 423, count = bookCopies(width, span) * 4;
  for (const offset of [-423, 0, 80, 422]) {
    const right = Math.max(...Array.from({ length: count }, (_, i) => bookPosition(offset, i, span, count) + book));
    assert.ok(right >= width, `right edge ${right} cannot cover viewport ${width}`);
  }
});

test('拖动越过多个循环后，书籍仍保持连续间距', () => {
  const span = 380, count = 8;
  for (const offset of [-1000000, -3041, -1, 0, 3070, 1000000]) {
    const positions = Array.from({ length: count }, (_, i) => bookPosition(offset, i, span, count)).sort((a, b) => a - b);
    assert.ok(positions.every(x => x >= -span && x < span * (count - 1)));
    for (let i = 1; i < count; i++) assert.equal(positions[i] - positions[i - 1], span);
  }
});

test('扫描的书籍和文字互补，边界和画布尺寸不会为负', () => {
  for (const x of [-10000, -300, 320, 720, 2000]) {
    const { textWidth, bookWidth, crossing } = scanCoverage(x, 320, 720);
    assert.ok(textWidth >= 0 && textWidth <= 320);
    assert.ok(bookWidth >= 0 && bookWidth <= 320);
    assert.equal(textWidth + bookWidth, 320);
    assert.equal(crossing, x < 720 && x + 320 > 720);
  }
});

test('减少动态时立即静止，拖动放手后保留惯性并收敛至巡航速度', () => {
  assert.deepEqual(advanceBelt({ offset: 150, velocity: 900 }, 0.016, -90, true), { offset: 150, velocity: 0 });
  let state = { offset: 0, velocity: 700 };
  const first = advanceBelt(state, 0.016, -90, false);
  assert.ok(first.velocity > 0 && first.velocity < 700);
  for (let i = 0; i < 1000; i++) state = advanceBelt(state, 0.016, -90, false);
  assert.ok(Math.abs(state.velocity + 90) < 0.001);
  assert.ok(Number.isFinite(state.offset));
});
