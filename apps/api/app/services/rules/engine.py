from copy import deepcopy
from . import strength, pattern, useful_god, life_themes, luck_cycle, annual_cycle, directions
from .common import evidence, unique_evidence
from ..bazi.adapter import ten_god


def analyze(draft):
    chart = deepcopy(draft)
    month = chart['pillars']['month']
    main = month['hiddenStems'][0]
    chart['monthCommand'] = {'conclusion':month['branch']+'月本气'+main,
        'branch':month['branch'], 'mainStem':main, 'tenGod':ten_god(chart['dayMaster']['stem'],main),
        'stability':'medium', 'evidence':[evidence('月令事实','pillars.month', 'neutral',
        f'按实际出生瞬间的十二节分月；月支{month["branch"]}，藏干本气{main}。')]}
    chart['strength'] = strength.evaluate(chart)
    chart['pattern'] = pattern.evaluate(chart)
    chart['usefulGod'] = useful_god.evaluate(chart)
    chart['lifeThemes'] = life_themes.evaluate(chart)
    chart['directions'] = directions.evaluate(chart)
    chart['metadata']['directionRuleVersion']=directions.METHOD
    chart['luckCycles'] = luck_cycle.evaluate(chart)
    chart['annualCycles'] = annual_cycle.evaluate(chart)
    chart['finalConclusion'] = {'conclusion':f'{chart["dayMaster"]["stem"]}{chart["dayMaster"]["element"]}日主，{chart["strength"]["conclusion"]}；{chart["pattern"]["primaryPattern"]}；{chart["usefulGod"]["conclusion"]}。',
        'plainLanguage':'先核实出生资料，再理解条件与证据。传统模型中的主题不等于现实事件或命运定论。',
        'stability':'disputed' if chart['strength']['stability'] == 'disputed' else 'medium',
        'evidence':unique_evidence(chart['strength']['evidence'][:1]+chart['pattern']['evidence'][:1]+chart['usefulGod']['evidence'])}
    chart['selfReview'] = self_review(draft,chart)
    if chart['selfReview']['issues']:
        raise ValueError('一致性检查失败：'+'；'.join(chart['selfReview']['issues']))
    return chart


def self_review(draft, chart):
    checks = {'pillars':draft['pillars'] == chart['pillars'],
              'tenGods':all(p is None or (p['tenGod'] == ('日主' if k == 'day' else ten_god(chart['dayMaster']['stem'],p['stem']))
                  and p['hiddenStemTenGods'] == [ten_god(chart['dayMaster']['stem'],h) for h in p['hiddenStems']])
                  for k,p in chart['pillars'].items()),
              'strengthConsistency':strength.evaluate(chart)['conclusion'] == chart['strength']['conclusion'],
              'patternConsistency':pattern.evaluate(chart)['primaryPattern'] == chart['pattern']['primaryPattern'],
              'usefulGodConsistency':useful_god.evaluate(chart)['primaryUsefulGod'] == chart['usefulGod']['primaryUsefulGod'],
              'directionConsistency':directions.evaluate(chart) == chart['directions'],
              'luckCycleConsistency':all(c['analysis']['natalUsefulGod'] == chart['usefulGod']['primaryUsefulGod'] for c in chart['luckCycles']),
              'annualCycleConsistency':all(s['analysis']['natalUsefulGod'] == chart['usefulGod']['primaryUsefulGod']
                  and any(e['factor']=='流年三层' for e in s['analysis']['evidence']) for c in chart['annualCycles'] for s in c['segments'])}
    return {**{k:'pass' if v else 'fail' for k,v in checks.items()},
            'hourCompleteness':'complete' if chart['pillars']['hour'] else 'insufficient',
            'issues':[k for k,v in checks.items() if not v],
            'scope':'程序内部一致性复核，不等于外部历书校准或传统命理科学验证。'}
