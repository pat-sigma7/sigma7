""" 
decor - module to store most decorator functions for sigma7
"""

import pandas as pd
import functools
from sigma7.utils import log
from time import time

def benchmark(func) -> str:
    """Tracks how long a function takes to complete, start to finish.

    Args:
        func (function): Wraps over a function

    Returns:
        str: String containing how long the function took to run
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time()
        func(*args, **kwargs)
        end = time()
        diff = end - start
        log(diff)
        return diff
    return wrapper

def dec_test(func) -> dict:
    """ test decorator function 
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        out = func(*args, **kwargs)
        if isinstance(out, list):
            out.append("hi")
        elif isinstance(out, dict):
            out["test"] = "hi"
        return out
    return wrapper


