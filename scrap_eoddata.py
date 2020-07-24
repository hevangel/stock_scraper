import sys
import time
import argparse
import pandas as pd
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import requests
import bs4
import datetime
from scrap_utils import *

def main():
    parser = argparse.ArgumentParser(description='scrap all etf')
    parser.add_argument('-use_firefox', action='store_true', help='Use firefox instead of phantomjs')
    parser.add_argument('-use_headless', action='store_true', help='Use headless mode in Firefox')
    parser.add_argument('-username', type=str, help='Username')
    parser.add_argument('-password', type=str, help='Password')
    parser.add_argument('-delay', type=int, default=1, help='delay in sec between each URL request')
    parser.add_argument('-date', type=str, help='Specify the date to download')
    parser.add_argument('-output_prefix', type=str, default='../stock_data/raw_daily_eoddata/eoddata_', help='prefix of the output file')
    args = parser.parse_args()

    if args.date is None:
        scrap_date = datetime.date.today()
    else:
        scrap_date = datetime.datetime.strptime(args.date, '%Y-%m-%d')

    if args.use_firefox:
        options = FirefoxOptions()
        if args.use_headless:
            options.add_argument("--headless")
        driver = webdriver.Firefox(options=options)
    else:
        driver = webdriver.PhantomJS()
    driver.implicitly_wait(10)
    wait = WebDriverWait(driver, 10)
    driver.get('http://www.eoddata.com')

    # login
    username_textbox = driver.find_element_by_id('ctl00_cph1_lg1_txtEmail')
    password_textbox = driver.find_element_by_id('ctl00_cph1_lg1_txtPassword')
    login_button = driver.find_element_by_id('ctl00_cph1_lg1_btnLogin')
    username_textbox.send_keys(args.username)
    password_textbox.send_keys(args.password)
    login_button.click()

    # download CSV
    driver.get('http://www.eoddata.com/download.aspx')
    exchange_list = ['INDEX', 'AMEX', 'NYSE', 'NASDAQ', 'OTCBB']
    for exchange in
    exchange_select = Select(driver.find_element_by_id('ctl00_cph1_d1_cboExchange'))
    exchange_select.select_by_value('INDEX')
    download_link = driver.find_element_by_link_text('Jul 22 2020')
    download_url = download_link.get_attribute('href')
    session = requests.Session()
    cookies = driver.get_cookies()
    for cookie in cookies:
        session.cookies.set(cookie['name'], cookie['value'])
    response = session.get(download_url)
    with open('a.csv', 'wb') as f:
        f.write(response.content)

if __name__ == "__main__":
    status = main()
    sys.exit(0 if status is None else status)
