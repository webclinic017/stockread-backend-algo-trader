from ta.momentum import RSIIndicator

from src.autotrade import Strategy
from src.autotrade import Indicator


class RSIStrategy(Strategy):

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

