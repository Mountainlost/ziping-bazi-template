from ..rules.common import evidence, unique_evidence
from .narrative import prepare_context, reading, build_overview


def render(chart):
    fact = {'conclusion':' / '.join(chart['pillars'][k]['stem']+chart['pillars'][k]['branch'] if chart['pillars'][k] else '时柱未知' for k in ['year','month','day','hour']),
            'plainLanguage':'年/月按交节，日/时按真太阳时；排盘事实与下文传统规则解释分开阅读。',
            'evidence':[evidence('排盘事实','pillars','neutral','四柱来自确定性排盘与时间校正；点击校验页核对原始信息和历法依据。')]}
    luck = {'conclusion':chart['calendar']['qiyun']+'，'+('顺排' if chart['calendar']['forward'] else '逆排'),
            'plainLanguage':'按原局喜忌 → 大运干支 → 生克关系 → 主题逐步解释；起运日期为传统天数折算近似。',
            'evidence':unique_evidence([e for c in chart['luckCycles'] for e in c['analysis']['evidence']]),
            'items':chart['luckCycles']}
    annual = {'conclusion':f'已计算{len(chart["annualCycles"])}个流年',
              'plainLanguage':'流年以立春起止，同时引用原局与所处大运；交运年按区间分段。',
              'evidence':unique_evidence([e for c in chart['annualCycles'] for a in ([s['analysis'] for s in c['segments']] or [c['analysis']]) for e in a['evidence']]),
              'items':chart['annualCycles']}
    if not annual['evidence']:
        annual['evidence'] = [evidence('流年覆盖','metadata.referenceYear','neutral','参考年份早于出生，未生成出生前的流年主题。')]
    contents = [('排盘事实',fact),('身强身弱',chart['strength']),('格局',chart['pattern']),
                ('喜忌用神',chart['usefulGod']),('性格',chart['lifeThemes']['personality']),
                ('事业',chart['lifeThemes']['career']),('财运',chart['lifeThemes']['finance']),
                ('感情',chart['lifeThemes']['relationship']),('五行与生活关注',chart['lifeThemes']['elementsAndLife']),
                ('大运',luck),('流年',annual),('最终结论',chart['finalConclusion'])]
    ctx=prepare_context(chart)
    chapters=[]
    for i,(name,value) in enumerate(contents):
        ev=list(value['evidence'])
        if i==0:
            ev+=chart['monthCommand']['evidence']+chart['strength']['evidence'][:1]
            ev.append(evidence('结构描述','pillars.*.branch','neutral','重复地支及天干/地支本气统计只作结构描述，不按数量推断旺衰。'))
        if i in (4,5,6,7):
            ev+=chart['monthCommand']['evidence']+chart['strength']['evidence'][:1]
            ev.append(evidence('象义解释','report.narrative.STEM_IMAGES/GOD_LANGUAGE','neutral',
                '日干和十神象义采用固定解释表，结合已锁定季节、旺衰与透干；不是人格测评或现实事件推断。'))
        ev=unique_evidence(ev)
        plain,pro,takeaway=reading(chart,i+1,ctx)
        if i in (3,7) and chart.get('directions'):
            appendix=chart['directions']['fiveElements' if i==3 else 'relationship']
            plain=plain+[appendix['plainLanguage']]
            pro=pro+[appendix['conclusion']+'；方法版本 '+chart['directions']['method']+'，为独立附录，不改变旺衰、格局及喜用。']
            ev=unique_evidence(ev+appendix['evidence'])
        ids=[e['id'] for e in ev]
        chapters.append({'number':i+1,'title':name,'conclusion':value['conclusion'],
            'body':'\n\n'.join(plain),'evidence':ev,'stability':value.get('stability','medium'),
            'plain':{'paragraphs':plain,'takeaway':takeaway,'evidenceIds':ids},
            'professional':{'paragraphs':pro,'evidenceIds':ids}})
    return {'chapters':chapters, 'defaultMode':'plain','overview':build_overview(chart,chapters,ctx),
            'coverage':{'available':['排盘事实','旺衰与格局候选','扶抑/调候/通关','性格、事业、财务与关系主题','八步大运及已算流年'],
                        'unavailable':['称骨模块未计算','鬼谷子论命未接入','寿数与疾病预测不生成','未计算的神煞不补写','祖业、亲属数量和子女现实情况不推断']},
            'disclaimer':'以上为传统文化解读，仅供参考，不作为医疗、投资或重大人生决定的唯一依据。',
            'generation':'deterministic-rules-and-fixed-templates','version':'3.1.0'}
