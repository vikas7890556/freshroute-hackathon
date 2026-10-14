"""Bounded deterministic candidate search, not an optimality certificate."""
from datetime import timedelta
try:
    from .models import Allocation, Result
    from .feasibility import reasons, times, markdown
    from .metrics import evaluate
except ImportError:  # Vercel's service root exposes backend modules top-level.
    from models import Allocation, Result
    from feasibility import reasons, times, markdown
    from metrics import evaluate

def edges(s):
    feasible=[]; rejected=[]
    for bi,b in enumerate(s.batches):
        for ri,r in enumerate(s.routes):
            d=next(d for d in s.destinations if d.id==r.destination)
            why=reasons(s,b,r,d)
            if why:
                rejected.append(dict(batch=b.id,produce=b.produce,route=r.id,destination=d.name,reasons=why)); continue
            q=next(q for q in d.demands if q.produce==b.produce)
            sale,pct,risk=markdown(s,b,r,q)
            expires_in_horizon=b.expiry<=s.planningTime+timedelta(hours=s.horizonHours)
            for tier,price,discount,limit in [('base',q.price,0,q.quantity)]:
                margin=price*(1-(s.platformRate or 0)-(s.taxRate or 0))-b.acquisition-r.perKg-r.handlingCost-(s.packagingPerKg or 0)
                if expires_in_horizon: margin+=b.acquisition+s.disposalPerKg
                feasible.append(dict(b=b,r=r,d=d,q=q,bi=bi,ri=ri,price=price,pct=discount,margin=margin,tier=tier,limit=limit))
            # Markdown volume is a separate, conditional demand tier. It can only
            # use explicitly provided headroom above base demand and stock that
            # would expire within this evaluation horizon.
            if s.applyDiscounts and risk and expires_in_horizon and q.maximum>q.quantity and pct>0:
                price_margin=sale*(1-(s.platformRate or 0)-(s.taxRate or 0))-b.acquisition-r.perKg-r.handlingCost-(s.packagingPerKg or 0)+b.acquisition+s.disposalPerKg
                feasible.append(dict(b=b,r=r,d=d,q=q,bi=bi,ri=ri,price=sale,pct=pct,margin=price_margin,tier='markdown',limit=q.maximum-q.quantity))
    return feasible,rejected

def allocate(s, rows, strategy):
    supply={b.id:b.quantity for b in s.batches}; capacity={r.id:r.capacity for r in s.routes}
    demand={(d.id,q.produce):q.quantity for d in s.destinations for q in d.demands}
    extra={(d.id,q.produce):max(0,q.maximum-q.quantity) for d in s.destinations for q in d.demands}; out=[]
    # Satisfy base-price demand first. Markdown rows can only consume remaining
    # batch/vehicle capacity and the separately declared incremental headroom.
    for tier in ('base','markdown'):
      for e in rows:
        if e['tier']!=tier: continue
        b,r,d,q=(e[k] for k in ['b','r','d','q']); key=(d.id,q.produce)
        room=demand[key] if tier=='base' else extra[key]
        qty=min(supply[b.id],capacity[r.id],room,e['limit'])
        if qty<=1e-6: continue
        departure,arrival,usable,slack=times(s,b,r)
        window=(d.closes-usable).total_seconds()/3600
        note=' Conditional markdown sale uses demand headroom above the base estimate; uplift is assumed, not forecast.' if tier=='markdown' else ' Quantity respects base demand, stock and route capacity.'
        latest_departure=min(b.expiry,d.closes,s.planningTime+timedelta(hours=s.horizonHours))-timedelta(hours=r.travel+r.handling)
        out.append(Allocation(batch=b.id,produce=b.produce,destination=d.id,destinationName=d.name,route=r.id,quantity=qty,price=e['price'],originalPrice=q.price,discount=e['pct'],departure=departure,arrival=arrival,usable=usable,latestDeparture=latest_departure,expiry=b.expiry,slackHours=slack,urgency=q.priority,reason=f'{slack:.1f}h shelf-life slack; {window:.1f}h receiving-window slack; demand priority {q.priority}/5.{note}'))
        supply[b.id]-=qty; capacity[r.id]-=qty
        if tier=='base': demand[key]-=qty
        else: extra[key]-=qty
    out.sort(key=lambda a:(min(a.slackHours,(next(d for d in s.destinations if d.id==a.destination).closes-a.usable).total_seconds()/3600),-a.urgency,a.departure,a.batch,a.route))
    return evaluate(s,out,strategy)

def rank_key(p, objective):
    m=p.metrics
    return ((m.spoilage,-m.fulfillment,-m.net) if objective=='spoilage' else (-m.net,m.spoilage,-m.fulfillment))+(m.fixedTransport+m.variableTransport,)

def select(candidates, objective, reference=None):
    valid=[p for p in candidates if not p.violations]
    base=reference or max(valid,key=lambda p:p.metrics.net)
    best_net=base.metrics.net
    floor=best_net-max(100,abs(best_net)*.1)
    if objective=='contribution': pool=valid; guardrail='No extra guardrail; maximize net contribution.'
    elif objective=='balanced':
        # Baseline is always a candidate, so this guardrail remains achievable.
        pool=[p for p in valid if p.metrics.fulfillment+1e-6>=base.metrics.fulfillment and p.metrics.spoilage<=base.metrics.spoilage+1e-6]
        guardrail=f'Fulfillment ≥ {base.metrics.fulfillment:.1f}% and spoilage ≤ {base.metrics.spoilage:.1f} kg (FIFO guardrails).'
    else:
        pool=[p for p in valid if p.metrics.net>=floor-1e-6]
        guardrail=f'Contribution ≥ ₹{floor:.2f}: best checked contribution less max(₹100, 10% of its absolute value).'
    return min(pool,key=lambda p:rank_key(p,objective)),guardrail

