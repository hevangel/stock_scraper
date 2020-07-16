#!/usr/bin/env python

import yahooquery as yq
import pandas as pd
import argparse
import datetime
import time
import sys
import glob
import os
from scrap_utils import *

scrap_delay = 1

def main():
    parser = argparse.ArgumentParser(description='scrap yahoo earning')
    parser.add_argument('-input_file', type=str, action='append', help='input file')
    parser.add_argument('-output', type=str, help='output file')
    parser.add_argument('-output_prefix', type=str, default='../stock_data/raw_daily_yahoo/yahoo_', help='prefix of the output file')
    parser.add_argument('-date', type=str, default=str(datetime.date.today()), help='Specify the date')
    args = parser.parse_args()

    if args.input_file == None:
        args.input_file = [
            'data_tickers/yahoo_indexes.csv',
            'data_tickers/all_tickers.csv',
            'data_tickers/etfs_info.csv'
        ]

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
    columns = {
        'price' : {
            'regularMarketOpen'             : 'Open',
            'regularMarketDayHigh'          : 'High',
            'regularMarketDayLow'           : 'Low',
            'regularMarketPrice'            : 'Close',
            'regularMarketVolume'           : 'Volume',
            'regularMarketChange'           : 'Change',
            'regularMarketChangePercent'    : 'ChangePercent',
            'quoteType'                     : 'Type',
        },
        'summary_detail' : {
            'marketCap'                     : 'MarketCap',
            'totalAssets'                   : 'TotalAssets',
            'navPrice'                      : 'NAV',
        },
        'key_stats' : {
            'floatShares'                   : 'SharesFloat',
            'sharesOutstanding'             : 'SharesOutstanding',
            'sharesShort'                   : 'SharesShort',
            'shortRatio'                    : 'SharesShortRatio',
            'shortPercentOfFloat'           : 'SharesShortPercentOfFloat',
            'heldPercentInsiders'           : 'SharesInsidersPercent',
            'heldPercentInstitutions'       : 'SharesInstitutionsPercent',
            'beta'                          : 'Beta'
        }
    }

    ticker_dict_list = []
    print('number of tickers:', len(ticker_list))
    for count,ticker in enumerate(ticker_list):
        print('downloading...', ticker, '-', count)
        try:
            yticker = yq.Ticker(ticker)
            ticker_dict = {}
            for module,module_dict in columns.items():
                for ycol, col in module_dict.items():
                    ymodule = getattr(yticker,module)
                    ticker_dict['Ticker'] = ticker
                    if ycol in ymodule[ticker]:
                        ticker_dict[col] = ymodule[ticker][ycol]
            ticker_dict_list.append(ticker_dict)
        except:
            print('Error, skip')

        time.sleep(scrap_delay)

    df = pd.DataFrame(ticker_dict_list)
    df['Date'] = args.date
    df.to_csv(filename)

if __name__ == "__main__":
    sys.exit(main())

