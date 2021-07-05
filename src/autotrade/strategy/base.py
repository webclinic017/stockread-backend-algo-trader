from abc import ABC, abstractmethod
from typing import Optional, Union

from src.autotrade import BarFrame
from src.autotrade import BrokerBase, BrokerBaseInterface, BrokerLiveInterface


class Strategy(ABC):

    def __init__(self):
        self._bar_frame: Optional[BarFrame] = None
        self._bars: Optional[BarFrame] = None
        self._broker: Union[BrokerBaseInterface, BrokerLiveInterface, None] = None
        self._is_prep_done: bool = False

    def set_bars(self, data):
        self._bar_frame = BarFrame(data)

    def set_broker(self, broker: BrokerBase):
        self._broker = broker

    def __iter__(self):
        return self

    def __next__(self):
        if self._is_prep_done:
            self._bars = next(self._bar_frame)
            return self.next()
        else:
            raise Exception('It is required to run setup() first before running next()')

    @property
    def bars(self):
        return self._bars

    @abstractmethod
    def prepare(self):
        raise NotImplementedError()

    def setup(self):
        self.prepare()
        self._is_prep_done = True

    @abstractmethod
    def next(self):
        raise NotImplementedError()

    def market_buy(self, ticker_symbol, quantity):
        self._broker.market_buy(ticker_symbol, quantity)

    def market_sell(self, ticker_symbol, quantity):
        self._broker.market_buy(ticker_symbol, quantity)

    def limit_buy(self, ticker_symbol, limit_price, quantity):
        self._broker.limit_buy(ticker_symbol, limit_price, quantity)

    def limit_sell(self, ticker_symbol, stop_price, limit_price, quantity):
        self._broker.limit_sell(ticker_symbol, stop_price, limit_price, quantity)

    def stop_limit_buy(self, ticker_symbol, stop_price, limit_price, quantity):
        self._broker.stop_limit_buy(ticker_symbol, stop_price, limit_price, quantity)

    def stop_limit_sell(self, ticker_symbol, stop_price, limit_price, quantity):
        self._broker.stop_limit_sell(ticker_symbol, stop_price, limit_price, quantity)

    # def start(self):
    #     pass
    #
    # def stop(self):
    #     pass
    #
    # def _notify_order(self, order):
    #     pass
    #
    # def notify_trade(self, trade):
    #     pass
    #
    # def notify_cashvalue(self, cash, value):
    #     pass
    #
    # def notify_fund(self, cash, value, fundvalue, shares):
    #     pass
    #
    # def close(self):
    #     pass
    #
    # def cancel(self):
    #     pass
