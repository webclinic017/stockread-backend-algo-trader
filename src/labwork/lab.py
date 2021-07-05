from collections import deque
from typing import Optional

from ta.momentum import RSIIndicator
from ta.trend import

from src.autotrade.barfeed.bar import Bar
from src.autotrade.barfeed.barframe import BarFrame
from src.datafeed.yahoofinance.data_api import YahooFinanceApi

from src.utility.logger import Logger


class DataBar:
    def __init__(self):
        self.timestamp: Optional[int] = None
        self.datetime: Optional[int] = None
        self.open: Optional[float] = None
        self.close: Optional[float] = None
        self.high: Optional[float] = None
        self.low: Optional[float] = None
        self.volume: Optional[int] = None
        self.ticker_symbol: Optional[str] = None

    def set_bar(self, bar_dict):
        self.__dict__.update(bar_dict)


class Looper:
    def __init__(self):
        self.mylist = iter([1, 3, 5, 4, 6, 9])

    def __iter__(self):
        return self

    def __next__(self):  # Python 2: def next(self)
        next(self.mylist)


# Python program to demonstrate writing of __repr__ and
# __str__ for user defined classes

# A user defined class to represent Complex numbers
class Complex:

    # Constructor
    def __init__(self, real, imag):
        self.real = real
        self.imag = imag

    # For call to repr(). Prints object's information
    def __repr__(self):
        return 'Rational(%s, %s)' % (self.real, self.imag)

        # For call to str(). Prints readable form

    def __str__(self):
        return '%s + i%s' % (self.real, self.imag)

    # Driver program to test above


def test2():
    t = Complex(10, 20)
    logger = Logger()
    logger.info("Shut up")
    # Same as "print t"
    print(t)
    print(str(t))
    print(repr(t))


def test():
    yf_api = YahooFinanceApi(region="CA", ticker_symbol="SHOP.TO")
    yf_api.set_range_by_default("3mo")
    yf_api.set_interval("1d")
    data = yf_api.get_candles()
    print(data)
    bars = BarFrame(data)
    chop
    bars.add_fields(rsi=RSIIndicator(bars.close).rsi())
    count = 0
    while count < 4:
        print(next(bars))
        count +=1

    # items = sf.frame.to_dict('index').values()
    # for each in items:
    #     print(each)

def test6():
    yf_api = YahooFinanceApi(region="CA", ticker_symbol="SHOP.TO")
    yf_api.set_range_by_default("3mo")
    yf_api.set_interval("1d")
    data = yf_api.get_candles()
    data[0]['rsi'] = 30
    databar = Bar()
    databar.set_bar(data[0])
    print(databar.rsi)


def test1():
    obj_dict = {'timestamp': 1624541400, 'open': 1860.0, 'high': 1863.2099609375, 'low': 1860.0,
                'close': 1863.2099609375, 'volume': 0, 'interval': '1m', 'ticker_symbol': 'SHOP.TO', 'rsi': None}
    # bar = Bar(obj_dict)
    # print(bar.timestamp)


def test3():
    for c in Looper():
        print(c)


def test4():
    mylist = [1, 2, 3, 4, 5]
    de = deque([])
    for each in mylist:
        de.appendleft(each)
        print(f'before: {de}')
        print(f'previous: {de[-1]} >> current: {de[0]}')
        de.append(de.popleft())
        print(f'after: {de}')


def test5(signal, *args):
    signals = list()
    signals.append(signal)
    signals.extend(args)
    for sgn in signals:
        print(sgn)


if __name__ == '__main__':
    test2()
