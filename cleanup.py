sheet = ''
df1 = pd.read_csv(f"../stock_data/temp/{sheet}.csv", header=None, index_col=0, parse_dates=True)
df2 = pd.read_csv(f"../stock_data/data_cpc/{sheet}.csv", index_col=0, parse_dates=True)
df1.columns = ['PCRatio','VolumeCall','VolumePut','VolumeTotal','OpenInterestCall','OpenInterestPut','OpenInterestTotal']
df3 = pd.concat([df2,df1]).sort_index()
df4 = df3[df1.columns]
df4[['OpenInterestCall','OpenInterestPut','OpenInterestTotal']] = df4[['OpenInterestCall','OpenInterestPut','OpenInterestTotal']].fillna(0)
df4[['OpenInterestCall','OpenInterestPut','OpenInterestTotal']] = df4[['OpenInterestCall', 'OpenInterestPut', 'OpenInterestTotal']].astype(int)
df4.to_csv(f"../stock_data/data_cpc/{sheet}.csv")