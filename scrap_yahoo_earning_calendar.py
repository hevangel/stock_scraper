#!/usr/bin/env python

import pandas as pd
import argparse
import datetime
import sys
import yfinance as yf

def onDay(date, day):
    """
    :param date: current date
    :param day: next monday(0) - sunday(7)
    :return:
    """
    return date + datetime.timedelta(days=(day-date.weekday()+7)%7)

def main():
    parser = argparse.ArgumentParser(description='scrap yahoo earning')
    parser.add_argument('-input', type=str, default='data_tickers/earnings.csv', help='input file')
    parser.add_argument('-output_prefix', type=str, default='data_yahoo_earnings_estimate/earnings_estimate_', help='output file')
    parser.add_argument('-today', type=str, help='Specify today date')
    args = parser.parse_args()

    if args.today is None:
        today = datetime.date.today()
    else:
        today = datetime.datetime.fromisoformat(args.today).date()
    df_input = pd.read_csv(args.input)
    df_input.set_index('Ticker', inplace=True)
    df_output = pd.DataFrame()

    for ticker in df_input.index:
        yf_ticker = yf.Ticker(ticker)
        try:
            yf_calendar = yf_ticker.calendar
        except:
            print(f"{ticker} has no earnings date yet")
        else:
            if yf_calendar is None or yf_calendar.shape[1] == 0:
                continue
            if yf_calendar.shape[1] > 1:
                print(f"{ticker} next earnings in week of {yf_calendar.at['Earnings Date',0].date()}")
            else:
                next_earnings_date = yf_calendar.at['Earnings Date','Value']
                print(f"{ticker} next earnings at {next_earnings_date.date()}")
                next_monday = onDay(today,0)
                next_friday = onDay(next_monday,4)
                if next_earnings_date >= next_monday and next_earnings_date <= next_friday:
                    new_row = yf_calendar.T
                    new_row.insert(1, 'Ticker', ticker)
                    new_row.insert(2, 'Report', df_input.at[ticker,'Report'])
                    df_output = df_output.append(new_row)

    df_output.reset_index(drop=True, inplace=True)
    df_output.sort_values(by=['Earnings Date', 'Ticker'], inplace=True)
    print(df_output)
    df_output.to_csv(args.output_prefix + str(onDay(today,0)) + '.csv', index=False)

if __name__ == "__main__":
    sys.exit(main())

