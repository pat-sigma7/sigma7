from pyEX import analystRecommendations, balanceSheet, cashFlow, ceoCompensation, incomeStatement, dividendsBasic, chart, news
from sigma7.iex_funcs import analyzeNews

func_routes = {
    "iex": {
        "analyst_recs": {
            "func": analystRecommendations,
            "params": {}
        },
        "balance_sheet": {
            "func": balanceSheet,
            "params": {}
        }, 
        "cash_flow": {
            "func": cashFlow,
            "params": {}
        },
        "ceo_pay": {
            "func": ceoCompensation,
            "params": {}
        },
        "income_statement": {
            "func": incomeStatement,
            "params": {}
        }, 
        "dividends": {
            "func": dividendsBasic,
            "params": {}
        },
        "prices": {
            "func": chart,
            "params": {"sort": "asc"}
        },
        "news": {
            "func": news,
            "params": {}
        }
    }
}
