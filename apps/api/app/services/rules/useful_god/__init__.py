from ..common import ELEMENTS, element, evidence


def evaluate(chart):
    i = ELEMENTS.index(chart['dayMaster']['element'])
    strength = chart['strength']['conclusion']
    if strength == '偏弱':
        primary, favorable = ELEMENTS[(i-1)%5], [ELEMENTS[i]]
        unfavorable = [ELEMENTS[(i+1)%5], ELEMENTS[(i+2)%5], ELEMENTS[(i+3)%5]]
    elif strength == '偏强':
        primary, favorable = ELEMENTS[(i+1)%5], [ELEMENTS[(i+2)%5], ELEMENTS[(i+3)%5]]
        unfavorable = [ELEMENTS[i], ELEMENTS[(i-1)%5]]
    else:
        primary, favorable, unfavorable = '暂不独定', [], []
    branch = chart['pillars']['month']['branch']
    climate = '水' if branch in '巳午未' else '火' if branch in '亥子丑' else '无统一调候项'
    present = {element(p['stem']) for p in chart['pillars'].values() if p}
    bridges = []
    for a,b,bridge in [('木','土','火'),('火','金','土'),('土','水','金'),('金','木','水'),('水','火','木')]:
        if a in present and b in present:
            bridges.append({'between':[a,b], 'element':bridge, 'status':'仅见相克元素，是否需要通关须复核力量；不自动升为主用神'})
    ev = [evidence('扶抑取用','strength.conclusion','neutral',
                   f'依据已锁定旺衰{strength}，常格扶抑规则取{primary}为首选方向，辅以{"、".join(favorable) or "待定"}；从格未成立，不反向取用。'),
          evidence('调候','monthCommand','neutral',f'{branch}月调候参考{climate}。寒暖燥湿与扶抑解决的问题不同，不一定矛盾；未细分日干专属调候古籍条款。'),
          evidence('通关','pillars.*.stem','neutral', f'已识别{len(bridges)}组透干相克的通关候选，仅作条件说明，不直接改变扶抑用神。')]
    return {'conclusion': f'扶抑首选：{primary}', 'primaryUsefulGod': primary,
            'supportingFavorableElements': favorable, 'unfavorableElements': unfavorable,
            'balance': {'method':'常格扶抑', 'element':primary},
            'climate': {'element':climate, 'scope':'月令寒暖粗分，非专属调候定论'},
            'mediation': bridges, 'reasoning': [e['explanation'] for e in ev], 'evidence': ev,
            'stability': 'disputed' if chart['strength']['stability'] == 'disputed' else 'medium',
            'plainLanguage':'用神描述传统模型希望补充或疏导的力量，不等于缺什么补什么，不对应购买物品或现实收益。'}
