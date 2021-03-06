""" Utils contains support functions used in other modules. 

These functions are largely used to organize code into smaller more modular chunks. 
They will be further documented later..
"""

from datetime import datetime  
import pandas as pd
from pandas import Timestamp
from numpy import int64, int32, float64, bool_
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
from os import environ
from datetime import date, timedelta
from .settings import comp_fields
from pyEX import chartDF
from numpy import sqrt, log1p
from statistics import median
from logging import info
from sys import getsizeof
from time import mktime

def log(_info: str):
    print(_info)
    info(_info)

def pull_key(args: dict) -> dict:
    if "symbol" in args.keys():
        return args["symbol"]
    elif "key" in args.keys():
        return args["key"]
    elif "_key" in args.keys():
        return args["_key"]
    else:
        return False

def convert(o):
    if isinstance(o, int64): return int(o)  
    if isinstance(o, int32): return int(o)
    if isinstance(o, float64): return float(o)
    if isinstance(o, datetime): return str(o)
    if isinstance(o, pd.Timestamp): return str(o)
    if isinstance(o, bool_): return bool(0)
    else: return o

def dfToDict(df: pd.DataFrame) -> dict:
    out = {}
    uniques = list(df.columns[df.nunique() <= 1])
    for item in uniques:
        out.update({item.lower(): df[item][0]})
    return(out)    

def flatten_df(df: pd.DataFrame, symbol: str, index: str) -> dict:
    if index not in list(df.columns):
        raise Exception("{} could not be found in the input Data Frame.".format(index))
    indx = df[index].astype(str)
    df = df.drop(columns = [index])
    out = {"symbol" : symbol}
    uniques = list(df.columns[df.nunique() <= 1])
    nons = list(set(list(df.columns)) - set(uniques))
    for item in uniques:
        out.update({item.lower(): df[item][0]})
    for item in nons:
        out.update({item.lower(): dict(zip(indx, df[item]))})
    return out

def format_small(df: pd.DataFrame, symbol: str, col: str) -> dict:
    if type(symbol) != str or type(col) != str:
        raise Exception("Input symbol/col is not string. Please provide a string.")
    dates = df["DATE"].astype(str)
    out = {
        "symbol" : symbol,
        "currency" : df["CURRENCY"][0],
        col.lower(): dict(zip(dates, df[col.upper()]))
    }
    return(out)

def authenticate_client() -> object:
    ta_credential = AzureKeyCredential(environ["AzureTextAnalysisKey"])
    text_analytics_client = TextAnalyticsClient(
            endpoint=environ["AzureTextAnalysisEP"], 
            credential=ta_credential) 
    return text_analytics_client

def sharpe_ratio(symbol: str, N:int, rf: float=0):
    prices = chartDF(symbol, timeframe=f"{N}y", sort="asc") 
    r = prices["changePercent"].mean()
    if rf > 0: r = r - rf
    std = prices["changePercent"].std()
    sharpe = (r / std) * sqrt(252)
    return {
        "sharpe": round(sharpe, 4),
        "avg_return": round(r, 4),
        "std": round(std, 4)
    }

def _remove(x: object, y: list) -> list: 
    try: 
        y.remove(x)
    except ValueError:
        return y
    return y

def top_botN(x: dict, N: int=3) -> dict:
    out, bottom = list(), list()
    for item in x.items():
        name, val = item
        if val >= 0:
            out.append(item)
        else: 
            bottom.append(item)
    out = out[:3]
    out.extend(bottom[-3:])
    return dict(out)

def filter_symbols(_symbols: list) -> list:
    out = list()
    for symbol in _symbols:
        if symbol["type"] not in ["cs", "et"]:
            continue
        out.append(symbol)
    return out

def filter_key_dict(_dict: dict, keys: list) -> dict:
    out = _dict.copy()
    unwanted_keys = set(keys) - set(_dict.keys())
    for ukey in unwanted_keys: 
        del out[ukey]
    return out

def econ_df(_dict: dict) -> dict:
    out = pd.DataFrame(_dict)
    if "date" in out.columns:
        out = out.sort_values("date") 
        out["date"] = pd.to_datetime(out["date"], unit = 'ms')
    out["changePercent"] = out["value"].pct_change(fill_method="ffill")
    return out

def _align(df1: dict, df2: dict) -> tuple:
    out = (df1, df2)
    align = False
    if len(df1) != len(df2):
        align = True
    else:
        indx_check = df1.index == df2.index
        if not indx_check[0]:
            align = True
        if not indx_check[len(indx_check)-1]:
            align = True
        if not all(indx_check):
            align = True
    if align:
        out = df1.align(df2, join = "inner", axis = 0)
    return out

def format_comp(_dict: dict) -> dict:
    out = dict()
    comp = dict()
    for item in _dict.items():
        key, _var = item
        if key in comp_fields:
            if _var != 0: comp[key] = _var
        else:
            out[key] = _var
    out["comp"] = comp
    return out

def sort_dict(_dict: dict) -> dict:
    out = dict(sorted(_dict.items(), key=lambda x: x[1], reverse=True))
    return out 

def gather_insiders(insiders: list) -> dict:
    out = {}
    for insider in insiders:
        _name, title = insider["fullName"], insider["reportedTitle"]
        if not title:
            title = "Employee"
        #_key = "{} - {}".format(_name, title)
        _key = _name.title()
        out[_key] = 0
    return out

def recent_price(_date: str, prices: pd.DataFrame) -> str:
    price = prices[_date]
    i = 1
    while not isinstance(price, float):
        _year, _mo,_d = _date.split("-")
        start = date(int(_year), int(_mo), int(_d))
        __date = str(start - timedelta(i))
        price = prices.loc[__date].squeeze()
        i -= 1
    return price

def within_date_range(_date: str, lastN: int) -> bool:
    n = lastN * 30
    if "/" in _date:
        _mo, d, _year = _date.split("/")
    else:
        _year, _mo, d = _date.split("-")
    start = date.today() - timedelta(n)
    __date = date(int(_year), int(_mo), int(d))
    return __date >= start 

def stringify_args(params: dict) -> str:
    out = list()
    for param in params.items():
        _key, val = param
        if type(val) not in [dict, list]:
            out.append(str(val))
    return "_".join(out)

def parse_amount(amt: str) -> int:
    raw = amt.replace("$", "").replace(",", "") 
    x, y = raw.split("-")
    if y == "" or not y:
        return int(x)
    out = median([int(x), int(y)])
    return int(out)

def parse_dates(_date: str) -> str:
    if "/" in _date:
        _mo, d, _year = _date.split("/")
    else:
        _year, _mo, d = _date.split("-")
    __date = date(int(_year), int(_mo), int(d))
    return str(__date)

def unique_list_append(_list: list, item) -> list:
    out = set(_list)
    out.add(item)
    return list(out)

def scan_cache(_cache: dict) -> dict:
    out = {}
    _size = 0
    for items in _cache.items():
        _key, vals = items
        _out = {}
        if _key not in ["iex", "sigma7"]: continue
        for _items in vals.items():
            func, _vals = _items
            entries = list(_vals.keys())
            _out[func] = entries
            for __items in _vals.items():
                __key, data = __items
                _size += getsizeof(data)
        out[_key] = _out
    out["size"] = _size
    return out

def date_to_ts(_date: str) -> int:
    if "/" in _date:
        _mo, d, _year = _date.split("/")
    else:
        _year, _mo, d = _date.split("-")
    __date = date(int(_year), int(_mo), int(d))
    tt = __date.timetuple()
    out = int(mktime(tt))
    return out