from typing import Optional

import pandas as pd

from src.autotrade.bars.bar import Bar
from collections import deque


class BarFeed:

    def __init__(self, dataframe: pd.DataFrame) -> None:
        """Initalizes the Stock Data Frame Object.
        Arguments:
        ----
        data {List[Dict]} -- The data to convert to a frame. Normally, this is
            returned from the historical prices endpoint.
        """

        self._frame = dataframe
        self._index = 0
        # replace NaN values with None
        self._replace_nan()

        # self._lastbar = Bar(bar_dict=list(self._frame.to_dict('index').values())[-1])

    def __iter__(self):
        return self

    @property
    def frame(self) -> pd.DataFrame:
        """The frame object.
        Returns:
        ----
        pd.DataFrame -- A pandas data frame with the price data.
        """
        return self._frame

    def _replace_nan(self):
        self._frame = self._frame.where(pd.notnull(self._frame), None)

    def __next__(self):

        de = deque([])
        bar_count = 0

        # replace NaN values with None
        self._replace_nan()
        # loop through dict list converted from the pandas frame
        for bar_dict in self._frame.to_dict('index').values():

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
    def latest_bar(self):
        return Bar(bar_dict=list(self._frame.to_dict('index').values())[-1])

    @property
    def last_bar(self):
        latest_bar = Bar(bar_dict=list(self._frame.to_dict('index').values())[-1])
        second_latest_bar = Bar(bar_dict=list(self._frame.to_dict('index').values())[-2])
        third_latest_bar = Bar(bar_dict=list(self._frame.to_dict('index').values())[-3])
        standard_time_gap = second_latest_bar.timestamp - third_latest_bar.timestamp
        last_time_gap = latest_bar.timestamp - latest_bar.timestamp
        if last_time_gap < standard_time_gap:
            return second_latest_bar
        else:
            return latest_bar

    @property
    def bar_count(self):
        return len(self._frame)

    @property
    def close(self):
        return self._frame['close']

    @property
    def open(self):
        return self._frame['open']

    @property
    def volume(self):
        return self._frame['volume']

    def add_fields(self, **kwargs):
        # kwargs is a dict of the keyword args passed to the function
        for key, value in kwargs.items():
            self._frame[key] = value


if __name__ == '__main__':
    pass
