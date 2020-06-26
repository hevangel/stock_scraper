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
import requests
import bs4
from scrap_utils import *

# -----------------------------------------------------------------
# hand crafted scrapper
# -----------------------------------------------------------------
etfdb_url = 'https://etfdb.com/etf/'
scrap_delay = 5

def get_etf_info(ticker):
    page_url = etfdb_url + ticker
    page = get_url(page_url)
    time.sleep(scrap_delay)
    if page is None:
        return None
    soup = bs4.BeautifulSoup(page, 'lxml')
    row_dict = {}
    row_dict['Ticker'] = ticker
    row_dict['Description'] = soup.find_all('h1')[0].find_next('div').next_sibling.replace('\n','')
    h3 = soup.find_all('h3')
    for i in range(3):
        for li in h3[i].find_next('ul').find_all('li'):
            span_list = li.find_all('span')
            row_dict[span_list[0].text] = span_list[1].text.replace('\n','')
    return row_dict


def main():
    parser = argparse.ArgumentParser(description='scrap all etf')
    parser.add_argument('-use_firefox', action='store_true', help='Use firefox instead of phantomjs')
    parser.add_argument('-use_headless', action='store_true', help='Use headless mode in Firefox')
    parser.add_argument('-delay', type=int, default=1, help='delay in sec between each URL request')
    parser.add_argument('-output_etfcom', type=str, default='data_tickers/etfs_etfcom.csv', help='etf.com etf list')
    parser.add_argument('-output_etfdb', type=str, default='data_tickers/etfs_etfdb.csv', help='etfdb etf list')
    parser.add_argument('-no_scrap_etf_list', action='store_true', help='no scrap etf list from etf.com and etfdb')
    parser.add_argument('-output', type=str, default='data_tickers/etfs_info.csv', help='etf info output file')
    args = parser.parse_args()
    args.no_scrap_etf_list = True

    if not args.no_scrap_etf_list:
        if args.use_firefox:
            options = FirefoxOptions()
            if args.use_headless:
                options.add_argument("--headless")
            driver = webdriver.Firefox(options=options)
        else:
            driver = webdriver.PhantomJS()
        driver.implicitly_wait(10)
        wait = WebDriverWait(driver, 10)

        # scrap ETF list from etf.com
        df_pages = []
        driver.get('https://www.etf.com/etfanalytics/etf-finder')
        wait.until(EC.presence_of_all_elements_located((By.ID, 'inactiveResult')))
        wait.until(EC.element_to_be_clickable((By.ID, 'inactiveResult')))
        button_100 = driver.find_elements_by_id('inactiveResult')[-1]
        button_100.location_once_scrolled_into_view
        wait.until(EC.visibility_of(button_100))
        time.sleep(5)
        button_100.click()
        while True:
            print('scrap page', driver.find_element_by_id('goToPage').get_attribute('value'))
            driver.find_element_by_id('finderTable')
            df_pages.append(pd.read_html(driver.find_element_by_id('finderTable').get_attribute('outerHTML'), header=0, index_col=0)[0])
            if len(driver.find_elements_by_class_name('nextPageInactive')) > 0:
                break
            button_nextpage = driver.find_element_by_id('nextPage')
            button_nextpage.location_once_scrolled_into_view
            wait.until(EC.visibility_of(button_nextpage))
            button_nextpage.click()
            time.sleep(args.delay)
        df_etfcom = pd.concat(df_pages)
        df_etfcom.to_csv(args.output_etfcom)

        # Scrap ETF list from etfdb
        df_pages = []
        driver.get('https://etfdb.com/screener')
        while True:
            print('scrap page', driver.find_element_by_css_selector("li[class='active page-number']").text)
            thead = driver.find_element_by_tag_name('thead')
            tbody = driver.find_element_by_tag_name('tbody')
            table = '<table>' + thead.get_attribute('outerHTML') + tbody.get_attribute('outerHTML') + '</table>'
            df_pages.append(pd.read_html(table, header=0, index_col=0)[0])
            df_pages[-1].drop(columns=['ETFdb Pro'], inplace=True)
            df_pages[-1].rename(index={'Symbol': 'Ticker'}, inplace=True)
            if driver.find_element_by_class_name('page-next').get_attribute('class').split()[0] == 'disabled':
                break
            driver.find_element_by_class_name('page-next').find_element_by_tag_name('a').click()
            time.sleep(args.delay)

        df_etfdb = pd.concat(df_pages)
        df_etfdb.to_csv(args.output_etfdb)

        driver.close()
    else:
        df_etfcom = pd.read_csv(args.output_etfcom)
        df_etfcom.set_index('Ticker', inplace=True)
        df_etfdb = pd.read_csv(args.output_etfdb)
        df_etfdb.set_index('Ticker', inplace=True)

    etfcom_list = set(df_etfcom.index.to_list())
    etfdb_list = set(df_etfdb.index.to_list())
    common_etf_list = etfcom_list & etfdb_list

    df = pd.read_csv(args.output)

    row_dict_list = []
    for i,ticker in enumerate(sorted(common_etf_list)):
        if i < 2081:
            continue
        print('get_etf_info',i,ticker)
        row_dict = get_etf_info(ticker)
        if row_dict is not None:
            row_dict_list.append(row_dict)
        if i % 10 == 0:
            df2 = pd.DataFrame(row_dict_list)
            df = df.append(df2)
            df.to_csv(args.output)
            row_dict_list = []

    df2 = pd.DataFrame(row_dict_list)
    df = df.append(df2)
    df.set_index('Ticker', inplace=True)
    df.to_csv(args.output)

if __name__ == "__main__":
    sys.exit(main())
