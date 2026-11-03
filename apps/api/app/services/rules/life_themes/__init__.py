from ..common import evidence

THEMES = {
    '比肩': ('自主与同伴', '独立推进、同伴协作', '协作边界与分工'),
    '劫财': ('协作与边界', '团队资源配置', '共同支出与边界'),
    '食神': ('表达与积累', '持续产出与技能实践', '长期积累与支出节奏'),
    '伤官': ('创新与表达', '创意表达及规则沟通', '避免冲动与过度承诺'),
    '偏财': ('资源与弹性', '跨领域资源协调', '机会筛选与预算纪律'),
    '正财': ('秩序与积累', '稳步交付与流程管理', '收支计划与长期积累'),
    '偏官': ('挑战与约束', '在压力下建立执行边界', '避免压力驱动的决策'),
    '正官': ('责任与规范', '职责、制度与专业积累', '合规与责任分配'),
    '偏印': ('探索与专注', '研究、学习及方法探索', '防止投入与产出脱节'),
    '正印': ('学习与支持', '知识积累、支持与协作', '规划资源和学习投入'),
}


def evaluate(chart):
    god = chart['monthCommand']['tenGod']
    mood, career, finance = THEMES[god]
    missing = '时柱信息不足；以下为三柱暂定主题。' if not chart['pillars']['hour'] else ''
    ev = [evidence('人生主题','monthCommand.tenGod','neutral', f'以月令本气十神{god}的传统象义组织主题，结合{chart["strength"]["conclusion"]}及扶抑取用；不将象义映射成必然事件。'),
          *chart['usefulGod']['evidence'][:1]]
    result = {'conclusion': mood, 'stability':'disputed' if missing else 'medium', 'evidence':ev}
    texts = {'personality': f'{mood}是本版关注的表达主题，不能代替人格评估。',
             'career': f'可把{career}作为自我观察主题；职业选择仍需能力、经验和行业信息。',
             'finance': f'财务关注：{finance}。不据此预测盈利，也不提供投资标的或收益承诺。',
             'relationship': '关系关注沟通、承诺和边界。日支关系仅作互动线索，不推断婚期、伴侣性别或必然分合。',
             'elementsAndLife': '五行用于整理季节与生克象义。生活作息以实际需要为准，不由命盘诊断疾病或指导治疗。'}
    for key, text in texts.items():
        result[key] = {'conclusion': missing + text, 'plainLanguage': missing + text,
                       'stability': result['stability'], 'evidence':ev}
    return result
