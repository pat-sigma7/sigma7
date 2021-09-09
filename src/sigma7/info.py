""" Info module containing strings. 

Just to keep things organized. These strings
will be referenced in other scripts.
"""

info = '''How-to: \n
\tURL: api/compare_metric/?symbol=[TICKER]&metric=[METRIC] \n
\n
Parameters: \n
\tsymbol: Supported ticker from Omega. All caps [REQUIRED] \n
\tmetric: Metric to return - [eps, div_yield, pe_ratio, beta, total_return]

'''

ticker_card_info = '''How-to: \n
\tURL: api/company/?symbol=[TICKER] \n
\n
Parameters: \n
\tsymbol: Supported ticker from Omega. All caps [REQUIRED] \n
'''
compare_info = '''How-to: \n
\tURL: api/compare_metric/?symbol=[TICKER]&metric=[METRIC] \n
\n
Parameters: \n
\tsymbol: Supported ticker from Omega. All caps [REQUIRED] \n
\tstat: Metric to return - [eps, div_yield, pe_ratio, beta, total_return]
'''

cor_info = '''How-to: \n
\tURL: api/correlaton_metric/?symbol=[TICKER]&frame=[FRAME] \n
\n
Parameters: \n
\tsymbol: Supported ticker from Omega. All caps [REQUIRED] \n
\fframe: Timeframe to analyze on - ["ytd", "max", "1m", "3m", "6m", "1y", "2y", "5y"]
'''

sentiment_info = '''How-to: \n
\tURL: api/news_sentiment/?symbol=[TICKER]&last=[FRAME] \n
\n
Parameters: \n
\tsymbol: Supported ticker from Omega. All caps [REQUIRED] \n
\flast: Last N articles to pull, defaults to 40 \n
\n
Description: \n
\tThis will filter out any non-English and empty summary articles. 
As a result, the exact number returned may not match the parameter last.
Likewise, this endpoints analyzes the remaining articles for sentiment.
'''

sharpe_info = '''How-to: \n
\tURL: api/sharpe/?symbol=[TICKER]&frame=[FRAME]&rf=[RISK-FREE-RATE] \n
\n
Parameters: \n
\tsymbol: Supported ticker from Omega. All caps [REQUIRED] \n
\tframe: Timeframe to calculate sharpe on. Defaults to 2 [1, 2, 5] \n
\trf: Risk free rate, defaults to 0.
\n
Description: \n
\t Generates sharpe ratio for given symbol and its peers.
'''

div_info = '''Dividend Yield: \n
\tURL: api/div_yied/?symbol=[TICKER] \n
\n
Parameters: \n
\tsymbol: Supported ticker from sigma7. All caps [REQUIRED] \n

'''

performance_info = '''Performance: \n
\tURL: api/performance/?symbol=[TICKER]&frame=[TIMEFRAME] \n
\n
Parameters: \n
\tsymbol: Supported ticker from sigma7. All caps [REQUIRED] \n
\tframe: Timeframe [ytd, 6m, 1y, 2y, 5y]
\n
Description: \n
\tCalculates total return for a particular stock and timeframe. \n
\tThis DOES account for dividends.
'''

ceo_pay_info = '''Insider: \n
\tURL: api/ceo_pay/?symbol=[TICKER] \n
\n
Parameters: \n
\tsymbol: Supported ticker from sigma7. All caps [REQUIRED] \n
\n
Description: \n
\tReturns the CEO Pay of a given stock, alongside its peer average and the CEO Pay of its peers.
'''

insider_info = '''Insider: \n
\tURL: api/insider?symbol=[TICKER] \n
\n
Parameters: \n
\tsymbol: Supported ticker from sigma7. All caps [REQUIRED] \n
\n
Description: \n
\tReturns transactions from company insiders.

'''
wrapper_info = ''' Wrapper Endpoint
\tURL: api/platform/func?param1=MSFT&param2=1y

Parameters: \n
\tplatform: Tell wrapper whether you want to wrap over an IEX function or sigma7 function. ["iex", "sigma7"]
\tfunc: What function to wrap over - see IEX/sigma7 docs for function names - THIS IS CASE SENSITIVE
\tparams: Unlike other endpoints, this one takes as many or as little parameters as necessary.\n
\t\t The name of the parameter should correspond with the parameters of the function you select. \n
\t\t Everything in this endpoint is case sensitive, make sure everything matches the docs.
'''

insiders_pie_info = ''' Insiders Pie: \n
\tURL: api/insiders_pie?symbol=[TICKER]
\n
Parameters: \n
\tsymbol: Supported ticker from sigma7. All caps [REQUIRED] \n
\tperiod: Period to pull insider data from - [3, 6, 12]
\n
Description: \n
\tReturns ratio of buys/sells from insiders over a given period
'''