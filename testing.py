#from sigma7.base import _prices
from sigma7.decor import route_func
from sigma7.dec_cache import append_cache, clean_cache, purge_cache
from sigma7 import CACHE
from pyEX import Client
import os
from sys import getsizeof
from time import time, sleep

os.environ["IEX_TOKEN"] = "pk_6fdc6387a2ae4f8e9783b029fc2a3774"
Client()
symbol = "MSFT"
frame = "1y"

@route_func
def test_func():
    return {
        "platform": "iex",
        "func": "ceo_pay",
        "params": {
            "symbol": "MSFT"
        }
    }

def test_func2(first: str, last: str):
    return f"hi {first} {last}"

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

test = {}
if not test["one"]:
    print("hi")