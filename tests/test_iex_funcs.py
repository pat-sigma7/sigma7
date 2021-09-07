
import pytest
from os import environ

environ["IEX_TOKEN"] = "Tpk_0a80aa79cd7244838ccc02f6ad231450"
environ["AzureTextAnalysisKey"] = "984d75c6374c4394bc4682f30d8b99f0"

def test_func_type(generate_funcs):

    function, params, out = generate_funcs
    assert type(function(**params)) == out 
