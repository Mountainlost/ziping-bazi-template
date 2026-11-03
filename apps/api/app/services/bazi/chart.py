import calendar as cal
from datetime import datetime, timedelta
from uuid import uuid4
from .adapter import engine, pillar, VENDOR_VERSION
from .solar_time import correct_time, standardize, BJ
from .relations import calculate_relations


def add_months(dt, months):
    index = dt.year * 12 + dt.month - 1 + months
    y, m = divmod(index, 12)
    return dt.replace(year=y, month=m + 1, day=min(dt.day, cal.monthrange(y, m + 1)[1]))


def build_one(data, standard_dt, unknown=False):
    correction = correct_time(standard_dt, data.longitude)
    solar = None if unknown else correction
    local = datetime.fromisoformat(correction['trueSolarTime'])
    # Year/month depend on actual UTC+8 instant. Day/hour follow solar clock.
    raw = engine.compute(standard_dt.date(), standard_dt.hour,
                         standard_dt.minute, sex=data.sex,
                         now=datetime(data.referenceYear, 7, 1, tzinfo=BJ))
    dg, dz, *_ = engine.resolve_day_pillar(local.date(), local.hour, local.minute)
    hg, hz = (None, None) if unknown else engine.resolve_hour_pillar(engine.GAN.index(dg), solar['correctedShichen'])
    pillars = {'year': pillar(*raw['pillars']['year'][:2], dg),
               'month': pillar(*raw['pillars']['month'][:2], dg),
               'day': pillar(dg, dz, dg, True), 'hour': pillar(hg, hz, dg)}
    events = engine.jie_events_around(standard_dt.year)
    previous = max((ev for ev in events if ev[0] <= standard_dt), key=lambda ev: ev[0])
    following = min((ev for ev in events if ev[0] > standard_dt), key=lambda ev: ev[0])
    distance = min((standard_dt - previous[0]).total_seconds(), (following[0] - standard_dt).total_seconds())
    start = add_months(standard_dt, raw['qiyun_years'] * 12 + raw['qiyun_months'])
    luck = []
    for i, row in enumerate(r for r in raw['dayun_rows'] if r[0] != '起运前'):
        a, b = add_months(start, i * 120), add_months(start, (i + 1) * 120)
        luck.append({'index': i + 1, 'stem': row[2][0], 'branch': row[2][1],
                     'startAge': raw['qiyun_years'] + raw['qiyun_months'] / 12 + i * 10,
                     'startDate': a.date().isoformat(), 'endDateExclusive': b.date().isoformat(),
                     'startYear': a.year, 'endYear': b.year,
                     'timingStability': 'disputed' if unknown else 'medium'})
    warnings = ['传统文化解释体系，不是科学预测模型；不构成医疗、财务或婚恋决策依据。',
                '第三方节气为简化天文算法，非秒级历书；交节或时辰边界附近请重新校验。',
                '本版用真太阳时换日（23时为日界）；年/月和起运用实际交节瞬间。']
    if distance <= 86400:
        warnings.append('距交节不足24小时，请重新确认出生时间；极近边界需权威历书复核。')
    if unknown:
        warnings.append('时辰未知：已枚举整日年/月/日候选，时柱保持未知。该候选仅代表所示区间，起运以区间起点估计，日内误差最多约4个月。涉及时柱的结论信息不足，不应把所选候选当作已证实唯一命盘。')
    if solar and min(abs((local.hour * 60 + local.minute + 60) % 120),
                     120 - (local.hour * 60 + local.minute + 60) % 120) < 5:
        warnings.append('真太阳时距时辰边界不足5分钟，均时差近似与出生记录误差可能影响时柱。')
    return {'id': str(uuid4()), 'locked': False, 'input': data.model_dump(), 'time': solar or {
                'standardTime': None, 'trueSolarTime': None, 'longitude': data.longitude,
                'unknown': True, 'note': '信息不足：时柱未知；仅按候选区间代表时刻区分三柱与排运方向。起运日期为范围估计，不是已知出生时刻。'},
            'calendar': {'solarDate': standard_dt.date().isoformat(), 'lunarDate': raw['lunar_text'],
                         'previousSolarTerm': {'name': previous[1], 'time': previous[0].isoformat()},
                         'nextSolarTerm': {'name': following[1], 'time': following[0].isoformat()},
                         'distanceFromBoundary': round(distance / 3600, 4), 'isNearBoundary': distance <= 86400,
                         'forward': raw['forward'], 'qiyun': raw['qiyun_text'],
                         'qiyunApproximate': True, 'dayBoundary': '真太阳时23:00换日'},
            'pillars': pillars, 'dayMaster': {'stem': dg, 'element': engine.GAN_WUXING[engine.GAN.index(dg)]},
            'tenGods': {k: p['tenGod'] if p else None for k, p in pillars.items()},
            'hiddenStems': {k: p['hiddenStems'] if p else None for k, p in pillars.items()},
            'relations': calculate_relations(pillars), 'luckCycles': luck, 'annualCycles': [],
            'shensha': [], 'warnings': warnings,
            'metadata': {'engine': 'jinchenma94/bazi-skill', 'engineVersion': VENDOR_VERSION,
                         'calculationVersion': '1.0.1', 'ruleVersion': 'ziping-conservative-1.0',
                         'scope': '中国大陆1901–2098；UTC+8；历史钟表可选Asia/Shanghai还原',
                         'shenshaPolicy': '当前版本未启用神煞，大师解盘不补算', 'referenceYear': data.referenceYear}}


