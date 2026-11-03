from itertools import combinations

TABLE = {
    '六合': ['子丑','寅亥','卯戌','辰酉','巳申','午未'],
    '六冲': ['子午','丑未','寅申','卯酉','辰戌','巳亥'],
    '六害': ['子未','丑午','寅巳','卯辰','申亥','酉戌'],
    '相破': ['子酉','丑辰','寅亥','卯午','巳申','未戌'],
    '相刑': ['寅巳','巳申','寅申','丑戌','戌未','丑未','子卯'],
    '三合': ['申子辰','亥卯未','寅午戌','巳酉丑'],
    '三会': ['寅卯辰','巳午未','申酉戌','亥子丑'],
    '天干五合': ['甲己','乙庚','丙辛','丁壬','戊癸'],
}


def calculate_relations(pillars):
    branches = [(k, p['branch']) for k, p in pillars.items() if p]
    stems = [(k, p['stem']) for k, p in pillars.items() if p]
    result = []
    for kind, groups in TABLE.items():
        for group in groups:
            pool = stems if kind == '天干五合' else branches
            for members in combinations(pool, len(group)):
                if sorted(x[1] for x in members) == sorted(group):
                    result.append({'type': kind, 'members': [x[0] for x in members], 'characters': group,
                                   'transformed': False,
                                   'explanation': f'{"、".join(x[0] for x in members)}见{group}{kind}，仅记录关系；合化须另核月令、透干与破坏条件，不自动成化。'})
    for char in '辰午酉亥':
        matches = [k for k, b in branches if b == char]
        if len(matches) >= 2:
            result.append({'type': '自刑', 'members': matches, 'characters': char * 2, 'transformed': False,
                           'explanation': f'{char}重复，按本版自刑规则记录；不直接对应现实事件。'})
    return result
