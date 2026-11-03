"""Read the packaged, attributed WGS84 location snapshot without network access."""
import base64
import gzip
import json
from functools import lru_cache
from pathlib import Path


@lru_cache(maxsize=1)
def location_index():
    data = json.loads((Path(__file__).parent / 'data' / 'locations.json').read_text(encoding='utf-8'))
    rows = json.loads(gzip.decompress(base64.b64decode(data['compressedLocations'])))
    return {key: data[key] for key in ('provider', 'datum', 'snapshotDate', 'sources', 'note')} | {'locations': rows}
