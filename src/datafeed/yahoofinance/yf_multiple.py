pass
'''
from typing import Set, List

from src.datafeed.yahoofinance.yf_base import PublicBase
import yfinance as yf
import pandas as pd


class PublicMultipleTickerYF(PublicBase):

    def __init__(self, ticker_set: [Set[str]], interval="15m", is_fromto: bool = False, period="5d",
                 start=None, end=None):
        super().__init__(interval=interval, is_fromto=is_fromto, period=period, start=start, end=end)
        self._ticker_set = ticker_set

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

    def get_candles(self):
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
        tickers = separator.join(self._ticker_set)
        combined_df = yf.download(tickers, start=self.start, end=self.end, actions=False, threads=True,
                                  group_by='ticker', period=self.period, show_errors=True,
                                  interval=self.interval, proxy=None, rounding=False)

        ticker_dataframes = dict()

        for ticker in self._ticker_set:
            ticker_df = combined_df[ticker]
            ticker_dataframes[ticker] = self._format_dataframe(ticker, ticker_df)

        return ticker_dataframes
'''