# middleware.py
from functools import wraps
from flask import g, request, session
from typing import Callable

def inject_context(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not hasattr(g, 'context'):
            #logging.debug("[inject_context] No context found in g, creating new context")
            g.context = session.get('user')['username']
        return f(*args, **kwargs)
    return decorated_function