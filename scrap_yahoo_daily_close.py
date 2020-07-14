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
    parser.add_argument('-input_file', type=str, action='append', help='input file')
    parser.add_argument('-output', type=str, help='output file')
    parser.add_argument('-output_prefix', type=str, default='../stock_data/raw_daily_yahoo/', help='prefix of the output file')
    parser.add_argument('-date', type=str, default=str(datetime.date.today()), help='Specify the date')
    args = parser.parse_args()

    if args.input_file == None:
        args.input_file = ['data_tickers/yahoo_indexes.csv', 'data_tickers/all_tickers.csv']

    if args.output is None:
        filename = args.output_prefix + args.date + '.csv'
    else:
        filename = args.output

    # run input files
    df_input_list = []
    for input_file in args.input_file:
        df_input_list.append(pd.read_csv(input_file))
    df_input = pd.concat(df_input_list)

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

            for col in df.columns:
                if col in yticker_info:
                    df.loc[ticker,col] = yticker_info[col]

        except:
            print('Error, skip')

        time.sleep(scrap_delay)

    df['Date'] = args.date
    df.to_csv(filename)

if __name__ == "__main__":
    sys.exit(main())

