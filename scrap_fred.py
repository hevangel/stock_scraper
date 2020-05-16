#!/usr/bin/env python

import pandas as pd
import argparse
import datetime
import time
import sys
from fredapi import Fred
from junit_xml import TestSuite, TestCase
import csv

def main():
    parser = argparse.ArgumentParser(description='scrap fred')
    parser.add_argument('-input', type=str, default='data_tickers/fred_stats.csv', help='input csv file list all tickers to scrap')
    parser.add_argument('-output_prefix', type=str, default='data_fred/fred_', help='prefix of the output file')
    parser.add_argument('-no_scrap', action='store_true', help='No scrapping, read existing csv file')
    parser.add_argument('-apikey', type=str, help='Fred API key')
    parser.add_argument('-date', type=str, default=str(datetime.date.today()), help='Specify the date')
    parser.add_argument('-report', type=str, default='weekly_report.xml', help='file name of the test report')
    args = parser.parse_args()

    # scrap the data
    if not args.no_scrap:
        fred = Fred(api_key=args.apikey)
        with open(args.input) as csvfile:
            fredreader = csv.reader(csvfile, delimiter=',')
            next(fredreader)
            for row in fredreader:
                filename = args.output_prefix + row[0] + '.csv'
                print('Getting', row[0], '-', row[1])
                s = fred.get_series(row[0])
                s.to_csv(filename)

if __name__ == "__main__":
    sys.exit(main())