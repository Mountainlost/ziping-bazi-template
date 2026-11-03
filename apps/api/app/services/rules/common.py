import hashlib
from ..bazi.adapter import engine

ELEMENTS = '木火土金水'


def element(stem):
    return engine.GAN_WUXING[engine.GAN.index(stem)]


def relation(day_element, other_element):
    return (ELEMENTS.index(other_element) - ELEMENTS.index(day_element)) % 5


def evidence(factor, source, effect, explanation):
    key = '|'.join([factor, source, effect, explanation])
    return {'id': 'e-' + hashlib.sha256(key.encode()).hexdigest()[:14], 'factor': factor,
            'source': source, 'effect': effect, 'explanation': explanation}


def unique_evidence(items):
    return list({item['id']: item for item in items}.values())
