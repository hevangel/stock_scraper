#!/usr/bin/env python

import pandas as pd
import argparse
import datetime
import time
import sys
import glob
import os
import wget
from scrap_utils import *

scrap_delay = 2

def main():
    parser = argparse.ArgumentParser(description='scrap yahoo earning')
    parser.add_argument('-output_dir', type=str, default='../stock_data/raw_daily_short_finra/', help='prefix of the output file')
    parser.add_argument('-date', type=str, default=datetime.date.today().strftime('%Y%m%d'), help='Specify the date')
    args = parser.parse_args()

    url = 'http://regsho.finra.org/CNMSshvol' + args.date + '.txt'
    print('downloading',url)
    wget.download(url, out=args.output_dir, bar=False)

if __name__ == "__main__":
    status = main()
    sys.exit(0 if status is None else status)
