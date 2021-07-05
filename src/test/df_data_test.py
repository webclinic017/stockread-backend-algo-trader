import time
import requests
import pandas as pd
import datetime
import pytz

url = "https://apidojo-yahoo-finance-v1.p.rapidapi.com/stock/v2/get-chart"
# get stock market open time in timestamp
open_timestamp = datetime.datetime.now().replace(hour=9, minute=30, second=0, microsecond=0).timestamp().__round__()
now_timestamp = datetime.datetime.now().timestamp().__round__()
close_timestamp = datetime.datetime.now().replace(hour=16, minute=0, second=0, microsecond=0).timestamp().__round__()

# interval = "1d"
# range = "3mo"

interval = "1m"
range = "1d"
ticker_symbol = "SHOP.TO"
region = "CA"
minutes_ago = 60

params = dict()

if open_timestamp < now_timestamp < close_timestamp and interval == "1m":

    period2_timestamp = now_timestamp
    period1_timestamp = now_timestamp - 60 * minutes_ago

    params = {"interval": interval, "symbol": ticker_symbol, "region": region,
              "period2": period2_timestamp, "period1": period1_timestamp}

else:
    params = {"interval": interval, "symbol": ticker_symbol, "range": range, "region": region}

headers = {
    'x-rapidapi-host': 'apidojo-yahoo-finance-v1.p.rapidapi.com',
    'x-rapidapi-key': '2bdfd8560emshea65c8701b0ce69p1cd88fjsnc44399c190fa'
}

response = requests.request("GET", url, headers=headers, params=params)

data = response.json()

print(data)
start_time = time.time()

df_input = list()
for i, timestamp in enumerate(data['chart']['result'][0]['timestamp']):
    open = data['chart']['result'][0]['indicators']['quote'][0]['open']
    low = data['chart']['result'][0]['indicators']['quote'][0]['low']
    high = data['chart']['result'][0]['indicators']['quote'][0]['high']
    close = data['chart']['result'][0]['indicators']['quote'][0]['close']
    volume = data['chart']['result'][0]['indicators']['quote'][0]['volume']

    df_input.append(
        {'timestamp': timestamp,
         'datetime': datetime.datetime.utcfromtimestamp(timestamp)
             .replace(tzinfo=pytz.timezone('UTC'))
             .astimezone(pytz.timezone('America/Montreal')),
         'open': open[i] if open[i] is not None else df_input[i - 1]['open'],
         'high': high[i] if high[i] is not None else df_input[i - 1]['high'],
         'low': low[i] if low[i] is not None else df_input[i - 1]['low'],
         'close': close[i] if close[i] is not None else df_input[i - 1]['close'],
         'volume': volume[i] if volume[i] is not None else df_input[i - 1]['volume']}
    )

# to display all columns and rows of pd dataframe
# pd.options.display.max_columns = None
# pd.options.display.max_rows = None

df = pd.DataFrame(df_input)
# print(df)

# rsi_indicator = RSIIndicator(df['close'])
# df['rsi'] = rsi_indicator.rsi()
# df_last15 = df.tail(15)
# print(df_last15)
# df_rsi_alert = df_last15.query("rsi > 70 or rsi < 30")
#
# alerted_rsi_timestamps = collections.deque(maxlen=15)
# for index, row in df_rsi_alert.iterrows():
#     if row['timestamp'] not in alerted_rsi_timestamps:
#         alerted_rsi_timestamps.append(row['timestamp'])
#         alert_type: str
#         if row['rsi'] < 30:
#             alert_type = 'BUY ALERT - RSI < 30'
#         else:
#             alert_type = 'SELL ALERT - RSI > 70'
#
#         subject_title = f"{alert_type}: @{row['datetime']} >> {ticker_symbol} is at $({round(row['close'],2)}"
#         msg = f"{alert_type}\nAt @{row['datetime']} {ticker_symbol} closed at ${round(row['close'],2)}" \
#               f" & with RSI of {round(row['rsi'],2)} "
#
#         my_email = 'tungstudies@gmail.com'
#         # my_sms = '5146388811@msg.telus.com'
#         benson_sms = 'benson1chn@gmail.com'
#         mailbox = MailBox()
#         mailbox.send_mail(subject_title, msg, [benson_sms])


# start_time = time.time()
# print("--- %s seconds ---" % (time.time() - start_time))
