#!/usr/bin/env python

import requests
import bs4
import pandas as pd
import argparse
import datetime
import time
import sys
import pprint

# -----------------------------------------------------------------
# hand crafted scrapper
# -----------------------------------------------------------------
etfdb_url = 'https://etfdb.com/etf/'
scrap_delay = 1

def get_url(url):
    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    if not response:
        print('Error', response.url, '-response code:', response.status_code)
        return None
    time.sleep(scrap_delay)
    return response.text

def get_etf_info(ticker):
    page_url = etfdb_url + ticker
    page = get_url(page_url)
    if page is None:
        return None
    soup = bs4.BeautifulSoup(page, 'lxml')
    row_dict = {}
    row_dict['Ticker'] = ticker
    row_dict['Description'] = soup.find_all('h1')[0].find_next('div').next_sibling.replace('\n','')
    h3 = soup.find_all('h3')
    for i in range(2):
        for li in h3[i].find_next('ul').find_all('li'):
            span_list = li.find_all('span')
            row_dict[span_list[0].text] = span_list[1].text.replace('\n','')
    return row_dict

def main():
    parser = argparse.ArgumentParser(description='scrap edfdb')
    parser.add_argument('-output', type=str, default='data_tickers/etf.csv', help='output file')
    args = parser.parse_args()

    row_dict_list = []
    df_all_tickers = pd.read_csv('data_tickers/all_tickers.csv')
    etf_list = df_all_tickers.query('Industry == "Exchange Traded Fund"')['Ticker'].tolist()
    print('ETFs:', len(etf_list))
    for ticker in etf_list:
        print('get_etf_info',ticker)
        row_dict = get_etf_info(ticker)
        if row_dict is not None:
            row_dict_list.append(row_dict)

    df = pd.DataFrame(row_dict_list)
    df.to_csv(args.output)

if __name__ == "__main__":
    sys.exit(main())

