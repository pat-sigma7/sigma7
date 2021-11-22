""" sigma7 wrapper - this module contains code to be used as wrappers/decorators throughout the .

The functions contained in this module support the wrapper/decorators in other modules. In particular, decor and dec_cache.
"""

from pyEX import analystRecommendations, balanceSheet, cashFlow, ceoCompensation, incomeStatement, dividendsBasic, chart, news
from logging import warning
import functools

func_routes = {
    "iex": {
        "analyst_recs": {
            "func": analystRecommendations,
            "params": {}
        },
        "balance_sheet": {
            "func": balanceSheet,
            "params": {}
        }, 
        "cash_flow": {
            "func": cashFlow,
            "params": {}
        },
        "ceo_pay": {
            "func": ceoCompensation,
            "params": {}
        },
        "income_statement": {
            "func": incomeStatement,
            "params": {}
        }, 
        "dividends": {
            "func": dividendsBasic,
            "params": {}
        },
        "prices": {
            "func": chart,
            "params": {"sort": "asc"}
        },
        "news": {
            "func": news,
            "params": {}
        }
    }
}

def check_route(platform: str,_func: str) -> dict:
    if platform in list(func_routes.keys()):
        return _func in list(func_routes[platform].keys())
    return False

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
        if check_route(platform, _func): 
            route = func_routes[platform][_func]
        else: 
            warning(f"Platform {platform} and or function {_func} not found in allowed routes..")
            return False
        _func = route["func"]
        params.update(route["params"])
        out = _func(**params)
        return out
    return wrapper

@route_func
def wrap(platform: str, _func: str, params: dict) -> dict:
    """Simple wrapper function to be used with the decorator above.

    See docs from decorator above..
    I know this isn't the best way to do it, but I'm too lazy to fix it right now. 
    Coming back to this later..
    """
    return {
        "platform": platform,
        "func": _func,
        "params": params
    }
