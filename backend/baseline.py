"""Provisional FIFO: oldest receipt, stable input order, then route input order."""
def fifo(s, rows):
    from .planner import allocate
    return allocate(s,sorted(rows,key=lambda e:(e['b'].received,e['bi'],e['ri'])),'Provisional FIFO')

def earliest_expiry(s, rows):
    from .planner import allocate
    return allocate(s,sorted(rows,key=lambda e:(e['b'].expiry,e['b'].received,e['bi'],e['ri'])),'Earliest expiry first')
