export type Evidence = { id: string; factor: string; source: string; effect: string; explanation: string };
export type Judgment = { conclusion: string; plainLanguage?: string; stability: string; evidence: Evidence[] };
export type Pillar = { stem: string; branch: string; tenGod: string; hiddenStems: string[]; hiddenStemTenGods: string[] };
export type Relation = { type: string; members: string[]; characters: string; explanation: string };
export type CycleAnalysis = Judgment & { stemEffect?: string; branchEffect?: string; relations: Relation[]; natalUsefulGod: string; themes?: Record<string,string>; plain?: { headline: string; paragraphs: string[]; focus: Record<string,string> } };
export type LuckCycle = { index: number; stem: string; branch: string; startAge: number; startDate: string; endDateExclusive: string; startYear: number; endYear: number; analysis: CycleAnalysis };
export type AnnualCycle = { year: number; stem: string; branch: string; activeLuck: string | null; startDate: string; endDateExclusive: string; analysis: CycleAnalysis; segments: { from: string; toExclusive: string; activeLuck: string; analysis: CycleAnalysis }[] };
export type Birth = { name?: string; calendar: string; year: number; month: number; day: number; leapMonth: boolean; time: string | null; accuracy: string; shichen: string | null; sex: string; province: string; city: string; district: string; longitude: number; latitude: number; clockBasis: string; referenceYear: number };
export type ReadingText = { paragraphs: string[]; takeaway?: string; evidenceIds: string[] };
export type ReportChapter = Judgment & { number: number; title: string; body: string; plain?: ReadingText; professional?: ReadingText };
export type ReportOverview = { headline: string; paragraphs: string[]; plainTags?: string[]; dominantBranches: { branch: string; count: number }[]; focus: { label: string; text: string; chapter: number }[];
  currentLuck: { stem: string; branch: string; from: string; toExclusive: string; theme: string; plainTheme?: string; evidence: Evidence[] }[];
  currentAnnual: { year: number; stem: string; branch: string; theme: string; plainTheme?: string; evidence: Evidence[]; segments?: { from: string; toExclusive: string; activeLuck: string; theme: string; evidence: Evidence[] }[] } | null; evidence: Evidence[] };
export type Chart = {
  id: string; locked: boolean; input: Birth;
  time: { standardTime: string | null; trueSolarTime: string | null; longitude: number; centralMeridian?: number; longitudeCorrectionMinutes?: number; equationOfTimeMinutes?: number; originalShichen?: string; correctedShichen?: string; crossedShichen?: boolean; note?: string; precisionNote?: string };
  calendar: { solarDate: string; lunarDate: string; previousSolarTerm: { name: string; time: string }; nextSolarTerm: { name: string; time: string }; distanceFromBoundary: number; isNearBoundary: boolean; forward: boolean; qiyun: string; dayBoundary: string };
  pillars: Record<string, Pillar | null>; dayMaster: { stem: string; element: string };
  strength: Judgment & { alternativeInterpretations: { conclusion: string; conditions: string[]; reason: string }[]; method: string };
  monthCommand: Judgment & { tenGod: string };
  pattern: Judgment & { primaryPattern: string; alternativePatterns: { name: string; conditions: string[]; current: string }[]; conditions: string[]; rejectedConditions: string[] };
  usefulGod: Judgment & { primaryUsefulGod: string; supportingFavorableElements: string[]; unfavorableElements: string[]; climate: { element: string; scope: string }; reasoning: string[]; mediation: { between: string[]; element: string; status: string }[] };
  lifeThemes: Record<string, Judgment>; finalConclusion: Judgment; relations: Relation[];
  luckCycles: LuckCycle[]; annualCycles: AnnualCycle[]; warnings: string[];
  candidateInterval?: { from: string; to: string; resolution: string };
  report: { chapters: ReportChapter[]; generation: string; version?: string; disclaimer?: string; defaultMode?: string; overview?: ReportOverview; coverage?: { available: string[]; unavailable: string[] } };
  selfReview: Record<string, string | string[]>;
  metadata: { calculationVersion: string; ruleVersion: string; scope: string; referenceYear: number };
};
export type Candidates = { possibleCharts: Chart[]; message: string };
export type Location = { province: string; city: string; district: string; longitude: number; latitude: number };

export function formatBirthTime(birth: Birth): string {
  if(birth.accuracy==='unknown') return '时辰未知';
  if(birth.accuracy==='shichen') return `仅知${birth.shichen || '未知'}时`;
  return birth.accuracy==='exact' ? birth.time || '未知' : `${birth.time || '未知'}（±${birth.accuracy}分钟）`;
}

export async function api<T>(url: string, body?: unknown, signal?: AbortSignal): Promise<T> {
  const result = await fetch(`/api/v1${url}`, { method: body === undefined ? 'GET' : 'POST', signal,
    headers: { 'Content-Type': 'application/json' }, ...(body !== undefined ? { body: JSON.stringify(body) } : {}) });
  const data = await result.json();
  if (!result.ok) {
    const detail = Array.isArray(data.detail) ? data.detail.map((e: { msg: string }) => e.msg).join('；') : data.detail;
    throw new Error(detail || '请求失败，请确认本地后端正在运行。');
  }
  return data as T;
}
