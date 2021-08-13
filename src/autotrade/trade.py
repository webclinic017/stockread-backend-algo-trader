import datetime
from enum import Enum
from typing import Optional, List
# Typing without cyclic imports
from typing import TYPE_CHECKING

from src.autotrade.artifacts.gain_loss import GainLossTracker
from src.autotrade.artifacts.market_hours import MarketHour
from src.autotrade.bars.barfeed import BarFeed
from src.autotrade.broker.base_broker import IBroker
from src.autotrade.artifacts.order import Order
from src.autotrade.artifacts.position import Position
from src.autotrade.errors import InvalidBrokerSetting
from src.autotrade.artifacts.quoter import IQuoter
from src.autotrade.artifacts.sizer import Sizer
from src.autotrade.strategy.strat_base import BaseStrategy
from src.datafeed.yahoofinance.yf_single import ICandleFeed, PYahooFinance

if TYPE_CHECKING:
    from src.autotrade.autotrader import AutoTrader


# TODO: process commission gainloss in tradebot and put in to resp order

class IntervalOption(Enum):
    I_1MIN = ('1m', 60)
    I_2MINS = ('2m', 120)
    I_5MINS = ('5m', 300)
    I_15MINS = ('15m', 900)
    I_30MINS = ('30m', 1800)
    I_1HOUR = ('1h', 3600)
    I_4HOURS = ('4h', 14400)
    I_1DAY = ('1d', 86400)


class TradeStatus(Enum):
    """ TradeStatus: specifies the current status of the trade (ACTIVATED, CANCELLED, STOPPED, RESUMED, CLOSED)."""

    ACTIVATED = 'Activated'
    CANCELLED = 'Cancelled'
    PAUSED = 'Stopped'
    RESUMED = 'Resumed'
    CLOSED = 'Closed'


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


