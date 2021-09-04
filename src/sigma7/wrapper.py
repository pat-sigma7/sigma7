from pyEX import analystRecommendations, balanceSheet, cashFlow, ceoCompensation, incomeStatement, dividendsBasic, chart, news
from sigma7.iex_funcs import analyzeNews
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
