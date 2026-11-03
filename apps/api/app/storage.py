import hashlib
import json
import os
import sqlite3
from pathlib import Path
from .models import LockedChart


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)


class ChartStore:
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.executescript('''
                CREATE TABLE IF NOT EXISTS charts (
                    id TEXT PRIMARY KEY, draft TEXT NOT NULL, locked TEXT, digest TEXT);
                CREATE TRIGGER IF NOT EXISTS no_locked_update BEFORE UPDATE ON charts
                WHEN OLD.locked IS NOT NULL BEGIN SELECT RAISE(ABORT, 'LockedChart is immutable'); END;
                CREATE TRIGGER IF NOT EXISTS no_locked_delete BEFORE DELETE ON charts
                WHEN OLD.locked IS NOT NULL BEGIN SELECT RAISE(ABORT, 'LockedChart is immutable'); END;
            ''')

    def connect(self):
        return sqlite3.connect(self.path, timeout=20)

    def add(self, chart):
        with self.connect() as db:
            db.execute('INSERT INTO charts(id, draft) VALUES (?,?)', (chart['id'], canonical(chart)))

    def get(self, chart_id, require_locked=False):
        with self.connect() as db:
            row = db.execute('SELECT draft,locked,digest FROM charts WHERE id=?', (chart_id,)).fetchone()
        if not row:
            raise KeyError(chart_id)
        if require_locked and not row[1]:
            raise RuntimeError('请先确认排盘并生成完整报告')
        if row[1] and hashlib.sha256(row[1].encode()).hexdigest() != row[2]:
            raise RuntimeError('命盘摘要校验失败')
        return json.loads(row[1] or row[0])

    def freeze(self, chart):
        payload = canonical(chart)
        with self.connect() as db:
            db.execute('UPDATE charts SET locked=?,digest=? WHERE id=? AND locked IS NULL',
                       (payload, hashlib.sha256(payload.encode()).hexdigest(), chart['id']))
        return self.snapshot(chart['id']).read()

    def snapshot(self, chart_id):
        return LockedChart(id=chart_id, payload=canonical(self.get(chart_id, require_locked=True)))


def default_db_path():
    return Path(os.getenv('BAZI_DB_PATH') or
                Path(os.getenv('LOCALAPPDATA', str(Path.home() / '.local/share'))) / 'CodexToolData/bazi/charts.sqlite')
