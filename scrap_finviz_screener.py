#!/usr/bin/env python

import requests
import bs4
import pandas as pd
import argparse
import datetime
import time
import sys
from io import StringIO
from finviz.screener import Screener
from junit_xml import TestSuite, TestCase

# -----------------------------------------------------------------
# hand crafted scrapper
# -----------------------------------------------------------------
finviz_url = 'https://finviz.com/screener.ashx?'
scrap_delay = 1

def get_url(url):
    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    if not response:
        print('Error', response.url, '-response code:', response.status_code)
    return response.text

def get_stock_table(tab,filter,page):
    page_url = finviz_url + tab + filter + '&r=' + str((page - 1) * 20 + 1)
    print('getting page', page, 'url:', page_url)
    page = get_url(page_url)
    soup = bs4.BeautifulSoup(page, 'lxml')
    stock_table = soup.find_all('table')[16]
    return pd.read_html(str(stock_table), header=0, index_col=1)[0]

def scrap_finviz(filter, tab_list = None):
    # get the front page
    front_page = get_url(finviz_url + filter)

    # get the last page
    soup = bs4.BeautifulSoup(front_page, 'lxml')
    screener_pages = soup.find_all('a', {'class' : 'screener-pages'})
    last_page = int(screener_pages[-1].text)
    print('total pages:', last_page)

    if tab_list is None:
        tab_list = ['v=111&', 'v=121&', 'v=131&', 'v=141&', 'v=161&', 'v=171&',]
    df_pages = []
    for i in range(1,last_page+1):
        df_tabs = []
        for tab in tab_list:
            time.sleep(scrap_delay)
            df_tabs.append(get_stock_table(tab,filter,i))
        df_pages.append(pd.concat(df_tabs, axis=1))
    df_merged = pd.concat(df_pages)

    return df_merged

def main():
    parser = argparse.ArgumentParser(description='scrap finviz screener')
    parser.add_argument('-output', type=str, help='output file')
    parser.add_argument('-output_prefix', type=str, default='data_finviz/finviz_', help='prefix of the output file')
    parser.add_argument('-use_bs4_scrapper', type=bool, default=True, help='Use my old bs4 scraper')
    parser.add_argument('-no_scrap', action='store_true', help='No scrapping, read existing csv file')
    parser.add_argument('-no_report', action='store_true', help='Do not generate XML report')
    parser.add_argument('-date', type=str, default=str(datetime.date.today()), help='Specify the date')
    parser.add_argument('-report', type=str, default='daily_report.xml', help='file name of the test report')
    parser.add_argument('-filter', type=str, action='append', help='filters apply to the screener')
    parser.add_argument('-tab', type=str, action='append', help='tabs to the scrap')
    parser.add_argument('-delay', type=int, help='delay in sec between each URL request')
    parser.add_argument('-drop_col', type=str, action='append', default=[], help='remove columns')
    args = parser.parse_args()

    if args.filter is None:
        args.filter = ['f=cap_microover', 'f=cap_microunder,sh_opt_option']
    if args.delay is not None:
        global scrap_delay
        scrap_delay = args.delay

    # check is the market closed today
    with open('market_close_dates.txt', 'r') as reader:
        market_close_dates = reader.read().splitlines()
    if args.date in market_close_dates:
        print('The market is closed today')
        return

    if args.output is None:
        filename = args.output_prefix + args.date + '.csv'
    else:
        filename = args.output

    # scrap the data
    if not args.no_scrap:
        if args.use_bs4_scrapper:
            # use my old code
            df_filters = []
            for filter in args.filter:
                df_filters.append(scrap_finviz(filter, args.tab))
            df = pd.concat(df_filters)
        else:
            # use the finviz package
            stock_list = Screener(filters=args.filter)
            df = pd.read_csv(StringIO(stock_list.to_csv()))

        df = df.loc[:, ~df.columns.duplicated()]
        df.drop_duplicates(subset='Ticker',inplace=True)
        df.drop(columns=['No.']+args.drop_col, inplace=True)
        df.insert(0, 'Date', args.date, True)
        df.to_csv(filename)

    # generate report
    if not args.no_report:
        df = pd.read_csv(filename)
        df.drop_duplicates(subset='Ticker',inplace=True)
        df.set_index('Ticker', inplace=True)
        ts_list = []
        for sector in df.Sector.unique():
            ts = TestSuite(name=sector)
            df_sector = df[df['Sector'] == sector]
            for industry in df_sector.Industry.unique():
                for ticker in df.index[df['Industry'] == industry]:
                    print(sector,'-',industry,'-',ticker)
                    if df.loc[ticker,'Market Cap'].find('B') > 0:
                        tc = TestCase(classname=industry,
                                      name=ticker,
                                      elapsed_sec=df.loc[ticker,'Price'],
                                      stdout=df.loc[ticker,'Change'],
                                      stderr=df.loc[ticker,'Market Cap'])
                        if df.loc[ticker,'Change'].find('-') >= 0:
                            tc.add_error_info(message='lower')
                        ts.test_cases.append(tc)
            ts_list.append(ts)

        with open(args.report, 'w') as f:
            TestSuite.to_file(f, ts_list, prettyprint=True)

if __name__ == "__main__":
    sys.exit(main())

