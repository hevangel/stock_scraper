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
    parser.add_argument('-skip', type=int, help='skip tickers')
    args = parser.parse_args()

    args.input_file = 'data_tickers/etfs_info.csv'
    args.skip = 361

    df_input = pd.read_csv(args.input_file)
    df_input.set_index('Ticker', inplace=True)

    for count,ticker in enumerate(df_input.index):
        if args.skip is not None:
            if count < args.skip:
                continue
        print('downloading...' + ticker, '-', count)
        filename = args.output_dir + ticker + '.csv'

        # scrap price history
        price_url ='https://www.macrotrends.net/assets/php/stock_price_history.php?t=' + ticker
        price_page = get_url(price_url)
        price_soup = bs4.BeautifulSoup(price_page, 'lxml')
        price_scripts = price_soup.find_all('script')[8]
        price_pattern = re.search('dataDaily = \[{(.*)}\];', str(price_scripts))
        price_history = []
        for price_row in price_pattern.group(1).split('},{'):
            tokens = price_row.split('","')
            price_history_row = []
            for token in tokens:
                price_history_row.append(token.split(':"')[1].replace('"',''))
            price_history.append(price_history_row)
        columns = ['Date', 'AdjOpen', 'AdjHigh', 'AdjLow', 'AdjClose', 'Volume', 'MA50', 'MA200']
        df = pd.DataFrame(price_history, columns=columns[:len(tokens)])
        df.set_index('Date', inplace=True)

        # scrap split history
        split_url ='https://www.macrotrends.net/assets/php/stock_splits.php?t=' + ticker
        split_page = get_url(split_url)
        split_soup = bs4.BeautifulSoup(split_page, 'lxml')
        split_scripts = split_soup.find_all('script')[4]
        split_pattern = re.search('dataDaily = \[{(.*)}\];', str(split_scripts))
        split_history = []
        for split_row in split_pattern.group(1).split('},{'):
            tokens = split_row.split('","')
            split_history_row = []
            for token in tokens:
                split_history_row.append(token.split(':"')[1].replace('"',''))
            split_history.append(split_history_row)
        df_split = pd.DataFrame(split_history, columns=['Date', 'Close'])
        df_split.set_index('Date', inplace=True)
        df['Close'] = df_split['Close']

        # download CSV, 200 limits per month
        #price_url = 'http://download.macrotrends.net/assets/php/stock_data_export.php?t=' + ticker
        #price_csv = get_url(price_url)
        #df = pd.read_csv(io.StringIO(price_csv), header=9, index_col=0)

        # scrap market cap history
        mktcap_url ='https://www.macrotrends.net/assets/php/market_cap.php?t=' + ticker
        mktcap_page = get_url(mktcap_url)
        mktcap_soup = bs4.BeautifulSoup(mktcap_page, 'lxml')
        mktcap_scripts = mktcap_soup.find_all('script')[13]
        mktcap_pattern = re.search('chartData = \[{(.*)}\];', str(mktcap_scripts))
        if mktcap_pattern is not None:
            mktcap_history = []
            for mktcap_row in mktcap_pattern.group(1).split('},{'):
                tokens = mktcap_row.split('","')
                mktcap_history.append([tokens[0].split(':"')[1], tokens[1].split(':')[1]])
            df_mktcap = pd.DataFrame(mktcap_history, columns=['Date','MarketCap'])
            df_mktcap.set_index('Date',inplace=True)
            df['MarketCap'] = df_mktcap['MarketCap']

        df.to_csv(filename)

        time.sleep(scrap_delay)


if __name__ == "__main__":
    status = main()
    sys.exit(0 if status is None else status)
