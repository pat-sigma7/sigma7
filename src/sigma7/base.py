# -*- coding: utf-8 -*-
""" sigma7 base - this module contains base functions that will be used in larger sigma7 function.

The functions contained in this module typically are smaller in output, less formatted, and are meant to be used
in other functions later. They are defined here to later allow for asynchronicity. 
"""

from json import loads
from sigma7.settings import econ_keys, econ_ep
from sigma7.utils import econ_df
from pyEX import chart
from os import environ
from sigma7.decor import dec_test
from requests import get

def econ_series(_key: str, range: str = "1y", format: str="dict") -> dict:
    """Returns a dict or dataframe of econ data from IEX. 

    Ensure that the key is one of those in settings (econ_keys).
    
    Args: 
        _key (str): Key to specify econ data
        range (str): Timeframe [ytd, 1yr, 2yr, 5yr]
        format (str): Dictionary or dataframe, defaults to dictionary [dict, df]

    Returns:
        dict: Econ data - also available as a dataframe.

    """

    if _key not in econ_keys.keys():
        raise Exception("_key Param not supported..")
    key = econ_keys[_key]
    token = environ["IEX_TOKEN"]
    url = econ_ep.format(key, token, range)
    load = get(url)
    out = loads(load.text)
    if format == "df": out = econ_df(out)
    return out
