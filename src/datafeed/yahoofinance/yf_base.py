# Copyright (C) 2021-2030 StockRead Inc.
# Author: Thanh Tung Nguyen
# Contact: tungstudies@gmail.com

import math
from abc import abstractmethod, ABC
from typing import Optional, List

import pandas as pd


# DIVIDER: --------------------------------------
# INFO: PublicBase Abstract Class (YahooFinance Public API - BaseClass)

class PublicBase:
    def __init__(self, ticker_symbol: str=None, interval_option: str=None,
                 period=None, is_fromto: bool = False, start=None, end=None):
        self._range_type = is_fromto
        self._period = None
        self._start = None
        self._end = None

        if is_fromto:
            self._start = start
            self._end = end

        else:
            self._period = period

        self._ticker_symbol = ticker_symbol
        self._interval_option = interval_option
        self._df_headers: Optional[List[str]] = None

    def set_dataframe_headers(self, df_headers: List[str]):
        self._df_headers = df_headers

    def _compute_data_days(self, number_of_bar_intervals: int):
        number = number_of_bar_intervals
        minutes_per_day = 390

        if self._interval_option == '1m':
            minutes = number
        elif self._interval_option == '2m':
            minutes = number * 2
        elif self._interval_option == '5m':
            minutes = number * 5
        elif self._interval_option == '15m':
            minutes = number * 15
        elif self._interval_option == '30m':
            minutes = number * 30
        elif self._interval_option == '1h':
            minutes = number * 60
        elif self._interval_option == '4h':
            minutes = number * 60 * 4
        elif self._interval_option == '1d':
            minutes = number * minutes_per_day
        else:
            raise ValueError('Invalid interval type')

        return math.ceil(minutes / minutes_per_day)


# DIVIDER: --------------------------------------
# INFO: ICandleFeed Interface

class ICandleRetriever(ABC):
    @abstractmethod
    def set_interval(self, interval: str):
        raise NotImplementedError()

    @abstractmethod
    def set_ticker_symbol(self, ticker_symbol: str):
        raise NotImplementedError()

    @abstractmethod
    def get_candles(self) -> pd.DataFrame:
        raise NotImplementedError()

    @abstractmethod
    def get_x_candles(self, candle_count: int) -> pd.DataFrame:
        raise NotImplementedError()

    @property
    @abstractmethod
    def ticker_symbol(self):
        raise NotImplementedError()
