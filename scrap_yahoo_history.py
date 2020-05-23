#!/usr/bin/env python

import pandas as pd
import argparse
import datetime
import sys
import yfinance as yf

def main():
    parser = argparse.ArgumentParser(description='scrap yahoo earning')
    parser.add_argument('-input', type=str, default='data_tickers/yahoo_indexes.csv', help='input file')
    parser.add_argument('-output_dir', type=str, default='data_yahoo_history/', help='output directory')
    args = parser.parse_args()

    df_input = pd.read_csv(args.input)
    df_input.set_index('Ticker', inplace=True)
    df_output = pd.DataFrame()

    for ticker in df_input.index:
        print('downloading...' + ticker)
        data = yf.download(ticker, period='max', auto_adjust=True, prepost=True)
        data.to_csv(args.output_dir + ticker + '.csv')

if __name__ == "__main__":
    sys.exit(main())

