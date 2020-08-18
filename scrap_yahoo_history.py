#!/usr/bin/env python

import pandas as pd
import argparse
import datetime
import sys
import yfinance as yf
import glob
import os
import time

scrap_delay = 2

def main():
    parser = argparse.ArgumentParser(description='scrap yahoo earning')
    parser.add_argument('-input_dir', type=str, help='input directory, use the latest file')
    parser.add_argument('-input_file', type=str, default='data_tickers/yahoo_indexes.csv', help='input file')
    parser.add_argument('-output_dir', type=str, default='../stock_data/raw_history_yahoo/', help='output directory')
    parser.add_argument('-skip', type=int, help='skip tickers')
    args = parser.parse_args()

    args.input_file = 'data_tickers/etfs_info.csv'
    args.skip = 2282

    if args.input_dir is not None:
        list_of_files = glob.glob(args.input_dir + '/*')
        input_file = max(list_of_files, key=os.path.getctime)
    else:
        input_file = args.input_file

    df_input = pd.read_csv(input_file)
    df_input.set_index('Ticker', inplace=True)
    ticker_list = df_input.index

    for count,ticker in enumerate(ticker_list):
        if args.skip is not None:
            if count < args.skip:
                continue
        print('downloading...' + ticker, '-', count)
        try:
            data = yf.download(ticker, period='max', auto_adjust=False, prepost=False)
        except:
            print('download failed, retry')
            time.sleep(30)
            data = yf.download(ticker, period='max', auto_adjust=False, prepost=False)

        try:
            yf_ticker = yf.Ticker(ticker)
        except:
            print('ticker get failed, retry')
            time.sleep(30)
            yf_ticker = yf.Ticker(ticker)

        try:
            dividends = yf_ticker.dividends
            splits = yf_ticker.splits
            if dividends is not None:
                data['Dividend'] = dividends
            if splits is not None:
                data['Split'] = splits
        except:
            print('dividend or split download failed')

        data.to_csv(args.output_dir + ticker + '.csv')

        time.sleep(scrap_delay)

if __name__ == "__main__":
    status = main()
    sys.exit(0 if status is None else status)
