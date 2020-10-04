#!/usr/bin/env python

import requests
import cloudscraper
import pandas as pd
import bs4
from pandas.tseries.offsets import BDay
import datetime
import selenium
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium import webdriver
import time

use_cloudscrapper = False
use_firefox = False
use_firefox_headless = False
scrapper = None
selenium_driver = None

# Use request or cloudscrapper
def get_scrapper():
    if not use_cloudscrapper:
        return requests
    else:
        global scrapper
        if scrapper is None:
            scrapper = cloudscraper.create_scraper(browser='firefox')
        return scrapper

# Get selenium driver
def get_driver(implicitly_wait = 10):
    global selenium_driver
    if selenium_driver is None:
        if use_firefox:
            options = FirefoxOptions()
            if use_firefox_headless:
                options.add_argument("--headless")
            selenium_driver = webdriver.Firefox(options=options)
        else:
            selenium_driver = webdriver.PhantomJS()
        selenium_driver.implicitly_wait(implicitly_wait)
    return selenium_driver

# Click link
def click_link(link_text):
    try:
        link = get_driver().find_element_by_link_text(link_text)
        link.click()
    except selenium.common.exceptions.NoSuchElementException:
        pass

# Click class name
def click_class_name(class_name):
    try:
        class_name = get_driver().find_element_by_class_name(class_name)
        class_name.click()
    except selenium.common.exceptions.NoSuchElementException:
        pass

# Click xpath
def click_xpath(xpath):
    try:
        xpath = get_driver().find_element_by_xpath(xpath)
        xpath.click()
    except selenium.common.exceptions.NoSuchElementException:
        pass


# Get session from Selenium
def get_session():
    session = requests.Session()
    cookies = get_driver().get_cookies()
    for cookie in cookies:
        session.cookies.set(cookie['name'], cookie['value'])
    return session

# HTTP get request
def get_url(url):
    response = get_scrapper().get(url, headers={'User-Agent': 'Mozilla/5.0'})
    if response.status_code != requests.codes.ok:
        print('Error', response.url, '- response code:', response.status_code)
        return None
    return response.text

# HTTP post request
def post_url(url,data):
    response = get_scrapper().post(url, data=data, headers={'User-Agent': 'Mozilla/5.0'})
    if response.status_code != requests.codes.ok:
        print('Error', response.url, '- response code:', response.status_code)
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

# Row dict to Datafrom to CSV
def row_dict_to_csv(row_dict_list, csv, index_column='Ticker'):
    df = pd.DataFrame(row_dict_list)
    df.set_index(index_column, inplace=True)
    df.to_csv(csv)

# Write DataFrame to CSV
def df_to_csv(df, output_prefix, start_date, end_date=None):
    if start_date == end_date or end_date is None:
        df.insert(0, 'Date', start_date, True)
        filename = output_prefix + start_date + '.csv'
    else:
        df.insert(0, 'Start Date', start_date, True)
        df.insert(0, 'End Date', end_date, True)
        filename = output_prefix + start_date + '_' + end_date + '.csv'
    df.to_csv(filename)

# get the next weekday from a date
def onDay(date, day):
    """
    :param date: current date
    :param day: next monday(0) - sunday(6)
    :return:
    """
    return date + datetime.timedelta(days=(day-date.weekday()+7)%7)
