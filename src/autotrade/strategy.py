from abc import abstractmethod, ABC


from ta.momentum import RSIIndicator

from src.autotrade.barfeed.barframe import BarFrame
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.autotrade.tradebot import TradeBot
    
    
class BaseStrategy(ABC):

    def __init__(self):
        # set from Trade class
        self._trade_bot = None
        self._broker = None

        self._bar_frame = None
        self._bars = None
        self._is_prep_done: bool = False

    def bind_to_trade(self, trade_bot: 'TradeBot'):
        self._trade_bot = trade_bot

    def set_broker(self, broker):
        self._broker = broker

    def set_bars(self, data):
        self._bar_frame = BarFrame(data)

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


class RSIStrategy(BaseStrategy):

    def prepare(self):
        self._bar_frame.add_fields(rsi=RSIIndicator(self._bar_frame.close, window=14, fillna=True).rsi())
        self._bar_frame.add_fields(rsi_uphit_70=Indicator(self._bar_frame.frame['rsi']).is_up_hit(70))

    def next(self):
    #     print('bar 0:', self.bars[0])
    #     print('bar -1:', self.bars[-1])
        rsi = self.bars[0].rsi
        price = self.bars[0].close
        if rsi and self.bars[0].rsi_uphit_70 == 1:
            # pass
            print(f'RSI: {self.bars[0].rsi} and close price: {price}')

