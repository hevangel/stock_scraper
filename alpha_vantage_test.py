from alpha_vantage.timeseries import TimeSeries
import matplotlib.pyplot as plt

f = open('key.txt', 'r')
key = f.read()
f.close()

ts = TimeSeries(key=key, output_format='pandas')
data, meta_data = ts.get_daily_adjusted(symbol='MSFT', outputsize='compact')
data['4. close'].plot()
plt.title('Intraday Times Series for the MSFT stock (1 min)')
plt.show()

