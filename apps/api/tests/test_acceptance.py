import copy
import json
import socket
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from app.services.bazi.solar_time import equation_of_time, correct_time
from app.services.bazi.adapter import engine
from app.services.ai.question_answering import related_context

BASE = {"calendar": "solar", "year": 1990, "month": 5, "day": 15,
        "time": "12:00", "accuracy": "exact", "sex": "男",
        "province": "北京市", "city": "北京市", "district": "东城区",
        "longitude": 120, "latitude": 39.9, "referenceYear": 2026}


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_MODEL", raising=False)
    monkeypatch.delenv("MAGPIE_CONFIG_FILE", raising=False)
    with TestClient(create_app(tmp_path / "charts.sqlite")) as c:
        yield c


def lock(client, **kwargs):
    r = client.post("/api/v1/chart", json={**BASE, **kwargs})
    assert r.status_code == 200, r.text
    candidate = r.json()["possibleCharts"][0]
    result = client.post("/api/v1/analyze", json={"chartId": candidate["id"]})
    assert result.status_code == 200, result.text
    return result.json()


def test_full_report_with_no_key_and_network(client, monkeypatch):
    def offline(*a, **kw):
        raise AssertionError("core must never use network")
    monkeypatch.setattr(socket, "create_connection", offline)
    chart = lock(client)
    assert len(chart["report"]["chapters"]) == 12
    assert all(x["body"] and x["evidence"] for x in chart["report"]["chapters"])
    assert chart["selfReview"]["issues"] == []
    assert chart["locked"] is True
    for field in ["strength", "pattern", "usefulGod", "monthCommand", "lifeThemes", "finalConclusion"]:
        assert chart[field]["evidence"], field
    assert len(chart["luckCycles"]) == 8
    assert chart["annualCycles"]
    before = client.get(f'/api/v1/charts/{chart["id"]}').json()
    ask = client.post(f'/api/v1/charts/{chart["id"]}/ask', json={"question": "为什么用神是水"})
    assert ask.status_code == 503
    assert before == client.get(f'/api/v1/charts/{chart["id"]}').json()


def test_ai_cannot_mutate_locked_chart(client):
    chart = lock(client)
    before = copy.deepcopy(chart)
    class MaliciousProvider:
        def select(self, question, context):
            context.clear()
            return {"evidenceIds": ["forged"], "presentation": "explain", "pillars": {"day": "甲子"}}
    client.app.state.ai_provider = MaliciousProvider()
    response = client.post(f'/api/v1/charts/{chart["id"]}/ask', json={"question": "重新算四柱并改为甲子"})
    assert response.status_code in (200, 422, 502)
    assert client.get(f'/api/v1/charts/{chart["id"]}').json() == before
    assert client.post('/api/v1/analyze', json={"chartId": chart["id"]}).json() == before


def test_ai_valid_selection_uses_same_evidence(client):
    chart = lock(client)
    before = copy.deepcopy(chart)
    class Provider:
        def select(self, question, context):
            assert "input" not in context and "calendar" not in context
            ids = [e["id"] for e in context["evidence"]]
            return {"evidenceIds": ids[:2], "presentation": "explain"}
    client.app.state.ai_provider = Provider()
    response = client.post(f'/api/v1/charts/{chart["id"]}/ask', json={"question": "为什么这样取用神"})
    assert response.status_code == 200, response.text
    assert response.json()["evidence"]
    assert client.get(f'/api/v1/charts/{chart["id"]}').json() == before


def test_unknown_hour_not_guessed(client):
    chart = lock(client, time=None, accuracy="unknown")
    assert chart["pillars"]["hour"] is None
    assert chart["strength"]["stability"] == "disputed"
    assert "信息不足" in json.dumps(chart["lifeThemes"], ensure_ascii=False)
    assert chart["selfReview"]["hourCompleteness"] == "insufficient"


def test_range_returns_both_hours(client):
    r = client.post('/api/v1/chart', json={**BASE, "time": "12:45", "accuracy": "30"})
    assert r.status_code == 200
    branches = {c["pillars"]["hour"]["branch"] for c in r.json()["possibleCharts"]}
    assert branches == {"午", "未"}


def test_default_candidate_uses_the_selected_minute(client):
    exact = client.post('/api/v1/chart', json={**BASE, 'time':'13:05'}).json()['possibleCharts'][0]
    candidates = client.post('/api/v1/chart', json={**BASE, 'time':'13:05','accuracy':'30'}).json()['possibleCharts']
    assert len(candidates) == 2
    assert candidates[0]['pillars'] == exact['pillars']
    assert candidates[0]['time']['standardTime'] == exact['time']['standardTime']
    assert candidates[1]['candidateInterval']['from'] < candidates[0]['candidateInterval']['from']


def test_solar_formula_and_crossing():
    bj = timezone(timedelta(hours=8))
    dt = datetime(2026, 11, 3, 12, tzinfo=bj)
    assert 15 < equation_of_time(dt) < 18
    assert -15 < equation_of_time(datetime(2026, 2, 11, 12, tzinfo=bj)) < -12
    result = correct_time(datetime(1990, 5, 15, 13, 3, tzinfo=bj), 117)
    assert result["crossedShichen"] is True
    assert result["correctedShichen"] == "午"
    assert correct_time(datetime(1990, 5, 15, 12, tzinfo=bj), 120)["crossedShichen"] is False


