""" Analytical functions derived from data internal to sigma7 and or not from one of our typical vendors.
"""

from json import loads
from requests import get
from copy import deepcopy
from statistics import mean
from sigma7.settings import political_trades
from sigma7.dec_cache import cache
from sigma7.utils import date_to_ts, parse_dates, within_date_range, parse_amount, unique_list_append

@cache(platform = "sigma7", _key = "misc")
def pull_political_trades(merge: bool=True, sort: bool=True) -> dict:
    """Pulls trades of politicians.

    This will ultimately be saved in a container somewhere in azure.

    Args:
        merge (bool): Whether or not to merge house/senate political transactions. Defaults to True
        sort (bool): Whether or not to sort transactions by disclosure date. Defaults to True

    Returns:
        dict: dictionary containing political trades 
    """

    for trades in political_trades.items():
        group, ep = trades
        raw = loads(get(ep).text)
        out = {}
        if merge:
            out = {"transactions": []}
            for trade in raw:
                _date = parse_dates(trade["disclosure_date"])
                trade["date"] = _date
                trade["timestamp"] = date_to_ts(_date)
                out["transactions"].append(trade)
            if sort:
                out["transactions"] = list(sorted(out["transactions"], key=lambda x: x["timestamp"], reverse=True))
        else:
            out["transactions"][group] = raw 
    return out

@cache(platform = "sigma7")
def search_political_trades(symbol: str, lastN: int=6) -> dict:
    """Search insider transactions by symbol

    Args:
        symbol (str): Supported IEX symbol
        lastN (int): Number of months (backwards) to search - defaults to 6
    Returns:
        dict: Insider transactions indexed by symbol
    """

    out = {
        "symbol": symbol
    }
    transactions = []
    trades = pull_political_trades(merge = True, sort = True)["transactions"]
    for trade in trades:
        if symbol == trade["ticker"]:
            _date = parse_dates(trade["disclosure_date"])
            if within_date_range(_date, lastN):
                trade["disclosure_date"] = _date
                transactions.append(trade)
    out["transactions"] = transactions
    return out

@cache(platform = "sigma7")
def political_pie(symbol: str, lastN: int = 6) -> dict:
    """Returns the ratio of buys/sells from politicians for a given symbol.

    Args:
        symbol (str): IEX supported symbol
        lastN (int): Last N months - defaults to 6
    Returns:
        dict: Buy/sell ratio of political insiders
    """

    out = {
        "symbol": symbol,
        "data": {
            "bought": {
                "transaction": "purchase",
                "est_volume": 0
            }, 
            "sold": {
                "transaction": "sale",
                "est_volume": 0
            }
        }
    } 
    trades = search_political_trades(symbol = symbol, lastN = lastN)["transactions"]
    trans = {"sale_partial": "sold", "sale_full": "sold", "purchase": "bought", "exchange": "bought"}
    for trade in trades:
        ra = trade["amount"]
        amt = parse_amount(ra)
        _type = trans[trade["type"]]
        out["data"][_type]["est_volume"] += amt
    return out

@cache(platform = "sigma7")
def politician_transactions(symbol: str, rollingN: int=4) -> dict:
    """Returns the time-series transactions of trades from politicians on a given symbol

    Args:
        symbol (str): Supported IEX ticker
    Returns:
        dict: Dictionary containing time-series transactions
    """

    out = {
        "symbol": symbol,
        "transactions": {}
    }
    sale_vol, purch_vol, total_vol = list(), list(), list()
    tp = {"date": False, "purchase_volume": 0, "sale_volume": 0, "total_volume": 0, "reps": list()}
    trans = {"sale_partial": "sale_volume", "sale_full": "sale_volume", "purchase": "purchase_volume", "exchange": "purchase_volume"}
    trans_loc = {"sale_partial": sale_vol, "sale_full": sale_vol, "purchase": purch_vol, "exchange": purch_vol}
    _trans_loc = {"sale_partial": purch_vol, "sale_full": purch_vol, "purchase": sale_vol, "exchange": sale_vol}
    trades = search_political_trades(symbol = symbol, lastN = 36)["transactions"]
    print(len(trades))
    for trade in trades:
        _date = trade["disclosure_date"]
        amt = parse_amount(trade["amount"])
        if _date not in out["transactions"].keys():
            _out = deepcopy(tp)
        else: _out = out["transactions"][_date]
        if not _out["date"]: _out["date"] = _date
        _type = trans[trade["type"]]
        trans_loc[trade["type"]].append(amt)
        _trans_loc[trade["type"]].append(0)
        total_vol.append(amt)
        _out[_type] += amt
        _out["total_volume"] += amt
        if len(total_vol) >= 4:
            _out["rolling_purchase_vol"] = mean(purch_vol[-rollingN:])
            _out["rolling_sale_vol"] = mean(sale_vol[-rollingN:])
            _out["rolling_total_vol"] = mean(total_vol[-rollingN:])
        else:
            _out["rolling_purchase_vol"] = 0
            _out["rolling_sale_vol"] = 0
            _out["rolling_total_vol"] = 0
        _out["reps"] = unique_list_append(_out["reps"], trade["representative"])
        out["transactions"][_date] = _out
    out["transactions"] = list(out["transactions"].values())[3:]
    return out

@cache(platform = "sigma7")
def top_political_traders(symbol: str) -> dict:
    """Returns the top political traders of a given stock by volume
        over the last 18 months.

    Args:
        symbol (str): Supported IEX symbol
    Returns:
        dict: Top N political insiders ordered least to greatest by volume
    """
    
    trades = search_political_trades(symbol = symbol, lastN = 18)["transactions"]
    insider = {"est_sale_volume": 0, "est_purchase_volume": 0, "est_volume": 0, "district": False}
    trans = {"sale_partial": "est_sale_volume", "sale_full": "est_sale_volume", "purchase": "est_purchase_volume", "exchange": "est_purchase_volume"}
    insiders = {}
    for trade in trades:
        name = trade["representative"]
        amt = parse_amount(trade["amount"])
        district = trade["district"]
        if name in insiders.keys():
            _insider = insiders[name]
        else: _insider = insider.copy()
        _insider["name"] = name
        _type = trans[trade["type"]]
        _insider[_type] += amt
        _insider["est_volume"] += amt
        if not _insider["district"] and district: 
            _insider["district"] = district
            _insider["state"] = district[0:2]
        insiders[name] = _insider
    insiders = dict(sorted(insiders.items(), key=lambda x: x[1]["est_volume"], reverse=True))
    insiders = list(insiders.values())
    out = {
        "symbol": symbol,
        "transactions": insiders
    }
    return out


    



    


    



        
        

