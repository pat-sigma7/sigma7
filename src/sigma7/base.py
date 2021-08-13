def econ_series(_key: str, range: str = "1y", format: str="dict"):
    if _key not in econ_keys.keys():
        raise Exception("_key Param not supported..")
    key = econ_keys[_key]
    token = environ["IEX_TOKEN"]
    url = econ_ep.format(key, token, range)
    load = get(url)
    out = loads(load.text)
    if format == "df": out = econ_df(out)
    return out