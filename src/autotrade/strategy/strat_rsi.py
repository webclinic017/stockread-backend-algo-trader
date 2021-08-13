from src.autotrade.strategy.strat_base import BaseStrategy


class RSIStrategy(BaseStrategy):
    def next(self):
        print(self.bars[0])