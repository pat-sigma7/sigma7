""" 
decor - module to store most decorator functions for sigma7
"""

import pandas as pd
import functools
from sigma7.wrapper import func_routes

def route_func(func) -> dict:
    """Routes a dictionary to the correct iex or sigma7 function.

    This function should be used on an endpoint to route a endpoint
    to the right iex or sigma7 function.

    Args: 
        func (function): Wraps over a function that SHOULD return a dictionary with the following structure:
            {"platform": ["iex", "sigma7"], "func": "supported_function", "params": {"symbol": "TICKER", etc}}
    
    Returns:
        dict: Dictionary output from a routed function
    
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        raw = func(*args, **kwargs)
        platform, _func, params = raw["platform"], raw["func"], raw["params"]
        route = func_routes[platform][_func]
        _func = route["func"]
        params.update(route["params"])
        out = _func(**params)
        return out
    return wrapper

def dec_test(func) -> dict:
    """ test decorator function 
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        out = func(*args, **kwargs)
        if isinstance(out, list):
            out.append("hi")
        elif isinstance(out, dict):
            out["test"] = "hi"
        return out
    return wrapper
