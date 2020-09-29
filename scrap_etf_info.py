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
from selenium.webdriver.support import expected_conditions as EC
import requests
import bs4
import scrap_utils
from scrap_utils import *

# -----------------------------------------------------------------
# hand crafted scrapper
# -----------------------------------------------------------------
etfdb_url = 'https://etfdb.com/etf/'
etfcom_url = 'https://www.etf.com/'

def etfcom_click_understand_button():
    try:
        understand_button = get_driver().find_element_by_link_text('I Understand')
        understand_button.click()
    except selenium.common.exceptions.NoSuchElementException:
        pass

def get_etfcom_info(ticker, output_etfcom_holdings = None):
    page_url = etfcom_url + ticker
    get_driver().get(page_url)
    etfcom_click_understand_button()
    try:
        viewall = get_driver().find_element_by_class_name('viewAll')
        get_driver().maximize_window()
        viewall.click()
        time.sleep(0.5)
    except:
        pass
    page = get_driver().page_source
    soup = bs4.BeautifulSoup(page, 'lxml')
    row_dict = {}
    row_dict['Ticker'] = ticker
    h1 = soup.find('h1')
    if h1 is None:
        return row_dict
    row_dict['Description'] = h1.find_next('span').text
    for id in ['fundSummaryData','fundPortfolioData','fundIndexData']:
        id_tag = soup.find(id=id)
        if id_tag is None:
            continue
        div_list = id_tag.find_all('div', class_='rowText')
        for div in div_list:
            label = div.find('label')
            if label is not None:
                row_dict[label.text.replace('\n','')] = label.find_next_sibling().text.replace('\n','')
    if bool(output_etfcom_holdings):
        cbox = soup.find(id='cboxOverlay')
        holdings_table = cbox.find_next('table')
        if bool(holdings_table):
            df_holdings = pd.read_html(str(holdings_table))[0]
            df_holdings.columns = ['Name','Allocation']
            df_holdings.to_csv(output_etfcom_holdings + ticker + '.csv')
    return row_dict

def get_etfdb_info(ticker, output_etfdb_fundflow = None):
    page_url = etfdb_url + ticker
    get_driver().get(page_url)
    page = get_driver().page_source
    soup = bs4.BeautifulSoup(page, 'lxml')
    row_dict = {}
    row_dict['Ticker'] = ticker
    h1 = soup.find_all('h1')
    if h1 is None:
        return None
    div_description = h1[0].find_next('div')
    if div_description is None:
        return None
    row_dict['Description'] = div_description.next_sibling.replace('\n','')
    ul_list = soup.find_all('ul', class_='list-unstyled')
    for i in range(4):
        for li in ul_list[i].find_all('li'):
            span_list = li.find_all('span')
            row_dict[span_list[0].text] = span_list[1].text.replace('\n','')

    # extract fund flow history
    if bool(output_etfdb_fundflow):
        fundflow_data = soup.find(id = 'fund-flow-chart-container').attrs['data-series'].replace('[[','').replace(']]','')
        fundflow_history = []
        for fundflow_row in fundflow_data.split('], ['):
            tokens = fundflow_row.split(',')
            fundflow_history.append([datetime.datetime.fromtimestamp(int(tokens[0])/1000).date(),tokens[1]])
        df_fundflow = pd.DataFrame(fundflow_history, columns=['Date','Fundflow'])
        df_fundflow.set_index('Date',inplace=True)
        df_fundflow.to_csv(output_etfdb_fundflow + ticker + '.csv')

    return row_dict

