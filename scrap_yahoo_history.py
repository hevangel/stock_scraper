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

    if args.input_dir is not None:
        list_of_files = glob.glob(args.input_dir + '/*')
        input_file = max(list_of_files, key=os.path.getctime)
    else:
        input_file = args.input_file

    df_input = pd.read_csv(input_file)
    df_input.set_index('Ticker', inplace=True)

    for count,ticker in enumerate(df_input.index):
        if args.skip is not None:
            if count < args.skip:
                continue
        print('downloading...' + ticker, '-', count)
        try:
            data = yf.download(ticker, period='max', auto_adjust=False, prepost=True)
        except:
            print('download failed, retry')
            time.sleep(30)
            data = yf.download(ticker, period='max', auto_adjust=False, prepost=True)

        data.to_csv(args.output_dir + ticker + '.csv')

if __name__ == "__main__":
    status = main()
    sys.exit(0 if status is None else status)
