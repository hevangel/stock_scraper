#!/usr/bin/env python

import pandas as pd
import argparse
import datetime
import time
import sys
from fredapi import Fred
from junit_xml import TestSuite, TestCase

def main():
    parser = argparse.ArgumentParser(description='scrap fred')
    parser.add_argument('-output_prefix', type=str, default='data_fred/fred_', help='prefix of the output file')
    parser.add_argument('-no_scrap', action='store_true', help='No scrapping, read existing csv file')
    parser.add_argument('-apikey', type=str, help='Fred API key')
    parser.add_argument('-date', type=str, default=str(datetime.date.today()), help='Specify the date')
    parser.add_argument('-report', type=str, default='weekly_report.xml', help='file name of the test report')
    args = parser.parse_args()

    series_id_list = {
        'WALCL'             : 'Total Assets',
        'SWPT'              : 'Central Bank Liquidity Swaps',
        'TREAS10Y'          : 'US Treasury 10 Years',
        'TREAS1T5'          : 'US Treasury 1 to 5 Years',
        'TREAS5T10'         : 'US Treasury 5 to 10 Years',
        'TREAS911Y'         : 'US Treasury 91 days to 1 Year',
        'TREAS1590'         : 'US Treasury 15 to 90 days',
        'TREAS15'           : 'US Treasury 15 days',
        'REP15'             : 'Repurchase Agreements 15 days',
        'REP1690'           : 'Repurchase Agreements 16 to 90 days',
        'RESPPALGUOXCH1NWW' : 'Change from previous week level',
        'FEDFUNDS'          : 'Effective Federal Funds Rate',
        'TB3MS'             : '3-Month Treasury Yield',
        'TB1YR'             : '1-Year Treasury Yield',
        'TB4WK'             : '4-Week Treasury Yield',
        'DTB6'              : '6-Month Treasury Yield',
    }

    # scrap the data
    if not args.no_scrap:
        fred = Fred()
        for series_id in series_id_list.keys():
            filename = args.output_prefix + series_id + '.csv'
            print('Getting ', series_id)
            s = fred.get_series(series_id)
            s.to_csv(filename)

if __name__ == "__main__":
    sys.exit(main())