def main():
    parser = argparse.ArgumentParser(description='scrap all etf')
    parser.add_argument('-use_firefox', action='store_true', help='Use firefox instead of phantomjs')
    parser.add_argument('-use_headless', action='store_true', help='Use headless mode in Firefox')
    parser.add_argument('-delay', type=int, default=2, help='delay in sec between each URL request')
    parser.add_argument('-no_scrap_etf_list', action='store_true', help='no scrap etf list from etf.com and etfdb')
    parser.add_argument('-no_scrap_etfdb_info', action='store_true', help='no scrap etf info from etfdb')
    parser.add_argument('-no_scrap_etfcom_info', action='store_true', help='no scrap etf info from etf.com')
    parser.add_argument('-output_etfcom', type=str, default='data_tickers/etfs_etfcom.csv', help='etf.com etf list output file')
    parser.add_argument('-output_etfdb', type=str, default='data_tickers/etfs_etfdb.csv', help='etfdb etf list output file')
    parser.add_argument('-output_all_etfs', type=str, default='data_tickers/all_etfs.csv', help='all etfs list output file')
    parser.add_argument('-output_etfdb_info', type=str, default='data_tickers/etfdb_info.csv', help='etfdb info output file')
    parser.add_argument('-output_etfdb_fundflow', type=str, default='../stock_data/raw_etfdb_fundflow/', help='output directory for eftdb fundflow')
    parser.add_argument('-output_etfcom_info', type=str, default='data_tickers/etfcom_info.csv', help='etf.com info output file')
    parser.add_argument('-output_etfcom_holdings', type=str, default='../stock_data/raw_etfcom_holdings/', help='output directory for eft.com holdings')
    parser.add_argument('-skip', type=int, help='skip tickers')
    args = parser.parse_args()

    scrap_utils.use_firefox = args.use_firefox
    scrap_utils.use_firefox_headless = args.use_headless

    if not args.no_scrap_etf_list:
        driver = get_driver()
        driver_wait = WebDriverWait(get_driver(), 10)

        # scrap ETF list from etf.com
        df_pages = []
        driver.get('https://www.etf.com/etfanalytics/etf-finder')
        etfcom_click_understand_button()
        #time.sleep(5)
        driver_wait.until(EC.presence_of_all_elements_located((By.ID, 'inactiveResult')))
        driver_wait.until(EC.element_to_be_clickable((By.ID, 'inactiveResult')))
        button_100 = driver.find_elements_by_id('inactiveResult')[-1]
        button_100.location_once_scrolled_into_view
        driver_wait.until(EC.visibility_of(button_100))
        time.sleep(5)
        button_100.click()
        time.sleep(1)
        while True:
            print('scrap etf.com page', driver.find_element_by_id('goToPage').get_attribute('value'))
            driver.find_element_by_id('finderTable')
            df_pages.append(pd.read_html(driver.find_element_by_id('finderTable').get_attribute('outerHTML'), header=0, index_col=0)[0])
            if len(driver.find_elements_by_class_name('nextPageInactive')) > 0:
                break
            button_nextpage = driver.find_element_by_id('nextPage')
            button_nextpage.location_once_scrolled_into_view
            driver_wait.until(EC.visibility_of(button_nextpage))
            button_nextpage.click()
            time.sleep(args.delay)
        df_etfcom = pd.concat(df_pages)
        df_etfcom.to_csv(args.output_etfcom)

        # Scrap ETF list from etfdb
        df_pages = []
        driver.get('https://etfdb.com/screener')
        while True:
            print('scrap etfdb page', driver.find_element_by_css_selector("li[class='active page-number']").text)
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

        etfcom_list = set(df_etfcom.index.to_list())
        etfdb_list = set(df_etfdb.index.to_list())
        all_etf_list = etfcom_list | etfdb_list
        df_all = pd.DataFrame(index=sorted(all_etf_list))
        df_all.index.name = 'Ticker'
        df_all['etfcom'] = df_all.index.isin(etfcom_list)
        df_all['etfdb'] = df_all.index.isin(etfdb_list)
        df_all.to_csv(args.output_all_etfs)

    else:
        df_all = pd.read_csv(args.output_all_etfs)
        df_all.set_index('Ticker', inplace=True)

    # Scrap etfdb info
    if not args.no_scrap_etfdb_info:
        etfdb_row_dict_list = []
        for count,ticker in enumerate(df_all.index):
            if args.skip is not None:
                if count < args.skip:
                    continue
            if df_all.loc[ticker,'etfdb']:
                print('get_etfdb_info',count,ticker)
                try:
                    row_dict = get_etfdb_info(ticker, args.output_etfdb_fundflow)
                except:
                    print('scrap fail - try again')
                    time.sleep(30)
                    row_dict = get_etfdb_info(ticker, args.output_etfdb_fundflow)
                if row_dict is not None:
                    etfdb_row_dict_list.append(row_dict)
                    row_dict_to_csv(etfdb_row_dict_list, args.output_etfdb_info)
                time.sleep(args.delay)

    # Scrap etfcom info
    if not args.no_scrap_etfcom_info:
        etfcom_row_dict_list = []
        for count, ticker in enumerate(df_all.index):
            if args.skip is not None:
                if count < args.skip:
                    continue
            if df_all.loc[ticker, 'etfcom']:
                print('get_etfcom_info',count,ticker)
                try:
                    row_dict = get_etfcom_info(ticker, args.output_etfcom_holdings)
                except:
                    print('scrap fail - try again')
                    time.sleep(30)
                    row_dict = get_etfcom_info(ticker, args.output_etfcom_holdings)
                if row_dict is not None:
                    etfcom_row_dict_list.append(row_dict)
                    row_dict_to_csv(etfcom_row_dict_list, args.output_etfcom_info)
                time.sleep(args.delay)

    get_driver().quit()

if __name__ == "__main__":
    status = main()
    sys.exit(0 if status is None else status)
