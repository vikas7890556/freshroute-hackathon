import unittest, json
from pathlib import Path
from datetime import timedelta
from pydantic import ValidationError
from fastapi.testclient import TestClient
from backend.models import Scenario
from backend.planner import solve
from backend.feasibility import audit
from backend.scenarios import compare, decisions
from backend.main import app

def sample(): return Scenario.model_validate_json((Path(__file__).parents[1]/'data/sample.json').read_text())
def tiny():
    s=sample();s.batches=s.batches[:1];s.destinations=s.destinations[:1];s.routes=s.routes[:1]
    b=s.batches[0];b.quantity=10;b.acquisition=3;b.expiry=s.planningTime+timedelta(hours=8)
    d=s.destinations[0];d.demands=d.demands[:1];q=d.demands[0];q.quantity=q.maximum=10;q.price=10;q.minimumPrice=0
    r=s.routes[0];r.capacity=8;r.fixedCost=4;r.perKg=1;r.handlingCost=1
    s.packagingPerKg=None;s.disposalPerKg=2;s.maxDiscount=0
    return s

class PlanningTests(unittest.TestCase):
    def test_hand_calculated_finance(self):
        m=solve(tiny()).proposed.metrics
        self.assertEqual((m.allocated,m.revenue,m.acquisition,m.fixedTransport,m.variableTransport,m.handling,m.spoilage,m.disposal,m.net),(8,80,30,4,8,8,2,4,26))
        self.assertEqual(m.spoilageValue,6)
        self.assertEqual(m.stock,m.allocated+m.spoilage+m.remaining)
    def test_expiry_window_eligibility_and_horizon(self):
        for change in ['expiry','window','eligible','horizon','early']:
            s=tiny()
            if change=='expiry':s.routes[0].handling=7
            if change=='window':s.destinations[0].closes=s.planningTime+timedelta(hours=1)
            if change=='eligible':s.routes[0].eligible=['Mango']
            if change=='horizon':s.horizonHours=1
            if change=='early':s.destinations[0].opens=s.planningTime+timedelta(hours=4)
            r=solve(s);self.assertEqual(r.proposed.metrics.allocated,0,change);self.assertTrue(r.rejected)
    def test_horizon_boundary_and_retained_stock(self):
        s=tiny();s.batches[0].expiry=s.planningTime+timedelta(hours=12)
        self.assertEqual(solve(s).proposed.metrics.spoilage,2)
        s.batches[0].expiry+=timedelta(seconds=1)
        self.assertEqual(solve(s).proposed.metrics.remaining,2)
    def test_fifo_stable_input_order(self):
        s=tiny();b=s.batches[0].model_copy(deep=True);b.id='A-first-lexically';b.expiry+=timedelta(hours=1);s.batches.append(b)
        self.assertEqual(solve(s).baseline.allocations[0].batch,s.batches[0].id)
    def test_discounts_bounded_no_uplift_no_double_count(self):
        s=tiny();s.applyDiscounts=True;s.maxDiscount=.2;s.destinations[0].demands[0].quantity=4;s.destinations[0].demands[0].maximum=8;s.destinations[0].demands[0].minimumPrice=9.5
        r=solve(s);m=r.proposed.metrics
        self.assertEqual(m.demand,4);self.assertEqual(m.markdownAllocated,4)
        self.assertEqual(m.revenue,78);self.assertEqual(m.spoilage,2)
        self.assertTrue(all(a.quantity <= 4 for a in r.proposed.allocations if a.discount>0))
        self.assertEqual(r.proposed.violations,[])
    def test_markdown_requires_incremental_demand_headroom(self):
        s=tiny();s.applyDiscounts=True;s.maxDiscount=.2
        r=solve(s)
        self.assertEqual(r.proposed.metrics.markdownAllocated,0)
        self.assertEqual(r.discounts,[])

    def test_unknown_cost_and_units_and_dates_rejected(self):
        for mutate in [lambda x:x.update(unknownCost=1),lambda x:x['batches'][0].update(unit='lb'),lambda x:x['batches'][0].update(received='invalid'),lambda x:x['batches'][0].update(quantity=-1),lambda x:x['destinations'][0]['demands'][0].pop('price'),lambda x:x['routes'][0].update(destination='missing'),lambda x:x['batches'][0].update(received='2026-10-14T06:00:00')]:
            raw=tiny().model_dump(mode='json');mutate(raw)
            with self.assertRaises(ValidationError):Scenario.model_validate(raw)
    def test_all_cost_components_once(self):
        s=tiny();s.packagingPerKg=1;s.storagePerKg=2;s.platformRate=.1;s.taxRate=.05
        m=solve(s).proposed.metrics
        self.assertEqual((m.packaging,m.storage,m.platform,m.tax,m.net),(8,20,8,4,-14))
    def test_trip_cost_can_prevent_dispatch(self):
        s=tiny();s.routes[0].fixedCost=500
        self.assertEqual(solve(s).proposed.metrics.allocated,0)
    def test_zero_demand_capacity_and_finite_metrics(self):
        s=tiny();s.destinations[0].demands[0].quantity=0;s.routes[0].capacity=0
        r=solve(s);self.assertEqual(r.proposed.metrics.fulfillment,0);self.assertEqual(r.proposed.violations,[])
    def test_all_scenarios_all_objectives_audited(self):
        for objective in ['contribution','balanced','spoilage']:
            report=compare(sample(),objective)
            self.assertNotIn('winner',report)
            self.assertIn('stress tests',report['explanation'])
            for c in report['cases']:
                r=c['result'];self.assertEqual(audit(c['scenario'],r.proposed.allocations),[])
                self.assertEqual(r.baseline.violations,[])
                if objective=='contribution':self.assertGreaterEqual(r.proposed.metrics.net+1e-6,r.baseline.metrics.net)
                if objective=='balanced':
                    self.assertGreaterEqual(r.proposed.metrics.fulfillment+1e-6,r.baseline.metrics.fulfillment)
                    self.assertLessEqual(r.proposed.metrics.spoilage,r.baseline.metrics.spoilage+1e-6)
    def test_lower_demand_stress_scales_base_and_acceptable_maximum(self):
        s=sample(); lower=next(c for c in compare(s,'contribution')['cases'] if c['name']=='Lower demand')['scenario']
        for original_destination, lower_destination in zip(s.destinations,lower.destinations):
            for original, reduced in zip(original_destination.demands,lower_destination.demands):
                self.assertAlmostEqual(reduced.quantity,original.quantity*.7)
                self.assertAlmostEqual(reduced.maximum,original.maximum*.7)
                self.assertLessEqual(reduced.quantity,reduced.maximum)
    def test_decision_recommendation_explains_winner_and_fifo_tradeoff(self):
        report=decisions(sample(),'contribution')
        self.assertIn(report['winner'],report['explanation'])
        self.assertIn('provisional FIFO',report['explanation'])
        self.assertIn('net contribution',report['explanation'])
        self.assertIn('fulfillment',report['explanation'])
    def test_deterministic(self):self.assertEqual(solve(sample()),solve(sample()))
    def test_api_health_plan_invalid_request(self):
        client=TestClient(app)
        self.assertEqual(client.get('/api/health').json()['status'],'ok')
        data=client.get('/api/sample').json()
        self.assertEqual(client.post('/api/plan',json={'scenario':data}).status_code,200)
        data['batches'][0]['quantity']=-1
        response=client.post('/api/plan',json={'scenario':data})
        self.assertEqual(response.status_code,422)

if __name__=='__main__':unittest.main()
