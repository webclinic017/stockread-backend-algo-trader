import numpy as np
import pandas as pd
import yfinance as yf
from yahooquery import Ticker

from src.datafeed.yahoofinance.yf_base import ICandleFeed, PublicBase


class PYahooFinance(PublicBase, ICandleFeed):

    def __init__(self, period=None, is_fromto: bool = False, start=None, end=None):
        super().__init__(period=period, is_fromto=is_fromto, start=start, end=end)

    def set_interval(self, interval: str):
        if interval in ['1m', '2m', '5m', '15m', '30m', '1h', '4h', '1d']:
            self._interval = interval
        else:
            raise ValueError('Invalid interval type')

    def set_ticker_symbol(self, ticker_symbol: str):
        self._ticker_symbol = ticker_symbol

    def _format_dataframe(self, dataframe: pd.DataFrame):
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

        dataframe = dataframe.assign(interval=self._interval)
        dataframe = dataframe.assign(ticker_symbol=self.ticker_symbol)

        if not self._df_headers:
            # re-order columns
            return dataframe[
                ['timestamp', 'datetime', 'open', 'high', 'low', 'close', 'volume', 'interval', 'ticker_symbol']]
        else:
            for header in self._df_headers:
                if header not in dataframe.columns:
                    raise Exception(f'The {header} field does not exist in the dataframe column names')

            return dataframe[[self._df_headers]]

    def get_candles(self):
        if self._range_type:
            if not(self._start and self._end):
                raise ValueError("Missing 'start' & 'end' parameters while requesting historical data")
        else:
            if not self._period:
                raise ValueError("Missing 'period' parameter while requesting historical data")

        single_df = yf.download(self.ticker_symbol, start=self._start, end=self._end, actions=False, threads=True,
                                group_by='ticker', period=self._period, show_errors=True,
                                interval=self._interval, proxy=None, rounding=False)
        return self._format_dataframe(single_df)

    def get_number_candles(self, number: int) -> pd.DataFrame:
        days = super()._compute_data_days(number)
        period = f'{days}d'
        single_df = yf.download(self.ticker_symbol, start=self._start, end=self._end, actions=False, threads=True,
                                group_by='ticker', period=period, show_errors=True,
                                interval=self._interval, proxy=None, rounding=False)
        df = self._format_dataframe(single_df).tail(number)
        df.reset_index(level=0, drop=True, inplace=True)
        return df

    @property
    def ticker_symbol(self):
        return self._ticker_symbol


class PYahooQuery(PublicBase, ICandleFeed):
    def __init__(self, period=None, is_fromto: bool = False, start=None, end=None):
        super().__init__(period=period, is_fromto=is_fromto, start=start, end=end)

    def set_interval(self, interval: str):
        if interval in ['1m', '2m', '5m', '15m', '30m', '1h', '4h', '1d']:
            self._interval = interval
        else:
            raise ValueError('Invalid interval type')

    def set_ticker_symbol(self, ticker_symbol: str):
        self._ticker_symbol = ticker_symbol

    def _format_dataframe(self, dataframe: pd.DataFrame):
        # convert datetime index column of a pandas dataframe into a normal column
        dataframe.reset_index(level=0, inplace=True)
        # lowercase dataframe column headers
        dataframe.columns = map(str.lower, dataframe.columns)
        dataframe['datetime'] = dataframe.index
        dataframe.reset_index(level=0, drop=True, inplace=True)

        # rename dataframe column header from 'symbol' to 'ticker_symbol'
        dataframe = dataframe.rename(columns={'symbol': 'ticker_symbol'})

        # add 'interval' column
        dataframe = dataframe.assign(interval=self._interval)

        # add 'timestamp' column translated from 'datetime' column
        dataframe = dataframe.assign(timestamp=dataframe['datetime'].values.astype(np.int64) // 10 ** 9)

        if not self._df_headers:
            # re-order columns
            return dataframe[
                ['timestamp', 'datetime', 'open', 'high', 'low', 'close', 'volume', 'interval', 'ticker_symbol']]
        else:
            for header in self._df_headers:
                if header not in dataframe.columns:
                    raise Exception(f'The {header} field does not exist in the dataframe column names')

            return dataframe[[self._df_headers]]

    def get_candles(self):

        if self._range_type:
            if not(self._start and self._end):
                raise ValueError("Missing 'start' & 'end' parameters while requesting historical data")
        else:
            if not self._period:
                raise ValueError("Missing 'period' parameter while requesting historical data")

        single_ticker = Ticker(self.ticker_symbol, asynchronous=False)
        single_df = single_ticker.history(period=self._period, interval=self._interval, start=self._start, end=self._end)
        return self._format_dataframe(single_df)

    def get_number_candles(self, number: int) -> pd.DataFrame:
        days = super()._compute_data_days(number)
        period = f'{days}d'
        single_ticker = Ticker(self.ticker_symbol, asynchronous=False)
        single_df = single_ticker.history(period=period, interval=self._interval, start=self._start, end=self._end)
        df = self._format_dataframe(single_df).tail(number)
        df.reset_index(level=0, drop=True, inplace=True)
        return df

    @property
    def ticker_symbol(self):
        return self._ticker_symbol


if __name__ == '__main__':
    # add a datafeed

    datafeed = PYahooFinance()
    datafeed.set_ticker_symbol('AC.TO')
    datafeed.set_interval('5m')
    # datafeed.get_candles()
    print(datafeed.get_number_candles(500))
