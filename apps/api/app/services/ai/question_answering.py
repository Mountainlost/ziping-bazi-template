from copy import deepcopy
import re
from .provider import Selection
from .magpie import Explanation
from ...models import LockedChart
from ..rules.common import evidence
from ..rules.strength import SEASON

ROUTES = [
    (('用神','喜用','喜忌','忌神','水','火','木','土','金'), ['strength','usefulGod','monthCommand']),
    (('旺衰','强弱','身弱','身强','通根'), ['strength','monthCommand']),
    (('格局','从格','成格'), ['pattern','strength','monthCommand']),
    (('四柱','十神','藏干','排盘'), ['pillars','tenGods','hiddenStems','monthCommand']),
    (('性格','事业','财运','感情','情感','婚姻','配偶','夫妻','生活','健康'), ['lifeThemes','usefulGod']),
    (('结论','报告'), ['finalConclusion']),
]


def related_context(chart, question):
    fields = []
    for keywords, names in ROUTES:
        if any(word in question for word in keywords):
            fields.extend(names)
    context = {k:deepcopy(chart[k]) for k in dict.fromkeys(fields or ['finalConclusion','strength','usefulGod'])}
    chapter_routes=[(('排盘','四柱'),1),(('强弱','身强','身弱','旺衰'),2),(('格局','从格'),3),
        (('喜忌','用神','喜用'),4),(('性格',),5),(('事业','工作'),6),(('财运','赚钱'),7),
        (('感情','情感','婚姻','配偶','夫妻'),8),(('生活','五行','健康'),9),(('总断','结论'),12)]
    numbers={n for words,n in chapter_routes if any(w in question for w in words)}
    if numbers:
        context['reportSections']=deepcopy([c for c in chart.get('report',{}).get('chapters',[]) if c['number'] in numbers])
    if any(word in question for word in ('方位','朝向','往哪','东南','西北')):
        key='relationship' if any(word in question for word in ('感情','情感','配偶','夫妻','桃花','婚姻')) else 'fiveElements'
        if chart.get('directions',{}).get(key):
            context['directionAppendix']=deepcopy(chart['directions'][key])
        else:
            context['missingCalculations']=['这份旧版报告尚未计算所问方位，请使用重新校验命盘功能生成新版报告。']
    years = [int(y) for y in re.findall(r'(?<!\d)(?:19|20)\d{2}(?!\d)',question)]
    if '流年' in question or years:
        selected = [c for c in chart['annualCycles'] if c['year'] in (years or [chart['metadata']['referenceYear']])]
        context['annualCycles'] = deepcopy(selected[:3])
        indices = {s['luckIndex'] for c in selected for s in c['segments']}
        context['luckCycles'] = deepcopy([c for c in chart['luckCycles'] if c['index'] in indices])
        context['usefulGod'] = deepcopy(chart['usefulGod'])
    elif '大运' in question:
        # Recognize an already computed stem/branch; otherwise retrieve current reference-year cycle.
        selected = [c for c in chart['luckCycles'] if c['stem']+c['branch'] in question]
        if not selected:
            selected = [c for c in chart['luckCycles'] if c['startYear'] <= chart['metadata']['referenceYear'] < c['endYear']]
        context['luckCycles'] = deepcopy(selected[:3])
        context['usefulGod'] = deepcopy(chart['usefulGod'])
    return with_evidence(context)


def with_evidence(context):
    registry = {}
    def collect(value):
        if isinstance(value,dict):
            value.pop('diagnostics',None)
            if 'evidence' in value:
                for ev in value['evidence']:
                    registry[ev['id']] = ev
            for child in value.values():
                collect(child)
        elif isinstance(value,list):
            for child in value:
                collect(child)
    collect(context)
    context['evidence'] = list(registry.values())[:40]
    return context


