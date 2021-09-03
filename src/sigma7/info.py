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