class Trade:
    """Keeps track of the life of a trade: broker, strategy, datafeed, orders, commission (and value?)"""

    def __init__(self, codename: str, is_live_trade: bool, trading_symbol: str, ticker_alias: str, currency: str,
                 data_interval: IntervalOption, interval_number: int, exchange: str,
                 country=None, reps: int = 1, duration_type=TradingDurationType.DAY):

        """
        :param codename: a unique name (unique identifier) for each trade created. Ex. "shopify_pilot_trading".
        :type codename: str

        :param is_live_trade: specify the trading modes if it's a LIVE trade or not. LIVE: is a real trade and executed
        real-time data and real brokers. A test trade (NOT LIVE) and will be executed with historical data and a test
        broker.
        :type is_live_trade: bool

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
        self._is_live_trade = is_live_trade
        self._trading_symbol = trading_symbol
        self._ticker_alias = ticker_alias
        self._currency = currency

        # data interval setup
        self._data_interval = data_interval
        self._interval_number = interval_number
        self._last_refresh_timestamp = None

        # setup exchange and market hour
        self._exchange = exchange
        self._market_hour: MarketHour = MarketHour(exchange)
        self._country = country

        # trade reps setup
        self._reps = reps
        self._filled_buy_count = 0
        self._filled_sell_count = 0

        self._duration_type = duration_type
        self._status: Optional[TradeStatus] = None

        # define compositions:
        self._trader: Optional['AutoTrader'] = None
        self._sizer: Optional[Sizer] = None
        self._strategy: Optional[BaseStrategy] = None
        self._position = Position(self._trading_symbol)
        self._broker: Optional[IBroker] = None
        self._gls_tracker: Optional[GainLossTracker] = None  # gain-loss tracker is used to track trading gain or loss

        self._quoter: Optional[IBroker] = None  # quoter is used to get trading price

        self._datafeed: Optional[ICandleFeed] = None
        self._barfeed: Optional[BarFeed] = None
        self.set_data()

        # order setup #
        self.active_order: Optional[Order] = None
        self.filled_orders: List[Order] = list()
        self.discarded_orders: List[Order] = list()

    # TRADE ATTRIBUTES
    @property
    def codename(self):
        return self._codename

    @property
    def trading_symbol(self):
        return self._trading_symbol

    @property
    def is_live_trade(self):
        return self._is_live_trade

    @property
    def currency(self):
        return self._currency

    @property
    def position(self):
        return self._position

    @property
    def trader(self):
        if self._trader:
            return self._trader
        else:
            raise Exception('Trader instance has not been bound to the trade')

    @property
    def sizer(self):
        if self._sizer:
            return self._sizer
        else:
            raise Exception('A sizer has not been provided (set) to the trade')

    @property
    def quoter(self):
        if self._quoter:
            return self._quoter
        else:
            raise Exception('A quoter has not been provided (set) to the trade')

    @property
    def strategy(self):
        if self._strategy:
            return self._strategy
        else:
            raise Exception('A strategy has not been provided (set) to the trade')

    @property
    def broker(self):
        """
        Returns the broker instance.
        """

        if self._broker:
            return self._broker
        else:
            raise Exception('A broker has not been provided (set) to the trade')

    # TRADE SETUPS
    def bind_to_trader(self, trader: 'AutoTrader'):
        self._trader = trader

    def set_sizer(self, sizer: Sizer):
        """set a ``Sizer`` class which is the default sizer for any
        strategy added to each trade
        """
        self._sizer = sizer

    def set_quoter(self, quoter: Optional[IQuoter]):
        """set a ``Strategy`` class to the trade for a single pass run.
        Instantiation will happen during ``run`` time.
        """
        self._quoter = quoter
        self._quoter.set_quoter(self._ticker_alias)

    def set_broker(self, broker: IBroker):
        """
        Sets a specific ``broker`` instance for this strategy
        """

        if self._is_live_trade == broker.is_live:
            broker.bind_to_trade(self)
            self._broker = broker
        else:
            raise InvalidBrokerSetting

    def set_strategy(self, strategy: Optional[BaseStrategy]):
        """set a ``Strategy`` class to the trade for a single pass run.
        Instantiation will happen during ``run`` time.
        """
        strategy.bind_to_trade(self)
        self._strategy = strategy

    def set_gainloss_tracker(self, gainloss_tracker: GainLossTracker = GainLossTracker()):
        self._gls_tracker = gainloss_tracker

    # TRADE STATUSES
    def activate_trade(self):
        self._status = TradeStatus.ACTIVATED

    def cancel_trade(self):
        self._status = TradeStatus.CANCELLED

    def stop_trade(self):
        self._status = TradeStatus.PAUSED

    def resume_trade(self):
        self._status = TradeStatus.RESUMED

    def close_trade(self):
        self._status = TradeStatus.CLOSED

    def is_stopped(self):
        return self._status in [TradeStatus.CANCELLED, TradeStatus.CLOSED, TradeStatus.PAUSED]

    def is_settled(self):
        return self._status in [TradeStatus.CANCELLED, TradeStatus.CLOSED]

    # AWAITING INTERVAL & DATA SETUP/REFRESHING
    def set_data(self, datafeed: ICandleFeed = PYahooFinance()):
        self._datafeed = datafeed

        if self._exchange == 'TSX' or self._currency == 'CAD':
            ticker_symbol = self._ticker_alias
        else:
            ticker_symbol = self._trading_symbol

        self._datafeed.set_ticker_symbol(ticker_symbol)
        self._datafeed.set_interval(self.interval)
        self._barfeed = BarFeed(self._datafeed.get_number_candles(self._interval_number))

    @property
    def bar_time_gap(self):
        return self._data_interval.value[1]

    @property
    def last_refresh_timestamp(self):
        return self._last_refresh_timestamp

    def refresh_data(self):
        if self.is_live_trade and self._market_hour.is_open_now():
            bar_df = self._datafeed.get_number_candles(self._interval_number)
            self._barfeed = BarFeed(bar_df)
            self._last_refresh_timestamp = datetime.datetime.now().timestamp()

    @property
    def barfeed(self):
        return self._barfeed

    @property
    def interval(self):
        return self._data_interval.value[0]

    # ORDERS, UPDATING & ADDING & REMOVING
    @property
    def filled_sell_count(self):
        return self._filled_sell_count

    @property
    def filled_buy_count(self):
        return self._filled_buy_count

    def add_order(self, order: Order):
        # check if there is already an active order in the trade or not
        if not self.active_order:
            self.active_order = order

        else:
            raise Exception('There is already an active order in the trade. New orders cannot be added')

    def is_order_addable(self, isbuy: bool):

        if self.is_stopped():
            return False

        if self.active_order:
            return False

        if isbuy and self._filled_buy_count == self._reps:
            return False

        if not isbuy and self._filled_sell_count == self._reps:
            return False

        return True

    def remove_order(self):
        # check if there is currently an active order to be removed or not
        if self.active_order:
            # check if the current active order is settled or not before removing
            if self.active_order.is_settled():

                if self.active_order.is_filled():

                    # increment buy/sell order count
                    if self.active_order.isbuy:
                        self._filled_buy_count += 1

                    else:
                        self._filled_sell_count += 1

                    if self._filled_sell_count == self._filled_buy_count == self._reps:
                        self.close_trade()

                    # append to filled order list
                    self.filled_orders.append(self.active_order)
                    self.active_order = None

                else:
                    # append to filled order list
                    self.discarded_orders.append(self.active_order)
                    self.active_order = None
            else:
                raise Exception('There is an active unsettled order in the trade. The order cannot be removed until '
                                'it is deactivated')
        else:
            raise Exception('There is no active order to remove. Please check the order removal logic & procedure.')

    def is_order_removable(self):

        if not self.active_order:
            return False

        if not self.active_order.is_settled():
            return False

        return True

    def update_order(self, order):
        # check if there is currently an active order to be updated or not
        if self.active_order:
            if not self.active_order.is_settled():
                self.active_order = order
            else:
                raise Exception('There is still a settled in place which cannot be updated. '
                                'Please check the order updating and removal logic & procedure.')
        else:
            raise Exception('There is no active order to update. Please check the order updating logic & procedure.')

    def is_order_updatable(self):

        if not self.active_order:
            return False

        if self.active_order.is_settled():
            return False

        return True

    # EXECUTION/RUN TRADE
    def execute(self):
        if not self.is_stopped():
            self.refresh_data()
            for _ in range(self.barfeed.bar_count):
                next(self.strategy)


if __name__ == '__main__':
    pass
