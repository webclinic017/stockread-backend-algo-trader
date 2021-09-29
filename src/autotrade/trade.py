# Copyright (C) 2021-2030 StockRead Inc.
# Author: Thanh Tung Nguyen
# Contact: tungstudies@gmail.com

import time
from typing import Optional, Union, List

from src.autotrade.artifacts.enums import IntervalOption, TradingDurationType, Exchange, TradeStatus
from src.autotrade.artifacts.gltracker import GainLossTracker
from src.autotrade.artifacts.mkhours import MarketHour
from src.autotrade.artifacts.quoter import IQuoter
from src.autotrade.artifacts.sizer import Sizer
from src.autotrade.artifacts.stopper import StopOrderPricer
from src.autotrade.bars.barfeed import BarFeed
from src.autotrade.broker.base_broker import IBroker, BaseLiveBroker, BaseBroker
from src.autotrade.errors import InvalidBrokerSetting
from src.autotrade.strategy.base_strategy import BaseStrategy
from src.datafeed.yahoofinance.yf_single import ICandleRetriever, PYahooQuery
from src.errors import ValueNotPresentException, MissingRequiredTradingElement
from src.utility.helper import countdown
from src.utility.logger import Logger


# DIVIDER: --------------------------------------
# INFO: Trade Concrete Class

