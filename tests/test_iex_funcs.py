
import pytest

def test_func_type(generate_funcs):

    function, params, out = generate_funcs
    assert type(function(**params)) == out 
