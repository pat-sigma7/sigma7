""" Analytical functions derived from data internal to sigma7 and or not from one of our typical vendors.
"""

from json import loads
from requests import get
from sigma7.settings import political_trades
from sigma7.dec_cache import cache

def pull_political_trades() -> dict:
    """ Pulls trades of congress men/women.

    This will ultimately be saved in a container somewhere in azure.

    Returns:
        dict: dictionary containing political trades indexed by house/senate

    """
    out = {}
    for trades in political_trades.items():
        group, ep = trades
        raw = loads(get(ep).text)
        out[group] = raw 
    return out

@cache(platform="sigma7")
def search_pinsiders(symbol: str, insiders: dict) -> dict:
    """Search insider transactions by symbol

    Args:
        symbol (str): Supported IEX symbol
        insiders (dict): Dictionary containing insiders to search
    Returns:
        dict: Insider transactions indexed by symbol
    """
    pass


        
        

