"""NOAA fractional-year equation of time, independent of LLM or vendor engine."""
import calendar
import math
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

BJ = timezone(timedelta(hours=8))
BRANCHES = '子丑寅卯辰巳午未申酉戌亥'


def shichen(dt):
    return BRANCHES[((dt.hour + 1) // 2) % 12]


def equation_of_time(dt):
    days = 366 if calendar.isleap(dt.year) else 365
    hour = dt.hour + dt.minute / 60 + dt.second / 3600
    g = 2 * math.pi / days * (dt.timetuple().tm_yday - 1 + (hour - 12) / 24)
    return 229.18 * (0.000075 + 0.001868 * math.cos(g) - 0.032077 * math.sin(g)
                     - 0.014615 * math.cos(2 * g) - 0.040849 * math.sin(2 * g))


def standardize(dt, basis):
    if basis == 'standard':
        return dt.replace(tzinfo=BJ)
    zone = ZoneInfo('Asia/Shanghai')
    a, b = dt.replace(tzinfo=zone, fold=0), dt.replace(tzinfo=zone, fold=1)
    if a.utcoffset() != b.utcoffset():
        raise ValueError('该历史钟表时间存在夏令时跳时或重叠，请核实后改用 UTC+8 标准时间')
    return a.astimezone(BJ)


def correct_time(standard_datetime, longitude, timezone_meridian=120):
    longitude_minutes = 4 * (longitude - timezone_meridian)
    eot = equation_of_time(standard_datetime)
    corrected = standard_datetime + timedelta(minutes=longitude_minutes + eot)
    return {'standardTime': standard_datetime.isoformat(), 'longitude': longitude,
            'centralMeridian': timezone_meridian, 'longitudeCorrectionMinutes': round(longitude_minutes, 4),
            'equationOfTimeMinutes': round(eot, 4), 'trueSolarTime': corrected.isoformat(),
            'originalShichen': shichen(standard_datetime), 'correctedShichen': shichen(corrected),
            'crossedShichen': shichen(standard_datetime) != shichen(corrected),
            'method': 'NOAA fractional-year approximation', 'precisionNote': '近似均时差；临界分钟请复核，非天文台秒级历书。'}
