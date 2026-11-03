"""A downloadable, deterministic chart attachment, derived from locked facts only."""
from html import escape

COLORS={'木':'#488663','火':'#ba5d48','土':'#ae8a3d','金':'#887340','水':'#5276b5'}


def render_chart_svg(chart):
    def text(x,y,value,size=16,color='#35405a',weight=400):
        return f'<text x="{x}" y="{y}" fill="{color}" font-size="{size}" font-weight="{weight}">{escape(str(value))}</text>'
    font='Microsoft YaHei, PingFang SC, Noto Sans CJK SC, sans-serif'
    items=[f'<svg xmlns="http://www.w3.org/2000/svg" width="1060" height="940" viewBox="0 0 1060 940" role="img">',
           '<title>子平命盘附件：由已锁定排盘生成</title>',f'<g font-family="{font}">',
           '<rect width="1060" height="940" rx="28" fill="#f5f7fb"/>',
           '<rect x="24" y="24" width="1012" height="130" rx="18" fill="#1c2744"/>',
           text(54,66,(chart['input'].get('name') or '子平')+' · 命盘资料',27,'#ffffff',600),
           text(54,102,chart['calendar']['solarDate']+'  '+(chart['input']['time'] or '时辰未知')+'  ·  '+chart['input']['sex']+'  ·  '+chart['input']['city']+' '+chart['input']['district'],16,'#d5dff6'),
           text(54,132,'真太阳时：'+(chart['time'].get('trueSolarTime') or '信息不足')[:19].replace('T',' ')+'    /    规则报告 · '+chart['metadata']['calculationVersion'],14,'#b8c5e2')]
    columns=[]
    overview=chart.get('report',{}).get('overview',{})
    annual=overview.get('currentAnnual')
    luck=next(iter(overview.get('currentLuck',[])),None)
    columns.append((str(chart['metadata']['referenceYear'])+'流年',annual,None))
    columns.append(('大运·首段' if len(overview.get('currentLuck',[]))>1 else '参考大运',luck,None))
    columns += [(label,chart['pillars'][key],key) for key,label in [('year','年柱'),('month','月柱'),('day','日柱'),('hour','时柱')]]
    from ..bazi.adapter import ten_god, engine
    for i,(label,p,key) in enumerate(columns):
        x=49+i*163
        items.append(f'<rect x="{x-12}" y="177" width="151" height="350" rx="14" fill="'+('#eaf0ff' if key=='day' else '#ffffff')+'"/>')
        items.append(text(x+18,214,label,17,'#777f91'))
        items.append(text(x+18,254,p.get('tenGod',ten_god(chart['dayMaster']['stem'],p['stem'])) if p else '信息不足',15))
        if p:
            color=COLORS[engine.GAN_WUXING[engine.GAN.index(p['stem'])]]
            branch_color=COLORS[engine.CANGGAN[p['branch']][0][1]]
            items += [text(x+30,321,p['stem'],47,color,600),text(x+30,385,p['branch'],47,branch_color,600)]
            for j,(h,g) in enumerate(zip(p.get('hiddenStems',[]),p.get('hiddenStemTenGods',[]))):
                items.append(text(x+10,429+j*26,h+' · '+g,13,'#6d7587'))
        else:
            items.append(text(x+30,342,'—',40,'#929aaa'))
    items += [text(49,570,'起运：'+chart['calendar']['qiyun']+'  ·  '+('顺排' if chart['calendar']['forward'] else '逆排')+'  ·  日期为传统折算近似',17),
              text(49,611,'大运',18,'#27365c',600)]
    for i,c in enumerate(chart['luckCycles']):
        x=49+i*122
        items += [f'<rect x="{x-8}" y="630" width="111" height="108" rx="12" fill="#ffffff"/>',
                  text(x+10,659,c['startDate'][:4]+' 起',12,'#7b8498'),text(x+15,696,c['stem']+c['branch'],26,'#3757c7',600),
                  text(x+10,722,f'{c["startAge"]:.1f}岁起',12,'#7b8498')]
    if len(overview.get('currentLuck',[]))>1:
        items.append(text(49,853,'交运：'+'；'.join(f'{c["stem"]}{c["branch"]} {c["from"]}至{c["toExclusive"]}（不含）' for c in overview['currentLuck']),12,'#67738d'))
    items += [text(49,786,'旺衰：'+chart['strength']['conclusion']+'   /   '+chart['pattern']['primaryPattern'],18),
              text(49,825,'扶抑首选：'+chart['usefulGod']['primaryUsefulGod']+'   /   调候参考：'+chart['usefulGod']['climate']['element'],18),
              text(49,879,'图示仅呈现已计算数据。未启用神煞、称骨、寿数等项目，不按参考图片补写结果。',13,'#7b8498'),
              text(49,907,'传统文化解释，不构成确定事件预测。完整条件与依据见报告。',13,'#7b8498'),'</g></svg>']
    return ''.join(items)
