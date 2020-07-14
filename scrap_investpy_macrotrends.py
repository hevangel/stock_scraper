#!/usr/bin/env python

import pandas as pd
import argparse
import datetime
import sys
import investpy
import glob
import os

scrap_delay = 5

4

http: // download.macrotrends.net / assets / php / stock_data_export.php?t = [SYMBOL NAME]

# Eg give csv file back
http: // download.macrotrends.net / assets / php / stock_data_export.php?t = MSFT

def main():
    parser = argparse.ArgumentParser(description='scrap yahoo earning')
    parser.add_argument('-input_dir', type=str, help='input directory, use the latest file')
    parser.add_argument('-input_file', type=str, default='data_tickers/yahoo_indexes.csv', help='input file')
    parser.add_argument('-output_dir', type=str, default='data_yahoo_history/', help='output directory')
    args = parser.parse_args()

    if args.input_dir is not None:
        list_of_files = glob.glob(args.input_dir + '/*')
        input_file = max(list_of_files, key=os.path.getctime)
    else:
        input_file = args.input_file

    df_input = pd.read_csv(input_file)
    df_input.set_index('Ticker', inplace=True)

    for count,ticker in enumerate(df_input.index):
        print('downloading...' + ticker)
        data = yf.download(ticker, period='max', auto_adjust=True, prepost=True)
        data.to_csv(args.output_dir + ticker + '.csv')

if __name__ == "__main__":
    sys.exit(main())

