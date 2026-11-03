import Link from 'next/link';
export default function Sources() {
  return <main id="main-content" className="sources-page"><Link href="/" className="inline-link">← 返回命盘工作台</Link><span className="eyebrow">数据与算法说明</span><h1>计算有来源，解读有边界。</h1>
    <section id="ziping-origin"><h2>子平之名</h2><p>徐居易，字子平，世称徐子平，是四柱命理发展中的重要人物。以出生年月日时、五行生克推演命局的方法，后世称为“子平法”。<a href="https://pedia.cloud.edu.tw/Entry/Detail?search=子平&amp;title=子平">教育百科“子平”词条</a>记载其姓名与字号；<a href="https://zh.wikisource.org/wiki/三命通會_(四庫全書本)/卷07">《三命通会》卷七</a>也收录相关记述。年代记载存在差异，本页不补写未经核实的生卒年份。</p><p>人物插画采用古代学者意象，并非传世肖像。</p></section>
    <section id="traditional-methods"><h2>典籍与推演方法</h2><p>首页展示《渊海子平》《三命通会》《滴天髓》《子平真诠》等子平相关典籍。书籍转化为文字的动效，用来说明从专业依据到白话阅读的过程；左侧文字为案例节选，不是古籍原文。</p><p>个人报告采用已经实现并经过校验的计算与规则。具体引用对应到每节的判断依据，尚未计算的古法项目不会作为个人结果出现。</p></section>
    <section><h2>排盘与历法</h2><p>复用 MIT 项目 <a href="https://github.com/jinchenma94/bazi-skill">jinchenma94/bazi-skill</a> 的确定性 Python 函数，保留原许可证与测试。年柱按立春，月柱按十二节，日柱以真太阳时23时换日。</p><p>第三方采用简化天文公式，交节时刻不是秒级权威历书。临界出生时间需外部历书交叉核验。</p></section>
    <section><h2>地点与真太阳时</h2><p>支持中国大陆、1901–2098年，中央经线120°E、UTC+8。省、市、区县逐级选择后自动匹配经纬度，无需手填。坐标来自 <a href="https://www.geonames.org/about.html">GeoNames</a>（CC BY 4.0，WGS84），行政区划层级来自 <a href="https://github.com/modood/Administrative-divisions-of-China">Administrative-divisions-of-China</a>（WTFPL）。本地数据快照含3066个可匹配地点；未可靠匹配的区县不随意填坐标。所用坐标为行政中心参考点，未定位到具体医院或街道。</p><p>真太阳时 = 标准时间 + 4 ×（地理经度 − 120）分钟 + 均时差。均时差使用 <a href="https://gml.noaa.gov/grad/solcalc/solareqns.PDF">NOAA fractional-year 近似公式</a>，有近似误差，不能承诺分钟边界绝对正确。纬度保留供校验，不参与经度差公式。</p><p>年、月和起运按标准时间的真实交节瞬间；日、时采用真太阳时。时区选“当年钟表时间”时，使用 Asia/Shanghai 还原夏令时；跳时/重叠时段要求核实后用标准时间。</p></section>
    <section><h2>结构化规则</h2><p>版本 ziping-conservative-1.0：旺衰综合月令、分层根气、透干、生克泄耗与刑冲。四季土月未细分司令；格局、从格和合化均保留成立条件。扶抑、调候、通关分别展示，不按五行数量直接判断。</p><p>大运按传统三天折一年换算，起运日期为近似。流年按立春起止，交运年份分段。未知时辰逐分钟枚举整日三柱候选，不虚构时柱，起运使用候选区间估计。</p></section>
    <section><h2>方位的依据</h2><p>五行方位直接读取已确定的喜用结论，再按木对应东与东南、火对应南、土对应中央与西南东北、金对应西与西北、水对应北映射；喜用未定时不指定方向。感情章节中的地支方位只是传统方位表的对应，不能定位配偶的住址或相遇地点。该附录不重新判断格局或喜用。</p><p>文昌位、称骨、神煞、鬼谷子等项目，只有具备明确规则、可靠资料并完成实际计算后才会出现在个人结果中。</p></section>
    <section><h2>问答与锁定数据</h2><p>排盘、完整报告与复核均由程序独立生成，不需要外部模型接口。确认后的命盘和报告保存为不可修改的快照；深度问答只解释其中已有的内容，不能重新排盘或改写结论。未配置问答时，计算与报告照常可用。</p><p>提问时仅按主题选取相关结论和依据，姓名与完整出生资料不作为命盘解释的输入。需要查证外部资料时可以联网检索，并展示来源；外部网页不能覆盖已锁定的命盘结果。问答每日最多50次，北京时间零点更新。</p></section>
    <section><h2>阅读边界</h2><p>传统命理属于传统文化解释体系，不是科学预测模型。报告不能替代现实信息、医疗诊断、投资判断或婚恋决策。程序自我复核只证明内部一致，不证明命理有效性。</p></section>
  </main>;
}
