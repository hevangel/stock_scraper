import sys
import wget
import argparse
import pandas as pd

def main():
    parser = argparse.ArgumentParser(description='scrap alpha vantage history')
    parser.add_argument('-api_key_file', type=str, default='../hevangel-com/api_keys/alpha_vantage.txt', help='API key file')
    parser.add_argument('-input_file', type=str, action='append', help='input file')
    parser.add_argument('-output_dir', type=str, default='../stock_data/raw_history_alpha_vantage/', help='output directory')
    parser.add_argument('-delay', type=int, default=1, help='delay in sec between each URL request')
    args = parser.parse_args()

    if args.input_file == None:
        args.input_file = [
            'data_tickers/all_tickers.csv',
            'data_tickers/etfs_info.csv'
        ]

    # Read Alpha Vantage API key
    api_key_list = []
    with open(args.api_key_file, 'r') as f:
        for line in f:
            api_key_list.append(f.readline().rstrip('\n'))

    # Read input tickets list
    df_input_list = []
    for input_file in args.input_file:
        df_input_list.append(pd.read_csv(input_file))
    df_input = pd.concat(df_input_list, sort=False)
    ticker_list = df_input['Ticker'].to_list()

    for count,ticker in enumerate(ticker_list):
        print('downloading...', ticker, '-', count)
        api_key = api_key_list[count % len(api_key_list)]
        url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol='+ticker+'&apikey='+api_key+'&outputsize=full&datatype=csv'
        wget.download(url, out=args.output_dir)


if __name__ == "__main__":
    status = main()
    sys.exit(0 if status is None else status)