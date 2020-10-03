#!/usr/bin/env python

import sys
import wget
import argparse
import pandas as pd
import time

scrap_delay = 2

def main():
    parser = argparse.ArgumentParser(description='scrap alpha vantage history')
    parser.add_argument('-api_key_file', type=str, default='../hevangel-com/api_keys/alpha_vantage.txt', help='API key file')
    parser.add_argument('-input_file', type=str, action='append', help='input file')
    parser.add_argument('-output_dir', type=str, default='../stock_data/raw_history_alpha_vantage/', help='output directory')
    parser.add_argument('-function', type=str, default='TIME_SERIES_DAILY_ADJUSTED', help='API function')
    parser.add_argument('-skip', type=int, help='skip tickers')
    args = parser.parse_args()

    args.output_dir = '../stock_data_local/raw_intraday_alpha_vantage/'
    args.function = 'TIME_SERIES_INTRADAY&interval=1min'
    if args.input_file == None:
        args.input_file = [
            #'data_tickers/all_etfs.csv'
            'data_tickers/all_stocks.csv',
        ]

    # Read Alpha Vantage API key
    api_key_list = []
    with open(args.api_key_file, 'r') as f:
        for line in f:
            api_key_list.append(f.readline().rstrip('\n'))

    # Read input tickets list
    df_input_list = []
    for input_file in args.input_file:
        df_input_list.append(pd.read_csv(input_file))
    df_input = pd.concat(df_input_list, sort=False)
    ticker_list = df_input['Ticker'].to_list()

    for count,ticker in enumerate(ticker_list):
        if args.skip is not None:
            if count < args.skip:
                continue
        print('downloading...', ticker, '-', count)
        api_key = api_key_list[count % len(api_key_list)]
        url = 'https://www.alphavantage.co/query?function='+args.function+'&symbol='+ticker+'&apikey='+api_key+'&outputsize=full&datatype=csv'

        wget_ok = False
        max_retry = 3
        for retry in range(max_retry):
            try:
                wget.download(url, out=args.output_dir, bar=False)
                wget_ok = True
            except:
                print('download failed, retry: ', retry)
                time.sleep((retry+1) * 60)
            if wget_ok == True:
                break

        time.sleep(scrap_delay)

if __name__ == "__main__":
    status = main()
    sys.exit(0 if status is None else status)
