"""
conftest.py
"""

import pytest
from collections import namedtuple
import sigma7.iex_funcs as iex

Function = namedtuple("Function", ["function", "params", "expected"])

@pytest.fixture(
    params=[
        Function(iex.compareStat, {"symbol": "MSFT", "stat": "marketcap"}, dict),
        Function(iex.analyzeNews, {"symbol": "MSFT"}, dict),
        Function(iex.calcSharpe, {"symbol": "MSFT", "frame": "2", "rf": 0}, dict),
        Function(iex.dividend_yield, {"symbol": "MSFT", "frame": "5y", "full": False}, dict),
        Function(iex.full_returns, {"symbol": "MSFT", "frame": "ytd"}, dict),
        Function(iex.compare_performance, {"symbol": "MSFT", "frame": "ytd"}, dict)
        #Function(iex.econ_series, {"_key": "FEDFUNDS", "range": "1y", "format": dict}, dict),
        #Function(iex.gather_correlates, {"_range": "1y"}, dict)
    ]
)
def generate_funcs(request):
    return request.param

