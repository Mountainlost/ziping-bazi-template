"""Chart-specific reading templates. Never change or replace engine judgments."""
from collections import Counter
from ..rules.common import element, evidence, unique_evidence
from .plain_reading import plain_reading, everyday_theme

STEM_IMAGES = {
    '甲':('树木','持续生长、建立方向与结构','坚持方向时，也为新信息保留调整空间'),
    '乙':('藤蔓与花木','适应环境、协调关系与细节表达','避免只顾适应别人而忽略自己的边界'),
    '丙':('日光','主动表达、分享信息与推动行动','热情之外，给计划留出验证和收尾的时间'),
    '丁':('灯火','专注、细致观察与持续投入','减少内耗，把观察落实为可完成的小步骤'),
    '戊':('山岳','稳定、责任与长期积累','保留稳定的基础，也避免把所有责任独自承担'),
    '己':('田园土壤','整理、照顾与资源协调','帮助别人之前，先明确自己的时间和精力预算'),
    '庚':('经锻炼的金属','决断、解决问题与建立标准','清晰表达标准，同时给协作留出沟通余地'),
    '辛':('精金与珠玉','分辨细节、审美与精确表达','把敏锐的判断变成方法和作品，压力下先沟通再下结论'),
    '壬':('江河','信息流动、探索与整体联想','给广泛的兴趣设置主线，避免同时开启太多方向'),
    '癸':('雨露','细腻观察、学习与耐心渗透','让细致观察形成明确表达，而不是反复猜测他人的想法'),
}
GOD_LANGUAGE = {
    '比肩':('自主与同伴协作','独立负责的工作、专业协作','把独立决策和协作分工都说清楚'),
    '劫财':('资源协作与边界','团队协作、项目推进和资源分配','合作前先确定投入、分工和退出方式'),
    '食神':('持续输出与技能积累','产品、内容、技能服务和长期交付','把零散想法整理为可重复交付的成果'),
    '伤官':('表达、分析与突破惯例','研究分析、策划、技术表达与问题解决','让洞察形成成果，并练习与规则和他人有效沟通'),
    '正财':('计划、交付与稳定积累','流程管理、持续经营与专业服务','先把交付和资源安排稳定，再考虑扩大范围'),
    '偏财':('资源发现与弹性协调','跨领域协调、业务拓展和项目经营','筛选机会，避免把所有变化都理解为必须抓住的机会'),
    '正官':('责任、秩序与规范','组织管理、专业规范和责任明确的工作','用清晰标准推进工作，别让责任变成无边界负担'),
    '偏官':('挑战、执行与压力应对','目标明确的项目、执行推进与风险识别','把压力拆成具体任务，先安排资源再提高速度'),
    '正印':('学习、支持与知识积累','知识服务、教育支持与专业积累','建立自己的知识框架，并通过实践验证'),
    '偏印':('研究、探索与方法意识','研究、技术探索与独立分析','保留探索的深度，同时检验方法是否解决了实际问题'),
}


def annual_theme(cycle):
    segments=cycle['segments']
    if len(segments)>1:
        return '交运年：'+' / '.join(dict.fromkeys(s['analysis']['conclusion'] for s in segments))
    return cycle['analysis']['conclusion']


def annual_paragraph(cycle):
    if len(cycle['segments'])>1:
        parts=[f'{s["from"][:10]}至{s["toExclusive"][:10]}（不含），{s["activeLuck"]}背景：{s["analysis"]["conclusion"]}' for s in cycle['segments']]
        return f'{cycle["year"]}{cycle["stem"]}{cycle["branch"]}为交运年，分段阅读：'+'；'.join(parts)+'。不把其中一段的结论覆盖全年。'
    return f'{cycle["year"]}{cycle["stem"]}{cycle["branch"]}：已计算主题为“{cycle["analysis"]["conclusion"]}”，背景大运为{cycle["activeLuck"] or "超出已算范围"}。这是原局、大运与流年的联合解释，不能单凭一个字确定现实事件。'


