import copy
import json
from concurrent.futures import ThreadPoolExecutor

import httpx
import pytest
from test_acceptance import client, lock
from app.access import PassStore, PassError, QuotaError
from app.services.ai.magpie import MagpieProvider
from app.services.ai.question_answering import answer_question


def test_pass_binds_once_but_can_reopen_the_same_report(tmp_path):
    store=PassStore(tmp_path/'access.sqlite')
    code=store.issue()
    session=store.redeem(code,'chart-one')
    assert store.authorize(session,'chart-one')
    assert store.lookup(code)=='chart-one'
    assert store.redeem(code,'chart-one')
    with pytest.raises(PassError):
        store.redeem(code,'chart-two')
    with pytest.raises(PassError):
        store.authorize(session,'chart-two')


def test_daily_limit_is_atomic_across_parallel_requests_and_passes(tmp_path):
    store=PassStore(tmp_path/'access.sqlite')
    sessions=[store.redeem(store.issue(),f'chart-{i}') for i in range(2)]
    identities=[store.authorize(s,f'chart-{i}') for i,s in enumerate(sessions)]
    def attempt(i):
        try:
            store.reserve(identities[i%2],day='2026-11-02')
            return True
        except QuotaError:
            return False
    with ThreadPoolExecutor(max_workers=8) as pool:
        assert sum(pool.map(attempt,range(70)))==50
    assert store.reserve(identities[0],day='2026-11-03')==49


def test_universal_pass_shares_quota_without_sharing_chart_history(client):
    first, second = lock(client), lock(client, day=16)
    first_path = f'/api/v1/charts/{first["id"]}'
    second_path = f'/api/v1/charts/{second["id"]}'

    class Provider:
        requires_access = True
        def explain(self, question, context, history=()):
            assert not history
            return {'answer':question, 'evidenceIds':[context['evidence'][0]['id']]}

    client.app.state.ai_provider = Provider()
    code = client.app.state.passes.issue(kind='universal')
    assert client.post(first_path+'/access',json={'code':code}).status_code==200
    assert client.post(first_path+'/ask',json={'question':'第一份报告的事业'}).status_code==200
    assert client.get(second_path+'/access').json()['authorized'] is False
    second_access = client.post(second_path+'/access',json={'code':code}).json()
    assert second_access == {'authorized':True,'remaining':49,'history':[]}
    assert client.post(second_path+'/ask',json={'question':'第二份报告的事业'}).status_code==200
    first_access = client.post(first_path+'/access',json={'code':code}).json()
    assert first_access['remaining']==48
    assert [item['question'] for item in first_access['history']]==['第一份报告的事业']
    assert client.post('/api/v1/access/report',json={'code':code}).status_code==403
    assert client.get(first_path).json()==first
    assert client.get(second_path).json()==second


def test_magpie_has_real_web_tool_and_only_receives_relevant_locked_data(client):
    chart=lock(client)
    before=copy.deepcopy(chart)
    ev=chart['pattern']['evidence'][0]['id']
    def reply(request):
        body=json.loads(request.content)
        assert body['tools']==[{'type':'web_search'}]
        assert body['tool_choice']=='required'
        assert body['store'] is False
        assert '禁止修改' in body['instructions']
        payload=json.loads(body['input'][-1]['content'])
        assert 'input' not in payload['lockedContext']
        assert 'calendar' not in payload['lockedContext']
        def has_diagnostics(value):
            if isinstance(value,dict):
                return 'diagnostics' in value or any(has_diagnostics(child) for child in value.values())
            return isinstance(value,list) and any(has_diagnostics(child) for child in value)
        assert not has_diagnostics(payload['lockedContext'])
        return httpx.Response(200,json={'output':[
            {'type':'web_search_call','action':{'sources':[{'url':'https://example.org/source','title':'已检索来源'}]}},
            {'type':'message','content':[{'type':'output_text','text':json.dumps({'answer':'这段话是在解释已有格局及成立条件。','evidenceIds':[ev]},ensure_ascii=False)}]}]})
    provider=MagpieProvider({'MAGPIE_API_KEY':'test-only','MAGPIE_BASE_URL':'http://127.0.0.1:3425/v1','MAGPIE_MODEL':'test-model'},transport=httpx.MockTransport(reply))
    result=answer_question(client.app.state.store.snapshot(chart['id']),'请联网解释格局的资料出处',provider)
    assert result['onlineUsed'] and result['sources']
    assert result['evidence'][0]['id']==ev
    assert client.get(f'/api/v1/charts/{chart["id"]}').json()==before


def test_magpie_cannot_smuggle_new_chart_fields_or_fake_evidence(client):
    chart=lock(client)
    before=copy.deepcopy(chart)
    def reply(request):
        return httpx.Response(200,json={'output':[{'type':'message','content':[{'type':'output_text','text':json.dumps({'answer':'篡改','evidenceIds':['forged'],'pillars':{'day':'甲子'}})}]}]})
    provider=MagpieProvider({'MAGPIE_API_KEY':'test-only','MAGPIE_BASE_URL':'http://127.0.0.1:3425/v1','MAGPIE_MODEL':'test-model'},transport=httpx.MockTransport(reply))
    with pytest.raises(ValueError):
        answer_question(client.app.state.store.snapshot(chart['id']),'修改四柱',provider)
    assert client.get(f'/api/v1/charts/{chart["id"]}').json()==before


