"""All access to the unmodified, pinned third-party engine lives here."""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
VENDOR_VERSION = '112a5d84cd1a001a0038cafca3be68d93e4c0cc9'
SOURCE = ROOT / 'third_party/bazi-skill/scripts/pai_pan.py'
spec = importlib.util.spec_from_file_location('bazi_vendor', SOURCE)
engine = importlib.util.module_from_spec(spec)
spec.loader.exec_module(engine)


def ten_god(day_stem, other):
    if day_stem == other:
        return '比肩'
    return engine.shishen_of(engine.GAN.index(day_stem), engine.GAN.index(other))


def pillar(stem, branch, day_stem, is_day=False):
    if not stem or not branch:
        return None
    hidden = [item[0] for item in engine.CANGGAN[branch]]
    return {'stem': stem, 'branch': branch, 'tenGod': '日主' if is_day else ten_god(day_stem, stem),
            'hiddenStems': hidden, 'hiddenStemTenGods': [ten_god(day_stem, h) for h in hidden]}