def solve(s, objective='contribution'):
    try:
        from .baseline import fifo, earliest_expiry
    except ImportError:  # Vercel imports this module outside the backend package.
        from baseline import fifo, earliest_expiry
    rows,rejected=edges(s)
    baseline=fifo(s,rows)
    expiry_baseline=earliest_expiry(s,rows)
    candidates=[baseline,expiry_baseline,evaluate(s,[],'Hold all stock')]
    for mask in range(1,1<<len(s.routes)):
        subset=[e for e in rows if mask & (1<<e['ri'])]
        strategies={
            'Margin first':lambda e:(-e['margin'],e['b'].expiry,-e['q'].priority,e['bi'],e['ri']),
            'Expiry first':lambda e:(e['b'].expiry,-e['margin'],-e['q'].priority,e['bi'],e['ri']),
            'Urgency first':lambda e:(-e['q'].priority,times(s,e['b'],e['r'])[3],-e['margin'],e['bi'],e['ri']),
            'Window first':lambda e:(e['d'].closes,e['b'].expiry,-e['margin'],e['bi'],e['ri'])}
        for name,key in strategies.items():
            candidates.append(allocate(s,sorted(subset,key=key),name))
            candidates.append(allocate(s,sorted([e for e in subset if e['margin']>0],key=key),name+' / positive margin'))
    reference=baseline if objective=='balanced' else None
    proposed,guardrail=select(candidates,objective,reference)
    markdown_plan=proposed if s.applyDiscounts else None
    if not s.applyDiscounts:
        markdown_scenario=s.model_copy(deep=True); markdown_scenario.applyDiscounts=True
        # Run a separate conditional alternative. It never changes the base plan.
        alt_rows,_=edges(markdown_scenario)
        alt_baseline=fifo(markdown_scenario,alt_rows)
        alt_expiry=earliest_expiry(markdown_scenario,alt_rows)
        alt_candidates=[alt_baseline,alt_expiry,evaluate(markdown_scenario,[],'Hold all stock')]
        for mask in range(1,1<<len(markdown_scenario.routes)):
            subset=[e for e in alt_rows if mask & (1<<e['ri'])]
            for name,key in strategies.items():
                alt_candidates.append(allocate(markdown_scenario,sorted(subset,key=key),'Conditional '+name))
                alt_candidates.append(allocate(markdown_scenario,sorted([e for e in subset if e['margin']>0],key=key),'Conditional '+name+' / positive margin'))
        markdown_plan=select(alt_candidates,objective,alt_baseline if objective=='balanced' else None)[0]
    discount_allocations=[a for a in markdown_plan.allocations if a.discount>0]
    discounts=[]
    for route_id in sorted({a.route for a in discount_allocations}):
        route=next(r for r in s.routes if r.id==route_id)
        route_rows=[a for a in discount_allocations if a.route==route_id]
        has_base=any(a.route==route_id and a.discount==0 for a in markdown_plan.allocations)
        margin=sum(a.price*(1-(s.platformRate or 0)-(s.taxRate or 0))-route.perKg-route.handlingCost-(s.packagingPerKg or 0)+s.disposalPerKg for a in route_rows)
        fixed=max(0,route.fixedCost) if not has_base else 0
        break_even=None if margin<=0 else fixed/(margin/sum(a.quantity for a in route_rows))
        for a in route_rows:
            discounts.append(dict(batch=a.batch,produce=a.produce,destination=a.destinationName,quantity=a.quantity,originalPrice=a.originalPrice,salePrice=a.price,percentage=a.discount*100,applied=s.applyDiscounts,breakEvenQuantity=break_even,routeQuantity=sum(x.quantity for x in route_rows),reason=f'Conditional rule-based markdown on surplus above base demand. Only stock expiring within the {s.horizonHours:g}h evaluation horizon is eligible. Extra demand up to destination maximum is assumed, not forecast. Route break-even quantity covers the incremental fixed trip cost only; variable costs and avoided disposal are included in the contribution check.'))
    binding=[]
    for r in s.routes:
        used=sum(a.quantity for a in proposed.allocations if a.route==r.id)
        if used>=r.capacity-1e-6: binding.append(f'{r.id}: route capacity fully used ({r.capacity:g} kg)')
    for a in proposed.allocations:
        if a.slackHours<1e-6: binding.append(f'{a.batch} → {a.destinationName}: handling completes at expiry')
    if proposed.metrics.unmet>0: binding.append(f'{proposed.metrics.unmet:.1f} kg demand remains unmet under the checked plans')
    return Result(proposed=proposed,baseline=baseline,earliestExpiryBaseline=expiry_baseline,rejected=rejected,discounts=discounts,objective=objective,candidatesChecked=len(candidates),guardrail=guardrail,binding=binding,explanation=f'Best feasible plan found among {len(candidates)} deterministic candidates. {proposed.strategy}. Every candidate uses the same horizon and cost accounting; no global optimality claim.')
