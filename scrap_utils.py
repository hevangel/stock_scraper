#!/usr/bin/env python

import requests
import cloudscraper
import pandas as pd
import bs4
from pandas.tseries.offsets import BDay

use_cloudscrapper = False
scrapper = None

# Use request or cloudscrapper
def get_scrapper():
    if not use_cloudscrapper:
        return requests
    else:
        global scrapper
        if scrapper is None:
            scrapper = cloudscraper.create_scraper(browser='firefox')
        return scrapper

# HTTP get request
def get_url(url):
    response = get_scrapper().get(url, headers={'User-Agent': 'Mozilla/5.0'})
    if not response:
        print('Error', response.url, '-response code:', response.status_code)
        return None
    return response.text

# HTTP post request
def post_url(url,data):
    response = get_scrapper().post(url, data=data, headers={'User-Agent': 'Mozilla/5.0'})
    if not response:
        print('Error', response.url, '-response code:', response.status_code)
        return None
    return response.text

# get dataframe from table in page
def get_df_from_page(page, table_index=0, header=0, index_col=0, drop_columns=None):
    soup = bs4.BeautifulSoup(page, 'lxml')
    table = soup.find_all('table')[table_index]
    df = pd.concat(pd.read_html(str(table), header=header, index_col=index_col))
    if drop_columns is not None:
        df.drop(columns=drop_columns, inplace=True)
    return df

# check is the market closed today
def is_market_close(date):
    with open('market_close_dates.txt', 'r') as reader:
        market_close_dates = reader.read().splitlines()
    if date in market_close_dates:
        return True
    else:
        return False

# Get previous market day
def get_prev_market_date(date):
    prev_date = (date.today() - BDay(1)).date()
    if is_market_close(str(prev_date)):
        prev_date = (prev_date - BDay(1)).date()
    return prev_date

# Write DataFrame to CSV
def df_to_csv(df, output_prefix, start_date, end_date):
    if start_date == end_date:
        df.insert(0, 'Date', start_date, True)
        filename = output_prefix + start_date + '.csv'
    else:
        df.insert(0, 'Start Date', start_date, True)
        df.insert(0, 'End Date', end_date, True)
        filename = output_prefix + start_date + '_' + end_date + '.csv'
    df.to_csv(filename)
