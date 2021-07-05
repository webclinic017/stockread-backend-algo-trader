import time

import pandas as pd
import yfinance as yf

# stock = yf.Ticker('apxt')
start_time = time.time()
# data = yf.download("AVPT", period="5d", interval="5m", threads=True)
data = yf.download("AVPT", period="2d", interval="1m")

# df = stock.history(period="5d", interval="1m",
# df.columns = map(str.lower, df.columns)
# to display all columns and rows of pd dataframe
pd.options.display.max_columns = None
# pd.options.display.max_rows = None
print(data.tail(10))

print("--- %s seconds ---" % (time.time() - start_time))
