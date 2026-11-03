"""Symbolic direction appendix. It never changes strength, pattern or useful god."""
from .common import evidence, unique_evidence

ELEMENT_DIRECTIONS={'木':['东','东南'],'火':['南'],'土':['中央','西南','东北'],'金':['西','西北'],'水':['北']}
BRANCH_DIRECTIONS=dict(zip('子丑寅卯辰巳午未申酉戌亥',['北','东北','东北','东','东南','东南','南','西南','西南','西','西北','西北']))
METHOD='symbolic-directions-1.0'


def evaluate(chart):
    elements=[e for e in dict.fromkeys([chart['usefulGod']['primaryUsefulGod']]+chart['usefulGod']['supportingFavorableElements']) if e in ELEMENT_DIRECTIONS]
    favorable=list(dict.fromkeys(d for element in elements for d in ELEMENT_DIRECTIONS[element]))
    branch=chart['pillars']['day']['branch']
    relationship=BRANCH_DIRECTIONS[branch]
    five_evidence=unique_evidence(chart['usefulGod']['evidence'][:1]+[
        evidence('五行方位映射','rules.directions.ELEMENT_DIRECTIONS','neutral',
                 '只将已经确定的扶抑有利元素'+ '、'.join(elements)+'映射为'+ '、'.join(favorable)+'；不重新判断喜用，不把调候参考混入同一列表。')])
    relationship_evidence=[
        evidence('夫妻宫事实','pillars.day.branch','neutral',f'已计算日支为{branch}，本附录以日支作为夫妻宫观察入口，不改变四柱。'),
        evidence('地支传统方位','rules.directions.BRANCH_DIRECTIONS','neutral',f'本版地支方位表将{branch}对应{relationship}。这里只提供传统支位象义，不能据此确定配偶出生地、住址或真实地理位置。')]
    return {'method':METHOD,'referenceFrame':'symbolic-only',
            'fiveElements':{'conclusion':'五行方位：'+('、'.join(favorable) or '暂不指定'),'elements':elements,'directions':favorable,
                'plainLanguage':('这份报告把'+ '、'.join(elements)+'列为需要补充的力量；按传统五行方位，对应'+ '、'.join(favorable)+'。这里的中央指空间中的位置，不指某座城市。') if elements else '这份报告还没有选定需要补充的五行，因此暂不指定有利方向。',
                'stability':'medium','evidence':five_evidence},
            'relationship':{'conclusion':'夫妻宫传统方位：'+relationship,'direction':relationship,'dayBranch':branch,
                'plainLanguage':'按这份报告采用的传统方位对应方法，感情章节中的方向参考为'+relationship+'。这个方向不能用来定位另一半的出生地、住址，也不能据此断言会在哪里遇见某个人。',
                'stability':'disputed','evidence':relationship_evidence},
            'references':[{'title':'《三命通会》地支方隅及戌亥西北、辰巳东南相关记载','url':'https://zh.wikisource.org/wiki/三命通會/卷三'},
                          {'title':'国立台北艺术大学《文资学报》所载二十四山与地支方位说明','url':'https://scr.tnua.edu.tw/wp-content/uploads/JCR14-%E6%96%87%E8%B3%87%E5%AD%B8%E5%A0%B1.pdf'}]}
