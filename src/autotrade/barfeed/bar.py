from typing import Optional


class Bar:
    def __init__(self, bar_dict: dict):
        self.timestamp: Optional[int] = None
        self.datetime: Optional[int] = None
        self.open: Optional[float] = None
        self.close: Optional[float] = None
        self.high: Optional[float] = None
        self.low: Optional[float] = None
        self.volume: Optional[int] = None
        self.interval: Optional[str] = None
        self.ticker_symbol: Optional[str] = None

        # this line of code must be at the end of the constructor to be able to overwrite the pre-declared attributes
        self.__dict__.update(bar_dict)

    def __repr__(self):
        return 'Bar({timestamp},{datetime},{open},{high},{low},{close},{volume},{interval},{ticker_symbol})'.format(
            timestamp=self.timestamp,
            datetime=self.datetime,
            open=self.open,
            high=self.high,
            low=self.low,
            close=self.close,
            volume=self.volume,
            interval=self.interval,
            ticker_symbol=self.ticker_symbol)

    def __str__(self):
        return 'Bar({datetime},C: {close},V: {volume},{frequency},{ticker_symbol})'.format(
            datetime=self.datetime,
            close=self.close,
            volume=self.volume,
            frequency=self.interval,
            ticker_symbol=self.ticker_symbol)

    def values(self):
        return {
            'timestamp': self.timestamp,
            'datetime': self.datetime,
            'open': self.open,
            'high': self.high,
            'low': self.low,
            'close': self.close,
            'volume': self.volume,
            'frequency': self.interval,
            'ticker': self.ticker_symbol
        }
