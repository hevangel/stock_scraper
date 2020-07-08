#!/usr/bin/env python

import yfinance as yf
import pandas as pd
import argparse
import datetime
import time
import sys
import glob
import os

scrap_delay = 5

def main():
    parser = argparse.ArgumentParser(description='scrap yahoo earning')
    parser.add_argument('-input_dir', type=str, help='input directory, use the latest file')
    parser.add_argument('-input_file', type=str, default='data_tickers/etfs_info.csv', help='input file')
    parser.add_argument('-output', type=str, help='output file')
    parser.add_argument('-output_prefix', type=str, default='data_yahoo_daily_close/yahoo_etf', help='prefix of the output file')
    parser.add_argument('-date', type=str, default=str(datetime.date.today()), help='Specify the date')
    args = parser.parse_args()

    if args.input_dir is not None:
        list_of_files = glob.glob(args.input_dir + '/*')
        input_file = max(list_of_files, key=os.path.getctime)
    else:
        input_file = args.input_file

    if args.output is None:
        filename = args.output_prefix + args.date + '.csv'
    else:
        filename = args.output

    df_input = pd.read_csv(input_file)
    ticker_list = df_input['Ticker'].to_list()

    columns = ['previousClose',
               'open',
               'dayHigh',
               'dayLow',
               'regularMarketPreviousClose',
               'regularMarketPrice',
               'regularMarketOpen',
               'regularMarketDayHigh',
               'regularMarketDayLow',
               'marketCap',
               'volume',
               'navPrice',
               'totalAssets',
               'sharesOutstanding',
               'sharesShort',
               'floatShares',
               'shortRatio',
               'shortPercentOfFloat',
               'fiftyDayAverage',
               'twoHundredDayAverage',
               ]
    df = pd.DataFrame(columns=columns)

    print('number of tickers:', len(ticker_list))
    for count,ticker in enumerate(ticker_list):
        print('downloading...', ticker, count)
        try:
            yticker = yf.Ticker(ticker)
            yticker_info = yticker.info
        except:
            print('Error, skip')
            exit(-1)

        for col in df.columns:
            if col in yticker_info:
                df.loc[ticker,col] = yticker_info[col]

        if count % 10 == 0:
            df['Date'] = args.date
            df.to_csv(filename)

        time.sleep(scrap_delay)

    df['Date'] = args.date
    df.to_csv(filename)

if __name__ == "__main__":
    sys.exit(main())

