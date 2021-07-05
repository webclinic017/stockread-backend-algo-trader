from datetime import datetime
from typing import Optional, List

from src.autotrade import BrokerBase
from src.autotrade.errors import InvalidBrokerTradeSetting
from src.autotrade import Strategy
from src.autotrade import RSIStrategy


class AutoTrader:
    def __init__(self):
        self._is_live_trading: Optional[bool] = None
        self._strategy: Optional[Strategy] = None
        self._broker: Optional[BrokerBase] = None
        self._sizer: int = 0
        self._data: Optional[List[dict]] = None

    def _set_live_trading(self, is_live_trading: bool):
        self._is_live_trading = is_live_trading

    @property
    def pre_market_open(self) -> bool:
        """Checks if pre-market is open.
        Uses the datetime module to create US Pre-Market Equity hours in
        UTC time.
        Usage:
        ----
           trading_robot = WealthSimpleTradingBot()
           pre_market_open_flag = trading_robot.pre_market_open
           print(pre_market_open_flag)

        Returns:
        ----
        bool -- True if pre-market is open, False otherwise.
        """

        pre_market_start_time = datetime.utcnow().replace(
            hour=8,
            minute=00,
            second=00
        ).timestamp()

        market_start_time = datetime.utcnow().replace(
            hour=13,
            minute=30,
            second=00
        ).timestamp()

        right_now = datetime.utcnow().timestamp()

        if market_start_time >= right_now >= pre_market_start_time:
            return True
        else:
            return False

    @property
    def post_market_open(self):
        """Checks if post-market is open.
        Uses the datetime module to create US Post-Market Equity hours in
        UTC time.
        Usage:
        ----
            trading_robot = WealthSimpleTradingBot()
            post_market_open_flag = trading_robot.post_market_open
            print(post_market_open_flag)

        Returns:
        ----
        bool -- True if post-market is open, False otherwise.
        """

        post_market_start_time = datetime.utcnow().replace(
            hour=00,
            minute=00,
            second=00
        ).timestamp()

        market_end_time = datetime.utcnow().replace(
            hour=20,
            minute=00,
            second=00
        ).timestamp()

        right_now = datetime.utcnow().timestamp()

        if post_market_start_time >= right_now >= market_end_time:
            return True
        else:
            return False

    @property
    def regular_market_open(self):
        """Checks if regular market is open.
        Uses the datetime module to create US Regular Market Equity hours in
        UTC time.
                Usage:
        ----
            trading_robot = WealthSimpleTradingBot()
            market_open_flag = trading_robot.market_open
            print(market_open_flag)

        Returns:
        ----
        bool -- True if post-market is open, False otherwise.
        """

        market_start_time = datetime.utcnow().replace(
            hour=13,
            minute=30,
            second=00
        ).timestamp()

        market_end_time = datetime.utcnow().replace(
            hour=20,
            minute=00,
            second=00
        ).timestamp()

        right_now = datetime.utcnow().timestamp()

        if market_end_time >= right_now >= market_start_time:
            return True
        else:
            return False

    def set_broker(self, broker: BrokerBase, is_live_trading: bool = True):
        """
        Sets a specific ``broker`` instance for this strategy
        """
        if is_live_trading == broker.IS_LIVE:
            self._set_live_trading(is_live_trading)
            self._broker = broker
        else:
            raise InvalidBrokerTradeSetting

    @property
    def broker(self):
        """
        Returns the broker instance.
        """
        return self._broker

    def adddata(self, data):
        """
        Adds a ``List[dict]`` instance to the mix.
        """
        self._data = data
        if self._strategy:
            self._strategy.set_bars(self._data)

    def set_strategy(self, strategy: Strategy):
        """
        Sets a specific ``strategy`` instance for this auto trading
        """

        self._strategy = strategy
        if self._data:
            self._strategy.set_bars(self._data)

    @property
    def strategy(self):
        return self._strategy


    def run(self):
        """
        The core method to perform backtesting or livetrading

        If ``autotrader`` has not data the method will immediately bail out.
        """

        if not self._data:
            return  # nothing can be run

        self._strategy.setup()

        for _ in self._data:
            print(_)
            next(self._strategy)


    # def addsizer(self, sizercls, *args, **kwargs):
    #     '''Adds a ``Sizer`` class (and args) which is the default sizer for any
    #     strategy added to cerebro
    #     '''
    #     self.sizers[None] = (sizercls, args, kwargs)


if __name__ == '__main__':
    from src.datafeed import YahooFinanceApi

    trading_robot = AutoTrader()
    yf_api = YahooFinanceApi(region="CA", ticker_symbol="SHOP.TO")
    yf_api.set_range_by_default()
    yf_api.set_interval()
    data = yf_api.get_candles()

    trading_robot.adddata(data)
    trading_robot.set_strategy(RSIStrategy())
    trading_robot.run()


