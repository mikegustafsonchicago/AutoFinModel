# middleware.py
from functools import wraps
from flask import g, request
from typing import Callable
import logging
from context_manager import get_user_context

def inject_context(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not hasattr(g, 'context'):
            #logging.debug("[inject_context] No context found in g, creating new context")
            g.context = get_user_context()
        return f(*args, **kwargs)
    return decorated_function