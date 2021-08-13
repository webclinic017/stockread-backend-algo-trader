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
        return 'Bar({timestamp}, {datetime}, {open}, {high}, {low}, {close}, {volume}, {interval}, {ticker_symbol})'.format(
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
        tojoin = list()
        tojoin.append('ClassType: {}'.format(type(self).__name__))
        tojoin.append('TickerSymbol: {}'.format(self.ticker_symbol))
        tojoin.append('Timestamp: {}'.format(self.timestamp))
        tojoin.append('Datetime: {}'.format(self.datetime))
        tojoin.append('OpenPrice: {}'.format(self.open))
        tojoin.append('HighPrice: {}'.format(self.high))
        tojoin.append('LowPrice: {}'.format(self.low))
        tojoin.append('ClosePrice: {}'.format(self.close))
        tojoin.append('Volume: {}'.format(self.volume))
        tojoin.append('Interval: {}'.format(self.interval))

        return ', '.join(tojoin)

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
