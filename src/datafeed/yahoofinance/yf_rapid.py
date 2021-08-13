# is not in use but just a backup implementation.
pass


'''
import datetime
from typing import Optional, List

import pytz
import requests
from pandas import pd

from src.datafeed.yahoofinance.yf_base import ICandleFeed
from src.datafeed.yahoofinance.yf_errors import YahooFinanceRangeSettingdError, YahooFinanceInvalidIntervalError, \
    NotRegularHoursDataRequest
from src.secrets.credentials import YAHOO_FINANCE_API_KEY, YAHOO_FINANCE_RAPID_API_HOST

class YahooFinanceRangeSettingdError(Exception):
    """Error thrown when a data range is set conflict with the chosen range setting"""

    def __init__(self):
        super(YahooFinanceRangeSettingdError, self).__init__("The chosen range setting conflicts with the range inputs")


class YahooFinanceInvalidIntervalError(Exception):
    """Error thrown when a interval input is not one of 1m|2m|5m|15m allowed options"""

    def __init__(self):
        super(YahooFinanceInvalidIntervalError, self).__init__("The interval input parameter is invalid")


class NotRegularHoursDataRequest(Exception):
    """Error thrown when a data request by minute/minutes is not within regular trading hours"""

    def __init__(self):
        super(NotRegularHoursDataRequest, self).__init__("The by-minute data request  is not in regular trading hours")
        
class RapidApiYF(ICandleFeed):

    def __init__(self, region: str, ticker_symbol: str, interval: str, is_fromto: bool,
                 period: str, start=None, end=None, api_key: str = YAHOO_FINANCE_API_KEY,
                 base_url: str = YAHOO_FINANCE_RAPID_API_HOST):

        self.region: str = region
        self._ticker_symbol: str = ticker_symbol
        self._api_key = api_key
        self._base_url = base_url

        self.interval = interval
        self.is_fromto = is_fromto

        # Range Settings
        self.__range_period: Optional[str] = None
        self.__range_from: Optional[int] = None  # from timestamp
        self.__range_to: Optional[int] = None  # from timestamp

        if self.is_fromto:
            self.__range_from = start
            self.__range_to = end
        else:
            self.__range_period = period

    def set_range_by_period(self, default_range: str = "5d"):
        self.is_fromto = False
        if default_range in ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"]:
            self.__range_period = default_range
        else:
            raise YahooFinanceRangeSettingdError()

    def set_range_by_fromto(self, from_timestamp: int, to_timestamp: int):
        self.is_fromto = True
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

            self.is_fromto = False
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
                 'ticker_symbol': self._ticker_symbol}
            )

        return dict_list

    def _get_candle_dicts(self) -> List[dict]:
        endpoint: str = "/stock/v2/get-chart"
        url_endpoint = f"https://{self._base_url}{endpoint}"

        if self.is_fromto:
            params = {"interval": self.interval, "symbol": self._ticker_symbol, "region": self.region,
                      "period2": self.__range_to, "period1": self.__range_from}

        else:
            params = {"interval": self.interval, "symbol": self._ticker_symbol,
                      "range": self.__range_period, "region": self.region}

        headers = {
            'x-rapidapi-host': self._base_url,
            'x-rapidapi-key': self._api_key
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

                if not duplicate_condition:
                    deduplicated_resp.append(current_item)

            else:
                deduplicated_resp.append(current_item)

        return deduplicated_resp

    def get_candles(self) -> pd.DataFrame:
        dict_list = self._get_candle_dicts()

        return pd.DataFrame(data=dict_list)

    @property
    def ticker_symbol(self):
        return self._ticker_symbol

    def get_number_candles(self, number: int) -> pd.DataFrame:
        pass
'''