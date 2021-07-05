from typing import List

import pandas as pd

from src.autotrade.barfeed.bar import Bar
from collections import deque


class BarFrame:

    def __init__(self, dataframe: List[pd.DataFrame]) -> None:
        """Initalizes the Stock Data Frame Object.
        Arguments:
        ----
        data {List[Dict]} -- The data to convert to a frame. Normally, this is
            returned from the historical prices endpoint.
        """

        self._frame = dataframe
        self._frame: pd.DataFrame = self._create_frame()
        self._index = 0

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

    def _create_frame(self) -> pd.DataFrame:
        """Creates a new data frame with the data passed through.
        Returns:
        ----
        {pd.DataFrame} -- A pandas dataframe.
        """

        # Make a data frame.
        price_df = pd.DataFrame(data=self._data)

        return price_df

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
