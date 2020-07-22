#!/usr/bin/env python

import requests
import bs4
import pandas as pd
import argparse
import datetime
import sys
import glob
import os
import time
import re
import io
from scrap_utils import *

scrap_delay = 2

def main():
    parser = argparse.ArgumentParser(description='scrap history from macrotrends')
    parser.add_argument('-input_file', type=str, default='data_tickers/all_tickers.csv', help='input file')
    parser.add_argument('-output_dir', type=str, default='../stock_data/raw_history_macrotrends/', help='output directory')
    parser.add_argument('-no_marketcap', action='store_true', help='scrap market cap history')
    args = parser.parse_args()

    df_input = pd.read_csv(args.input_file)
    df_input.set_index('Ticker', inplace=True)

    for count,ticker in enumerate(df_input.index):
        print('downloading...' + ticker)
        filename = args.output_dir + ticker + '.csv'

        price_url = 'http://download.macrotrends.net/assets/php/stock_data_export.php?t=' + ticker
        price_csv = get_url(price_url)
        df = pd.read_csv(io.StringIO(price_csv), header=9, index_col=0)

        # scrap market cap history
        if not bool(args.no_marketcap):
            mktcap_url ='https://www.macrotrends.net/assets/php/market_cap.php?t=' + ticker
            mktcap_page = get_url(mktcap_url)
            mktcap_soup = bs4.BeautifulSoup(mktcap_page, 'lxml')
            mktcap_scripts = mktcap_soup.find_all('script')[13]
            mktcap_pattern = re.search('chartData = \[{(.*)}\];', str(mktcap_scripts))
            mktcap_history = []
            for mktcap_row in mktcap_pattern.group(1).split('},{'):
                tokens = mktcap_row.split('","')
                mktcap_history.append([tokens[0].split(':"')[1], tokens[1].split(':')[1]])
            df_mktcap = pd.DataFrame(mktcap_history, columns=['Date','MarketCap'])
            df_mktcap.set_index('Date',inplace=True)
            df['MarketCap']  = df_mktcap['MarketCap']

        df.to_csv(filename)

        time.sleep(scrap_delay)


if __name__ == "__main__":
    status = main()
    sys.exit(0 if status is None else status)
