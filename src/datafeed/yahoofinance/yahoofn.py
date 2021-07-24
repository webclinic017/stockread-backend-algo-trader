import datetime
from abc import abstractmethod, ABC
from enum import Enum
from typing import List, Optional

import numpy as np
import pandas as pd
import pytz
import requests
import yfinance as yf

from src.datafeed.yahoofinance.yfrapid_errors import YahooFinanceRangeSettingdError, YahooFinanceInvalidIntervalError, \
    NotRegularHoursDataRequest
from src.secrets.credentials import YAHOO_FINANCE_API_KEY, YAHOO_FINANCE_RAPID_API_HOST


class ICandleFeed(ABC):
    @abstractmethod
    def get_candles(self) -> pd.DataFrame:
        raise NotImplementedError()


class RangeType(Enum):
    FROM_TO = 1
    PERIOD = 2


class BaseYF:
    def __init__(self, interval, range_type, period, start, end):
        self.df_headers: Optional[List[str]] = None
        self.interval = interval
        self.range_type = range_type
        self.period = None
        self.start = None
        self.end = None

        if self.range_type == RangeType.PERIOD:
            self.period = period
        else:
            self.start = start
            self.end = end

    def set_dataframe_headers(self, df_headers: List[str]):
        self.df_headers = df_headers

    def _format_dataframe(self, ticker_symbol, dataframe: pd.DataFrame):
        # convert datetime index column of a pandas dataframe into a normal column
        dataframe.reset_index(level=0, inplace=True)
        # lowercase dataframe column headers
        dataframe.columns = map(str.lower, dataframe.columns)

        if 'date' in dataframe.columns:
            # add 'timestamp' column translated from 'date' column
            dataframe = dataframe.assign(timestamp=dataframe['date'].values.astype(np.int64) // 10 ** 9)
            # rename dataframe column header from 'date' to 'datetime'
            dataframe = dataframe.rename(columns={'date': 'datetime'})
        else:
            # add 'timestamp' column translated from 'date' column
            dataframe = dataframe.assign(timestamp=dataframe['datetime'].values.astype(np.int64) // 10 ** 9)

        if not ticker_symbol:
            raise Exception('Missing data "ticker_symbol" method input parameter')

        dataframe = dataframe.assign(interval=self.interval)
        dataframe = dataframe.assign(ticker_symbol=ticker_symbol)

        if not self.df_headers:
            # re-order columns
            return dataframe[
                ['timestamp', 'datetime', 'open', 'high', 'low', 'close', 'volume', 'interval', 'ticker_symbol']]
        else:
            for header in self.df_headers:
                if header not in dataframe.columns:
                    raise Exception(f'The {header} field does not exist in the dataframe column names')

            return dataframe[[self.df_headers]]


class SingleTickerYF(BaseYF, ICandleFeed):

    def __init__(self, ticker_symbol: str, interval="15m", range_type: RangeType = RangeType.PERIOD, period="5d",
                 start=None, end=None):
        super().__init__(interval, range_type, period, start, end)
        self.ticker_symbol = ticker_symbol

    def get_candles(self):
        single_df = yf.download(self.ticker_symbol, start=self.start, end=self.end, actions=False, threads=True,
                                group_by='ticker', period=self.period, show_errors=True,
                                interval=self.interval, proxy=None, rounding=False)
        return self._format_dataframe(self.ticker_symbol, single_df)


class MultipleTickerYF(BaseYF, ICandleFeed):
    def __init__(self, ticker_list: [List[str]], interval="15m", range_type: RangeType = RangeType.PERIOD, period="5d",
                 start=None, end=None):
        super().__init__(interval, range_type, period, start, end)
        self.ticker_list = ticker_list

    def get_candles(self, start=None, end=None, actions=False, threads=True, group_by='ticker', period="max",
                    show_errors=True, interval="1d", proxy=None, rounding=False):
        """Download yahoo tickers
        :Parameters:
            tickers : str, list
                List of tickers to download

            period : str
                Valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
                Either Use period parameter or use start and end

            interval : str
                Valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
                Intraday data cannot extend last 60 days

            start: str
                Download start date string (YYYY-MM-DD) or _datetime.
                Default is 1900-01-01
            end: str
                Download end date string (YYYY-MM-DD) or _datetime.
                Default is now
            group_by : str
                Group by 'ticker' or 'column' (default)

            threads: bool / int
                How many threads to use for mass downloading. Default is True

            proxy: str
                Optional. Proxy server URL scheme. Default is None

            rounding: bool
                Optional. Round values to 2 decimal places?

            show_errors: bool
                Optional. Doesn't print errors if True
        """
        separator = ' '
        tickers = separator.join(self.ticker_list)
        combined_df = yf.download(tickers, start=self.start, end=self.end, actions=False, threads=True,
                                  group_by='ticker', period=self.period, show_errors=True,
                                  interval=self.interval, proxy=None, rounding=False)

        ticker_dataframes = dict()

        for ticker in self.ticker_list:
            ticker_df = combined_df[ticker]
            ticker_dataframes[ticker] = self._format_dataframe(ticker, ticker_df)

        return ticker_dataframes


class RapidApiYF(ICandleFeed):
    def __init__(self, region: str, ticker_symbol: str, interval="15m", range_type: RangeType = RangeType.PERIOD,
                 period="5d", start=None, end=None, api_key: str = YAHOO_FINANCE_API_KEY,
                 base_url: str = YAHOO_FINANCE_RAPID_API_HOST):

        self.region: str = region
        self.ticker_symbol: str = ticker_symbol
        self.api_key = api_key
        self.base_url = base_url

        self.interval = interval
        self.range_type = range_type

        # Range Settings
        self.__range_period: Optional[str] = None
        self.__range_from: Optional[int] = None  # from timestamp
        self.__range_to: Optional[int] = None  # from timestamp

        if self.range_type == RangeType.PERIOD:
            self.__range_period = period
        else:
            self.__range_from = start
            self.__range_to = end

    def set_range_by_period(self, default_range: str = "5d"):
        self.range_type = RangeType.PERIOD
        if default_range in ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"]:
            self.__range_period = default_range
        else:
            raise YahooFinanceRangeSettingdError()

    def set_range_by_fromto(self, from_timestamp: int, to_timestamp: int):
        self.range_type = RangeType.FROM_TO
        self.__range_from = from_timestamp
        self.__range_to = to_timestamp

    def set_day_range_data(self, minutes_ago: int, interval: str = "1m"):

        if interval == "1m":
            seconds_ago = 60 * minutes_ago
        elif interval == "2m":
            seconds_ago = 2 * 60 * minutes_ago
        elif interval == "5m":
            seconds_ago = 5 * 60 * minutes_ago
        elif interval == "15m":
            seconds_ago = 15 * 60 * minutes_ago
        else:
            raise YahooFinanceInvalidIntervalError()

        market_start_time = datetime.datetime.utcnow().replace(
            hour=13,
            minute=30,
            second=00
        ).timestamp()

        market_end_time = datetime.datetime.utcnow().replace(
            hour=20,
            minute=00,
            second=00
        ).timestamp()

        right_now = datetime.datetime.utcnow().timestamp()

        if market_start_time < right_now < market_end_time:
            period2 = right_now
            if right_now - seconds_ago > market_start_time:
                period1 = right_now - seconds_ago
            else:
                period1 = market_start_time

            self.range_type = RangeType.BY_PERIOD_RANGE
            self.__range_from = period1
            self.__range_to = period2

        else:
            raise NotRegularHoursDataRequest()

    def _format_output(self, resp, is_utc=False, local='America/Montreal'):

        dict_list = list()
        for i, timestamp in enumerate(resp['chart']['result'][0]['timestamp']):
            open = resp['chart']['result'][0]['indicators']['quote'][0]['open']
            low = resp['chart']['result'][0]['indicators']['quote'][0]['low']
            high = resp['chart']['result'][0]['indicators']['quote'][0]['high']
            close = resp['chart']['result'][0]['indicators']['quote'][0]['close']
            volume = resp['chart']['result'][0]['indicators']['quote'][0]['volume']

            if is_utc:
                dt_value = datetime.datetime.utcfromtimestamp(timestamp).isoformat()
            else:
                dt_value = datetime.datetime.utcfromtimestamp(timestamp).replace(tzinfo=pytz.timezone('UTC')) \
                    .astimezone(pytz.timezone(local)).isoformat()

            dict_list.append(
                {'timestamp': timestamp,
                 'datetime': dt_value,
                 'open': open[i] if open[i] is not None else dict_list[i - 1]['open'],
                 'high': high[i] if high[i] is not None else dict_list[i - 1]['high'],
                 'low': low[i] if low[i] is not None else dict_list[i - 1]['low'],
                 'close': close[i] if close[i] is not None else dict_list[i - 1]['close'],
                 'volume': volume[i] if volume[i] is not None else dict_list[i - 1]['volume'],
                 'interval': self.interval,
                 'ticker_symbol': self.ticker_symbol}
            )

        return dict_list

    def _get_candle_dicts(self, endpoint: str = "/stock/v2/get-chart") -> List[dict]:
        url_endpoint = f"https://{self.base_url}{endpoint}"
        if self.range_type == RangeType.PERIOD:
            params = {"interval": self.interval, "symbol": self.ticker_symbol,
                      "range": self.__range_period, "region": self.region}

        elif self.range_type == RangeType.FROM_TO:
            params = {"interval": self.interval, "symbol": self.ticker_symbol, "region": self.region,
                      "period2": self.__range_to, "period1": self.__range_from}
        else:
            raise YahooFinanceRangeSettingdError

        headers = {
            'x-rapidapi-host': self.base_url,
            'x-rapidapi-key': self.api_key
        }

        response = requests.request("GET", url=url_endpoint, headers=headers, params=params)

        resp = response.json()
        original_formatted = self._format_output(resp)

        # to filter out the time series data points where stock bars remain unchanged
        deduplicated_resp = list()
        for index, current_item in enumerate(original_formatted):
            if index > 0:
                duplicate_condition = current_item['open'] == original_formatted[index - 1]['open'] and \
                                      current_item['high'] == original_formatted[index - 1]['high'] and \
                                      current_item['low'] == original_formatted[index - 1]['low'] and \
                                      current_item['close'] == original_formatted[index - 1]['close'] and \
                                      current_item['volume'] == original_formatted[index - 1]['volume']

                if duplicate_condition:
                    # skip the datapoint
                    pass
                else:
                    deduplicated_resp.append(current_item)

            else:
                deduplicated_resp.append(current_item)

        return deduplicated_resp

    def get_candles(self, endpoint: str = "/stock/v2/get-chart") -> pd.DataFrame:
        dict_list = self._get_candle_dicts(endpoint=endpoint)

        return pd.DataFrame(data=dict_list)


if __name__ == '__main__':
    pass

