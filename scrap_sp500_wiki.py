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
