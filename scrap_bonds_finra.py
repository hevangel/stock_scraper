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

def get_bonds_table(page):
    page_url = bonds_url + '&p=' + str(page)
    print('getting page', page)
    page = get_url(page_url)
    soup = bs4.BeautifulSoup(page, 'lxml')
    bond_table = soup.find('table')
    return pd.read_html(str(bond_table), header=0, index_col=1)[0]

def main():
    parser = argparse.ArgumentParser(description='scrap bond yield from finra')
    parser.add_argument('-output_prefix', type=str, default='../stock_data/raw_bonds_finra/bonds_', help='prefix of the output file')
    parser.add_argument('-date', type=str, default=str(datetime.date.today()), help='Specify the date')
    parser.add_argument('-output', type=str, help='output file')
    args = parser.parse_args()

    args.use_firefox = True

    scrap_utils.use_firefox = args.use_firefox
    scrap_utils.use_firefox_headless = args.use_headless

    # bypass agreement page
    driver = get_driver()
    driver_wait = WebDriverWait(get_driver(), 10)

    front_page = driver.get(result_url)
    click_class_name('agree')
    click_link('EDIT SEARCH')
    click_class_name('hide')
    Select(driver.find_element_by_name('subProductType')).select_by_value('1')
    click_xpath("//input[@value='SHOW RESULTS']")
    total_page = int(driver.find_element_by_class_name('qs-pageutil-total').text.split()[1])


    # Get number of pages
    session = get_session()
    response = session.post(result_url,{'showResultsAs':'B','subProductType':'1'})
    soup = bs4.BeautifulSoup(response.text, 'lxml')



    # get the number of search result
    soup = bs4.BeautifulSoup(front_page, 'lxml')
    search_results = soup.find(id='bond-searchresults-container').find('h2')
    results = int(re.sub(' Results.*\t', '', re.sub('\r\n.*\(', '', search_results.text)).replace(',', ''))

    print('results:', results)

    filename = args.output_prefix + args.date + '.csv'

    df_pages = []
    for page in range(1,math.ceil(results/20)+1):
        df_pages.append(get_bonds_table(page))
        time.sleep(scrap_delay)
    df = pd.concat(df_pages)
    df.to_csv(filename)

if __name__ == "__main__":
    status = main()
    sys.exit(0 if status is None else status)

