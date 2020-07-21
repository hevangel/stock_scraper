#!/usr/bin/env python

import pandas as pd
import argparse
import datetime
import sys
import glob
import os
import time
import requests

scrap_delay = 2

def main():
    parser = argparse.ArgumentParser(description='scrap history from macrotrends')
    parser.add_argument('-input_file', type=str, default='data_tickers/yahoo_indexes.csv', help='input file')
    parser.add_argument('-output_dir', type=str, default='../stock_data/raw_history_macrotrends/', help='output directory')
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
        url = 'http://download.macrotrends.net/assets/php/stock_data_export.php?t=' + ticker
        filename = args.output_dir + ticker + '.csv'
        response = requests.get(url)
        with open(filename) as f:
            f.write(response.content)
        time.sleep(scrap_delay)

if __name__ == "__main__":
    status = main()
    sys.exit(0 if status is None else status)