def prepare_context(chart):
    pillars=[p for p in chart['pillars'].values() if p]
    branches=Counter(p['branch'] for p in pillars)
    visible=[p['tenGod'] for k,p in chart['pillars'].items() if p and k!='day']
    counts=Counter()
    for p in pillars:
        counts[element(p['stem'])]+=1
        counts[element(p['hiddenStems'][0])]+=1
    annual=next((a for a in chart['annualCycles'] if a['year']==chart['metadata']['referenceYear']),None)
    current=[]
    if annual:
        indices={s['luckIndex'] for s in annual['segments']}
        current=[c for c in chart['luckCycles'] if c['index'] in indices]
    return {'branches':branches,'visible':visible,'counts':counts,'annual':annual,'current':current,
            'dominant':[{'branch':b,'count':n} for b,n in branches.items() if n>=2]}


def reading(chart, number, ctx):
    stem=chart['dayMaster']['stem']; el=chart['dayMaster']['element']
    strength=chart['strength']['conclusion']; month=chart['pillars']['month']['branch']
    god=chart['monthCommand']['tenGod']; theme,work,action=GOD_LANGUAGE[god]
    useful=chart['usefulGod']; primary=useful['primaryUsefulGod']
    weak=strength=='偏弱'; strong=strength=='偏强'
    capacity=('先把能力、支持和执行基础做稳，再增加任务和机会的数量。' if weak else
              '把已有动力用于产出和合作，让行动有方向、有反馈。' if strong else
              '先观察不同环境下的承载情况，避免把自己简单归为强或弱。')
    root_count=sum(r['sameElement'] for r in chart['strength']['diagnostics']['roots'])
    repeated='、'.join(f'{d["count"]}个{d["branch"]}' for d in ctx['dominant'])
    climate=useful['climate']['element']
    image,traits,trait_action=STEM_IMAGES[stem]
    financial=sum(g in ('正财','偏财') for g in ctx['visible'])
    branch_rel=[r for r in chart['relations'] if 'day' in r['members'] and r['type']!='天干五合']
    if number==1:
        paragraphs=[f'你的日主是{stem}{el}，可以把它理解为这份传统模型观察“自身”的起点。出生在{month}月，季节环境与其余干支共同构成背景，不能只看单一字就下判断。',
            f'四柱中出现{repeated}，重复的地支使相关季节与生克关系更值得留意。' if repeated else '原局没有重复两次以上的地支，阅读时更应综合月令、根气与不同位置的作用。',
            f'这份命盘的主线是“{theme}”，同时要结合自身力量理解机会与压力。{capacity}']
        pro=[f'四柱：'+ '、'.join(chart['pillars'][k]['stem']+chart['pillars'][k]['branch'] if chart['pillars'][k] else '时柱未知' for k in ['year','month','day','hour'])+'。',
             '天干及地支本气观察统计：'+'、'.join(f'{e}{ctx["counts"][e]}' for e in '木火土金水')+'。此统计仅为可见结构描述，不参与“按数量定旺衰”。',
             f'月令本气十神为{god}；原局旺衰{strength}，取格为{chart["pattern"]["primaryPattern"]}。']
        takeaway='先了解结构，再读解释；五行数量不是命局结论。'
    elif number==2:
        paragraphs=[chart['strength']['plainLanguage'],
            f'系统先看出生季节，再看地支中是否有支持自身的根基、这些根基是否受到刑冲影响，以及表面的力量怎样生扶或消耗自身。当前识别到{root_count}处同类根气记录；有根不等于自动身强，仍要看层次与作用。',
            f'把它放到生活中，值得观察的是任务规模与自身资源是否相称，而不是给自己贴“强者”或“弱者”的标签。{capacity}']
        pro=[f'综合结果：{strength}；稳定性{chart["strength"]["stability"]}。',chart['strength']['method'],
             '替代解释仍需核准时柱、月令司令以及刑冲后的有效根气，不能靠单一规则反转结论。']
        takeaway=capacity
    elif number==3:
        paragraphs=[f'“格局”是在传统术语中概括命盘组织方式的名称。本盘从月令本气入手，得到的是{chart["pattern"]["primaryPattern"]}；候选表示仍有成立条件要核实。',
            f'换成日常语言，这里先观察{theme}怎样组织你的行动与资源，而不是把格名理解为身份高低、财富等级或成功保证。',
            '常格与从格的解释路径不同。本版保留两者的成立条件，有根气、印比是否有力等关键问题尚未满足时，不因为某一元素很多就宣布从格。']
        pro=[f'月支{month}，本气{chart["monthCommand"]["mainStem"]}为{god}。主取格：{chart["pattern"]["primaryPattern"]}。',
             *[e['explanation'] for e in chart['pattern']['evidence']]]
        takeaway='先核实格局条件，不把一个格名当作人生等级。'
    elif number==4:
        paragraphs=[f'这份报告把“怎样平衡自身力量”和“怎样理解季节寒暖”分开处理。扶抑方向依据{strength}，当前首选{primary}，辅助方向为'+('、'.join(useful['supportingFavorableElements']) or '暂不独定')+'。',
            f'调候参考为{climate}，它讨论的是{month}月的季节环境。即使调候与扶抑出现不同元素，也是在回答不同问题，不宜删掉其中一个来制造简单答案。',
            f'落到现实，可以把它作为安排精力、学习和协作方式的观察框架。{capacity}不需要把某种颜色、饰品或消费行为当作必需的“改运措施”。']
        pro=[f'扶抑主用：{primary}；辅助喜元素：'+('、'.join(useful['supportingFavorableElements']) or '待定')+'；需谨慎元素：'+('、'.join(useful['unfavorableElements']) or '待定')+'。',
             *useful['reasoning']]
        takeaway='扶抑、调候和通关各有前提；不要把用神简化成“缺什么就买什么”。'
    elif number==5:
        paragraphs=[f'传统日干象义把{stem}{el}比作{image}，借此表达{traits}。这是一种观察角度，可以与你的实际经验对照。',
            f'月令本气{god}带来的另一条主题是{theme}。当这两组线索放在一起，更值得关注的是：你如何把自己的观察、判断和偏好落实到行动。',
            f'可以尝试的方向是：{trait_action}。若你发现描述不符合自己，以实际经历为准，不必为了“符合命盘”改变对自己的认识。']
        pro=[f'日主{stem}{el}的固定象义模板：{traits}；月令本气{god}对应{theme}。',
             f'旺衰{strength}作为承载条件；日干象义不等于已验证的人格测评。']
        takeaway=trait_action+'。'
    elif number==6:
        paragraphs=[f'从本盘的传统象义出发，可以优先观察{work}这一类工作内容。它们描述的是工作方式，不能直接推断你必须进入哪个行业。',
            f'职业发展的关键在于把{theme}转成看得见的成果。{action}；通过作品、项目复盘和长期反馈验证自己的优势，比频繁根据命理更换赛道更有用。',
            f'{capacity}岗位选择还需结合实际能力、经验和行业条件，命盘不会替你完成这些验证。']
        pro=[f'事业主题取月令{god}象义，并结合原局{strength}及扶抑{primary}。',
             '透干十神：'+('、'.join(ctx['visible']) or '信息不足')+'。判断先描述作用，不由财官食伤直接推出升职、创业成功或指定行业。']
        takeaway=action+'。'
    elif number==7:
        paragraphs=[f'原局年、月、时干中有{financial}处财星透出。财星在这个模型里讨论资源和交换，不能把它等同于现实收入、资产规模或“命中一定有钱”。',
            ('当财的线索与偏弱的承载条件同时出现时，解释重点在于资源是否与能力和支持相匹配。可以先建立稳定的交付方式和合作规则，避免一个人承担所有环节。' if financial and weak else
             f'这份命盘在财务主题上仍需回到{theme}和自身承载来看。机会、投入与实际成果之间存在距离，不因为某个十神出现就预设获利。'),
            '涉及合作、共同投入和收入分配时，把责任、交付与边界写清楚。这是管理现实关系的方法，不是命盘对某项财务行为的收益预测。']
        pro=[f'财星透干记录{financial}处；以日主十神对应表识别，不按财富分数展示。',
             f'原局{strength}，扶抑首选{primary}；财星作用须先经过原局承载与岁运条件，不直接断财。']
        takeaway='机会要经过能力、交付与合作边界，才能转成可检验的成果。'
    elif number==8:
        paragraphs=['感情部分先观察相处方式和边界，不根据命盘给出结婚年龄、伴侣外貌或必然分合。对你而言，可以把表达需求、确认承诺和分配责任作为长期观察的重点。',
            (f'日支参与了{len(branch_rel)}条已记录的合冲刑害等关系。这些只是命盘中的结构联系，适合提醒自己在变化中多确认彼此需求，不能直接等同于关系中的某一事件。' if branch_rel else
             '本版关系表没有命中涉及日支的作用，但“没有命中”并不表示关系没有变化；实际沟通仍比符号更重要。'),
            '亲友合作与家庭资源也需要现实信息。比劫、印星或时柱的象义不能据此推出兄弟人数、父母财富、子女聪明程度；这些未计算的内容不会补写成结论。']
        pro=[f'日支{chart["pillars"]["day"]["branch"]}；涉及日支的关系：'+('、'.join(r['type']+r['characters'] for r in branch_rel) or '本版未命中')+'。',
             '家庭、手足和子女的现实情况无充分计算依据，不从神煞或五行数量补断。']
        takeaway='关系的质量要靠沟通和长期相处来确认。'
    elif number==9:
        paragraphs=[f'{month}月的季节背景在本版中采用{climate}作为调候参考。它与生活中的寒暖、光照、作息偏好可以作文化层面的对照，不是医学上的体质或疾病判定。',
            '可执行的生活关注是保持规律作息、适度活动、合理安排连续工作的时间，并根据自己的真实感受调整环境。具体身体不适应通过医学检查处理。',
            '本版没有把五行对应到疾病、器官寿命或疗法，也不会把所谓补救法包装成必须购买的物品。与其追求一次性的改运，不如建立自己能持续做到的生活节奏。']
        pro=[f'调候：{climate}；范围：{useful["climate"]["scope"]}。',
             '五行本气描述不构成医疗指标；没有医疗诊断或寿数计算模块。']
        takeaway='生活关注回到作息、活动与实际感受，不把命理当作医疗指标。'
    elif number==10:
        current=ctx['current']
        current_text='、'.join(c['stem']+c['branch'] for c in current)
        paragraphs=[f'本版按出生信息计算了八步大运，起运为{chart["calendar"]["qiyun"]}，采用'+('顺排。' if chart['calendar']['forward'] else '逆排。')+'大运用于整理十年背景，不意味着每一步都有固定的好坏。',
            (f'参考年度{chart["metadata"]["referenceYear"]}涉及{current_text}大运。'+('该年有交运区间，两个背景应分段阅读。' if len(current)>1 else
             f'当前所选背景中，{current[0]["analysis"]["stemEffect"]}，系统给出的主题是“{current[0]["analysis"]["conclusion"]}”。') if current else
             '参考年度不在已计算的大运范围内，因此不会补写一个“当前大运”。'),
            '阅读顺序是原局承载与喜忌、运的干支作用、与原局的关系，最后才是可能关注的生活主题。切换时间轴可逐步查看，而不是只看到财星就解释为发财。']
        pro=[f'方向：'+('顺' if chart['calendar']['forward'] else '逆')+f'；起运：{chart["calendar"]["qiyun"]}。',
             ' → '.join(c['stem']+c['branch'] for c in chart['luckCycles']),
             '起运以距交节天数折成年/月，日期为近似；不确定时间还会影响起运范围。']
        takeaway='先看十年背景怎样作用于原局，再看现实任务如何安排。'
    elif number==11:
        selected=[c for c in chart['annualCycles'] if chart['metadata']['referenceYear']<=c['year']<=chart['metadata']['referenceYear']+2]
        paragraphs=[annual_paragraph(c) for c in selected]
        if not paragraphs:
            paragraphs=['参考年度不在已计算的流年范围内。','当前信息不足，不补写具体年份事件。']
        paragraphs.append('比较年份时，更适合看责任、资源和关系的侧重点如何变化，而不是比较“运势分数”。遇到交运年份，需要同时核对前后两个区间。')
        pro=[f'流年以立春起止，已计算{len(chart["annualCycles"])}年。',
             *[annual_paragraph(c) for c in selected],
             '每个区间引用锁定的原局喜忌及当时所处大运；不额外补算重大关口年份。']
        takeaway='比较已经计算的变化条件，避免把年份主题理解成确定事件。'
    else:
        paragraphs=[f'把整份报告合起来，你的核心线索是{stem}{el}日主、{strength}的承载条件，以及{theme}这一传统象义主题。',
            f'事业上，{action}。资源与合作上，{capacity}关系与生活则回到沟通、习惯和现实反馈中观察，不必让命理标签代替判断。',
            '这份报告能帮助你整理问题，但不能替你决定人生。如果出生时间、地点或历法记录有疑问，先重新校验命盘；不在已有结论上反复叠加未经计算的解释。']
        pro=[chart['finalConclusion']['conclusion'],
             '扶抑、调候、格局候选与旺衰分别保留条件，完整性和一致性见自我复核。']
        takeaway=capacity
    paragraphs,takeaway=plain_reading(chart,number,ctx)
    return paragraphs,pro,takeaway


