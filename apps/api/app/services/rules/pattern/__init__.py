from ..common import evidence
from ...bazi.adapter import ten_god


def evaluate(chart):
    month = chart['pillars']['month']
    main = month['hiddenStems'][0]
    god = ten_god(chart['dayMaster']['stem'], main)
    exposed = [p for k,p in chart['pillars'].items() if p and k != 'day' and main == p['stem']]
    same_roots = [r for r in chart['strength']['diagnostics']['roots'] if r['sameElement']]
    title = {'比肩':'建禄/月劫候选', '劫财':'月劫/羊刃候选'}.get(god, god + '格候选')
    ev = [evidence('月令取格', 'pillars.month.hiddenStems', 'neutral',
                   f'月支{month["branch"]}本气{main}为{god}，先取{title}。尚未穷尽成格、破格与救应。'),
          evidence('透藏', 'pillars.*.stem', 'neutral', f'月令本气{"已" if exposed else "未"}透出到年/月/时干；不因名称相同就直接宣布成格。'),
          evidence('从格条件', 'strength.diagnostics.roots', 'neutral',
                   f'同类根气记录{len(same_roots)}处；从格需无有效根、无有力印比且气势专一，MVP不自动成立从格。')]
    return {'conclusion': title, 'primaryPattern': title, 'evidence': ev,
            'alternativePatterns': [{'name':'身弱正格', 'conditions':['日主偏弱但仍有根或印比可扶'],
                                      'current': '优先保留常格解释'},
                                     {'name':'从格候选', 'conditions':['无有效根','印比无力','克泄耗气势专一','复核时柱与合化'],
                                      'current': '条件未完全核实，不认定从格'}],
            'conditions': ['按月令本气确定候选','透干作为辅助证据'],
            'rejectedConditions': ['不以五行缺失判从格','不自动把六合、三合认作化局', '建禄/羊刃须另核日干阴阳与禄刃，当前仅候选'],
            'stability': 'disputed', 'plainLanguage':'这是传统取格路径下的候选结构；有格名不等于现实成就，也不等于已经成格。'}
