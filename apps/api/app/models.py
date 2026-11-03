from datetime import date, datetime, timezone, timedelta
from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator


class BirthInput(BaseModel):
    model_config = ConfigDict(extra='forbid')
    name: str = Field(default='', max_length=30)
    calendar: Literal['solar', 'lunar'] = 'solar'
    year: int = Field(ge=1901, le=2098)
    month: int = Field(ge=1, le=12)
    day: int = Field(ge=1, le=31)
    leapMonth: bool = False
    time: str | None = Field(default=None, pattern=r'^([01]\d|2[0-3]):[0-5]\d$')
    accuracy: Literal['exact', '10', '30', '60', 'shichen', 'unknown'] = 'exact'
    shichen: Literal['子','丑','寅','卯','辰','巳','午','未','申','酉','戌','亥'] | None = None
    sex: Literal['男', '女']
    province: str = Field(min_length=1, max_length=40)
    city: str = Field(min_length=1, max_length=40)
    district: str = Field(default='', max_length=40)
    longitude: float = Field(ge=73.5, le=135.1, allow_inf_nan=False)
    latitude: float = Field(ge=18, le=54, allow_inf_nan=False)
    clockBasis: Literal['standard', 'wall'] = 'standard'
    referenceYear: int = Field(default_factory=lambda: datetime.now(timezone(timedelta(hours=8))).year, ge=1901, le=2098)

    @model_validator(mode='after')
    def validate_birth(self):
        if self.calendar == 'solar':
            date(self.year, self.month, self.day)
            if self.leapMonth:
                raise ValueError('闰月只用于农历')
        if self.accuracy not in ('unknown', 'shichen') and not self.time:
            raise ValueError('请提供出生时间或选择完全不知道')
        if self.accuracy == 'shichen' and not self.shichen:
            raise ValueError('请选择已知时辰')
        if self.accuracy == 'unknown' and self.clockBasis == 'wall':
            raise ValueError('未知时辰请提供已还原为 UTC+8 标准时间的日期')
        return self


class AnalyzeInput(BaseModel):
    model_config = ConfigDict(extra='forbid')
    chartId: str = Field(min_length=1, max_length=80)


class QuestionInput(BaseModel):
    model_config = ConfigDict(extra='forbid')
    question: str = Field(min_length=1, max_length=1000)
    mode: Literal['question', 'rederive'] = 'question'


class PassInput(BaseModel):
    model_config = ConfigDict(extra='forbid')
    code: str = Field(min_length=12, max_length=120)


class LockedChart(BaseModel):
    """Serialized snapshot: immutable bytes, never a nested mutable model."""
    model_config = ConfigDict(frozen=True)
    id: str
    payload: str

    def read(self) -> dict[str, Any]:
        import json
        return json.loads(self.payload)