def rederive_context(chart):
    """Use computed structure and timing, leaving the original prose out of the request."""
    fields = ('pillars', 'dayMaster', 'monthCommand', 'strength', 'pattern', 'usefulGod', 'relations')
    context = {key: deepcopy(chart[key]) for key in fields if key in chart}
    context['readingMode'] = 'rederive'
    context['luckTimeline'] = [
        {key: cycle[key] for key in ('stem', 'branch', 'startDate', 'endDateExclusive') if key in cycle}
        for cycle in chart['luckCycles']
    ]
    year = chart['metadata']['referenceYear']
    annual = [cycle for cycle in chart['annualCycles'] if year <= cycle['year'] <= year + 2]
    indices = {segment['luckIndex'] for cycle in annual for segment in cycle['segments']}
    luck = [cycle for cycle in chart['luckCycles']
            if cycle['index'] in indices or cycle['startYear'] <= year < cycle['endYear']]
    def summarize_cycle(cycle):
        summary = {key: cycle[key] for key in
                   ('year', 'stem', 'branch', 'startDate', 'endDateExclusive', 'activeLuck', 'from', 'toExclusive')
                   if key in cycle}
        analysis = cycle.get('analysis') or {}
        specific = [ev for ev in analysis.get('evidence', []) if ev.get('factor') != '扶抑取用']
        branch = cycle.get('branch')
        if branch in SEASON:
            branch_element = SEASON[branch]
            useful = chart.get('usefulGod', {})
            favorable = [useful.get('primaryUsefulGod'), *useful.get('supportingFavorableElements', [])]
            if branch_element in favorable:
                specific.append(evidence('运年地支五行', 'rules.strength.SEASON', 'support',
                    f'{cycle["stem"]}{branch}的地支{branch}属{branch_element}，对应已确认的扶抑有利元素，仅表示这一项有支持方向。'))
        summary['analysis'] = {'stemEffect': analysis.get('stemEffect'), 'relations': analysis.get('relations', []),
                               'evidence': specific[:4]}
        if len(cycle.get('segments', [])) > 1:
            summary['segments'] = [summarize_cycle(segment) for segment in cycle['segments']]
        return summary

    context['luckCycles'] = deepcopy([summarize_cycle(cycle) for cycle in luck])
    context['annualCycles'] = deepcopy([summarize_cycle(cycle) for cycle in annual])
    return with_evidence(context)


def answer_question(snapshot: LockedChart, question, provider, history=(), *, mode='question'):
    chart = snapshot.read()
    rederive = mode == 'rederive'
    context = rederive_context(chart) if rederive else related_context(chart,question)
    # Pass a detached JSON tree. Provider has neither model mutators nor storage handle.
    allowed = {e['id']:deepcopy(e) for e in context['evidence']}
    if hasattr(provider,'explain'):
        raw=provider.explain(question,deepcopy(context),history=() if rederive else history)
        if set(raw)-{'answer','evidenceIds','sources','onlineUsed'}:
            raise ValueError('解读包含不允许的命盘字段')
        result=Explanation.model_validate({k:raw[k] for k in ('answer','evidenceIds')})
        if any(i not in allowed for i in result.evidenceIds):
            raise ValueError('AI引用了未提供的证据，已拒绝展示')
        return {'answer':result.answer,'evidence':[allowed[i] for i in dict.fromkeys(result.evidenceIds)],
                'sources':raw.get('sources',[]),'onlineUsed':bool(raw.get('onlineUsed')),
                'chartId':snapshot.id,'readOnly':True,'presentation':'rederive' if rederive else 'explain'}
    result = Selection.model_validate(provider.select(question,deepcopy(context)))
    if any(i not in allowed for i in result.evidenceIds):
        raise ValueError('AI引用了未提供的证据，已拒绝展示')
    chosen = [allowed[i] for i in dict.fromkeys(result.evidenceIds)]
    # No provider-generated facts enter the report or answer. This enforces the lock at output too.
    text = '\n\n'.join(f'{e["factor"]}：{e["explanation"]}' for e in chosen)
    return {'answer':text, 'presentation':result.presentation, 'evidence':chosen,
            'chartId':snapshot.id, 'readOnly':True,
            'note':'回答只引用当前锁定结论；如质疑计算结果，请使用“重新校验命盘”。未计算的结论不会补算。'}
