"""Run from the project root; no network or external dataset."""
import sys,json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root))
from backend.models import Scenario
from backend.scenarios import compare
s=Scenario.model_validate_json((root/'backend/data/sample.json').read_text())
reports={objective:compare(s,objective) for objective in ['contribution','balanced','spoilage']}
def encode(x):
    if hasattr(x,'model_dump'):return x.model_dump(mode='json')
    raise TypeError(type(x).__name__)
(root/'output').mkdir(exist_ok=True)
(root/'output/evaluation-v2.json').write_text(json.dumps(reports,default=encode,indent=2))
for c in reports['contribution']['cases']:
    p=c['result'].proposed.metrics;b=c['result'].baseline.metrics
    print(f"{c['name']:22} net={p.net:9.2f} FIFO={b.net:9.2f} spoilage={p.spoilage:6.1f} fulfillment={p.fulfillment:5.1f}%")
