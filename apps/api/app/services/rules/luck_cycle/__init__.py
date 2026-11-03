from ...bazi.adapter import ten_god
from ...bazi.relations import calculate_relations
from ..common import element, evidence
from ..life_themes import THEMES


def interpret(chart, cycle, prefix='大运', active=None):
    useful = chart['usefulGod']['primaryUsefulGod']
    god = ten_god(chart['dayMaster']['stem'], cycle['stem'])
    extra = {'natal.'+k:p for k,p in chart['pillars'].items() if p}
    name = 'annual' if active is not None else 'luck'
    extra[name] = {'stem':cycle['stem'], 'branch':cycle['branch']}
    if active is not None:
        extra['activeLuck'] = {'stem':active['stem'], 'branch':active['branch']}
    relations = [r for r in calculate_relations(extra) if name in r['members']]
    supportive = element(cycle['stem']) in [useful, *chart['usefulGod']['supportingFavorableElements']]
    label = '资源机会增加' if supportive else '承载与压力需关注'
    if any(r['type'] in ('六冲','相刑','自刑') for r in relations):
        label = '变化较明显'
    ev = [*chart['usefulGod']['evidence'][:1],
          evidence(prefix+'天干',prefix+'.stem','support' if supportive else 'neutral',
                   f'{cycle["stem"]}为{god}，属{element(cycle["stem"])}；与原局扶抑首选{useful}及有利元素比较，先看承载，不据十神断事件。'),
          evidence(prefix+'地支',prefix+'.branch','neutral',
                   f'{cycle["branch"]}与原局识别{len(relations)}条关系。' + (' '.join(r['explanation'] for r in relations) or '未命中本版关系表，不代表现实没有变化。'))]
    if active is not None:
        ev.append(evidence('流年三层','annualCycles.activeLuck','neutral',
                           f'本流年分段结合原局、{active["stem"]}{active["branch"]}大运和{cycle["stem"]}{cycle["branch"]}流年共同分析。'))
    _, career, finance = THEMES[god]
    plain_title={'资源机会增加':'多留意新的合作和发展机会','变化较明显':'给工作和生活的调整留点空间',
                 '承载与压力需关注':'事情变多时，先排好时间和人手'}[label]
    plain_paragraphs=[('这一段可以多看看新的任务与合作，但先筛选自己真正做得好的事情。' if supportive else
                       '这一段更需要把手头的事情安排好，别因为新的要求一来就全部接下。'),
                      '遇到变化时，先确认哪些事必须做、哪些可以放后、哪些需要找人配合。把具体安排讲清楚，比单纯加快速度更有用。']
    return {'conclusion':label, 'plainLanguage':f'{prefix}作为环境主题参考，始终以原局喜忌和生克关系为前提。',
            'plain':{'headline':plain_title,'paragraphs':plain_paragraphs,
                     'focus':{'工作':career,'合作':'把分工和约定提前说清楚','相处':'有需要就直接表达，不让猜测代替沟通'}},
            'stemEffect':f'{cycle["stem"]} / {god} / {element(cycle["stem"])}',
            'branchEffect':f'{cycle["branch"]}支与原局及已选大运的关系如下',
            'relations':relations, 'natalUsefulGod':useful,
            'themes':{'career':career, 'finance':finance, 'relationship':'观察互动及约定的调整',
                      'pressure':'依据实际处境安排资源，避免把象义理解为必然事件'},
            'evidence':ev, 'stability':'disputed' if not chart['pillars']['hour'] else 'medium'}


def evaluate(chart):
    return [{**c, 'analysis':interpret(chart,c)} for c in chart['luckCycles']]
