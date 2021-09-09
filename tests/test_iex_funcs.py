
import pytest
from os import environ

environ["IEX_TOKEN"] = "pk_6fdc6387a2ae4f8e9783b029fc2a3774"
environ["AzureTextAnalysisKey"] = "984d75c6374c4394bc4682f30d8b99f0"
environ["AzureTextAnalysisEP"] = "https://sigma7-text.cognitiveservices.azure.com/"

def test_func_type(generate_funcs):

    function, params, out = generate_funcs
    assert type(function(**params)) == out 
