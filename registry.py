ACTIONS = {}

def register(fn):
    ACTIONS[fn.__name__] = fn
    return fn