def build_overview(chart, chapters, ctx):
    current=ctx['current']
    annual=ctx['annual']
    return {'headline':chapters[-1]['plain']['takeaway'],
        'paragraphs':chapters[0]['plain']['paragraphs'][:2],
        'dominantBranches':ctx['dominant'],
        'plainTags':['先稳基础' if chart['strength']['conclusion']=='偏弱' else '专注一条主线','工作重在积累','合作讲清边界'],
        'focus':[{'label':'能力与承载','text':chapters[1]['plain']['takeaway'],'chapter':2},
                 {'label':'事业与资源','text':chapters[5]['plain']['takeaway'],'chapter':6},
                 {'label':'关系与生活','text':chapters[7]['plain']['takeaway'],'chapter':8}],
        'currentLuck':[{'stem':c['stem'],'branch':c['branch'],'from':c['startDate'],'toExclusive':c['endDateExclusive'],
                        'theme':c['analysis']['conclusion'],'plainTheme':everyday_theme(c['analysis']['conclusion']),'evidence':c['analysis']['evidence']} for c in current],
        'currentAnnual':{'year':annual['year'],'stem':annual['stem'],'branch':annual['branch'],
                         'theme':annual_theme(annual),'plainTheme':'这一年分段看，重点会有变化' if len(annual['segments'])>1 else everyday_theme(annual['analysis']['conclusion']),
                         'segments':[{'from':s['from'],'toExclusive':s['toExclusive'],'activeLuck':s['activeLuck'],
                                      'theme':s['analysis']['conclusion'],'evidence':s['analysis']['evidence']} for s in annual['segments']],
                         'evidence':unique_evidence([e for s in annual['segments'] for e in s['analysis']['evidence']]) or annual['analysis']['evidence']} if annual else None,
        'evidence':unique_evidence(chapters[0]['evidence']+chapters[1]['evidence']+chapters[5]['evidence'])}
