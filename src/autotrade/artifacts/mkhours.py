# Copyright (C) 2021-2030 StockRead Inc.
# Author: Thanh Tung Nguyen
# Contact: tungstudies@gmail.com

import datetime

import pandas_market_calendars as mcal
import pytz

from src.autotrade.artifacts.enums import IntervalOption
from src.errors import ValueNotPresentException
import math


# DIVIDER: --------------------------------------
# INFO: MarketHour Concrete Class


class MarketHour:

    def __init__(self, exchange: str, interval_option: str):

        # INFO: Constructor Input Parameter Check
        if interval_option.lower() not in IntervalOption.interval_options():
            raise ValueNotPresentException(provided_value=interval_option.lower(),
                                           value_list=IntervalOption.interval_options())

        self.exchange = exchange
        self._exch: mcal.MarketCalendar = mcal.get_calendar(self.exchange)
        self._local_tz = self._exch.tz.zone
        self._interval_option = IntervalOption.get_interval(interval_option=interval_option)
        self._bar_gap_seconds = self._interval_option.value[1]

    # DIVIDER: Publicly Accessible Method Properties ----------------------------------------------
    @property
    def exchange_open(self):
        return datetime.datetime.now(tz=self._exch.tz).replace(hour=self._exch.open_time.hour,
                                                               minute=self._exch.open_time.minute,
                                                               second=0, microsecond=0)

    @property
    def exchange_close(self):
        return datetime.datetime.now(tz=self._exch.tz).replace(hour=self._exch.close_time.hour,
                                                               minute=self._exch.close_time.minute,
                                                               second=0, microsecond=0)

    @property
    def local_open(self):
        return self.exchange_open.astimezone()

    @property
    def local_close(self):
        return self.exchange_close.astimezone()

    @property
    def open_timestamp(self):
        return self.local_open.timestamp()

    @property
    def close_timestamp(self):
        return self.local_close.timestamp()

    @property
    def utc_open(self):
        return self.local_open.astimezone(pytz.UTC)

    @property
    def utc_close(self):
        return self.local_close.astimezone(pytz.UTC)

    # DIVIDER: Publicly Accessible Methods --------------------------------------------------------
    def is_open_now(self):
        if len(self._exch.schedule(start_date=datetime.datetime.utcnow().date(),
                                   end_date=datetime.datetime.utcnow().date())) > 0:
            return self.utc_open <= datetime.datetime.now(tz=pytz.UTC) <= self.utc_close
        else:
            return False

    @property
    def bar_gap_seconds(self):
        return self._bar_gap_seconds

    @property
    def bar_zero_timestamp(self):
        if datetime.datetime.now().timestamp() >= self.close_timestamp:
            return int(self.close_timestamp)
        else:
            time_diff = datetime.datetime.now().timestamp() - self.open_timestamp
            return int(self.open_timestamp + math.floor(time_diff / self._bar_gap_seconds) * self._bar_gap_seconds)

    @property
    def seconds_to_next_bar(self):
        return self.bar_zero_timestamp + self._bar_gap_seconds - datetime.datetime.now().timestamp()


# DIVIDER: --------------------------------------
# INFO: Usage Examples

if __name__ == '__main__':
    market_hour = MarketHour(exchange='NYSE', interval_option='5m')
    print(market_hour.bar_zero_timestamp())
    pass
