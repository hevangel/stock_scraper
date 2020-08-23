#!/usr/bin/env python

import pandas as pd
import numpy as np
import argparse
import datetime
import sys
import time
from scrap_utils import *
import os
import itertools

def main():
    parser = argparse.ArgumentParser(description='clean up ETF history')
    parser.add_argument('-input', type=str, default='data_tickers/etfs_info.csv', help='input file')
    parser.add_argument('-output_dir', type=str, default='../stock_data/data_etf/', help='output directory')
    parser.add_argument('-skip', type=int, help='skip tickers')
    args = parser.parse_args()

    df_input = pd.read_csv(args.input, comment='#')
    df_input.set_index('Ticker', inplace=True)
    ticker_list = df_input.index

    source_list = {
        'Yahoo': 'raw_history_yahoo',
        'Macrotrends': 'raw_history_macrotrends',
        'AlphaVantage': 'raw_history_alpha_vantage'
    }

    for count,ticker in enumerate(ticker_list):
        if args.skip is not None:
            if count < args.skip:
                continue
        print('=== cleaning...',ticker,'-',count,'===')

        df_raw = {}
        for k,v in source_list.items():
            csv_file = f"../stock_data/{v}/{ticker}.csv"
            if os.path.exists(csv_file):
                df_raw[k] = pd.read_csv(f"../stock_data/{v}/{ticker}.csv", index_col=0, parse_dates=True)
            else:
                print('file not found:', csv_file)

        # Create the final DataFrame
        fields = ['Open', 'High', 'Low', 'Close', 'AdjOpen', 'AdjHigh', 'AdjLow', 'AdjClose', 'Volume', 'Dividend', 'Split', 'SplitFactor']
        sources = ['Data'] + list(df_raw.keys())
        columns = pd.MultiIndex.from_product([sources, fields], names=['Source','Fields'])

        df_raw_dates = []
        for source in df_raw:
            df_raw_dates.append(set(df_raw[source].index.to_list()))
        clean_dates = sorted(set.union(*df_raw_dates))[:-2]
        df = pd.DataFrame(index=clean_dates, columns=columns)
        df.index.name = 'Date'

        if 'Yahoo' in df_raw:
            df_raw['Yahoo'].drop(columns = ['Adj Close'], inplace=True)
            df_raw['Yahoo'].rename(columns={
                'Open' : 'AdjOpen',
                'High' : 'AdjHigh',
                'Low' : 'AdjLow',
                'Close': 'AdjClose',
            }, inplace=True)
            df_raw['Yahoo']['Split'].fillna(1.0, inplace=True)
            df_raw['Yahoo']['SplitFactor'] = df_raw['Yahoo']['Split'][::-1].cumprod().shift(1, fill_value=1.0)
            df_raw['Yahoo']['Open'] = df_raw['Yahoo']['AdjOpen'] * df_raw['Yahoo']['SplitFactor']
            df_raw['Yahoo']['High'] = df_raw['Yahoo']['AdjHigh'] * df_raw['Yahoo']['SplitFactor']
            df_raw['Yahoo']['Low'] = df_raw['Yahoo']['AdjLow'] * df_raw['Yahoo']['SplitFactor']
            df_raw['Yahoo']['Close'] = df_raw['Yahoo']['AdjClose'] * df_raw['Yahoo']['SplitFactor']
            df_raw['Yahoo']['Dividend'].fillna(0.0, inplace=True)

        if 'AlphaVantage' in df_raw:
            #df_raw['AlphaVantage'].drop(columns = ['adjusted_close'], inplace=True)
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
            df_raw['AlphaVantage']['SplitFactor'] = df_raw['AlphaVantage']['Split'].cumprod().shift(1, fill_value=1.0)
            df_raw['AlphaVantage']['AdjOpen'] = df_raw['AlphaVantage']['Open'] / df_raw['AlphaVantage']['SplitFactor']
            df_raw['AlphaVantage']['AdjHigh'] = df_raw['AlphaVantage']['High'] / df_raw['AlphaVantage']['SplitFactor']
            df_raw['AlphaVantage']['AdjLow'] = df_raw['AlphaVantage']['Low'] / df_raw['AlphaVantage']['SplitFactor']
            df_raw['AlphaVantage']['AdjClose'] = df_raw['AlphaVantage']['Close'] / df_raw['AlphaVantage']['SplitFactor']

        if 'Macrotrends' in df_raw:
            df_raw['Macrotrends']['SplitFactor'] = df_raw['Macrotrends']['Close'] / df_raw['Macrotrends']['AdjClose']
            df_raw['Macrotrends']['Split'] = df_raw['Macrotrends']['SplitFactor'].shift(1) / df_raw['Macrotrends']['SplitFactor']
            df_raw['Macrotrends']['Split'].fillna(1.0, inplace=True)
            df_raw['Macrotrends']['Dividend'] = np.nan
            df_raw['Macrotrends']['Open'] = df_raw['Macrotrends']['AdjOpen'] * df_raw['Macrotrends']['SplitFactor']
            df_raw['Macrotrends']['High'] = df_raw['Macrotrends']['AdjHigh'] * df_raw['Macrotrends']['SplitFactor']
            df_raw['Macrotrends']['Low'] = df_raw['Macrotrends']['AdjLow'] * df_raw['Macrotrends']['SplitFactor']

        # Copy raw to final DataFrame
        for field in fields:
            for source in df_raw.keys():
                df[(source, field)] = df_raw[source][field]

        # Merge and clean up raw data
        print('Merging Split')
        df_split_mode = df[itertools.product(df_raw.keys(),['Split'])].round(4).mode(axis=1)
        if len(df_split_mode.columns) > 2:
            print('Split - no majority:\n', df_split_mode[df_split_mode[2].notna()])
        df[('Data','Split')] = df_split_mode[0]
        df[('Data','SplitFactor')] = df[('Data','Split')][::-1].cumprod().shift(1, fill_value=1.0)

        # Fix the missing split
        for source in df_raw.keys():
            df_split_diff = (~ np.isclose(df[('Data', 'Split')],df[(source, 'Split')])) & df[(source, 'Split')].notna()
            if df_split_diff.any():
                print('Fixing split error for', source)
                if source == 'Macrotrends':
                    for field in ['Open', 'High', 'Low', 'Close']:
                        df[('Macrotrends','Adj'+field)] = df[('Macrotrends',field)] / df[('Data','SplitFactor')]

        # Merge columns
        for field in ['Open', 'High', 'Low', 'Close', 'AdjOpen', 'AdjHigh', 'AdjLow', 'AdjClose', 'Volume', 'Dividend']:
            print('Merging ', field)
            df_mode = df[itertools.product(df_raw.keys(),[field])].round(2).mode(axis=1)
            if len(df_mode.columns) > 2:
                print('No majority:\n', df_mode[df_mode[1].notna()])
                df_mode[df_mode[1].notna()][0] = df_mode[df_mode[1].notna()].median(axis=1)
            df[('Data', field)] = df_mode[0]

        # Output CSV files
        df_out = df['Data'].copy()
        df_ff = pd.read_csv('../stock_data/temp/' + ticker + '.csv', index_col=1, names=['File','Date','FundFlow'], parse_dates=True)
        df_ff = df_ff[~df_ff.index.duplicated()]
        df_out['FundFlow'] = df_ff[:df.index[-1]]['FundFlow']
        df_out.to_csv(args.output_dir + ticker + '.csv')

if __name__ == "__main__":
    status = main()
    sys.exit(0 if status is None else status)
