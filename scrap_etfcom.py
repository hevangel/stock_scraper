#!/usr/bin/env python

import requests
import bs4
import pandas as pd
import argparse
import datetime
import time
import sys

# -----------------------------------------------------------------
# hand crafted scrapper
# -----------------------------------------------------------------
eftfundflow_url = 'https://www.etf.com/etfanalytics/etf-fund-flows-tool'
scrap_delay = 1

def post_url(url,data):
    response = requests.post(url, data=data, headers={'User-Agent': 'Mozilla/5.0'})


    if not response:
        print('Error', response.url, '-response code:', response.status_code)
    return response.text

def get_etf_table(state_date,end_date):
    page_url = eftfundflow_url
    data = {'startDate[date]' : '2015-01-01', 'endDate[date]' : '2015-12-31'}

    page = post_url(page_url, data)
    soup = bs4.BeautifulSoup(page, 'lxml')

    etf_table = soup.find_all('table')
    df = pd.concat(pd.read_html(str(etf_table), header=0, index_col=1))
    df.drop(columns=['Details'], inplace=True)
    return df

def scrap_finviz(filter):
    # get the front page
    front_page = get_url(finviz_url + filter)

    # get the last page
    soup = bs4.BeautifulSoup(front_page, 'lxml')
    screener_pages = soup.find_all('a', {'class' : 'screener-pages'})
    last_page = int(screener_pages[-1].text)
    print('total pages:', last_page)

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
    parser.add_argument('-output_prefix', type=str, default='data_finviz/finviz_', help='prefix of the output file')
    parser.add_argument('-no_scrap', action='store_true', help='No scrapping, read existing csv file')
    parser.add_argument('-date', type=str, default=str(datetime.date.today()), help='Specify the date')
    parser.add_argument('-report', type=str, default='daily_report.xml', help='file name of the test report')
    parser.add_argument('-filter', type=str, action='append', help='filters apply to the screener')
    args = parser.parse_args()

    page = get_url(eftfundflow_url)
    soup = bs4.BeautifulSoup(page, 'lxml')

    if args.filter is None:
        args.filter = ['f=cap_microover', 'f=cap_microunder,sh_opt_option']

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
            df_filters = []
            for filter in args.filter:
                df_filters.append(scrap_finviz(filter))
            df = pd.concat(df_filters)
        else:
            # use the finviz package
            stock_list = Screener(filters=args.filter)
            df = pd.read_csv(StringIO(stock_list.to_csv()))

        df.drop(columns=['No.'], inplace=True)
        df.insert(0, 'Date', args.date, True)
        df.to_csv(filename)


if __name__ == "__main__":
    sys.exit(main())

