from datetime import datetime, timedelta
from ...bazi.adapter import engine
from ...bazi.solar_time import BJ
from ..luck_cycle import interpret
from ..common import evidence


def evaluate(chart):
    results = []
    ref = chart['metadata']['referenceYear']
    birth = datetime.fromisoformat(chart['time'].get('standardTime') or
        chart.get('candidateInterval',{}).get('from') or chart['calendar']['solarDate']).replace(tzinfo=BJ)
    birth_flow_year = engine.resolve_year_pillar(birth)[0]
    for year in range(max(birth_flow_year, ref-5), min(2099,ref+11)):
        start = engine.solar_term_beijing(year,315)
        end = engine.solar_term_beijing(year+1,315)
        cycle = {'year':year, 'stem':engine.liunian_gz(year)[0], 'branch':engine.liunian_gz(year)[1],
                 'startDate':start.isoformat(), 'endDateExclusive':end.isoformat()}
        segments = []
        # A flow year can span a change of decade cycle. Keep each interval explicit.
        for luck in chart['luckCycles']:
            ls = datetime.fromisoformat(luck['startDate']).replace(tzinfo=BJ)
            le = datetime.fromisoformat(luck['endDateExclusive']).replace(tzinfo=BJ)
            a,b = max(start,ls,birth), min(end,le)
            if a < b:
                segments.append({'from':a.isoformat(), 'toExclusive':b.isoformat(), 'luckIndex':luck['index'],
                                 'activeLuck':luck['stem']+luck['branch'], 'analysis':interpret(chart,cycle,'流年',luck)})
        first_start = datetime.fromisoformat(chart['luckCycles'][0]['startDate']).replace(tzinfo=BJ)
        if max(start,birth) < min(end,first_start):
            pre = {'stem':chart['pillars']['month']['stem'], 'branch':chart['pillars']['month']['branch']}
            segments.insert(0, {'from':max(start,birth).isoformat(), 'toExclusive':min(end,first_start).isoformat(),
                               'luckIndex':0, 'activeLuck':'起运前（月柱参照）', 'analysis':interpret(chart,cycle,'流年',pre)})
        if segments:
            cycle.update({'segments':segments, 'analysis':segments[0]['analysis'],
                          'activeLuck':' / '.join(s['activeLuck'] for s in segments)})
        else:
            ev = evidence('覆盖范围','luckCycles','neutral','本年不在已计算八步大运覆盖期，信息不足，不补算大运或完整流年判断。')
            cycle.update({'segments':[], 'activeLuck':None, 'analysis':{'conclusion':'信息不足', 'plainLanguage':ev['explanation'],
                          'stability':'disputed', 'evidence':[ev], 'relations':[], 'natalUsefulGod':chart['usefulGod']['primaryUsefulGod']}})
        results.append(cycle)
    return results
