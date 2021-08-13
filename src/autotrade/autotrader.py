from src.autotrade.trade import Trade


class AutoTrader:
    def __init__(self):
        self._cash: float = 0.0
        self._active_trades = dict()
        self._settled_trade = dict()

    @property
    def cash(self):
        """Returns the current cash"""
        return self._cash

    @property
    def remaining_cash(self):
        cash_used = 0
        for trade in self._active_trades.values():
            cash_used += trade.sizer.amount
        return self._cash - cash_used

    @property
    def portfolio_value(self):
        """Returns the current cash"""
        # TODO: To be implemented
        return

    def set_cash(self, cash: float):
        """Sets the cash parameter"""
        if self._cash:
            raise ValueError('Invalid cash budget setup. Cash budget can only be added once before trading.')
        self._cash = cash

    def add_cash(self, cash):
        """Add/Remove cash to the system (use a negative value to remove)"""
        self._cash += cash

    def add_trade(self, trade: Trade):

        """set a ``Sizer`` class which is the default sizer for any
        strategy added to each trade
        """
        trade.bind_to_trader(self)
        self._active_trades[trade.codename] = trade

    def remove_trade(self):
        pass


    def run(self):
        """
        The core method to perform backtesting or livetrading

        If ``autotrader`` has not data the method will immediately bail out.
        """
        # TODO: To be implemented
        pass


if __name__ == '__main__':
    pass
