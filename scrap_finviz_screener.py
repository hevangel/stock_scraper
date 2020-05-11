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
finviz_url = 'https://finviz.com/screener.ashx?v=111&f=cap_smallover'
def get_url(url):
    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    if not response:
        print('Error', response.url, '-response code:', response.status_code)
    return response.text

def get_stock_table(page):
    page_url = finviz_url + '&r=' + str((page - 1) * 20 + 1)
    print('getting page', page, 'url:', page_url)
    page = get_url(page_url)
    soup = bs4.BeautifulSoup(page, 'lxml')
    stock_table = soup.find_all('table')[16]
    return pd.read_html(str(stock_table), header=0, index_col=1)[0]

def scrap_finviz():
    # get the front page
    front_page = get_url(finviz_url)

    # get the last page
    soup = bs4.BeautifulSoup(front_page, 'lxml')
    screener_pages = soup.find_all('a', {'class' : 'screener-pages'})
    last_page = int(screener_pages[-1].text)
    print('total pages:', last_page)

    df_pages = []
    for i in range(1,last_page+1):
        time.sleep(1)
        df_pages.append(get_stock_table(i))
    df_merged = pd.concat(df_pages)

    return df_merged

def main():
    parser = argparse.ArgumentParser(description='scrap finviz screener')
    parser.add_argument('-output_prefix', type=str, default='data_finviz/finviz_', help='prefix of the output file')
    parser.add_argument('-use_bs4_scrapper', type=bool, default=True, help='Use my old bs4 scraper')
    parser.add_argument('-no_scrap', action='store_true', help='No scrapping, read existing csv file')
    parser.add_argument('-date', type=str, default=str(datetime.date.today()), help='Specify the date')
    parser.add_argument('-report', type=str, default='daily_report.xml', help='file name of the test report')
    args = parser.parse_args()
    args.no_scrap = True
    args.date = '2020-05-04'

    # check is the market closed today
    with open('market_close_dates.txt', 'r') as reader:
        market_close_dates = reader.read().splitlines()
    if args.date in market_close_dates:
        print('The market is closed today')
        return

    filename = args.output_prefix + args.date + '.csv'

    # scrap the data
    if not args.no_scrap:
        if args.use_bs4_scrapper:
            # use my old code
            df = scrap_finviz()
        else:
            # use the finviz package
            stock_list = Screener(filters=['cap_smallover'])
            df = pd.read_csv(StringIO(stock_list.to_csv()))

        df.drop(columns=['No.'], inplace=True)
        df.insert(0, 'Date', args.date, True)
        df.to_csv(filename)

    # generate report
    df = pd.read_csv(filename)
    ts_list = []
    df.set_index('Ticker', inplace=True)
    for sector in df.Sector.unique():
        ts = TestSuite(name=sector)
        df_sector = df[df['Sector'] == sector]
        for industry in df_sector.Industry.unique():
            for ticker in df.index[df['Industry'] == industry]:
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

    # pretty printing is on by default but can be disabled using prettyprint=False
    #print(TestSuite.to_xml_string(ts_list))

    with open(args.report, 'w') as f:
        TestSuite.to_file(f, ts_list, prettyprint=True)

if __name__ == "__main__":
    sys.exit(main())

