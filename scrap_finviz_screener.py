#!/usr/bin/env python

import requests
import bs4
import lxml
import pandas as pd
import argparse
import urllib.parse as up
import datetime
import time
import sys

finviz_url = 'https://finviz.com/screener.ashx?v=111&f=cap_smallover'
output_file_prefix = 'finviz_'

def get_url(url):
    response = requests.get(url)
    if not response:
        print('Error', response.url, '-response code:', response.status_code)
    return response.text


def get_stock_table(page):
    print('getting page', page)
    page_url = finviz_url + '=&r=' + str((page - 1) * 20 + 1)
    page = get_url(page_url)
    soup = bs4.BeautifulSoup(page, 'lxml')
    stock_table = soup.find_all('table')[16]
    return pd.read_html(str(stock_table), header=0, index_col=1)[0]

def main():
    # get the front page
    front_page = get_url(finviz_url)

    # get the last page
    soup = bs4.BeautifulSoup(front_page, 'lxml')
    screener_pages = soup.find_all('a', {'class' : 'screener-pages'})
    last_page = int(screener_pages[-1].text)
    print('total pages:', last_page)

    df_pages = [] 
    today = str(datetime.date.today())

    for i in range(1,last_page+1):
        df_pages.append(get_stock_table(i))
    df_merged = pd.concat(df_pages)
    df_merged.drop(columns=['No.'])
    df_merged.insert(0, 'Date', today, True)

    # write to 
    filename = output_file_prefix + today + '.csv'
    df_merged.to_csv(filename)
    print('write', filename)

if __name__ == "__main__":
    sys.exit(main())

