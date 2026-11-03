import copy
from xml.etree import ElementTree
from test_acceptance import BASE, client, lock


def test_report_has_two_real_reading_modes_with_evidence(client):
    chart=lock(client)
    report=chart['report']
    assert report['defaultMode']=='plain'
    assert report['overview']['paragraphs']
    for chapter in report['chapters']:
        assert len(chapter['plain']['paragraphs'])>=2,chapter['title']
        assert chapter['plain']['takeaway']
        assert chapter['professional']['paragraphs']
        allowed={e['id'] for e in chapter['evidence']}
        assert allowed
        assert set(chapter['plain']['evidenceIds']) <= allowed
        assert set(chapter['professional']['evidenceIds']) <= allowed


def test_report_detail_is_chart_specific_and_keeps_technical_conclusions(client):
    chart=lock(client,year=1983,month=11,day=19,time='12:00',longitude=116.4,latitude=39.9)
    assert chart['pillars']['day']['stem']=='辛'
    assert chart['report']['overview']['dominantBranches']==[{'branch':'亥','count':3}]
    assert '亥' in ''.join(chart['report']['chapters'][0]['professional']['paragraphs'])
    professional=chart['report']['chapters'][3]['professional']
    assert chart['usefulGod']['primaryUsefulGod'] in ''.join(professional['paragraphs'])
    assert chart['report']['coverage']['unavailable']
    for label in ['称骨','鬼谷子','寿数']:
        assert any(label in item for item in chart['report']['coverage']['unavailable'])


def test_chart_attachment_is_a_safe_derived_image_without_mutation(client):
    chart=lock(client)
    before=copy.deepcopy(chart)
    response=client.get(f'/api/v1/charts/{chart["id"]}/image.svg')
    assert response.status_code==200
    assert 'image/svg+xml' in response.headers['content-type']
    root=ElementTree.fromstring(response.text)
    assert root.tag.endswith('svg')
    assert '庚' in response.text and '1990' in response.text
    assert '<script' not in response.text
    assert client.get(f'/api/v1/charts/{chart["id"]}').json()==before


def test_name_is_optional_and_not_sent_to_ai(client):
    from app.services.ai.question_answering import related_context
    chart=lock(client,name='测试用户')
    assert chart['input']['name']=='测试用户'
    assert '测试用户' not in str(related_context(chart,'解释事业'))


def test_old_locked_report_is_preserved(client):
    chart=lock(client)
    before=copy.deepcopy(chart)
    assert client.post('/api/v1/analyze',json={'chartId':chart['id']}).json()==before


def test_relationship_does_not_label_stem_combination_as_day_branch(client):
    chart=lock(client,year=1990,month=5,day=8)
    relationship=chart['report']['chapters'][7]
    assert '天干五合' not in ''.join(relationship['professional']['paragraphs'])
    assert not any('日支参与了1条' in p for p in relationship['plain']['paragraphs'])


def test_reading_keeps_both_luck_segments_in_transition_year(client):
    chart=lock(client,year=1990,month=5,day=11,referenceYear=2018)
    annual=next(c for c in chart['annualCycles'] if c['year']==2018)
    assert len(annual['segments'])==2
    current=chart['report']['overview']['currentAnnual']
    assert len(current['segments'])==2
    text=''.join(chart['report']['chapters'][10]['professional']['paragraphs'])
    for segment in annual['segments']:
        assert segment['activeLuck'] in text
        assert segment['analysis']['conclusion'] in text
        assert segment['from'][:10] in text
    annual_ids={e['id'] for e in chart['report']['chapters'][10]['evidence']}
    assert all(e['id'] in annual_ids for s in annual['segments'] for e in s['analysis']['evidence'])
    svg=client.get(f'/api/v1/charts/{chart["id"]}/image.svg').text
    assert '交运' in svg and '首段' in svg


def test_question_retrieval_uses_same_new_report_evidence(client):
    from app.services.ai.question_answering import related_context
    chart=lock(client)
    context=related_context(chart,'解释我的事业')
    assert {s['number'] for s in context['reportSections']}=={6}
    shown={e['id'] for e in chart['report']['chapters'][5]['evidence']}
    supplied={e['id'] for e in context['evidence']}
    assert shown <= supplied
    assert 'input' not in context and 'report' not in context


def test_plain_version_uses_everyday_words_and_one_bottom_disclaimer(client):
    chart=lock(client,year=1983,month=11,day=19,longitude=116.4)
    for c in chart['report']['chapters']:
        text=''.join(c['plain']['paragraphs'])+c['plain']['takeaway']
        for word in ['日主','月令','承载','象义','扶抑','原局','调候','通关','本版','传统模型','仅供参考','不构成']:
            assert word not in text,(c['number'],word)
    assert '仅供参考' in chart['report']['disclaimer']


def test_existing_openai_key_cannot_activate_a_paid_provider(client,monkeypatch):
    monkeypatch.setenv('OPENAI_API_KEY','test-not-a-real-key')
    monkeypatch.setenv('OPENAI_MODEL','not-used')
    chart=lock(client)
    assert client.get('/api/v1/status').json()['aiConfigured'] is False
    result=client.post(f'/api/v1/charts/{chart["id"]}/ask',json={'question':'这句话是什么意思？'})
    assert result.status_code==503
    assert client.get(f'/api/v1/charts/{chart["id"]}').json()==chart


def test_plain_luck_transition_uses_flow_year_intervals(client):
    chart=lock(client,year=1990,month=5,day=11,referenceYear=2018)
    text=''.join(chart['report']['chapters'][9]['plain']['paragraphs'])
    annual=next(a for a in chart['annualCycles'] if a['year']==2018)
    for s in annual['segments']:
        assert s['from'][:10] in text
        assert s['toExclusive'][:10] in text
    assert '（不含）' in text
    assert '2008-12-11至2018-12-11' not in text


def test_neutral_strength_does_not_use_strong_wording(client):
    chart=lock(client,year=1990,month=5,day=1)
    assert chart['strength']['conclusion']=='中和附近'
    texts=''.join(p for i in [1,5] for p in chart['report']['chapters'][i]['plain']['paragraphs'])
    assert '行动意愿比较足' not in texts
    assert '能力越强' not in texts
    assert '具体任务' in texts
