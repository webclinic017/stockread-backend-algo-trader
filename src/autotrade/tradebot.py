import datetime
from enum import Enum
from typing import Optional, List

import pandas

from src.autotrade.broker.brok_base import IBroker
from src.autotrade.broker.order import Order
from src.autotrade.broker.position import Position
from src.autotrade.broker.quoter import IQuoter
from src.autotrade.broker.sizer import Sizer, SizerType
from src.autotrade.broker.stoploss import StopLoss
from src.autotrade.errors import InvalidBrokerSetting
from src.autotrade.strategy import BaseStrategy
from src.datafeed.yahoofinance.yahoofn import ICandleFeed

# Typing without cyclic imports
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.autotrade.autotrader import AutoTrader


class TradeStatus(Enum):
    """ TradeStatus: specifies the current status of the trade (ACTIVATED, CANCELLED, STOPPED, RESUMED, CLOSED)."""

    ACTIVATED = 'Activated'
    CANCELLED = 'Cancelled'
    STOPPED = 'Stopped'
    RESUMED = 'Resumed'
    CLOSED = 'Closed'


class TradingMode(Enum):
    """ TradingMode: Trading modes allow you to choose if you want to real trade or test trade.
    The following is a list of trading modes available.

    - LIVE: is a real trade and executed real-time data and real brokers.

    - BACK: is a test trade and will be executed with historical data and a test broker.

    - PILOT: is a test trade and will be executed with real-time data and a test broker.
    """

    LIVE = 'Live'
    BACK = 'Back'
    PILOT = 'Pilot'


class TradingDurationType(Enum):
    """ TradeDurationType: Trading durations allow you to control how long your trade remains active.
    The following is a list of durations available in a certain trade.

    - DAY: The trade will remain active until the end of the current trading day. The trade is terminated at the end
           of the trading day

    - GTD: Good ‘till date - the trade will remain active until the specified date. The trade will be terminated at
           the end of the chosen day

    - GTC: Good ‘till cancelled - the trade will remain active until it is manually cancelled
    """

    DAY = 'DAY'
    GTD = 'GTD'
    GTC = 'GTC'


