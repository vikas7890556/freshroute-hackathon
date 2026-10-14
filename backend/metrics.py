from datetime import timedelta
from .models import Metrics, Plan
from .feasibility import audit

def evaluate(s, allocations, strategy):
    sent={}; used=set(); sold={}; base_sold={}; markdown_allocated=0.0
    revenue=variable=fixed=handling=0.0
    for a in allocations:
        r=next(r for r in s.routes if r.id==a.route)
        sent[a.batch]=sent.get(a.batch,0)+a.quantity
        key=(a.destination,a.produce); sold[key]=sold.get(key,0)+a.quantity
        if a.discount > 0: markdown_allocated += a.quantity
        else: base_sold[key]=base_sold.get(key,0)+a.quantity
        revenue+=a.price*a.quantity; variable+=r.perKg*a.quantity; handling+=r.handlingCost*a.quantity
        if r.id not in used: fixed+=r.fixedCost; used.add(r.id)
    horizon=s.planningTime+timedelta(hours=s.horizonHours)
    unallocated=[dict(batch=b.id,produce=b.produce,quantity=max(0,b.quantity-sent.get(b.id,0)),expires=b.expiry<=horizon,expiry=b.expiry.isoformat()) for b in s.batches if b.quantity-sent.get(b.id,0)>1e-6]
    spoilage=sum(x['quantity'] for x in unallocated if x['expires'])
    value=sum(max(0,b.quantity-sent.get(b.id,0))*b.acquisition for b in s.batches if b.expiry<=horizon)
    remaining_value=sum(max(0,b.quantity-sent.get(b.id,0))*b.acquisition for b in s.batches if b.expiry>horizon)
    stock=sum(b.quantity for b in s.batches); allocated=sum(a.quantity for a in allocations)
    requested=sum(q.quantity for d in s.destinations for q in d.demands)
    purchase=sum(b.quantity*b.acquisition for b in s.batches)
    sold_purchase=sum(a.quantity*next(b.acquisition for b in s.batches if b.id==a.batch) for a in allocations)
    packaging=None if s.packagingPerKg is None else allocated*s.packagingPerKg
    storage=None if s.storagePerKg is None else stock*s.storagePerKg
    platform=None if s.platformRate is None else revenue*s.platformRate
    tax=None if s.taxRate is None else revenue*s.taxRate
    disposal=spoilage*s.disposalPerKg
    costs=sold_purchase+value+fixed+variable+handling+disposal+sum(x or 0 for x in [packaging,storage,platform,tax])
    fulfilled=sum(min(q.quantity,base_sold.get((d.id,q.produce),0)) for d in s.destinations for q in d.demands)
    m=Metrics(stock=stock,allocated=allocated,unallocated=stock-allocated,demand=requested,unmet=max(0,requested-fulfilled),fulfillment=100*fulfilled/requested if requested else 0,spoilage=spoilage,spoilageValue=value,remaining=max(0,stock-allocated-spoilage),revenue=revenue,acquisition=purchase,soldAcquisition=sold_purchase,spoilageWriteoff=value,remainingInventoryValue=remaining_value,markdownAllocated=markdown_allocated,fixedTransport=fixed,variableTransport=variable,handling=handling,packaging=packaging,storage=storage,platform=platform,tax=tax,disposal=disposal,net=revenue-costs)
    unmet=[dict(destination=d.name,produce=q.produce,quantity=max(0,q.quantity-base_sold.get((d.id,q.produce),0))) for d in s.destinations for q in d.demands if q.quantity-base_sold.get((d.id,q.produce),0)>1e-6]
    return Plan(allocations=allocations,metrics=m,unallocated=unallocated,unmet=unmet,violations=audit(s,allocations),strategy=strategy)
