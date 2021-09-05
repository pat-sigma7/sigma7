#from sigma7.base import _prices
from numpy.core.numeric import full
from sigma7.dec_cache import append_cache, clean_cache, purge_cache
from sigma7.iex_funcs import analyzeNews, calcSharpe, compare_performance, corAnalysis, dividend_yield, full_returns
from sigma7.utils import pull_key
from sigma7 import CACHE
from pyEX import Client
import os
from sys import getsizeof
from time import time, sleep
from inspect import getargvalues

#os.environ["IEX_TOKEN"] = "pk_6fdc6387a2ae4f8e9783b029fc2a3774"
#Client()
symbol = "MSFT"
frame = "1y"
def test_func2(**kwargs):
    return kwargs

def test3():
    return "hi"

from collections import namedtuple
tpl = namedtuple("Function", ["func", "params", "expected"])

func, params, out = tpl("test_func", {"hi": "yo"}, str)
print(func, params, out)

'''
plt = "iex"
symbol = "MSFT"
func = "ceo_pay"
_data = {"test": 1}
append_cache(plt, symbol, func, _data)
print(CACHE)
sleep(2)
purge_cache(False)
clean_cache(True)
print(CACHE)
'''
