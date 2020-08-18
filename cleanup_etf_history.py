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

    ticker_list = ['SPY','QQQ','USO','GDX']

    for count,ticker in enumerate(ticker_list):
        print('cleaning...',ticker,'-',count)
        df_raw = {}
        df_raw['Yahoo'] = pd.read_csv('../stock_data/raw_history_yahoo/' + ticker + '.csv', index_col=0, parse_dates=True)
        df_raw['Macrotrends'] = pd.read_csv('../stock_data/raw_history_macrotrends/' + ticker + '.csv', index_col=0, parse_dates=True)
        df_raw['AlphaVantage'] = pd.read_csv('../stock_data/raw_history_alpha_vantage/daily_adjusted_' + ticker + '.csv', index_col=0, parse_dates=True)

        df_raw['Yahoo'].drop(columns = ['Adj Close'], inplace=True)
        df_raw['Yahoo'].rename(columns={
            'Open' : 'AdjOpen',
            'High' : 'AdjHigh',
            'Low' : 'AdjLow',
            'Close': 'AdjClose',
        }, inplace=True)

        df_raw['AlphaVantage'].drop(columns = ['adjusted_close'], inplace=True)
        df_raw['AlphaVantage'].rename(columns={
            'timestamp' : 'Date',
            'open' : 'Open',
            'high' : 'High',
            'low' : 'Low',
            'close' : 'Close',
            'volume' : 'Volume',
            'dividend_amount' : 'Dividend',
            'split_coefficient' : 'Split',
        }, inplace=True)

        fields = ['Open', 'High', 'Low', 'Close', 'AdjOpen', 'AdjHigh', 'AdjLow', 'AdjClose', 'Volume', 'Dividend', 'Split', 'SplitFactor']
        columns = pd.MultiIndex.from_product([['Data','Yahoo','Macrotrends','AlphaVantage'], fields], names=['Source','Fields'])
        date_y = set(df_raw['Yahoo'].index.to_list())
        date_m = set(df_raw['Macrotrends'].index.to_list())
        date_a = set(df_raw['AlphaVantage'].index.to_list())
        date_clean = sorted(date_y | date_a | date_m)
        df = pd.DataFrame(index=date_clean, columns=columns)
        df.index.name = 'Date'

        # Fix split factor
        df_raw['Macrotrends']['SplitFactor'] = df_raw['Macrotrends']['Close'] / df_raw['Macrotrends']['AdjClose']
        df_raw['Macrotrends']['Split'] = df_raw['Macrotrends']['SplitFactor'].shift(1) / df_raw['Macrotrends']['SplitFactor']
        df_raw['Macrotrends']['Split'].fillna(1.0, inplace=True)
        df_raw['Yahoo']['Split'].fillna(1.0, inplace=True)

        for source in df_raw.keys():
            df[(source, 'Split')] = df_raw[source]['Split']
        df[('Data','Split')] = df[[('Macrotrends','Split'),('AlphaVantage','Split'),('Yahoo','Split')]].mode(axis=1)[0]
        df[('Data','SplitFactor')] = df[('Data','Split')][::-1].cumprod().shift(1, fill_value=1.0)

        # Clean up raw data
        df_raw['Macrotrends']['Dividend'] = 0.0
        for field in ['AdjOpen','AdjHigh','AdjLow','AdjClose']:
            df_raw['Macrotrends'][field].where(df_raw['Macrotrends']['SplitFactor'] == df[('Data','SplitFactor')], df_raw['Macrotrends'][field] / df[('Data','SplitFactor')], inplace=True)
        df_raw['Macrotrends']['Open'] = df_raw['Macrotrends']['AdjOpen'] * df[('Data','SplitFactor')]
        df_raw['Macrotrends']['High'] = df_raw['Macrotrends']['AdjHigh'] * df[('Data','SplitFactor')]
        df_raw['Macrotrends']['Low'] = df_raw['Macrotrends']['AdjLow'] * df[('Data','SplitFactor')]

        df_raw['AlphaVantage']['AdjOpen'] = df_raw['AlphaVantage']['Open'] / df[('Data','SplitFactor')]
        df_raw['AlphaVantage']['AdjHigh'] = df_raw['AlphaVantage']['High'] / df[('Data','SplitFactor')]
        df_raw['AlphaVantage']['AdjLow'] = df_raw['AlphaVantage']['Low'] / df[('Data','SplitFactor')]
        df_raw['AlphaVantage']['AdjClose'] = df_raw['AlphaVantage']['Close'] / df[('Data','SplitFactor')]

        df_raw['Yahoo']['Dividend'].fillna(0.0, inplace=True)
        df_raw['Yahoo']['Open'] = df_raw['Yahoo']['AdjOpen'] * df[('Data','SplitFactor')]
        df_raw['Yahoo']['High'] = df_raw['Yahoo']['AdjHigh'] * df[('Data','SplitFactor')]
        df_raw['Yahoo']['Low'] = df_raw['Yahoo']['AdjLow'] * df[('Data','SplitFactor')]
        df_raw['Yahoo']['Close'] = df_raw['Yahoo']['AdjClose'] * df[('Data','SplitFactor')]

        # Copy and merge columns
        for field in ['Open', 'High', 'Low', 'Close', 'AdjOpen', 'AdjHigh', 'AdjLow', 'AdjClose', 'Volume', 'Dividend']:
            print('  Merging ', field)
            merge_columns = []
            for source in df_raw.keys():
                df[(source,field)] = df_raw[source][field]
                merge_columns.append((source,field))
            df_mode = df[merge_columns].round(2).mode(axis=1)
            df[('Data', field)] = df_mode[0]
            if len(df_mode.columns) > 2:
                print(df_mode[df_mode[2].notna()])

        # Output CSV files
        df_out = df['Data'].copy()
        df_ff = pd.read_csv('../stock_data/temp/' + ticker + '.csv', index_col=1, names=['File','Date','FundFlow'], parse_dates=True)
        df_out['FundFlow'] = df_ff[:df.index[-1]]['FundFlow']
        df_out.to_csv(args.output_dir + ticker + '.csv')

if __name__ == "__main__":
    status = main()
    sys.exit(0 if status is None else status)