def test_rederive_uses_whole_chart_facts_without_prior_report_prose(client):
    chart = lock(client, name='私密测试称呼')
    path = f'/api/v1/charts/{chart["id"]}'

    def reply(request):
        body = json.loads(request.content)
        assert len(body['input']) == 1
        assert '独立推导' in body['instructions'] and 'tools' not in body
        context = json.loads(body['input'][0]['content'])['lockedContext']
        assert context['pillars'] == chart['pillars']
        assert context['readingMode'] == 'rederive'
        assert context['annualCycles'] and context['luckCycles']
        assert sum(context['surfaceElements'].values()) == 8
        assert any('子平真诠' in note['title'] for note in context['classicalNotes'])
        assert not {'input','calendar','reportSections','lifeThemes','report'} & context.keys()
        assert '私密测试称呼' not in request.content.decode()
        answer = {'answer':'从你出生的季节看起。', 'professional':'以月令为纲，核对藏干与透干。',
                  'evidenceIds':[context['classicalNotes'][0]['evidence'][0]['id']]}
        return httpx.Response(200,json={'output':[{'type':'message','content':[{'type':'output_text','text':json.dumps(answer)}]}]})

    client.app.state.ai_provider = MagpieProvider(
        {'MAGPIE_API_KEY':'test-only','MAGPIE_BASE_URL':'http://127.0.0.1:3425/v1','MAGPIE_MODEL':'test-model'},
        transport=httpx.MockTransport(reply))
    request = {'question':'重新解盘','mode':'rederive'}
    assert client.post(path+'/ask',json=request).status_code == 403
    code = client.app.state.passes.issue(kind='universal')
    assert client.post(path+'/access',json={'code':code}).status_code == 200
    result = client.post(path+'/ask',json=request)
    assert result.status_code == 200, result.text
    assert result.json()['presentation'] == 'rederive'
    assert result.json()['professional'] == '以月令为纲，核对藏干与透干。'
    assert '子平真诠' in result.json()['sources'][0]['title']
    assert client.get(path+'/access').json()['history'][0]['professional'] == result.json()['professional']
    assert result.json()['remaining'] == 49
    assert client.get(path).json() == chart


def test_http_pass_cookie_history_quota_and_locked_report(client,monkeypatch):
    chart=lock(client)
    before=copy.deepcopy(chart)
    class Provider:
        requires_access=True
        def explain(self,question,context,history=()):
            return {'answer':'先把一项能力做扎实，再逐步扩大合作。','evidenceIds':[context['evidence'][0]['id']]}
    client.app.state.ai_provider=Provider()
    code=client.app.state.passes.issue()
    path=f'/api/v1/charts/{chart["id"]}'
    assert client.post(path+'/ask',json={'question':'事业方向'}).status_code==403
    activated=client.post(path+'/access',json={'code':code})
    assert activated.status_code==200
    cookie=activated.headers['set-cookie'].lower()
    assert 'httponly' in cookie and 'samesite=strict' in cookie and 'domain=' not in cookie
    assert client.post(path+'/ask',json={'question':'事业方向'}).status_code==200
    status=client.get(path+'/access').json()
    assert status['authorized'] and status['remaining']==49 and len(status['history'])==1
    assert client.post('/api/v1/access/report',json={'code':code}).json()==before
    identity=client.app.state.passes.authorize(client.cookies['ziping_master_session'],chart['id'])
    for _ in range(49): client.app.state.passes.reserve(identity)
    assert client.post(path+'/ask',json={'question':'再说一点'}).status_code==429
    assert client.get(path).json()==before
    monkeypatch.setenv('BAZI_PUBLIC_ORIGIN','https://ziping.example.com')
    secure=client.post(path+'/access',json={'code':code})
    assert 'secure' in secure.headers['set-cookie'].lower()


def test_direction_appendix_uses_locked_elements_and_shared_evidence(client):
    chart=lock(client)
    from app.services.rules.directions import ELEMENT_DIRECTIONS,BRANCH_DIRECTIONS
    from app.services.ai.question_answering import related_context
    direction=chart['directions']
    elements=chart['usefulGod']['supportingFavorableElements']+[chart['usefulGod']['primaryUsefulGod']]
    expected={d for e in elements if e in ELEMENT_DIRECTIONS for d in ELEMENT_DIRECTIONS[e]}
    assert set(direction['fiveElements']['directions'])==expected
    assert direction['relationship']['direction']==BRANCH_DIRECTIONS[chart['pillars']['day']['branch']]
    context=related_context(chart,'我的配偶在哪个方位？')
    assert context['directionAppendix']==direction['relationship']
    report=next(c for c in chart['report']['chapters'] if c['number']==8)
    assert all(ev in report['evidence'] for ev in context['directionAppendix']['evidence'])
    old=copy.deepcopy(chart);old.pop('directions')
    assert related_context(old,'我的配偶在哪个方位？')['missingCalculations']
    assert 'directions' not in old