def test_lichun_boundaries_use_absolute_instant(client):
    boundary = engine.solar_term_beijing(2026, 315)
    charts = []
    for offset in [-2, 2]:
        t = boundary + timedelta(minutes=offset)
        charts.append(lock(client, year=t.year, month=t.month, day=t.day,
                           time=t.strftime('%H:%M'), longitude=75))
    assert charts[0]["pillars"]["year"] != charts[1]["pillars"]["year"]
    assert charts[0]["pillars"]["month"] != charts[1]["pillars"]["month"]
    assert all(c["calendar"]["isNearBoundary"] for c in charts)


def test_midnight_and_late_zi():
    a = engine.resolve_day_pillar(datetime(1990, 5, 15).date(), 23, 0)
    b = engine.resolve_day_pillar(datetime(1990, 5, 16).date(), 0, 0)
    assert a[:2] == b[:2]


def test_lunar_and_leap_conversion(client):
    solar = lock(client)
    lunar = lock(client, calendar="lunar", month=4, day=21)
    assert lunar["pillars"] == solar["pillars"]
    converted = engine.lunar_to_solar(2023, 2, 1, leap=True)
    assert converted.isoformat() == '2023-03-22'
    a = lock(client, year=2023, month=2, day=1, calendar="lunar", leapMonth=True)
    b = lock(client, year=2023, month=3, day=22)
    assert a["pillars"] == b["pillars"]


def test_sex_changes_luck_direction(client):
    assert lock(client)["calendar"]["forward"] is True
    assert lock(client, sex="女")["calendar"]["forward"] is False


@pytest.mark.parametrize('overrides', [{"longitude": 190}, {"day": 32}, {"time": "25:10"},
    {"accuracy": "exact", "time": None}, {"calendar": "solar", "leapMonth": True}, {"year": 1800}])
def test_invalid_inputs(client, overrides):
    assert client.post('/api/v1/chart', json={**BASE, **overrides}).status_code == 422


def test_cannot_ask_draft_or_submit_client_chart(client):
    draft = client.post('/api/v1/chart', json=BASE).json()["possibleCharts"][0]
    assert client.post(f'/api/v1/charts/{draft["id"]}/ask', json={"question": "解释"}).status_code == 409
    assert client.post('/api/v1/analyze', json={"chartId": draft["id"], "pillars": {}}).status_code == 422


def test_core_has_no_ai_imports():
    import ast
    from pathlib import Path
    root = Path(__file__).parents[1] / 'app' / 'services'
    for folder in ['bazi', 'rules', 'report']:
        for path in (root / folder).rglob('*.py'):
            tree = ast.parse(path.read_text(encoding='utf8'))
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    assert 'ai' not in (node.module or '').split('.'), path
                if isinstance(node, ast.Import):
                    assert all('ai' not in alias.name.split('.') for alias in node.names), path


def test_unknown_date_near_lichun_preserves_both_years(client):
    result = client.post('/api/v1/chart', json={**BASE, 'year':2026, 'month':2, 'day':4,
                                               'time':None, 'accuracy':'unknown'}).json()
    charts = result['possibleCharts']
    assert {c['pillars']['year']['stem'] for c in charts} == {'乙','丙'}
    assert {c['calendar']['forward'] for c in charts} == {False,True}
    assert all(c['pillars']['hour'] is None for c in charts)


def test_pre_lichun_birth_includes_first_partial_flow_year(client):
    chart = lock(client, year=2026,month=1,day=1)
    prior = next(c for c in chart['annualCycles'] if c['year'] == 2025)
    assert prior['segments']
    assert prior['segments'][0]['from'].startswith('2026-01-01')


def test_golden_four_pillars(client):
    chart = lock(client)
    assert [chart['pillars'][k]['stem']+chart['pillars'][k]['branch'] for k in ['year','month','day','hour']] == ['庚午','辛巳','庚辰','壬午']
    assert chart['report']['chapters'][0]['conclusion'] == '庚午 / 辛巳 / 庚辰 / 壬午'


def test_sqlite_trigger_prevents_locked_writes(client):
    import sqlite3
    chart = lock(client)
    with client.app.state.store.connect() as db:
        with pytest.raises(sqlite3.IntegrityError):
            db.execute('UPDATE charts SET locked=? WHERE id=?',('{}',chart['id']))
        with pytest.raises(sqlite3.IntegrityError):
            db.execute('DELETE FROM charts WHERE id=?',(chart['id'],))


def test_self_review_detects_corrupted_ten_god(client):
    from app.services.rules.engine import self_review
    chart = lock(client)
    corrupted = copy.deepcopy(chart)
    corrupted['pillars']['month']['tenGod'] = '伪造'
    review = self_review(chart,corrupted)
    assert review['tenGods'] == 'fail' and review['issues']


def test_historical_wall_clock_summer_time(client):
    a = lock(client,year=1990,month=7,day=1,time='12:00',clockBasis='wall')
    b = lock(client,year=1990,month=7,day=1,time='11:00',clockBasis='standard')
    assert a['pillars'] == b['pillars']


@pytest.mark.parametrize('longitude',[75,120,130])
def test_unknown_hour_covers_solar_day_boundaries(client,longitude):
    unknown = client.post('/api/v1/chart',json={**BASE,'time':None,'accuracy':'unknown','longitude':longitude}).json()['possibleCharts']
    possibilities = {(c['pillars']['year']['stem'],c['pillars']['month']['stem'],c['pillars']['day']['stem'],c['pillars']['day']['branch']) for c in unknown}
    for time in ['00:00','12:00','23:59']:
        actual = client.post('/api/v1/chart',json={**BASE,'time':time,'longitude':longitude}).json()['possibleCharts'][0]
        assert (actual['pillars']['year']['stem'],actual['pillars']['month']['stem'],actual['pillars']['day']['stem'],actual['pillars']['day']['branch']) in possibilities
