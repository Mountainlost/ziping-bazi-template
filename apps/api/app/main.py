import os
from pathlib import Path
from datetime import datetime
from fastapi import FastAPI, HTTPException, Request
from threading import BoundedSemaphore
from fastapi.responses import JSONResponse, Response
from pydantic import ValidationError
from .models import BirthInput, AnalyzeInput, QuestionInput, PassInput
from .storage import ChartStore, default_db_path, canonical
from .services.bazi.chart import generate_candidates
from .services.bazi.solar_time import BJ
from .services.rules.engine import analyze
from .services.report.renderer import render
from .services.report.chart_image import render_chart_svg
from .services.ai.provider import DeferredProvider, NotConfigured
from .services.ai.question_answering import answer_question
from .locations import location_index
from .access import PassStore, PassError, QuotaError
from .services.ai.magpie import configured_provider, MagpieProvider


def create_app(db_path=None):
    app = FastAPI(title='子平 · 确定性命盘', version='1.0.0')
    app.state.store = ChartStore(db_path or default_db_path())
    app.state.ai_provider = configured_provider()
    app.state.passes = PassStore(app.state.store.path.with_suffix('.access.sqlite'))
    app.state.ai_gate = BoundedSemaphore(1)

    @app.exception_handler(KeyError)
    async def missing(request, exc):
        return JSONResponse({'detail':'命盘不存在'},status_code=404)

    @app.exception_handler(RuntimeError)
    async def conflict(request, exc):
        return JSONResponse({'detail':str(exc)},status_code=409)

    @app.exception_handler(PassError)
    async def invalid_pass(request,exc):
        return JSONResponse({'detail':str(exc)},status_code=403)

    @app.exception_handler(QuotaError)
    async def no_quota(request,exc):
        return JSONResponse({'detail':str(exc)},status_code=429)

    @app.get('/api/v1/status')
    def status():
        enabled=isinstance(app.state.ai_provider,MagpieProvider)
        return {'ok':True,'aiConfigured':enabled,'aiIntegration':'magpie' if enabled else 'deferred-magpie',
                'dailyQuestionLimit':50,'siteDailyQuestionLimit':50,
                'referenceYear':datetime.now(BJ).year,
                'message':'大师解盘已配置，需大师签启用。' if enabled else '大师解盘暂未启用，仍可排盘并阅读报告。'}

    @app.post('/api/v1/access/report')
    def report_by_pass(data:PassInput):
        chart_id=app.state.passes.lookup(data.code)
        return app.state.store.get(chart_id,require_locked=True)

    @app.get('/api/v1/charts/{chart_id}/access')
    def access_status(chart_id:str,request:Request):
        app.state.store.get(chart_id,require_locked=True)
        try:
            identity=app.state.passes.authorize(request.cookies.get('ziping_master_session'),chart_id)
        except PassError:
            return {'authorized':False,'remaining':0,'history':[]}
        return {'authorized':True,'remaining':app.state.passes.remaining(identity),'history':app.state.passes.history(identity,chart_id=chart_id)}

    @app.post('/api/v1/charts/{chart_id}/access')
    def activate_pass(chart_id:str,data:PassInput,response:Response):
        app.state.store.get(chart_id,require_locked=True)
        token=app.state.passes.redeem(data.code,chart_id)
        secure=os.getenv('BAZI_PUBLIC_ORIGIN','').startswith('https://')
        response.set_cookie('ziping_master_session',token,httponly=True,secure=secure,samesite='strict',max_age=30*86400,path='/api/v1')
        identity=app.state.passes.authorize(token,chart_id)
        return {'authorized':True,'remaining':app.state.passes.remaining(identity),'history':app.state.passes.history(identity,chart_id=chart_id)}

    @app.get('/api/v1/locations')
    def locations():
        return location_index()

    @app.post('/api/v1/chart')
    def chart(data: BirthInput):
        try:
            charts = generate_candidates(data)
        except (ValueError,OverflowError) as exc:
            raise HTTPException(422,str(exc)) from exc
        for item in charts:
            app.state.store.add(item)
        return {'possibleCharts':charts, 'requiresConfirmation':True, 'sampling':'一分钟分辨率',
                'message':'请比较候选命盘并核对时间，确认后生成完整规则报告。'}

    @app.post('/api/v1/analyze')
    def analysis(data: AnalyzeInput):
        draft = app.state.store.get(data.chartId)
        if draft['locked']:
            return draft
        chart = analyze(draft)
        chart['report'] = render(chart)
        chart['locked'] = True
        return app.state.store.freeze(chart)

    @app.get('/api/v1/charts/{chart_id}')
    def get_chart(chart_id: str):
        return app.state.store.get(chart_id)

    @app.get('/api/v1/charts/{chart_id}/analysis')
    def get_analysis(chart_id: str):
        return app.state.store.get(chart_id,require_locked=True)['report']

    @app.get('/api/v1/charts/{chart_id}/image.svg')
    def get_image(chart_id: str):
        locked=app.state.store.get(chart_id,require_locked=True)
        return Response(render_chart_svg(locked),media_type='image/svg+xml',
            headers={'Cache-Control':'private, no-store','X-Content-Type-Options':'nosniff',
                     'Content-Security-Policy':"default-src 'none'; style-src 'unsafe-inline'"})

    @app.post('/api/v1/charts/{chart_id}/revalidate')
    def revalidate(chart_id: str):
        existing = app.state.store.get(chart_id)
        return chart(BirthInput.model_validate(existing['input']))

    @app.post('/api/v1/charts/{chart_id}/ask')
    def ask(chart_id: str, data: QuestionInput, request:Request):
        snapshot = app.state.store.snapshot(chart_id)
        identity=None
        history=[]
        protected=getattr(app.state.ai_provider,'requires_access',False)
        if protected:
            identity=app.state.passes.authorize(request.cookies.get('ziping_master_session'),chart_id)
            history=app.state.passes.history(identity,limit=3,chart_id=chart_id)
        if not app.state.ai_gate.acquire(blocking=False):
            raise HTTPException(409,'上一条解读仍在进行，请等它完成后再继续。')
        try:
            remaining=app.state.passes.reserve(identity) if identity else None
            answer = answer_question(snapshot,data.question,app.state.ai_provider,history=history,mode=data.mode)
        except NotConfigured as exc:
            raise HTTPException(503,str(exc)) from exc
        except QuotaError:
            raise
        except Exception as exc:
            # Never reflect provider errors that may contain private request headers or payloads.
            raise HTTPException(502,'这次解读未能完成，请稍后重试。已保存的命盘和报告保持不变。') from exc
        finally:
            app.state.ai_gate.release()
        if snapshot.payload != app.state.store.snapshot(chart_id).payload:
            raise HTTPException(409,'LockedChart一致性检查失败')
        if identity:
            answer['remaining']=remaining
            app.state.passes.save_answer(identity,data.question,answer,chart_id=chart_id)
        return answer

    return app


app = create_app()
