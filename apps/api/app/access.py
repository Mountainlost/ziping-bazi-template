"""Independent master passes, report binding and atomic Beijing-day question limits."""
import hashlib
import json
import secrets
import sqlite3
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

BJ=timezone(timedelta(hours=8))


class PassError(ValueError):
    pass


class QuotaError(ValueError):
    pass


def digest(value):
    return hashlib.sha256(value.encode()).hexdigest()


def pass_digest(code):
    return digest(''.join(code.upper().split()).replace('-',''))


class PassStore:
    def __init__(self,path,daily_limit=50,site_limit=50):
        self.path=Path(path)
        self.path.parent.mkdir(parents=True,exist_ok=True)
        self.daily_limit=daily_limit
        self.site_limit=site_limit
        with self.connect() as db:
            db.executescript('''
            CREATE TABLE IF NOT EXISTS passes(digest TEXT PRIMARY KEY,kind TEXT NOT NULL,chart_id TEXT,created REAL NOT NULL);
            CREATE TABLE IF NOT EXISTS sessions(digest TEXT PRIMARY KEY,pass_digest TEXT NOT NULL,expires REAL NOT NULL);
            CREATE TABLE IF NOT EXISTS session_charts(session_digest TEXT PRIMARY KEY,chart_id TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS daily(pass_digest TEXT NOT NULL,day TEXT NOT NULL,count INTEGER NOT NULL,PRIMARY KEY(pass_digest,day));
            CREATE TABLE IF NOT EXISTS site_daily(day TEXT PRIMARY KEY,count INTEGER NOT NULL);
            CREATE TABLE IF NOT EXISTS questions(id INTEGER PRIMARY KEY AUTOINCREMENT,pass_digest TEXT NOT NULL,question TEXT NOT NULL,response TEXT NOT NULL,created REAL NOT NULL);
            CREATE INDEX IF NOT EXISTS question_owner ON questions(pass_digest,id);
            ''')

    def connect(self):
        return sqlite3.connect(self.path,timeout=30)

    def issue(self,kind='master'):
        if kind not in ('master','universal'):
            raise ValueError('Unknown pass kind')
        alphabet='ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
        code='ZP-M-'+'-'.join(''.join(secrets.choice(alphabet) for _ in range(4)) for _ in range(6))
        with self.connect() as db:
            db.execute('INSERT INTO passes VALUES(?,?,NULL,?)',(pass_digest(code),kind,time.time()))
        return code

    def lookup(self,code):
        with self.connect() as db:
            row=db.execute('SELECT chart_id,kind FROM passes WHERE digest=?',(pass_digest(code),)).fetchone()
        if not row:
            raise PassError('签子未通过验证，请核对完整签子。')
        if row[1]=='universal':
            raise PassError('万能签用于启用大师解盘。请先打开要解读的命盘，再输入万能签。')
        if not row[0]:
            raise PassError('这枚签子还未绑定命盘。请先生成报告，再在子平大师中启用。')
        return row[0]

    def redeem(self,code,chart_id):
        identity=pass_digest(code)
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            row=db.execute('SELECT chart_id,kind FROM passes WHERE digest=?',(identity,)).fetchone()
            if not row or row[1] not in ('master','universal'):
                raise PassError('大师签未通过验证，请核对完整签子。')
            if row[1]=='master':
                if row[0] and row[0]!=chart_id:
                    raise PassError('这枚签子已绑定另一份报告，可凭原签查看原报告。')
                db.execute('UPDATE passes SET chart_id=? WHERE digest=? AND chart_id IS NULL',(chart_id,identity))
            token=secrets.token_urlsafe(32)
            session=digest(token)
            db.execute('INSERT INTO sessions VALUES(?,?,?)',(session,identity,time.time()+30*86400))
            if row[1]=='universal':
                db.execute('INSERT INTO session_charts VALUES(?,?)',(session,chart_id))
        return token

    def authorize(self,token,chart_id):
        with self.connect() as db:
            row=db.execute('''
                SELECT p.digest, CASE WHEN p.kind='universal' THEN c.chart_id ELSE p.chart_id END
                FROM sessions s JOIN passes p ON p.digest=s.pass_digest
                LEFT JOIN session_charts c ON c.session_digest=s.digest
                WHERE s.digest=? AND s.expires>? AND p.kind IN ('master','universal')
            ''',(digest(token or ''),time.time())).fetchone()
        if not row or row[1]!=chart_id:
            raise PassError('请先使用本命盘的大师签启用深度问答。')
        return row[0]

    def remaining(self,identity,day=None):
        day=day or datetime.now(BJ).date().isoformat()
        with self.connect() as db:
            own=db.execute('SELECT count FROM daily WHERE pass_digest=? AND day=?',(identity,day)).fetchone()
            total=db.execute('SELECT count FROM site_daily WHERE day=?',(day,)).fetchone()
        return max(0,min(self.daily_limit-(own[0] if own else 0),self.site_limit-(total[0] if total else 0)))

    def reserve(self,identity,day=None):
        day=day or datetime.now(BJ).date().isoformat()
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            own=db.execute('SELECT count FROM daily WHERE pass_digest=? AND day=?',(identity,day)).fetchone()
            total=db.execute('SELECT count FROM site_daily WHERE day=?',(day,)).fetchone()
            own_count=own[0] if own else 0
            total_count=total[0] if total else 0
            if own_count>=self.daily_limit or total_count>=self.site_limit:
                raise QuotaError('今日问答次数已用完，北京时间零点后可继续。已生成的报告仍可查看。')
            db.execute('INSERT INTO daily VALUES(?,?,1) ON CONFLICT(pass_digest,day) DO UPDATE SET count=count+1',(identity,day))
            db.execute('INSERT INTO site_daily VALUES(?,1) ON CONFLICT(day) DO UPDATE SET count=count+1',(day,))
        return min(self.daily_limit-own_count-1,self.site_limit-total_count-1)

    @staticmethod
    def _history_owner(db,identity,chart_id):
        universal=db.execute("SELECT 1 FROM passes WHERE digest=? AND kind='universal'",(identity,)).fetchone()
        if universal:
            if not chart_id:
                raise ValueError('Universal pass history requires a chart')
            return digest(f'universal-history:{identity}:{chart_id}')
        return identity

    def save_answer(self,identity,question,response,*,chart_id=None):
        with self.connect() as db:
            owner=self._history_owner(db,identity,chart_id)
            db.execute('INSERT INTO questions(pass_digest,question,response,created) VALUES(?,?,?,?)',(owner,question,json.dumps(response,ensure_ascii=False),time.time()))

    def history(self,identity,limit=20,*,chart_id=None):
        with self.connect() as db:
            owner=self._history_owner(db,identity,chart_id)
            rows=db.execute('SELECT id,question,response FROM questions WHERE pass_digest=? ORDER BY id DESC LIMIT ?',(owner,min(limit,50))).fetchall()
        return [{'id':row[0],'question':row[1],**json.loads(row[2])} for row in reversed(rows)]
