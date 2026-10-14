import json, os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
if __package__:
    from .models import PlanRequest, Result, Scenario
    from .planner import solve
    from .scenarios import compare, decisions
else:  # Vercel loads backend/main.py as the top-level module ``main``.
    from models import PlanRequest, Result, Scenario
    from planner import solve
    from scenarios import compare, decisions

app=FastAPI(title='FreshRoute',version='2.0.0')
app.add_middleware(CORSMiddleware,allow_origins=os.getenv('FRESHROUTE_ORIGINS','http://127.0.0.1:5173,http://localhost:5173').split(','),allow_methods=['GET','POST'],allow_headers=['Content-Type'])
@app.get('/api/health')
def health(): return {'status':'ok','engine':'bounded deterministic planner','version':'2.0.0'}
@app.get('/api/sample',response_model=Scenario)
def sample(): return json.loads((Path(__file__).parent/'data/sample.json').read_text())
@app.post('/api/plan',response_model=Result)
def plan(request:PlanRequest): return solve(request.scenario,request.objective)
@app.post('/api/compare')
def comparison(request:PlanRequest): return compare(request.scenario,request.objective)
@app.post('/api/decisions')
def decision_options(request:PlanRequest): return decisions(request.scenario,request.objective)
dist=Path(__file__).resolve().parent.parent/'dist'
if dist.exists(): app.mount('/',StaticFiles(directory=dist,html=True),name='frontend')