class Trade:
    """Keeps track of the life of a trade: broker, strategy, datafeed, orders, commission (and value?)"""

    def __init__(self, codename: str, is_live_trade: bool, trading_symbol: str, ticker_alias: str, currency: str,
                 interval_option: str, candle_count: int, exchange: str,
                 country=None, reps: int = 1, duration_type: str = 'DAY',
                 logger: Logger = Logger(), to_notify: Union[tuple, str, None] = None):

        # INFO: Constructor Input Parameter Check
        if interval_option.lower() not in IntervalOption.interval_options():
            raise ValueNotPresentException(provided_value=interval_option.lower(),
                                           value_list=IntervalOption.interval_options())

        if currency.upper() not in Exchange.currencies():
            raise ValueNotPresentException(provided_value=currency.upper(),
                                           value_list=Exchange.currencies())

        if exchange.upper() not in Exchange.exchanges():
            raise ValueNotPresentException(provided_value=exchange.upper(),
                                           value_list=Exchange.exchanges())

        if duration_type.upper() not in TradingDurationType.duration_options():
            raise ValueNotPresentException(provided_value=duration_type.upper(),
                                           value_list=TradingDurationType.duration_options())



        self._codename = codename
        self._status = TradeStatus.ACTIVATED
        self._is_live_trade = is_live_trade
        self._trading_symbol = trading_symbol
        self._ticker_alias = ticker_alias
        self._currency = currency
        self._reps = reps
        self._logger = logger
        self._to_notify = to_notify

        self._to_notify: List[str] = list()

        if to_notify:
            if isinstance(to_notify, str):
                if to_notify.lower() not in ['trade', 'order', 'signal']:
                    raise ValueNotPresentException(provided_value=to_notify.lower(),
                                                   value_list=['trade', 'order', 'signal'])
                else:
                    self._to_notify.append(to_notify)

            elif isinstance(to_notify, tuple):
                for item in to_notify:
                    if item.lower() not in ['trade', 'order', 'signal']:
                        raise ValueNotPresentException(provided_value=item.lower(),
                                                       value_list=['trade', 'order', 'signal'])
                    else:
                        self._to_notify.append(item)

        # INFO: Exchange and Market Hour Setup
        self._exchange = exchange
        self._market_hour: MarketHour = MarketHour(exchange=exchange, interval_option=interval_option)
        self._country = country

        # INFO: Key Component Setup
        self._strategy: Optional[BaseStrategy] = None
        self._sizer: Optional[Sizer] = None
        self._broker: Optional[Union[BaseBroker, BaseLiveBroker, IBroker]] = None
        self._quoter: Optional[IQuoter] = None  # quoter is used to get trading price
        self._stp_pricer: Optional[StopOrderPricer] = None
        self._gls_tracker = GainLossTracker()  # gain-loss tracker is used to track trading gain or loss

        # INFO: Candle/Bar Data and Interval Setup
        self._interval_option = IntervalOption.get_interval(interval_option=interval_option)
        self._candle_count = candle_count
        self._candle_retriever: Optional[ICandleRetriever] = None
        self._barfeed: Optional[BarFeed] = None
        self.set_data()

    # DIVIDER: Publicly Accessible Method Properties ----------------------------------------------

    # INFO: Class Key Attribute/Component Setters
    @property
    def trading_symbol(self):
        return self._trading_symbol

    @property
    def currency(self):
        return self._currency

    @property
    def sizer(self):
        if self._sizer:
            return self._sizer
        else:
            raise MissingRequiredTradingElement(element_type='sizer')

    @property
    def stp_pricer(self):
        if self._stp_pricer:
            return self._stp_pricer
        else:
            raise MissingRequiredTradingElement(element_type='stop_order_pricer')

    @property
    def quoter(self):
        if self._quoter:
            return self._quoter
        else:
            raise MissingRequiredTradingElement(element_type='quoter')

    @property
    def strategy(self):
        if self._strategy:
            return self._strategy
        else:
            raise MissingRequiredTradingElement(element_type='strategy')

    @property
    def broker(self):
        if self._broker:
            return self._broker
        else:
            raise MissingRequiredTradingElement(element_type='broker')

    @property
    def logger(self):
        return self._logger

    @property
    def to_notify(self):
        return self._to_notify

    @property
    def market_hour(self):
        return self._market_hour

    @property
    def gl_tracker(self):
        return self._gls_tracker

    # INFO: Class Default Attribute Getters
    @property
    def is_live_trade(self):
        return self._is_live_trade

    @property
    def codename(self):
        return self._codename

    @property
    def bar_time_gap(self):
        return self._interval_option.value[1]

    @property
    def reps_limit(self):
        return self._reps

    @property
    def barfeed(self):
        return self._barfeed

    # DIVIDER: Publicly Accessible Methods --------------------------------------------------------

    # INFO: Class Key Attribute/Component Setters
    def set_sizer(self, sizer: Sizer):
        """set a ``Sizer`` class which is the default sizer for any
        strategy added to each trade
        """
        self._sizer = sizer

    def set_stp_pricer(self, stp_pricer: StopOrderPricer = StopOrderPricer(is_trailed_by_percent=True,
                                                                           is_price_increase_by_percent=True,
                                                                           trail_percent=0.007,
                                                                           price_increase_percent=0.003)):
        """set a ``StopOrderPricer`` class which decides the stop_price and limit_price of stop orders
        """
        self._stp_pricer = stp_pricer

    def set_quoter(self, quoter: Optional[IQuoter]):
        """set a ``Strategy`` class to the trade for a single pass run.
        Instantiation will happen during ``run`` time.
        """
        self._quoter = quoter
        self._quoter.set_ticker_symbol(self._ticker_alias)

    def set_broker(self, broker: Optional[Union[BaseBroker, BaseLiveBroker, IBroker]]):
        """
        Sets a specific ``broker`` instance for this strategy
        """

        if self._is_live_trade == broker.is_live:
            broker.initialize(trading_symbol=self.trading_symbol, currency=self.currency)
            self._broker = broker
        else:
            raise InvalidBrokerSetting

    def set_strategy(self, strategy: Optional[BaseStrategy]):
        """set a ``Strategy`` class to the trade for a single pass run.
        Instantiation will happen during ``run`` time.
        """
        strategy.bind_to_trade(self)
        self._strategy = strategy

    def set_gls_tracker(self, gls: GainLossTracker = GainLossTracker()):
        self._gls_tracker = gls

    # INFO: Dealing with Trade Status
    def reset_trade(self):
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

    # INFO: Dealing with Candle/Bar Data and Interval
    def set_data(self, datafeed: ICandleRetriever = PYahooQuery()):
        self._candle_retriever = datafeed


        if self._exchange == 'TSX' or self._currency == 'CAD':
            ticker_symbol = self._ticker_alias
        else:
            ticker_symbol = self._trading_symbol

        self._candle_retriever.set_ticker_symbol(ticker_symbol)
        self._candle_retriever.set_interval(self._interval_option.value[0])
        bar_df = self._candle_retriever.get_x_candles(self._candle_count)
        print(bar_df)
        self._barfeed = BarFeed(dataframe=bar_df,market_hour=self._market_hour)

    def refresh_data(self):
        new_bar_df = self._candle_retriever.get_x_candles(self._candle_count)
        print(new_bar_df)
        self._barfeed.update(dataframe=new_bar_df)

    # EXECUTION/RUN TRADE
    def execute(self):
        if not self.is_stopped():
            bar_count = self.barfeed.valid_bar_count
            next_count = 1
            while next_count <= bar_count:
                print(f'NextCount {next_count}-{bar_count} BarCount')
                next(self.strategy)

                if self.is_live_trade and self.market_hour.is_open_now() and next_count == bar_count:
                    if self.barfeed.last_valid_bar.is_live_bar:
                        print(f'SecondToNextBar: {round(self.market_hour.seconds_to_next_bar)} seconds')
                        countdown(message='Countdown to next data candle',
                                  time_sec=round(self.market_hour.seconds_to_next_bar))

                        if next_count <= bar_count:
                            # wait extra seconds before getting new bar because YFinance doesn't update data fast enough
                            countdown(message='Countdown to data refresh',
                                      time_sec=round(self._barfeed.data_delay_seconds))
                            self.refresh_data()

                            bar_count = self.barfeed.valid_bar_count
                            next_count += 1

                else:
                    next_count += 1

                if self.is_stopped():
                    break

    # DIVIDER: Class Private Methods to Process Data Internally -----------------------------------


# DIVIDER: --------------------------------------
# INFO: Usage Examples

if __name__ == '__main__':
    is_test_run = True

    if is_test_run:
        air_can_trade = Trade(codename='AirCanadaSampleTrade', is_live_trade=False, trading_symbol='AC',
                              ticker_alias='AC.TO',
                              currency='CAD', interval_option='5m', candle_count=100,
                              exchange='TSX', reps=1)

        latest_bar = air_can_trade.barfeed.latest_retrieved_bar
        print(latest_bar)

    else:
        pass
