"""Wrapper IEX functions used on sigma7 endpoints.

These functions generally consist of further logic and data manipulation being added to
iex functions.
"""

from os import environ
from numpy.core.fromnumeric import cumsum
from sigma7.utils import authenticate_client, format_comp, sharpe_ratio, _remove, top_botN, econ_df, format_comp, gather_insiders, sort_dict, within_date_range
from sigma7.dec_cache import cache
from sigma7.decor import benchmark
from sigma7.settings import correlates
from pyEX.stocks.profiles import peers
from pyEX.stocks.research import keyStats
from pyEX.stocks.prices import chart, chartDF, ohlcDF
from pyEX import dividendsBasicDF, insiderTransactions, ceoCompensation, PyEXception
from scipy.stats import trim_mean
from math import ceil 
from statistics import mean
from scipy.stats import spearmanr
from pyEX import news
from time import ctime, time
from logging import info
import pandas as pd
from numpy import NAN, NaN, prod, cumprod
from sigma7.settings import correlates, econ_ep, econ_keys, econ_correlates
from requests import get
from json import loads

@cache(platform = "iex")
def compareStat(symbol: str, stat: str, **args) -> dict:
    """Compares a given stat of a given stock with its peers

    This function, given a stock and statistic, will compare said stock and statistic
    to its peers. It will also return the average or adjusted average of its peer group as a
    baseline.

    Args: 
        symbol (str): Given IEX symbol to compare
        stat (str): Supported statistic to compare symbols with (see IEX for supported stats)
    Returns:
        dict: Dictionary containing the symbol's stat, its peer stats, and baseline stats.
    """
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

@cache(platform = "iex")
def corAnalysis(symbol: str, correlates: dict, frame: str="1y") -> dict:
    """Correlates a given symbol to given correlates (usually several markets and econometrics) 

    Args:
        symbol (str): Symbol to correlate to
        correlates (dict): Dictionary containing keys with correlate names and values containing time series data to correlate.
        frame (str): Defaults to 1 year - how long to run correlation on.
    Returns:
        dict: Dictionary containing top correlated results 
    """
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
            y["date"] = pd.to_datetime(y["date"])
            y = y.set_index("date")       
            _x, y = _x.align(y, join = "inner", axis = 0)
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

def analyzeNews(symbol: str) -> dict:
    """Runs sentiment analysis on news for a given symbol

    Pulls news for a given symbol, and classifies its sentiment.
    Not cached because this one could refresh every few seconds.

    Args:
        symbol (str): Supported IEX symbol
    Returns:
        dict: a dictionary containing news entries
    """
    client = authenticate_client()
    raw = news(symbol, 10)
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
    return {"news": out}

@cache(platform = "iex")
def calcSharpe(symbol: str, frame: int=2, rf: float=.0) -> dict:
    """Calculates sharpe ratio for a given stock along with its peers

    Args:
        symbol (str): Supported IEX symbol
        frame (int): Number of periods/years to generate sharpe ratio on.
        rf (float): Risk free ratio - defaults to 0
    Returns:
        dict: Dictionary containing sharpe ratio alongside a given symbols peers
    """
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

@cache(platform = "iex")
def dividend_yield(symbol: str, frame: str="5y", full: bool=False) -> dict:
    """Calculates dividend yield for a given stock and formats it in an optimal way

    Calculates dividend yield, compounded dividend yield growth, and forward yield
    for a particular stock. 

    Args:
        symbol (str): Supported IEX symbol
        frame (str): Period to calculate yield from (defaults to 5 years)
        full (bool): Whether to return a dataframe of dividends - defaults to False
    Returns:
        dict: Dictionary containing dividend yield data
    """
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

@cache(platform = "iex")
def full_returns(symbol: str, frame: str="ytd") -> dict:
    """ Calculates the total return/full return of a stock

    This function calculates total return, and incorporates dividend yield 
    in the CAGR. 

    Args:
        symbol (str): Supported IEX symbol
        frame (str): Period to calculate full returns on
    Returns:
        dict: Dictionary containing time series data
    """
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

@cache(platform = "iex")
def compare_performance(symbol: str, frame:str="ytd") -> dict:
    """Compares total performance of a given symbol and its peers

    Uses full_returns function to generate full returns on a symbol
    and its peers.

    Args:
        symbol (str): Supported IEX symbol
        frame (str): Period to calculate performance on - defaults to "ytd"
    Returns:
        dict: Dictionary containing performance data of a symbol and its peers 
    """
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
    __peers = list()
    for peer in _peers:
        pout = full_returns(peer, frame)
        returns[peer] = pout["percent_return"]
        __peers.append(pout["percent_return"])     
    returns[symbol] = sout["percent_return"]
    returns = dict(sorted(returns.items(), key=lambda x: x[1], reverse=True)) 
    out["returns"] = returns
    out["average"] = sout["percent_return"]
    out["peerAvg"] = mean(__peers)
    return out

@cache(platform = "iex")
def econ_series(_key: str, range: str = "1y", format: str="dict"):
    """Generates time series data for a given econometric

    Args:
        _key (str): Supported key/econometric in IEX
        range (str): Period to generate time series on
        format (str): Format to return data in (defaults to dict)
    Returns:
        dict: Dictionary containing econometric data
    """
    if _key not in econ_keys.keys():
        raise Exception("_key Param not supported..")
    key = econ_keys[_key]
    token = environ["IEX_TOKEN"]
    url = econ_ep.format(key, token, range)
    load = get(url)
    out = loads(load.text)
    if format == "df": out = econ_df(out)
    else: out = dict(out)
    return out

