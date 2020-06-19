import pandas as pd
import time
import argparse
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium import webdriver

def main():
    parser = argparse.ArgumentParser(description='scrap finviz screener')
    parser.add_argument('-output', type=str, default='data_tickers/etfs/csv', help='output file')
    parser.add_argument('-use_firefox', type=bool, help='Use firefox instead of phantomjs')
    parser.add_argument('-scrap_etfcom', type=bool, help='Scrap the list from etf.com instead of etfdb.com')
    parser.add_argument('-delay', type=int, default=1, help='delay in sec between each URL request')
    args = parser.parse_args()

    if args.use_firefox:
        options = FirefoxOptions()
        options.add_argument("--headless")
        driver = webdriver.Firefox(options=options)
    else:
        driver = webdriver.PhantomJS()

    df_pages = []

    driver.get('https://etfdb.com/screener')
    #while True:
    for i in range(2):
        print('scrap page', driver.find_element_by_css_selector("li[class='active page-number']").text)
        thead = driver.find_element_by_tag_name('thead')
        tbody = driver.find_element_by_tag_name('tbody')
        table = '<table>'+thead.get_attribute('innerHTML')+tbody.get_attribute('innerHTML')+'</table>'
        df_pages.append(pd.read_html(table, header=0, index_col=0)[0])
        if driver.find_element_by_class_name('page-next').get_attribute('class').split()[0] == 'disabled':
            break
        driver.find_element_by_link_text('Next ›').click()
        time.sleep(args.delay)

    df = pd.concat(df_pages)
    df.drop(columns=['ETFdb Pro'], inplace=True)
    df.to_csv(args.output)

    driver.close()

if __name__ == "__main__":
    sys.exit(main())
