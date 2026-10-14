from datetime import timedelta
from .models import Scenario, Batch, Route, Destination

EPS = 1e-6
def times(s: Scenario, b: Batch, r: Route):
    departure = s.planningTime + timedelta(hours=r.delay)
    arrival = departure + timedelta(hours=r.travel)
    usable = arrival + timedelta(hours=r.handling)
    return departure, arrival, usable, (b.expiry - usable).total_seconds()/3600

def reasons(s: Scenario, b: Batch, r: Route, d: Destination):
    _, arrival, usable, slack = times(s,b,r)
    errors = []
    if not any(q.produce == b.produce and q.quantity > 0 for q in d.demands): errors.append('No positive demand for this produce')
    if r.eligible and b.produce not in r.eligible: errors.append('Route is not eligible for this produce')
    if r.capacity <= 0: errors.append('Vehicle capacity is zero')
    if b.quantity <= 0: errors.append('Batch has no available stock')
    if arrival < d.opens: errors.append('Arrival is before the receiving window opens; increase departure delay')
    if arrival > d.closes: errors.append('Arrival is after the receiving window closes')
    elif usable > d.closes: errors.append('Handling finishes after the receiving window closes')
    if slack < -EPS: errors.append(f'Arrival plus handling is {-slack:.1f} hours after the batch expires')
    if usable > s.planningTime + timedelta(hours=s.horizonHours): errors.append('Usable arrival is beyond the evaluation horizon')
    return errors

def markdown(s, b, r, q):
    slack = times(s,b,r)[3]
    life = (b.expiry-s.planningTime).total_seconds()/3600
    at_risk = 0 <= life <= s.riskHours or 0 <= slack <= 3
    pct = min(s.maxDiscount, .15 if slack <= 3 else .10) if at_risk else 0
    price = max(q.minimumPrice, q.price*(1-pct))
    return price, (1-price/q.price if q.price else 0), at_risk

def audit(s, allocations):
    errors=[]; stock={}; cap={}; demand={}; extra_demand={}
    for a in allocations:
        b=next(x for x in s.batches if x.id==a.batch)
        r=next(x for x in s.routes if x.id==a.route)
        d=next(x for x in s.destinations if x.id==a.destination)
        q=next(x for x in d.demands if x.produce==a.produce)
        key=(d.id,q.produce)
        errors.extend(reasons(s,b,r,d))
        if r.destination != d.id or b.produce != a.produce: errors.append('Route or produce mismatch')
        expected_price,expected_pct,risk=markdown(s,b,r,q)
        expected=expected_price if a.discount>0 else q.price
        if a.quantity < 0 or abs(a.price-expected)>EPS or (a.discount>0 and abs(a.discount-expected_pct)>EPS): errors.append('Invalid quantity or sale price')
        if a.discount>0:
            horizon=s.planningTime+timedelta(hours=s.horizonHours)
            if not s.applyDiscounts or not risk or b.expiry>horizon or q.maximum<=q.quantity: errors.append('Markdown allocation is not eligible surplus demand')
            extra_demand[key]=extra_demand.get(key,0)+a.quantity
        else:
            demand[key]=demand.get(key,0)+a.quantity
        stock[b.id]=stock.get(b.id,0)+a.quantity
        cap[r.id]=cap.get(r.id,0)+a.quantity
    for b in s.batches:
        if stock.get(b.id,0)>b.quantity+EPS: errors.append(f'{b.id}: stock exceeded')
    for r in s.routes:
        if cap.get(r.id,0)>r.capacity+EPS: errors.append(f'{r.id}: capacity exceeded')
    for d in s.destinations:
        for q in d.demands:
            key=(d.id,q.produce)
            if demand.get(key,0)>q.quantity+EPS: errors.append(f'{d.id}: base demand exceeded')
            if extra_demand.get(key,0)>max(0,q.maximum-q.quantity)+EPS: errors.append(f'{d.id}: markdown demand ceiling exceeded')
    return errors
