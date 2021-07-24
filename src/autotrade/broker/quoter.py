from abc import ABC, abstractmethod
from typing import Optional

from src.datafeed.questrade.questrade_api import QuesTradeApi


class IQuoter(ABC):

    @abstractmethod
    def set_quoter(self, ticker_symbol_alias: str):
        raise NotImplementedError()

    @abstractmethod
    def _get_quote(self):
        raise NotImplementedError()

    @property
    @abstractmethod
    def bid_price(self):
        raise NotImplementedError()

    @property
    @abstractmethod
    def bid_size(self):
        raise NotImplementedError()

    @property
    @abstractmethod
    def ask_price(self):
        raise NotImplementedError()

    @property
    @abstractmethod
    def ask_size(self):
        raise NotImplementedError()

    @property
    @abstractmethod
    def mid_price(self):
        raise NotImplementedError()

    @property
    @abstractmethod
    def price_gap(self):
        raise NotImplementedError()


class QuestradeQuoter(IQuoter):

    def __init__(self):
        self.ticker_symbol_alias = None
        self.questrade_api: Optional[QuesTradeApi] = None

    def set_quoter(self, ticker_symbol_alias: str):
        self.ticker_symbol_alias = ticker_symbol_alias
        self.questrade_api = QuesTradeApi(self.ticker_symbol_alias)

    def _get_quote(self):
        return self.questrade_api.get_quotes()

    @property
    def bid_price(self):
        return self._get_quote()['bidPrice']

    @property
    def bid_size(self):
        return self._get_quote()['bidSize']

    @property
    def ask_price(self):
        return self._get_quote()['askPrice']

    @property
    def ask_size(self):
        return self._get_quote()['askSize']

    @property
    def mid_price(self):
        quote = self._get_quote()
        mid_price = (quote['bidPrice'] * quote['bidSize'] + quote['askPrice'] * quote['askSize']) / (
                    quote['bidSize'] + quote['askSize'])
        return round(mid_price, 2)

    @property
    def price_gap(self):
        quote = self._get_quote()
        price_gap = quote['askPrice'] - quote['bidPrice']
        return price_gap


if __name__ == '__main__':
    qq = QuestradeQuoter()
    qq.set_quoter('CTS.TO')
    print(qq.mid_price)
