#!/usr/bin/env python

import sys
import time
import argparse
import pandas as pd
import selenium
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
import requests
import bs4
import scrap_utils
from scrap_utils import *

# -----------------------------------------------------------------
# hand crafted scrapper
# -----------------------------------------------------------------
result_url = 'https://finra-markets.morningstar.com/BondCenter/Results.jsp'
bond_search_url = 'https://finra-markets.morningstar.com/bondSearch.jsp'
scrap_delay = 10


def main():
    parser = argparse.ArgumentParser(description='scrap bond yield from finra')
    parser.add_argument('-use_firefox', action='store_true', help='Use firefox instead of phantomjs')
    parser.add_argument('-use_headless', action='store_true', help='Use headless mode in Firefox')
    parser.add_argument('-output_prefix', type=str, default='../stock_data/raw_bonds_finra/bonds_', help='prefix of the output file')
    parser.add_argument('-today', action='store_true', help='Trade Date = today')
    parser.add_argument('-price', type=int, default=70, help='zero to the price range ')
    args = parser.parse_args()

    args.use_firefox = True
    args.today = True

    # initialize web driver
    scrap_utils.use_firefox = args.use_firefox
    scrap_utils.use_firefox_headless = args.use_headless
    driver = get_driver()
    driver_wait = WebDriverWait(get_driver(), 10)

    # bypass agreement page
    front_page = driver.get(result_url)
    click_class_name('agree')

    # enter search filter
    click_link('EDIT SEARCH')
    click_class_name('hide')
    Select(driver.find_element_by_name('subProductType')).select_by_value('1')
    trade_parameters_element = driver.find_element_by_id('firscreener-tradeParameters')
    if args.today:
        trade_date_elements = trade_parameters_element.find_elements_by_name('tradeDate')
        trade_date_elements[0].click()
        driver.find_element_by_class_name('today').click()
        trade_date_elements[1].click()
        driver.find_element_by_class_name('today').click()
    trade_price_elements = trade_parameters_element.find_elements_by_name('tradePrice')
    trade_price_elements[0].send_keys('0')
    trade_price_elements[1].send_keys(str(args.price))
    click_xpath("//input[@value='SHOW RESULTS']")

    time.sleep(1)
    total_element = driver.find_element_by_class_name('qs-pageutil-total')
    total_page = int(total_element.text.split()[1])
    print('total pages:', total_page)

    # scrap the data table
    columns = []
    row_data = []
    while True:
        page_num = driver.find_element_by_class_name('qs-pageutil-input').get_attribute('value')
        print('page',page_num)

        page_source = get_driver().page_source
        soup = bs4.BeautifulSoup(page_source, 'lxml')
        soup.find('input', class_='qs-pageutil-input')
        resultdata = soup.find('div', class_='qs-resultData-body')

        # get column headers
        if page_num == '1':
            gridhd = resultdata.find('div', class_='rtq-grid-hd')
            columns = [cell.text for cell in gridhd.find_all('div', class_='rtq-grid-cell-ctn')[1:]]

        gridbd = resultdata.find('div', class_='rtq-grid-bd')
        gridrows = gridbd.find_all('div', class_='rtq-grid-row')
        for row in gridrows:
            row_data.append([cell.text for cell in row.find_all('div', class_='rtq-grid-cell-ctn')[1:]])

        next_link = soup.find('a', text='Next')
        if 'qs-pageutil-disable' in next_link.get('class'):
            break
        driver.find_element_by_link_text('Next').click()

    df = pd.DataFrame(row_data, columns=columns)
    csv_filename = args.output_prefix + str(datetime.date.today()) + '.csv'
    df.to_csv(csv_filename)

    get_driver().quit()

if __name__ == "__main__":
    status = main()
    sys.exit(0 if status is None else status)

