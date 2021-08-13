# Copyright (C) 2021-2030 StockRead Inc.
# Author: Thanh Tung Nguyen
# Contact: tungstudies@gmail.com

import pytz
import datetime
import pandas_market_calendars as mcal


# DIVIDER: --------------------------------------
# INFO: MarketHour Concrete Class

class MarketHour:

    def __init__(self, exchange: str):
        self.exchange = exchange
        self._exch: mcal.MarketCalendar = mcal.get_calendar(self.exchange)
        self._local_tz = self._exch.tz.zone

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


# DIVIDER: --------------------------------------
# INFO: Usage Examples

if __name__ == '__main__':
    market_hour = MarketHour(exchange='NYSE')
    pass
