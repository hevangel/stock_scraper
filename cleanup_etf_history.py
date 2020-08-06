#!/usr/bin/env python

import pandas as pd
import argparse
import datetime
import sys
import time
from scrap_utils import *
import os

def main():
    parser = argparse.ArgumentParser(description='clean up ETF history')
    parser.add_argument('-input', type=str, default='data_tickers/etfs_info.csv', help='input file')
    parser.add_argument('-output_dir', type=str, default='../stock_data/data_etf/', help='output directory')
    args = parser.parse_args()

    df_input = pd.read_csv(args.input, comment='#')
    df_input.set_index('Ticker', inplace=True)
    ticker_list = df_input.index

    for count,ticker in enumerate(ticker_list):
        print('cleaning...',ticker,'-',count)
        df_y = pd.read_csv('../stock_data/raw_history_yahoo/' + ticker + '.csv', index_col=0, parse_dates=True)
        df_m = pd.read_csv('../stock_data/raw_history_macrotrends/' + ticker + '.csv', index_col=0, parse_dates=True)
        df_a = pd.read_csv('../stock_data/raw_history_alpha_vantage/daily_adjusted_' + ticker + '.csv', index_col=0, parse_dates=True)

        date_y = set(df_y.index.to_list())
        date_m = set(df_m.index.to_list())
        date_a = set(df_a.index.to_list())
        date_clean = sorted(date_y | date_a | date_m)
        df = pd.DataFrame(index=date_clean)

        df_m['Open'] = df_m['AdjOpen'] / df_m['AdjClose'] * df_m['Close']
        df_m['High'] = df_m['AdjHigh'] / df_m['AdjClose'] * df_m['Close']
        df_m['Low'] = df_m['AdjLow'] / df_m['AdjClose'] * df_m['Close']

        # Merge columns
        df['yClose'] = df_y['Close'].round(2)
        df['mClose'] = df_m['Close'].round(2)
        df['aClose'] = df_a['close'].round(2)
        df['ymCloseDiff'] = df['yClose'] == df['mClose']
        df['yaCloseDiff'] = df['yClose'] == df['aClose']
        df['Close'] = df['mClose'].where(df['ymCloseDiff'],df['aClose'].where(df['yaCloseDiff'],df['yClose']))

        df['yOpen'] = df_y['Open'].round(2)
        df['mOpen'] = df_m['Open'].round(2)
        df['aOpen'] = df_a['open'].round(2)
        df['ymOpenDiff'] = df['yOpen'] == df['mOpen']
        df['yaOpenDiff'] = df['yOpen'] == df['aOpen']
        df['Open'] = df['mOpen'].where(df['ymOpenDiff'],df['aOpen'].where(df['yaOpenDiff'],df['yOpen']))

        df['yHigh'] = df_y['High'].round(2)
        df['mHigh'] = df_m['High'].round(2)
        df['aHigh'] = df_a['high'].round(2)
        df['ymHighDiff'] = df['yHigh'] == df['mHigh']
        df['yaHighDiff'] = df['yHigh'] == df['aHigh']
        df['High'] = df['mHigh'].where(df['ymHighDiff'],df['aHigh'].where(df['yaHighDiff'],df['yHigh']))

        df['yLow'] = df_y['Low'].round(2)
        df['mLow'] = df_m['Low'].round(2)
        df['aLow'] = df_a['low'].round(2)
        df['ymLowDiff'] = df['yLow'] == df['mLow']
        df['yaLowDiff'] = df['yLow'] == df['aLow']
        df['Low'] = df['mLow'].where(df['ymLowDiff'],df['aLow'].where(df['yaLowDiff'],df['yLow']))

        df['Volume'] = df_y['Volume']
        df['Dividend'] = df_a['dividend_amount']
        df['Dividend'].bfill(inplace=True)
        df['Split'] = df_a['split_coefficient']
        df['Split'].bfill(inplace=True)

        df_ff = pd.read_csv('../stock_data/temp/' + ticker + '.csv', index_col=1, names=['File','Date','FundFlow'], parse_dates=True)
        df['FundFlow'] = df_ff['FundFlow']

        df_out = df[:df_y.index[-1]][['Open', 'High', 'Low', 'Close', 'Volume', 'Dividend', 'Split', 'FundFlow']]
        df_out.to_csv(args.output_dir + ticker + '.csv')

if __name__ == "__main__":
    status = main()
    sys.exit(0 if status is None else status)
