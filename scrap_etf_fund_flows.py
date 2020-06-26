#!/usr/bin/env python
import requests
import bs4
import pandas as pd
from pandas.tseries.offsets import BDay
import argparse
from datetime import datetime, date, timedelta
import time
import sys
import scrap_utils
from scrap_utils import *
scrap_utils.use_cloudscrapper = True

# -----------------------------------------------------------------
# hand crafted scrapper
# -----------------------------------------------------------------
eftfundflow_url = 'https://www.etf.com/etfanalytics/etf-fund-flows-tool'
scrap_delay = 5

def get_etf_fundflow_page(tickers,start_date,end_date):
    page_url = eftfundflow_url
    data = {'tickers' : tickers,
            'startDate[date]' : start_date,
            'endDate[date]' : end_date}
    page = post_url(page_url, data)
    df = get_df_from_page(page, drop_columns=['Details'])
    time.sleep(scrap_delay)
    return df

def get_etf_fundflow_all_tickers(tickers, start_date, end_date):
    tickers_per_page = 100
    tickers_list = [tickers[x:x + tickers_per_page] for x in range(0, len(tickers), tickers_per_page)]

    df_pages = []
    for page,tickers_page in enumerate(tickers_list):
        if page > 2:
            break
        print('scraping page', page)
        tickers = ','.join(tickers_page)
        df_pages.append(get_etf_fundflow_page(tickers,start_date,end_date))

    df_merged = pd.concat(df_pages)

    return df_merged

def main():
    parser = argparse.ArgumentParser(description='scrap finviz screener')
    parser.add_argument('-input', type=str, default='data_tickers/etfs_info.csv', help='list of ETFs to scrap')
    parser.add_argument('-output_prefix', type=str, default='data_etf_fundflow/etf_fund_flow_', help='prefix of the output file')
    parser.add_argument('-date', type=str, help='Specify the date')
    parser.add_argument('-start_date', type=str, help='Specify the start date')
    parser.add_argument('-end_date', type=str, help='Specify the end date')
    args = parser.parse_args()

    if args.date is None:
        args.date = str((date.today() - BDay(1)).date())
    if args.start_date is None:
        args.start_date = args.date
    if args.end_date is None:
        args.end_date = args.date

    df_etf_list = pd.read_csv(args.input)
    tickers = df_etf_list['Ticker'].to_list()
    df = get_etf_fundflow_all_tickers(tickers, args.start_date, args.end_date)

    if args.start_date == args.end_date:
        df.insert(0, 'Date', args.date, True)
        filename = args.output_prefix + args.start_date + '.csv'
    else:
        df.insert(0, 'Start Date', args.start_date, True)
        df.insert(0, 'End Date', args.end_date, True)
        filename = args.output_prefix + args.start_date + '_' + args.end_date + '.csv'

    df.to_csv(filename)

if __name__ == "__main__":
    sys.exit(main())

