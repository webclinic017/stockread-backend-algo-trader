from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Optional, List
import pandas as pd

import pytz
import requests

from src.datafeed.yfrapidapi.yfrapid_errors import NotRegularHoursDataRequest
from src.datafeed.yfrapidapi.yfrapid_errors import YahooFinanceInvalidIntervalError
from src.datafeed.yfrapidapi.yfrapid_errors import YahooFinanceRangeSettingdError
from src.secrets.credentials import YAHOO_FINANCE_API_KEY
from src.secrets.credentials import YAHOO_FINANCE_RAPID_API_HOST

rapid_api_key = YAHOO_FINANCE_API_KEY
rapid_api_host = YAHOO_FINANCE_RAPID_API_HOST


class StockDataApi(ABC):
    def __init__(self, region: str, ticker_symbol: str):
        self.region: str = region
        self.ticker_symbol: str = ticker_symbol

    @abstractmethod
    def get_candle_dicts(self) -> List[dict]:
        raise NotImplementedError()

    @abstractmethod
    def get_candle_dataframe(self) -> pd.DataFrame:
        raise NotImplementedError()


class YahooFinanceRangeSetting(Enum):
    BY_DEFAULT_RANGE = 1
    BY_PERIOD_RANGE = 2


class YFRapidApi(StockDataApi):
    def __init__(self, region: str, ticker_symbol: str, api_key: str = rapid_api_key, base_url: str = rapid_api_host):
        self.api_key = api_key
        self.base_url = base_url
        super().__init__(region, ticker_symbol)

        # Range Settings
        self._range_setting: Optional[YahooFinanceRangeSetting] = None
        self.__range_default: Optional[str] = None
        self.__range_period_from: Optional[int] = None  # from timestamp
        self.__range_period_to: Optional[int] = None  # from timestamp

        self._interval: Optional[str] = None

    def set_range_by_default(self, default_range: str = "1d"):
        self._range_setting = YahooFinanceRangeSetting.BY_DEFAULT_RANGE
        if default_range in ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"]:
            self.__range_default = default_range
        else:
            raise YahooFinanceRangeSettingdError()

    def set_range_by_period(self, from_timestamp: int, to_timestamp: int):
        self._range_setting = YahooFinanceRangeSetting.BY_PERIOD_RANGE
        self.__range_period_from = from_timestamp
        self.__range_period_to = to_timestamp

    def set_interval(self, interval: str = "1m"):
        self._interval = interval

    @property
    def interval(self):
        return self._interval

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

        market_start_time = datetime.utcnow().replace(
            hour=13,
            minute=30,
            second=00
        ).timestamp()

        market_end_time = datetime.utcnow().replace(
            hour=20,
            minute=00,
            second=00
        ).timestamp()

        right_now = datetime.utcnow().timestamp()

        if market_start_time < right_now < market_end_time:
            period2 = right_now
            if right_now - seconds_ago > market_start_time:
                period1 = right_now - seconds_ago
            else:
                period1 = market_start_time

            self._range_setting = YahooFinanceRangeSetting.BY_PERIOD_RANGE
            self.__range_period_from = period1
            self.__range_period_to = period2

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
                dt_value = datetime.utcfromtimestamp(timestamp).isoformat()
            else:
                dt_value = datetime.utcfromtimestamp(timestamp).replace(tzinfo=pytz.timezone('UTC')) \
                    .astimezone(pytz.timezone(local)).isoformat()

            dict_list.append(
                {'timestamp': timestamp,
                 'datetime': dt_value,
                 'open': open[i] if open[i] is not None else dict_list[i - 1]['open'],
                 'high': high[i] if high[i] is not None else dict_list[i - 1]['high'],
                 'low': low[i] if low[i] is not None else dict_list[i - 1]['low'],
                 'close': close[i] if close[i] is not None else dict_list[i - 1]['close'],
                 'volume': volume[i] if volume[i] is not None else dict_list[i - 1]['volume'],
                 'interval': self._interval,
                 'ticker_symbol': self.ticker_symbol}
            )

        return dict_list

    def get_candle_dicts(self, endpoint: str = "/stock/v2/get-chart") -> List[dict]:
        url_endpoint = f"https://{self.base_url}{endpoint}"
        if self._range_setting == YahooFinanceRangeSetting.BY_DEFAULT_RANGE:
            params = {"interval": self._interval, "symbol": self.ticker_symbol,
                      "range": self.__range_default, "region": self.region}
        elif self._range_setting == YahooFinanceRangeSetting.BY_PERIOD_RANGE:
            params = {"interval": self._interval, "symbol": self.ticker_symbol, "region": self.region,
                      "period2": self.__range_period_to, "period1": self.__range_period_from}
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

    def get_candle_dataframe(self, endpoint: str = "/stock/v2/get-chart") -> pd.DataFrame:
        dict_list = self.get_candle_dicts(endpoint=endpoint)

        return pd.DataFrame(data=dict_list)


if __name__ == '__main__':
    yf_api = YFRapidApi(region="CA", ticker_symbol="SHOP.TO")
    yf_api.set_range_by_default()
    yf_api.set_interval("1m")
    dataframe = yf_api.get_candle_dataframe()
    print(f'Result: \n{dataframe}')