def gather_correlates(_range: str="1y") -> dict:
    """ Returns correlate time series data as outlined in the correlates var

    Args:
        _range (str): Period to generate data on
    Returns:
        dict: Time series data for all correlates
    """
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

@cache(platform = "iex")
def compare_ceo_comp(symbol: str) -> dict:
    """Compares CEO Compensation of a given stock with its peers.

    This function compares CEO Compensation amongst a stocks peers, and also
    computes the average or baseline compensation among its peers and returns that.

    Args:
        symbol (str): Supported IEX symbol/ticker
    Returns:
        dict: Dictionary containing ceo compensation data
    """
    _peers = peers(symbol)
    _symbol = ceoCompensation(symbol)
    out = format_comp(_symbol)
    out["comp"] = sort_dict(out["comp"])
    peer_comp = dict()
    peer_avg = list()
    for _peer in _peers:
        try:
            raw = ceoCompensation(_peer)
        except PyEXception:
            continue
        peer_comp[_peer] = raw["total"]
        peer_avg.append(raw["total"])
    peer_avg.append(_symbol["total"])
    peer_comp[symbol] = _symbol["total"]
    out["peerAvg"] = round(mean(peer_avg),2)
    peer_comp = sort_dict(peer_comp)
    out["peers"] = peer_comp
    return out

@cache(platform = "iex")
def insider_transactions(symbol: str) -> dict:
    """Formats, orders, and computes insider transactions for a given symbol.

    Args:
        symbol (str): Supported IEX symbol
    Returns:
        dict: Dictionary containing insider transaction data
    """
    raw = insiderTransactions(symbol)
    out = {
        "symbol": symbol,
        "transactions": {}
    }
    _raw = gather_insiders(raw)
    for trx in raw:
        if trx["filingDate"] not in out["transactions"].keys():
            out["transactions"][trx["filingDate"]] = {}
        shares = trx["tranShares"]
        #_key = "{} - {}".format(trx["fullName"], trx["reportedTitle"])
        _key = trx["fullName"].title()
        _out = _raw.copy()
        _out["date"] = trx["filingDate"]
        _out[_key] = shares
        out["transactions"][trx["filingDate"]].update(_out)
    transactions = {}
    ok = sorted(out["transactions"].keys())
    for _key in ok:
        transactions[_key] = out["transactions"][_key]
    out["transactions"] = list(transactions.values())
    return out

@cache(platform = "iex")
def top_insiders(symbol: str) -> dict:
    """Returns the top insiders by volume

    Args:
        symbol (str): Supported IEX symbol
    Returns:
        dict: Top N insiders ordered least to greatest by volume
    """
    raw = insiderTransactions(symbol)
    insider = {"sale": 0, "buy": 0, "total_volume": 0}
    insiders = {}
    for trans in raw:
        name = trans["fullName"].title()
        title = trans["reportedTitle"]
        shares = trans["tranShares"]
        if name in insiders.keys():
            _insider = insiders[name]
        else:
            _insider = insider.copy()
        if shares > 0:
            _insider["buy"] += shares
        else:
            _insider["sale"] -= shares
        if "title" not in _insider.keys():
            _insider["title"] = title
        elif "title" in _insider.keys():
            if not _insider["title"]: _insider["title"] = title
        _insider["total_volume"] = _insider["total_volume"] + abs(shares)
        _insider["name"] = name
        insiders[name] = _insider
    insiders = dict(sorted(insiders.items(), key=lambda x: x[1]["total_volume"], reverse=True))
    for x in insiders.copy().items():
        _key, data = x
        if not data["title"]: insiders[_key]["title"] = "Employee"
    out = {
        "symbol": symbol,
        "insiders": list(insiders.values())
    }
    return out

@cache(platform = "iex")
def insider_trades(symbol: str) -> dict:
    """Formats, orders, and computes insider transactions for a given symbol.

    Args:
        symbol (str): Supported IEX symbol
    Returns:
        dict: Dictionary containing insider transaction data
    """
    raw = insiderTransactions(symbol)
    out = {
        "symbol": symbol,
        "transactions": {}
    }
    for trx in raw:
        if trx["filingDate"] not in out["transactions"].keys():
            out["transactions"][trx["filingDate"]] = {"date": False, "purchase": 0, "sale": 0}
        _date = trx["filingDate"]
        _out = out["transactions"][_date].copy()
        if not _out["date"]: _out["date"] = _date
        shares = trx["tranShares"]
        if shares > 0:
            _out["purchase"] += shares
        else:
            _out["sale"] -= shares
        out["transactions"][_date] = _out 
    out["transactions"] = list(out["transactions"].values())
    return out

@cache(platform = "iex")
def insider_pie(symbol: str, n: int=3) -> dict:
    """Returns the insider transactions as a fraction

    Args:
        symbol (str): Supported IEX ticker
        n (int): Number of months to look back
    Returns:
        dict: Insider transaction proportions
    """
    if n not in [3, 6, 12]: 
        raise Exception("Param n not [3, 6, 12]")
    raw = insiderTransactions(symbol)
    out = {
        "symbol": symbol,
        "data": {
            "bought": {
                "transaction": "purchase",
                "shares": 0
            }, 
            "sold": {
                "transaction": "sale",
                "shares": 0
            }
        }
    } 
    for trx in raw:
        _date = trx["filingDate"]
        if not within_date_range(_date, n): continue
        shares = trx["tranShares"]
        if shares > 0:
            out["data"]["bought"]["shares"] += shares
        else:
            out["data"]["sold"]["shares"] -= shares
    out["data"] = list(out["data"].values())
    return out
    

