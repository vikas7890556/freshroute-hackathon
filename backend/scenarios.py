from .planner import solve, rank_key
from .metrics import evaluate

def compare(s, objective):
    cases=[]
    def add(name,change,edit):
        x=s.model_copy(deep=True); x.name=name; edit(x)
        cases.append(dict(name=name,change=change,scenario=x,result=solve(x,objective)))
    def reduce_demand(x):
        for destination in x.destinations:
            for demand in destination.demands:
                demand.quantity *= .7
                demand.maximum *= .7
    add('Current conditions','Your current inputs',lambda x:None)
    add('Route delay','First route departs 3 hours later',lambda x:setattr(x.routes[0],'delay',min(168,x.routes[0].delay+3)))
    add('Reduced capacity','All route capacities reduced by 40%',lambda x:[setattr(r,'capacity',r.capacity*.6) for r in x.routes])
    add('Lower demand','Base demand and acceptable maximum both reduced by 30%; prices unchanged',reduce_demand)
    add('Lower price','All sale prices reduced by 10%, respecting minimum prices',lambda x:[setattr(q,'price',max(q.minimumPrice,q.price*.9)) for d in x.destinations for q in d.demands])
    add('Extra handling','All routes need 2 additional hours of handling',lambda x:[setattr(r,'handling',min(168,r.handling+2)) for r in x.routes])
    add('At-risk markdowns','Use eligible surplus above base demand; extra demand assumed, not forecast',lambda x:setattr(x,'applyDiscounts',True))
    # Conditions are illustrative, not controllable business actions. Keep that visible.
    return dict(cases=cases,explanation='These are stress tests, not choices to rank. Operating conditions are hypothetical and may not be controllable. Selecting a case loads it for review; it does not book a dispatch.')

def decisions(s, objective):
    base=s.model_copy(deep=True); base.applyDiscounts=False
    full=solve(base,objective)
    discounted_s=base.model_copy(deep=True); discounted_s.applyDiscounts=True
    discounted=solve(discounted_s,objective)
    held=evaluate(base,[],'Hold all stock')
    held_result=full.model_copy(update={'proposed':held})
    options=[
        dict(name='Sell at base price',change='Meet base demand at the listed price; keep remaining stock.',scenario=base,result=full),
        dict(name='Markdown eligible surplus',change='Use only expiring stock and demand headroom above the base estimate.',scenario=discounted_s,result=discounted),
        dict(name='Hold stock',change='Dispatch nothing; retain inventory and leave demand unserved.',scenario=base,result=held_result),
    ]
    valid=[o for o in options if not o['result'].proposed.violations]
    if objective=='balanced':
        ref=full.baseline.metrics
        valid=[o for o in valid if o['result'].proposed.metrics.fulfillment+1e-6>=ref.fulfillment and o['result'].proposed.metrics.spoilage<=ref.spoilage+1e-6]
    elif objective=='spoilage' and valid:
        best=max(o['result'].proposed.metrics.net for o in valid)
        floor=best-max(100,abs(best)*.1)
        valid=[o for o in valid if o['result'].proposed.metrics.net>=floor-1e-6]
    if not valid: valid=options[:1]
    winner=min(valid,key=lambda o:rank_key(o['result'].proposed,objective))
    metrics=winner['result'].proposed.metrics
    fifo=full.baseline.metrics
    net_delta=metrics.net-fifo.net
    direction='above' if net_delta>=0 else 'below'
    explanation=(
        f"Best among {len(valid)} feasible choices for the {objective} objective: {winner['name']}. "
        f"Estimated net contribution is ₹{metrics.net:,.2f} ({abs(net_delta):,.2f} {direction} provisional FIFO), "
        f"base-demand fulfillment is {metrics.fulfillment:.1f}%, and estimated spoilage is {metrics.spoilage:.1f} kg. "
        "This ranking uses the modeled inputs and stated guardrails; it is not a forecast or a guarantee."
    )
    return dict(options=options,winner=winner['name'],explanation=explanation)
