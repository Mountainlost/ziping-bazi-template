import math
from test_acceptance import client


def test_offline_locations_cover_provinces_and_link_suining_to_its_own_coordinates(client):
    data = client.get('/api/v1/locations').json()
    assert data['datum'] == 'WGS84'
    rows = data['locations']
    assert len({r['province'] for r in rows}) == 31
    assert len(rows) >= 2800
    suining = next(r for r in rows if (r['province'], r['city'], r['district']) == ('江苏省', '徐州市', '睢宁县'))
    assert 117 < suining['longitude'] < 119
    assert 33 < suining['latitude'] < 35
    assert suining['longitude'] != 120.173
    assert any(source['name'] == 'GeoNames' and source['license'] == 'CC BY 4.0' for source in data['sources'])


def test_same_named_districts_are_scoped_to_their_province_and_city(client):
    rows = client.get('/api/v1/locations').json()['locations']
    keys = [(r['province'], r['city'], r['district']) for r in rows]
    assert len(keys) == len(set(keys))
    districts = [r for r in rows if r['district'] == '新城区']
    assert len(districts) >= 2
    assert len({(r['longitude'], r['latitude']) for r in districts}) == len(districts)
    for row in rows:
        assert math.isfinite(row['longitude']) and math.isfinite(row['latitude'])
        assert 73.5 <= row['longitude'] <= 135.1 and 18 <= row['latitude'] <= 54