def generate_candidates(data):
    from datetime import date
    birth_date = (engine.lunar_to_solar(data.year, data.month, data.day, leap=data.leapMonth)
                  if data.calendar == 'lunar' else date(data.year, data.month, data.day))
    unknown = data.accuracy == 'unknown'
    preferred = None
    if unknown:
        minutes = range(1440)
    elif data.accuracy == 'shichen':
        i = engine.ZHI.index(data.shichen)
        preferred = i * 120
        minutes = list(range(0, 60)) + list(range(1380, 1440)) if i == 0 else list(range(i * 120 - 60, i * 120 + 60))
    else:
        h, m = map(int, data.time.split(':'))
        center = h * 60 + m
        preferred = center
        spread = 0 if data.accuracy == 'exact' else int(data.accuracy)
        minutes = range(center - spread, center + spread + 1)
    # Signature sampling is cheap; calculate the complete calendar only once per distinct chart.
    unique = {}
    default_key = None
    for minute in minutes:
        naive = datetime.combine(birth_date, datetime.min.time()) + timedelta(minutes=minute)
        dt = standardize(naive, data.clockBasis)
        solar = correct_time(dt, data.longitude)
        local = datetime.fromisoformat(solar['trueSolarTime'])
        year, yg, yz, _ = engine.resolve_year_pillar(dt)
        mg, mz, *_ = engine.resolve_month_pillar(dt, engine.GAN.index(yg))
        dg, dz, *_ = engine.resolve_day_pillar(local.date(), local.hour, local.minute)
        key = (yg, yz, mg, mz, dg, dz, None if unknown else solar['correctedShichen'])
        if key not in unique:
            unique[key] = {'dt': dt, 'from': naive.isoformat(timespec='minutes'), 'to': naive.isoformat(timespec='minutes')}
        else:
            unique[key]['to'] = naive.isoformat(timespec='minutes')
        if minute == preferred:
            default_key = key
            unique[key]['dt'] = dt
    charts = []
    for key, item in sorted(unique.items(), key=lambda pair: pair[0] != default_key):
        chart = build_one(data, item['dt'], unknown=unknown)
        chart['candidateInterval'] = {'from': item['from'], 'to': item['to'], 'resolution': '1 minute'}
        if len(unique) > 1:
            chart['warnings'].append('出生时间范围跨越命盘边界。默认采用所选时间对应的命盘，可在排盘校验查看其他候选；起运时间为近似值。' if not unknown else '时辰未知，仅按三柱暂定，可在排盘校验查看其他候选。')
        charts.append(chart)
    return charts
