import wget
import time
import numpy as np
import pandas as pd
from alpha_vantage.timeseries import TimeSeries
import matplotlib.pyplot as plt

# Read Alpha Vantage API key
f = open('key.txt', 'r')
key = f.read()
f.close()

# Get S&P500 list from Wiki
data = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
cur_symbols = data[0]['Symbol']
added_symbols = data[1][('Added','Ticker')]
removed_symbols = data[1][('Removed', 'Ticker')]
symbols = set()
symbols.update(cur_symbols.to_list())
symbols.update(added_symbols.to_list())
symbols.update(removed_symbols.to_list())
symbols.discard(np.nan)

for i, symbol in enumerate(sorted(symbols)):
    url= 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol='+symbol+'&apikey='+key+'&outputsize=full&datatype=csv'
    print(symbol)
    filename = wget.download(url)

