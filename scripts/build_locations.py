"""Build an offline location index from GeoNames CN.zip and modood pca-code.json.

GeoNames coordinates: CC BY 4.0, WGS84. Division labels: WTFPL.
No network calls are made by this builder or by the resulting runtime index.
Usage: python build_locations.py CN.zip pca-code.json [--summary]
"""
import hashlib
import base64
import gzip
import json
import re
import sys
import zipfile
from pathlib import Path

CHINESE = re.compile(r'^[\u3400-\u9fff·]+$')
SUFFIX = re.compile(r'(自治县|自治旗|自治区|特别行政区|地区|省|市|区|县|旗|盟)$')


def short_name(name):
    return SUFFIX.sub('', name)


def build(zip_path, divisions_path):
    divisions = json.loads(Path(divisions_path).read_text(encoding='utf-8'))
    features = []
    with zipfile.ZipFile(zip_path) as archive:
        with archive.open('CN.txt') as stream:
            for raw in stream:
                fields = raw.decode('utf-8').rstrip('\n').split('\t')
                if fields[7] not in {'ADM1', 'ADM2', 'ADM3'}:
                    continue
                latitude, longitude = float(fields[4]), float(fields[5])
                if not (18 <= latitude <= 54 and 73.5 <= longitude <= 135.1):
                    continue
                aliases = {n for n in fields[3].split(',') if CHINESE.fullmatch(n)}
                features.append({'id': int(fields[0]), 'names': aliases, 'latitude': latitude,
                                 'longitude': longitude, 'level': fields[7], 'province': fields[10], 'city': fields[11]})
    provinces = [f for f in features if f['level'] == 'ADM1']
    locations, missing = [], []

    def select(candidates, name):
        exact = [f for f in candidates if name in f['names']]
        if len(exact) == 1:
            return exact[0]
        normalized = [f for f in candidates if any(short_name(n) == short_name(name) for n in f['names'])]
        return normalized[0] if len(normalized) == 1 else None

    def append(province, city, district, code, feature):
        locations.append({'province': province, 'city': city, 'district': district, 'code': code,
                          'longitude': feature['longitude'], 'latitude': feature['latitude'],
                          'geonameId': feature['id'], 'level': 'district' if district else 'city'})

    for province in divisions:
        parent = select(provinces, province['name'])
        if not parent:
            missing.append(province['name'])
            continue
        regional = [f for f in features if f['province'] == parent['province'] and f['level'] != 'ADM1']
        for city in province['children']:
            city_name = province['name'] if city['name'] == '市辖区' else city['name']
            centers = [f for f in regional if f['level'] == 'ADM2' and f['city'] == city['code']]
            center = centers[0] if len(centers) == 1 else select([f for f in regional if f['level'] == 'ADM2'], city_name)
            if center:
                append(province['name'], city_name, '', city['code'], center)
            district_features = [f for f in regional if f['level'] == 'ADM3' and f['city'] == city['code']]
            for district in city.get('children', []):
                match = select(district_features, district['name'])
                if not match:
                    match = select(regional, district['name'])
                if match:
                    append(province['name'], city_name, district['name'], district['code'], match)
                else:
                    missing.append(province['name'] + '/' + city_name + '/' + district['name'])
    locations.sort(key=lambda location: location['code'])
    return {'provider': '本地离线省市区中心点', 'datum': 'WGS84', 'snapshotDate': '2026-11-02',
            'sources': [{'name': 'GeoNames', 'url': 'https://download.geonames.org/export/dump/', 'license': 'CC BY 4.0'},
                        {'name': 'Administrative-divisions-of-China', 'url': 'https://github.com/modood/Administrative-divisions-of-China', 'license': 'WTFPL'}],
            'sourceSha256': {'CN.zip': hashlib.sha256(Path(zip_path).read_bytes()).hexdigest(),
                             'pca-code.json': hashlib.sha256(Path(divisions_path).read_bytes()).hexdigest()},
            'note': '行政区中心点为近似位置；仅收录唯一匹配的记录。未匹配区县不可沿用其他地点坐标。',
            'locations': locations, 'unmatched': missing}


if __name__ == '__main__':
    result = build(sys.argv[1], sys.argv[2])
    if '--summary' in sys.argv:
        print(json.dumps({'locations': len(result['locations']), 'provinces': len({r['province'] for r in result['locations']}),
                          'cities': len({(r['province'], r['city']) for r in result['locations']}),
                          'unmatched': len(result['unmatched']), 'missingExamples': result['unmatched'][:12],
                          'suining': [r for r in result['locations'] if r['district'] == '睢宁县']}, ensure_ascii=False))
    elif '--packed' in sys.argv:
        rows = result.pop('locations')
        result['compressedLocations'] = base64.b64encode(gzip.compress(json.dumps(rows, ensure_ascii=False, separators=(',', ':')).encode('utf-8'), mtime=0)).decode('ascii')
        print(json.dumps(result, ensure_ascii=False, separators=(',', ':')))
    else:
        print(json.dumps(result, ensure_ascii=False, separators=(',', ':')))
