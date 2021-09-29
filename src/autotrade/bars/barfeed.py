# Copyright (C) 2021-2030 StockRead Inc.
# Author: Thanh Tung Nguyen
# Contact: tungstudies@gmail.com
from collections import deque
from typing import Deque, List

import pandas as pd

from src.autotrade.artifacts.mkhours import MarketHour
from src.autotrade.bars.bar import Bar


# DIVIDER: --------------------------------------
# INFO: BarFeed Concrete Class

class BarFeed:

    def __init__(self, dataframe: pd.DataFrame, market_hour: MarketHour,
                 data_delay_seconds: int = 10, data_refresh_limit: int = 3) -> None:
        """Initializes the Stock Data Frame Object.
        Arguments:
        ----
        data {List[Dict]} -- The data to convert to a frame. Normally, this is
            returned from the historical prices endpoint.
        """

        self._index = 0
        self._market_hour = market_hour
        self._data_delay_seconds = data_delay_seconds
        self._data_refresh_limit = data_refresh_limit
        self._frame = dataframe
        self._valid_timestamps = set()

        self._first_retrieval_last_valid_bar_timestamp = self.last_valid_bar.timestamp

        live_tsp = self._first_retrieval_last_valid_bar_timestamp
        self._frame['is_live_bar'] = self._frame['timestamp'] >= live_tsp if self._market_hour.is_open_now() else False

        # replace NaN values with None
        self._replace_nan()

    # DIVIDER: Required Class Construction Methods --------------------------------------------------------

    def __iter__(self):
        return self

    def __next__(self) -> Deque[Bar]:

        de: Deque[Bar] = deque([])
        bar_count = 0

        # loop through dict list converted from the pandas frame
        for bar_dict in self._find_bar_zero_dict_list():

            bar = Bar(bar_dict=bar_dict)

            if bar_count < self._index + 1:
                if bar_count == 0:
                    de.appendleft(bar)
                else:
                    # take the previous bar from the top and put it back to the end of the deque
                    previous_bar = de.popleft()
                    de.append(previous_bar)

                    # add current bar to the top of the queue
                    de.appendleft(bar)
                bar_count += 1
            else:
                break

        self._index += 1
        return de

    @property
    def frame(self) -> pd.DataFrame:
        """The frame object.
        Returns:
        ----
        pd.DataFrame -- A pandas data frame with the price data.
        """
        return self._frame

    @property
    def data_delay_seconds(self):
        return self._data_delay_seconds

    @property
    def data_refresh_limit(self):
        return self._data_refresh_limit

    @property
    def latest_retrieved_bar(self):
        return Bar(bar_dict=list(self._frame.to_dict('index').values())[-1])

    @property
    def last_valid_bar(self):
        return Bar(bar_dict=self._find_bar_zero_dict_list()[-1])

    @property
    def valid_bar_count(self):
        return len(self._find_bar_zero_dict_list())

    @property
    def close(self):
        return self._frame['close']

    @property
    def open(self):
        return self._frame['open']

    @property
    def high(self):
        return self._frame['high']

    @property
    def low(self):
        return self._frame['low']

    @property
    def volume(self):
        return self._frame['volume']

    def add_fields(self, **kwargs):
        # kwargs is a dict of the keyword args passed to the function
        for key, value in kwargs.items():
            self._frame[key] = value

    def update(self, dataframe: pd.DataFrame):
        self._frame = self._frame[dataframe.columns]

        old_dict_list = self._find_valid_dict_list()
        new_dict_list = list(dataframe.to_dict('index').values())

        for bar_dict in new_dict_list:
            if bar_dict['timestamp'] not in self._valid_timestamps:
                old_dict_list.append(bar_dict)

        self._frame = pd.DataFrame(data=old_dict_list)
        live_tsp = self._first_retrieval_last_valid_bar_timestamp
        self._frame['is_live_bar'] = self._frame['timestamp'] >= live_tsp if self._market_hour.is_open_now() else False
        self._replace_nan()

    # DIVIDER: Class Private Methods to Process Data Internally -----------------------------------

    def _replace_nan(self):
        self._frame = self._frame.where(pd.notnull(self._frame), None)

    def _find_bar_zero_dict_list(self):

        bar_dict_list: List[dict] = list(self._frame.to_dict('index').values())

        valid_minute_index = 0

        if bar_dict_list[-1].get('timestamp') % 60 == 0:
            if bar_dict_list[-1].get('timestamp') == self._market_hour.bar_zero_timestamp:
                return bar_dict_list
            else:
                valid_minute_index = -1

        for i in range(2, len(bar_dict_list)):
            if bar_dict_list[-i].get('timestamp') % 60 == 0:
                if bar_dict_list[-i].get('timestamp') == self._market_hour.bar_zero_timestamp:
                    return bar_dict_list[:-i + 1]
                else:
                    valid_minute_index = -i

        if abs(valid_minute_index) > 1:
            return bar_dict_list[:-valid_minute_index + 1]
        else:
            return bar_dict_list

    def _find_valid_dict_list(self):
        bar_dict_list = list(self._frame.to_dict('index').values())
        valid_dict_list = list()
        for bar_dict in bar_dict_list:
            if (bar_dict['timestamp'] - self._market_hour.open_timestamp) % self._market_hour.bar_gap_seconds == 0:
                valid_dict_list.append(bar_dict)
                self._valid_timestamps.add(bar_dict['timestamp'])

        return valid_dict_list


# DIVIDER: --------------------------------------
# INFO: Usage Examples

if __name__ == '__main__':
    pass
