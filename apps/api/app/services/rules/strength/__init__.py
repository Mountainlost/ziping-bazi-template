from ..common import ELEMENTS, element, relation, evidence

SEASON = {'寅':'木','卯':'木','辰':'土','巳':'火','午':'火','未':'土',
          '申':'金','酉':'金','戌':'土','亥':'水','子':'水','丑':'土'}
REL_LABEL = {0:'同类比劫', 4:'生我印星', 1:'我生食伤', 2:'我克财星', 3:'克我官杀'}


def evaluate(chart):
    day = chart['dayMaster']['element']
    branch = chart['pillars']['month']['branch']
    seasonal = SEASON[branch]
    sr = relation(day, seasonal)
    seasonal_score = {0:3.0, 4:2.0, 1:-1.5, 2:-1.0, 3:-2.5}[sr]
    ev = [evidence('月令', 'pillars.month.branch', 'support' if sr in (0,4) else 'weaken',
                   f'{branch}月以{seasonal}气为主，对{day}日主为{REL_LABEL[sr]}；月令优先于表面五行数量。四季土月采用本气土，未细分司令天数。')]
    root_score, stem_score, drain_score = 0.0, 0.0, 0.0
    root_details = []
    for pos, p in chart['pillars'].items():
        if not p:
            continue
        clash = any(r['type'] in ('六冲','相刑','自刑') and pos in r['members'] for r in chart['relations'])
        for rank, stem in enumerate(p['hiddenStems']):
            r = relation(day, element(stem))
            weight = [1.0, .55, .25][rank] * (1.3 if pos == 'day' else 1)
            if r in (0,4):
                adjusted = weight * (.5 if clash else 1) * (1 if r == 0 else .65)
                root_score += adjusted
                root_details.append({'position': pos, 'stem': stem, 'sameElement': r == 0,
                                     'rank': rank, 'affectedByClash': clash})
                ev.append(evidence('通根/地支生扶', f'pillars.{pos}.hiddenStems', 'support',
                    f'{pos}支{p["branch"]}藏{stem}（{"本气" if rank == 0 else "余/中气"}），提供{REL_LABEL[r]}；'
                    + ('见刑冲，按规则折减有效根气，未直接判拔根。' if clash else '按根气层次与位置纳入判断。')))
            else:
                drain_score += weight * {1:.45, 2:.35, 3:.55}[r]
        if pos != 'day':
            r = relation(day, element(p['stem']))
            delta = {0:1.2,4:1,1:-.8,2:-.7,3:-1.1}[r]
            stem_score += delta
            ev.append(evidence('透干/生克泄耗', f'pillars.{pos}.stem', 'support' if delta > 0 else 'weaken',
                f'{pos}干{p["stem"]}透出，为{p["tenGod"]}（{REL_LABEL[r]}），按位置作用参与扶抑。'))
    score = seasonal_score + root_score + stem_score - drain_score
    conclusion = '偏强' if score >= 2.5 else '偏弱' if score <= -.5 else '中和附近'
    unknown = chart['pillars']['hour'] is None
    stability = 'disputed' if unknown or -.9 < score < 3 else 'medium'
    for item in chart['relations']:
        ev.append(evidence('刑冲合会', 'relations', 'neutral', item['explanation']))
    ev.append(evidence('克泄耗', 'pillars.*.hiddenStems', 'weaken',
                       '财官食伤的地支作用按本中余气区分；结合月令、根气及透干，不以五行个数直接定旺衰。'))
    if unknown:
        ev.append(evidence('完整性', 'pillars.hour', 'neutral', '时柱信息不足；旺衰仅作三柱暂定，完整命局无法确认。'))
    return {'conclusion': conclusion, 'stability': stability, 'evidence': ev,
            'plainLanguage': {'偏强':'支持自身的力量在本版规则下相对明显，可关注表达、产出与约束之间的平衡。',
                '偏弱':'支持自身的力量相对有限，消耗或约束自身的力量更明显，宜先理解资源与承载的平衡。',
                '中和附近':'生扶与克泄耗较接近，对时间误差与规则权重较敏感，不宜强分旺衰。'}[conclusion],
            'alternativeInterpretations': [{'conclusion': '边界取另一旺衰倾向',
                'conditions': ['补全时柱','四季土月细分司令','复核刑冲有效根气及合化条件'],
                'reason': '本版是透明的保守规则，不代表全部子平流派。'}],
            'diagnostics': {'ruleIndex': round(score,4), 'season': seasonal_score, 'root': round(root_score,4),
                            'visibleStems': stem_score, 'drain': round(drain_score,4), 'roots': root_details},
            'method': '季节优先 + 分层根气 + 透干生克泄耗 + 刑冲折减；内部规则指数不是运势评分'}
