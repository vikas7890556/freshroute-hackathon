"""Provisional FIFO: oldest receipt, stable input order, then route input order."""
def fifo(s, rows):
    try:
        from .planner import allocate
    except ImportError:  # Vercel imports backend modules as top-level files.
        from planner import allocate
    return allocate(s,sorted(rows,key=lambda e:(e['b'].received,e['bi'],e['ri'])),'Provisional FIFO')

def earliest_expiry(s, rows):
    try:
        from .planner import allocate
    except ImportError:  # Vercel imports backend modules as top-level files.
        from planner import allocate
    return allocate(s,sorted(rows,key=lambda e:(e['b'].expiry,e['b'].received,e['bi'],e['ri'])),'Earliest expiry first')
