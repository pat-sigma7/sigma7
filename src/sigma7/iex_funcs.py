from os import environ
from numpy.core.fromnumeric import cumsum
from sigma7.utils import dfToDict, authenticate_client, sharpe_ratio, _remove, top_botN, econ_df, _align
from sigma7.settings import correlates
from pyEX.stocks.profiles import peers
from pyEX.stocks.research import keyStats
from pyEX.stocks.prices import chart, chartDF
from pyEX import dividendsBasicDF
from scipy.stats import trim_mean
from math import ceil 
from statistics import mean
from datetime import date
from pandasql import sqldf
from scipy.stats import spearmanr
from pyEX import news
from time import ctime, time
from logging import info
import pandas as pd
from numpy import NAN, NaN, prod
from sigma7.settings import correlates, econ_ep, econ_keys, econ_correlates
from requests import get
from json import loads
from math import isnan

#requires iex environment
def compareStat(symbol: str, stat: str, **args) -> dict:
    peersOf = peers(symbol)
    stats = []
    peer_data = {}
    for peer in peersOf:
        val = round(keyStats(peer, stat), 2)
        stats.append(val)
        peer_data[peer] = val
    trim = ceil(100/len(peersOf))
    trimmedAvg = trim_mean(stats, trim/100)
    peerAvg = mean(stats)
    og_stat = keyStats(symbol, stat)
    if (trimmedAvg - og_stat) < (peerAvg - og_stat):
        out_stat = trimmedAvg
    else:
        out_stat = peerAvg
    output = peer_data
    output[symbol] = og_stat
    output = dict(sorted(output.items(), key=lambda x: x[1], reverse=True)) 
    out = {"symbol": symbol, "average": og_stat, "peerAvg": out_stat, 
            "peers": peersOf, "peer_metrics": peer_data,
            "output": output,
             "meta": {
                 "trimmed_meta": f"Trimmed Mean - {trim}%",
                 "trimmedAvg": trimmedAvg, "realPeerAvg": peerAvg 
                }
        }
    return out

def avgMonthlyReturns(symbol: str, yearsBack:int) -> dict:
    query = '''
        SELECT 
          AVG(changePercent) AS AVG_PRICE
        , MONTH(date) as MONTH
        FROM (SELECT date, changePercent FROM PRICES) p 
        GROUP BY changePercent, date 
    '''
    end = date.today().year
    start = end - yearsBack
    prices = chartDF(symbol, exactDate = "{}-01-01".format(start))
    prices = sqldf(query)
    return prices

def corAnalysis(symbol: str, correlates: dict, frame: str="1y") -> dict:
    if (frame not in ["ytd", "1y", "2y", "5y"]):
        raise Exception('Parameter frame {} not supported. Options are ytd, 1y, 2y, and 5y'.format(frame))

    crs = {}
    all = {}
    x = chartDF(symbol, timeframe=frame, changeFromClose=True, sort="asc")[["changePercent"]]
    for cors in correlates.items():
        _key, _val = cors
        _out = dict()
        for correlate in _val.items():
            _x = x.copy()
            _symbol, y = correlate
            _info = f"Correlating {symbol} @ {_symbol}"
            info(_info)
            if _key == 'econ':
                y = econ_df(y)[["date", "changePercent"]]
            else:
                y = pd.DataFrame(y)[["date", "changePercent"]]
            _x = _x.dropna()
            y = y.dropna()
            y = y.set_index("date")
            #_x, y = _x.align(y, join = "inner", axis = 0)
            _x, y = _align(_x, y)
            rho, p = spearmanr(_x, y)
            info(rho)
            if p < .05 and (rho > .55 or rho < 0):
                _rho = round(rho, 2)
                _out[_symbol] = _rho
                all[_symbol] = _rho
        _out = dict(sorted(_out.items(), key=lambda x: x[1], reverse=True)) 
        crs[_key] = _out
    all = dict(sorted(all.items(), key=lambda x: x[1], reverse=True))
    out = {
        "symbol": symbol,
        "correlates": crs,
        "all": all,
        "output": top_botN(all)
    }
    return out
    
def analyzeNews(ticker: str) -> list:
    client = authenticate_client()
    raw = news(ticker, 10)
    fields = ["headline", "summary", "source", "sentiment", "date", "url", "related"]
    out, docs, loads = list(), list(), list()  
    for article in raw:
        if article["lang"] != "en" or article["hasPaywall"]:
            continue
        info = article["summary"]
        if article["summary"] == "No summary available.":
            info = article["headline"]
        docs.append(info)
        loads.append(article)
    
    analyses = client.analyze_sentiment(docs)
    for load, analysis in zip(loads, analyses):
        load["sentiment"] = analysis["sentiment"]
        load["date"] = ctime(load["datetime"]/1000)
        _out = load.copy()
        for key in load.keys():
            if key not in fields:
                del _out[key]
        out.append(_out)
    return out
    
