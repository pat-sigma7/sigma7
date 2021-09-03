
correlates = {
        "S&P 500": "SPY", "Gold": "GLD", 
        "Crypto": "GBTC", "Asia Pacific": "VPL",
        "Europe": "IEUR", "Latin America": "ILF",
        "Emerging Markets": "VWO", "Long Term Treasuries": "VGLT", 
        "Short Term Treasuries": "VGSH", "Energy": "VDE", 
        "Real Estate": "VNQ", "Healthcare": "VHT",
        "Communications": "VOX", "Consumer Discretionary": "VCR", 
        "Consumer Staples": "VDC", "Financials": "VFH", "Industrials": "VIS",
        "Technology": "VGT", "Materials": "VAW", "Utilities": "VPU"
    }

comp_fields = [
    "salary", 
    "bonus", 
    "stockAwards", 
    "optionAwards", 
    "nonEquityIncentives", 
    "pensionAndDeferred",
    "otherComp"
]

econ_correlates = {
    "Federal Funds Rate": "FEDFUNDS", 
    "Industrial Production Index": "INDPRO", 
    "Payroll": "PAYROLL", 
    "Housing Starts": "HOUSING",
    "Unemployment": "UNEMPLOYMENT", 
    "Vehicle Sales": "VEHICLES", 
    "Retail Funds": "RETAILMONEY",
    "Institutional Funds": "INSTITUTIONALMONEY"
    }

econ_keys = {
    "FEDFUNDS": "FEDFUNDS",
    "GDP": "A191RL1Q225SBEA", 
    "INDPRO": "INDPRO", 
    "CPI": "CPIAUCSL", 
    "PAYROLL": "PAYEMS", 
    "HOUSING": "HOUST", 
    "UNEMPLOYMENT": "UNRATE", 
    "VEHICLES": "TOTALSA", 
    "RECESSION_PROB": "RECPROUSM156N", 
    "INITIALCLAIMS": "IC4WSA", 
    "RETAILMONEY": "WRMFSL", 
    "INSTITUTIONALMONEY": "WIMFSL"
}

econ_ep = "https://cloud.iexapis.com/stable/time-series/economic/{}?token={}&range={}"

cache_limit = 1048576 * 300 # modify second number for mb limit 
cache_time_limit = 1

