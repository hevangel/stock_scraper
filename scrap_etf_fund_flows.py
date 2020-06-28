#!/usr/bin/env python
import requests
import bs4
import pandas as pd
from pandas.tseries.offsets import BDay
import argparse
from datetime import datetime, date, timedelta
import datetime
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
    try:
        page = post_url(page_url, data)
    except:
        print('Scrap failed, try again in 1 minute')
        time.sleep(60)
        page = post_url(page_url, data)

    df = get_df_from_page(page, drop_columns=['Fund Name','Details'])
    time.sleep(scrap_delay)
    return df

def get_etf_fundflow_all_tickers(tickers, start_date, end_date):
    tickers_per_page = 100
    tickers_list = [tickers[x:x + tickers_per_page] for x in range(0, len(tickers), tickers_per_page)]

    df_pages = []
    for page,tickers_page in enumerate(tickers_list):
        print('scraping page', page)
        tickers = ','.join(tickers_page)
        df_pages.append(get_etf_fundflow_page(tickers,start_date,end_date))

    df_merged = pd.concat(df_pages)
    return df_merged

def df_to_csv(df, output_prefix, start_date, end_date):
    if start_date == end_date:
        df.insert(0, 'Date', start_date, True)
        filename = output_prefix + start_date + '.csv'
    else:
        df.insert(0, 'Start Date', start_date, True)
        df.insert(0, 'End Date', end_date, True)
        filename = output_prefix + start_date + '_' + end_date + '.csv'
    df.to_csv(filename)

def main():
    parser = argparse.ArgumentParser(description='scrap finviz screener')
    parser.add_argument('-input', type=str, default='data_tickers/etfs_info.csv', help='list of ETFs to scrap')
    parser.add_argument('-output_prefix', type=str, default='data_etf_fundflow/etf_fundflow_', help='prefix of the output file')
    parser.add_argument('-date', type=str, help='Specify the date (default to last bussiness date)')
    parser.add_argument('-start_date', type=str, help='Specify the start date (default to date)')
    parser.add_argument('-end_date', type=str, help='Specify the end date (default to date)')
    parser.add_argument('-scrap_year', type=int, help='Scrap the fund flow of the specified year')
    parser.add_argument('-start_month', type=int, default=1, help='Start month for scrap year')
    parser.add_argument('-start_day', type=int, default=1, help='Start day for scrap year')
    args = parser.parse_args()

    df_etf_list = pd.read_csv(args.input)

    if args.scrap_year is None:
        if args.date is None:
            args.date = str((date.today() - BDay(1)).date())
        if args.start_date is None:
            args.start_date = args.date
        if args.end_date is None:
            args.end_date = args.date

        tickers = df_etf_list['Ticker'].to_list()
        df = get_etf_fundflow_all_tickers(tickers, args.start_date, args.end_date)
        df_to_csv(df, args.output_prefix, args.start_date, args.end_date)

    else:
        tickers = df_etf_list[pd.to_datetime(df_etf_list['Inception']) < datetime.datetime(args.scrap_year+1,1,1)]['Ticker'].to_list()
        print('numbers of ETF:', len(tickers))
        date_list = list([str(d.date()) for d in pd.bdate_range(datetime.datetime(args.scrap_year,args.start_month,args.start_day), datetime.datetime(args.scrap_year,12,31))])
        for d in date_list:
            print('date:', d)
            df = get_etf_fundflow_all_tickers(tickers, d, d)
            df_to_csv(df, args.output_prefix, d, d)

if __name__ == "__main__":
    sys.exit(main())

