""" Analytical functions derived from data internal to sigma7 and or not from one of our typical vendors.
"""

from json import loads
from requests import get
from copy import deepcopy
from sigma7.settings import political_trades
from sigma7.dec_cache import cache
from sigma7.utils import parse_dates, within_date_range, parse_amount, unique_list_append

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
                out["transactions"].append(trade)
            if sort:
                out["transactions"] = list(sorted(out["transactions"], key=lambda x: x["disclosure_date"], reverse=True))
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
    trans = {"sale_partial": "sale", "sale_full": "sale", "purchase": "purchase", "exchange": "purchase"}
    for trade in trades:
        ra = trade["amount"]
        amt = parse_amount(ra)
        _type = trans[trade["type"]]
        out["data"][_type]["est_volume"] += amt
    return out

@cache(platform = "sigma7")
def politician_transactions(symbol: str) -> dict:
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
    tp = {"date": False, "purchase_volume": 0, "sale_volume": 0, "reps": list()}
    trans = {"sale_partial": "sale_volume", "sale_full": "sale_volume", "purchase": "purchase_volume", "exchange": "purchase_volume"}
    trades = search_political_trades(symbol = symbol, lastN = 36)["transactions"]
    for trade in trades:
        _date = trade["disclosure_date"]
        amt = parse_amount(trade["amount"])
        if _date not in out["transactions"].keys():
            _out = deepcopy(tp)
        else: _out = trades["transactions"][_date]
        if not _out["date"]: _out["date"] = _date
        _type = trans[trade["type"]]
        _out[_type] += amt
        _out["reps"] = unique_list_append(_out["reps"], trade["representative"])
        out[_date] = _out
    out["transactions"] = list(out["transactions"].values())
    return out



    



    


    



        
        

