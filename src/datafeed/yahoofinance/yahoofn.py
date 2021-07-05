from typing import List, Optional
import yfinance as yf
import pandas as pd
import numpy as np


class YahooFinance:
    def __init__(self, multiple_tickers: bool, ticker_symbol: Optional[str] = None,
                 ticker_list: Optional[List[str]] = None):
        self.multiple_tickers = multiple_tickers

        if self.multiple_tickers:
            if not ticker_list:
                raise Exception('Missing "ticker ticker_list" constructor input parameter')
            self.ticker_list = ticker_list

        else:
            if not ticker_symbol:
                raise Exception('Missing "ticker symbol" constructor input parameter')
            self.ticker_symbol = ticker_symbol

        self.df_headers: Optional[List[str]] = None

    def set_dataframe_headers(self, df_headers: List[str]):
        self.df_headers = df_headers

    def _format_dataframe(self, interval, ticker_symbol, dataframe: pd.DataFrame):
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

        if not interval:
            raise Exception('Missing data "interval" method input parameter')
        if not ticker_symbol:
            raise Exception('Missing data "ticker_symbol" method input parameter')

        dataframe = dataframe.assign(interval=interval)
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

    def get_candle_dataframes(self, start=None, end=None, actions=False, threads=True, group_by='ticker', period="max",
                              show_errors=True, interval="1d", proxy=None, rounding=False):

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

        if self.multiple_tickers:
            separator = ' '
            tickers = separator.join(self.ticker_list)
            combined_df = yf.download(tickers, start=start, end=end, actions=actions, threads=threads,
                                      group_by=group_by, period=period, show_errors=show_errors,
                                      interval=interval, proxy=proxy, rounding=rounding)

            ticker_dataframes = dict()

            for ticker in self.ticker_list:
                ticker_df = combined_df[ticker]
                ticker_dataframes[ticker] = self._format_dataframe(interval, ticker, ticker_df)

            return ticker_dataframes

        else:
            single_df = yf.download(self.ticker_symbol, start=start, end=end, actions=actions, threads=threads,
                                    group_by=group_by, period=period, show_errors=show_errors,
                                    interval=interval, proxy=proxy, rounding=rounding)
            return self._format_dataframe(interval, self.ticker_symbol, single_df)


if __name__ == '__main__':
    pass
    # yf_dfs = YahooFinance(multiple_tickers=True, ticker_list=['AAPL', 'MSFT'])
    # yf_dfs = YahooFinance(multiple_tickers=False, ticker_symbol='AAPL')
    # ticker_dfs = yf_dfs.get_candle_dataframes(period="1y")
    # print(ticker_dfs)