class TradeBot:

    def __init__(self, codename: str, trading_mode: TradingMode, trading_symbol: str, ticker_alias: str, currency: str,
                 country=None, exchange=None, reps: int = 1, duration_type=TradingDurationType.DAY):

        """
        :param codename: a unique name (unique identifier) for each trade created. Ex. "shopify_pilot_trading".
        :type codename: str

        :param trading_mode: specify the trading modes if it is LIVE, BACK or PIVOT
        :type trading_mode: TradingMode

        :param trading_symbol: the trading instrument resembled by the ticker symbol.
        Where ***trading_symbol*** is the ticker of the company or ETF. Ex. AMZN, APPL, GOOGL, SPY.
        :type trading_symbol: str

        :param ticker_alias: for some brokers, it is required to provide exchange suffix to differentiate same
        ticker symbols of one exchange from the others. Ex. SHOP.TO vs SHOP.
        :type ticker_alias: str

        :param exchange: country/exchange in which the trading ticker symbol is listed
        :type exchange: str

        :param reps: the number of times to perform the trade. Default is 1 (one round of buy & sell)
        :type reps: int

        :param duration_type: specify the durations which controls how long your trade remains active. Default is
        TradingDurationType.DAY
        :type duration_type: TradingDurationType
        """

        self._codename = codename
        self._trading_mode = trading_mode
        self._trading_symbol = trading_symbol
        self._ticker_alias = ticker_alias
        self._currency = currency
        self._exchange = exchange
        self._country = country
        self._reps = reps
        self._reps_count = 0
        self._duration_type = duration_type

        self._status: Optional[TradeStatus] = None

        # define compositions:
        self._trader: Optional['AutoTrader'] = None
        self._sizer: Optional[Sizer] = None
        self._strategy: Optional[BaseStrategy] = None
        self.position = Position()
        self._broker: Optional[IBroker] = None

        # quoter is used to get trading price
        self._quoter: Optional[IBroker] = None

        self._datafeed: Optional[ICandleFeed] = None
        self._data: Optional[pandas.DataFrame] = None

        # order setup #
        self.unsettled_order: Optional[Order] = None
        self.filled_orders: List[Order] = list()
        self.discarded_orders: List[Order] = list()
        self.unexecuted_sls: List[StopLoss] = list()
        self.executed_sls: List[StopLoss] = list()
        self.killed_sls: List[StopLoss] = list()

    def add_order(self, order: Order):
        if not self.unsettled_order:
            self.unsettled_order = order
        else:
            raise Exception('There is already an active unsettled order in the trade. New orders cannot be added')

    # def update_order_status(self, order: Order):
    #     if order.ref_id:
    #         if order.state == self.unsettled_order.size:
    #             print(f'Order status is still unchanged: {self.unsettled_order}')
    #         else:
    #             self.unsettled_order.state = order.state
    #             if self.unsettled_order.is_settled():




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

        pre_market_start_time = datetime.datetime.utcnow().replace(
            hour=8,
            minute=00,
            second=00
        ).timestamp()

        market_start_time = datetime.datetime.utcnow().replace(
            hour=13,
            minute=30,
            second=00
        ).timestamp()

        right_now = datetime.datetime.utcnow().timestamp()

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

        post_market_start_time = datetime.datetime.utcnow().replace(
            hour=00,
            minute=00,
            second=00
        ).timestamp()

        market_end_time = datetime.datetime.utcnow().replace(
            hour=20,
            minute=00,
            second=00
        ).timestamp()

        right_now = datetime.datetime.utcnow().timestamp()

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

        market_start_time = datetime.datetime.utcnow().replace(
            hour=13,
            minute=30,
            second=00
        ).timestamp()

        market_end_time = datetime.datetime.utcnow().replace(
            hour=20,
            minute=00,
            second=00
        ).timestamp()

        right_now = datetime.datetime.utcnow().timestamp()

        if market_end_time >= right_now >= market_start_time:
            return True
        else:
            return False

    @property
    def codename(self):
        return self._codename

    @property
    def trading_symbol(self):
        return self._trading_symbol

    @property
    def currency(self):
        return self._currency


    def activate(self):
        self._status = TradeStatus.ACTIVATED

    def cancel(self):
        self._status = TradeStatus.CANCELLED

    def stop(self):
        self._status = TradeStatus.STOPPED

    def resume(self):
        self._status = TradeStatus.STOPPED

    def close(self):
        self._status = TradeStatus.CLOSED

    def bind_to_trader(self, trader: 'AutoTrader'):
        self._trader = trader

    @property
    def trader(self):
        if self._trader:
            return self._trader
        else:
            raise Exception('Trader instance has not been bound to the trade')

    def set_sizer(self, sizer_type: SizerType, value):
        """set a ``Sizer`` class which is the default sizer for any
        strategy added to each trade
        """
        if self._sizer:
            self._sizer.set_new(sizer_type, value)
        else:
            self._sizer = Sizer(sizer_type=sizer_type, value=value)

    @property
    def sizer(self):
        if self._sizer:
            return self._sizer
        else:
            raise Exception('A sizer has not been provided (set) to the trade')

    def set_quoter(self, quoter: Optional[IQuoter]):
        """set a ``Strategy`` class to the trade for a single pass run.
        Instantiation will happen during ``run`` time.
        """
        self._quoter = quoter
        self._quoter.set_quoter(self._ticker_alias)

    @property
    def quoter(self):
        if self._quoter:
            return self._quoter
        else:
            raise Exception('A quoter has not been provided (set) to the trade')

    def set_broker(self, broker: IBroker):
        """
        Sets a specific ``broker`` instance for this strategy
        """
        is_live = True if self._trading_mode == TradingMode.LIVE else False
        if is_live == broker.is_live:
            broker.bind_to_trade(self)
            self._broker = broker
        else:
            raise InvalidBrokerSetting

    @property
    def broker(self):
        """
        Returns the broker instance.
        """
        return self._broker

    def set_data(self, datafeed: ICandleFeed):
        self._datafeed = datafeed
        if self._trading_mode == TradingMode.BACK:
            self._data = self._datafeed.get_candles()

    @property
    def data(self):
        if self._trading_mode == TradingMode.BACK:
            return self._data
        else:
            return self._datafeed.get_candles()


    def set_strategy(self, strategy: Optional[BaseStrategy]):
        """set a ``Strategy`` class to the trade for a single pass run.
        Instantiation will happen during ``run`` time.
        """
        strategy.bind_to_trade(self)
        self._strategy = strategy

    def execute(self):
        # TODO: To be implemented.
        raise NotImplementedError()


if __name__ == '__main__':
    pass