def calcSharpe(symbol: str, frame: int=2, rf: float=.0) -> dict:
    peersOf = list(peers(symbol))
    peersOf = _remove("SPY", peersOf)
    sharpe = sharpe_ratio(symbol, frame, rf)
    _peers = {}
    spy = sharpe_ratio("SPY", frame, rf)
    out = {
        symbol: sharpe,
        "S&P 500": spy
    }
    for peer in peersOf:
        _sharpe = sharpe_ratio(peer, frame, rf)
        _peers[peer] = _sharpe
    out["peers"] = _peers
    return out

def dividend_yield(symbol: str, frame: str="5y", full: bool=False) -> dict:
    if frame not in ["1y", "3y", "5y"]:
        raise Exception("param frame not supported. Please input 1yr, 3yr, or 5yr")
    prices = chartDF(symbol, timeframe = frame, sort="asc")[["uClose"]]
    divs = dividendsBasicDF(symbol, timeframe = frame)
    if len(divs) ==  0:
        out = {
            "symbol": symbol,
            "range": frame,
            "1yr_growth" : NAN,
            "3yr_growth": NAN,
            "forward_yield": NAN,
            "chart": "No dividends available."
        }
        return out
    divs = divs[["amount"]]
    price_today = prices.tail(1)["uClose"].squeeze()
    today_div = divs.tail(1)["amount"].squeeze()
    divs = divs.rename_axis("date")
    _out = pd.merge(divs, prices, how = "inner", on = "date")[::-1]
    _out["_yield"] = _out["amount"] / _out["uClose"]
    _out["yield"] = _out["_yield"].rolling(4).apply(lambda x: prod(1+x) - 1)
    print(_out)
    back4 = _out.tail(4)["amount"].head(1).squeeze()
    back12 =  _out.tail(12)["amount"].head(1).squeeze()
    today_yield = _out.tail(1)["_yield"].squeeze()
    _1yr_growth =  (today_div - back4) / today_div 
    _3yr_growth = (today_div - back12) / today_div
    fwd_yield = (today_div * 4) / price_today
    _out = _out.dropna()
    chart = _out[["yield"]]
    chart["yield"] = chart["yield"] * 100
    if _1yr_growth == 0: _1yr_growth = NAN
    if _3yr_growth == 0: _3yr_growth = NAN
    chart.index = chart.index.astype('str')
    out = {
        "symbol": symbol,
        "frame": frame, 
        "3yr_growth": round(_3yr_growth * 100, 3), 
        "1yr_growth": round(_1yr_growth * 100, 3),
        "forward_yield": round(fwd_yield * 100, 3),
        "last_issue": round(today_div, 3),
        "chart": chart.round(3).to_dict()
    }
    if full:
        out["raw"] = _out
    return out

def full_returns(symbol: str, frame: str="ytd") -> dict:
    divs = dividendsBasicDF(symbol = symbol, timeframe= frame)
    prices = chartDF(symbol, timeframe = frame, sort="asc")[["close"]]
    if divs.empty: 
        total_div = 0
    else:
        divs = divs["amount"].tolist()
        total_div = sum(divs)
    start = prices.head(1).squeeze()
    end = prices.tail(1).squeeze()
    total_return = (end - start) + total_div
    per_return = round((total_return/start) * 100, 2) 
    out = {
        "symbol": symbol,
        "frame": frame,
        "return": round(total_return, 2),
        "percent_return": per_return
    }
    return out

def compare_performance(symbol: str, frame:str="ytd") -> dict:
    _peers = peers(symbol)
    sout = full_returns(symbol, frame)
    out = {
        "symbol": symbol,
        "frame": frame
    }
    if not _peers:
        out["returns"] = ["No peers to compare"]
        return out
    returns = {}
    for peer in _peers:
        pout = full_returns(peer, frame)
        returns[peer] = pout["percent_return"]
    returns[symbol] = sout["percent_return"]
    returns = dict(sorted(returns.items(), key=lambda x: x[1], reverse=True)) 
    out["returns"] = returns
    return out

def econ_series(_key: str, range: str = "1y", format: str="dict"):
    if _key not in econ_keys.keys():
        raise Exception("_key Param not supported..")
    key = econ_keys[_key]
    token = environ["IEX_TOKEN"]
    url = econ_ep.format(key, token, range)
    load = get(url)
    out = loads(load.text)
    if format == "df": out = econ_df(out)
    return out

def gather_correlates(_range: str="1y") -> dict:
    out = dict()
    markets = dict()
    for correlate in correlates.items():
        _key, _val = correlate
        __out = chart(_val, timeframe = _range, sort = "asc")
        markets[_key] = __out
    out["markets"] = markets
    
    econ = dict()
    for correlate in econ_correlates.items():
        _key, _val = correlate
        __out = econ_series(_val, _range)
        econ[_key] = __out
    out["econ"] = econ

    return out


    
