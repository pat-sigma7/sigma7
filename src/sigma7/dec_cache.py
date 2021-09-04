"""
Cache module for sigma7

This module contains the code for the sigma7 cache. 
"""

from sigma7.settings import cache_limit, cache_time_limit
from sigma7 import CACHE
from sigma7.utils import log, pull_key
import functools
from copy import deepcopy
from sys import getsizeof
from time import time


def check_cache_size() -> bool:
    """Ensures that the cache size less than the designated limit.

    Returns:
        bool: Whether or not the cache is equal to or past the limit. 
    
    """
    _size = getsizeof(CACHE)
    return _size < cache_limit

def check_cache(platform: str, key: str, func: str):
    """Checks the cache for a given symbol and function.

    This function indexes the cache to determine if there is data available.
    If not, the function returns False.

    Args:
        platform (str): Which platform to search the cache for - top layer of cache [iex, sigma7]
        key (str): Usually a stock ticker/econ ticker - second most layer of cache
        func (str): Name of function for cache, lowest layer of cache

    """
    if key in CACHE[platform].keys():
        if func in CACHE[platform][key].keys():
            return CACHE[platform][key][func]
    return False
             
        
def append_cache(platform: str, key: str, func: str, _dict: dict):
    """Appends an object to the sigma7 cache 

    Args:
        platform (str): Which platform to search the cache for - top layer of cache [iex, sigma7]
        key (str): Usually a stock ticker/econ ticker - second most layer of cache
        func (str): Name of function for cache, lowest layer of cache
        _dict (dict): data to append into platform -> key -> func -> data

    Returns:
        bool: Whether the operation was successful

    """
    _dict["cache_ts"] = time()
    CACHE[platform][key] = {
        func: _dict
    }
    return True

def pop_cache(platform: str, key: str, func: str) -> bool:
    """Deletes a specific entry in the sigma7 cache.

    Args:
        platform (str): Which platform to search the cache for - top layer of cache [iex, sigma7]
        key (str): Usually a stock ticker/econ ticker - second most layer of cache
        func (str): Name of function for cache, lowest layer of cache
    
    Returns:
        bool: Whether the operation was successful
    """
    del CACHE[platform][key][func]
    return True
    
def purge_cache(verbose = False) -> bool:
    """Purge expired entries in the sigma7 cache

    Returns:
        bool: Whether the operation was successful
    """
    _cache = deepcopy(CACHE)
    for item in _cache.items():
        platform, _out = item
        if verbose: log(platform)
        for _item in _out.items():
            symbol, __out = _item
            if verbose: log(symbol)
            for __item in __out.items():
                func, _data = __item
                if verbose: log(func)
                ts = _data["cache_ts"]
                diff = time() - ts
                if cache_time_limit <= diff:
                    if verbose: log("removing..")
                    del CACHE[platform][symbol][func]
    return True

def clean_cache(verbose = False) -> bool:
    """Cleans cache of empty dicts (symbols)

    Returns: 
        bool: Whether the operation was successful
    """
    _cache = deepcopy(CACHE)
    for item in _cache.items():
        platform, out = item
        if verbose: log(platform)
        for _item in out.items():
            symbol, _out = _item
            if verbose: log(symbol)
            if not _out: 
                del CACHE[platform][symbol]
                if verbose: log(f"Cleaning {platform} - {symbol}")
    return True

def cache(platform, _key = None) -> dict:
    """Decorator cache function 

    This function checks the cache available data on a given
    platform, symbol, and function. If data is available, it will be
    returned. If data is not available, the function is run and the data
    is appended into the cache for later use.

    Args:
        func (function): Wraps over a function to enable a cache
                        This function should have params - platform, key, and func
    
    Returns:
        dict: A cached output or newly generated output
    """
    def dec_wrapper(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            _func = func.__name__
            key = pull_key(kwargs)
            if _key: key = _key
            if key:
                _cache = check_cache(platform, key, _func)
                if _cache: return _cache
            out = func(*args, **kwargs)
            if check_cache_size() and key:
                append_cache(platform, key, _func, out)
            else: log("Cannot log entry")
            return out
        return wrapper
    return dec_wrapper

        




            



