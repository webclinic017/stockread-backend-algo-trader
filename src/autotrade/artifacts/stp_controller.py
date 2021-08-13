# Copyright (C) 2021-2030 StockRead Inc.
# Author: Thanh Tung Nguyen
# Contact: tungstudies@gmail.com


from typing import Optional, List, Union

from src.autotrade.artifacts.order import StopOrder
from src.autotrade.broker.base_broker import IBroker, BaseBroker
from src.errors import BrokerTypeError, InputParameterConflict, MissingPrice


# TODO: Allow reset counter for new trade reps if there is no stop loss executed
# TODO: Allow strategy to check if there is any stop loss executed before (prenext) processing next bar
# TODO: Report gain loss and add the executed stoploss to filled_orders
# TODO: Update & Add & Replace, Remove stoploss operation
# TODO: Check if strategy required stop loss or not before adding stoploss logic to methods
# TODO: Check if strategy required stop loss or not before creating TrailingStopOrderController instance in strategy (if add else no)
# TODO: Implement system stoploss

# DIVIDER: --------------------------------------
# INFO: TrailingStopOrderController Concrete Class


class StopOrderController:
    """Manage stop orders and control actions on these stop orders"""

    def __init__(self, broker: Union[IBroker, BaseBroker],
                 is_trailed_by_percent: bool, is_price_increase_by_percent: bool, is_slt_price_gap_by_percent: bool,
                 trail_percent: float = 0.0, trail_amount: float = 0.0,
                 price_increase_percent: float = 0.0, price_increase_amount: float = 0.0,
                 stop_limit_price_gap_percent: float = 0.0, stop_limit_price_gap_amount: float = 0.0):

        """
        :param broker: a broker to which stop orders are submitted
        :type broker: Union[IBroker, BaseBroker]

        :param is_trailed_by_percent: if the trailing difference is 'by_percent' or 'by_amount' between
        the anchor price and stop price
        :type is_trailed_by_percent: float

        :param is_price_increase_by_percent: if the price increase is 'by_percent' or 'by_amount' from
        one price to the next that trigger the new higher stop price
        :type is_price_increase_by_percent: float

        :param is_slt_price_gap_by_percent: if the difference between 'stop_price' and 'limit price' of
        the stop limit order
        :type is_slt_price_gap_by_percent: float

        :param trail_percent: If is_slt_price_gap_by_percent is True, trail_percent defines the stop_price based on the
        anchor price (ref_price) [ref_price * (1 - trail_percent)]
        :type trail_percent: float

        :param trail_amount: If is_slt_price_gap_by_percent is False, trail_amount defines the stop_price based on the
        anchor price (ref_price) [ref_price - trail_amount]
        :type trail_amount: float

        :param price_increase_percent: trailing stop order should only be updated when the price increase a certain
        amount from its prior anchor price. The price_increase_percent defines this increase amount in percent
        :type price_increase_percent: float

        :param price_increase_amount: trailing stop order should only be updated when the price increase a certain
        amount from its prior anchor price. The price_increase_percent defines this increase amount in amount
        :type price_increase_amount: float

        :param stop_limit_price_gap_percent: the difference in percent between stop_price and limit_price when placing a
        stop_limit order
        :type stop_limit_price_gap_percent: float

        :param stop_limit_price_gap_amount: the difference in $amount between stop_price and limit_price when placing a
        stop_limit order
        :type stop_limit_price_gap_amount: float
        """

        # IMPORTANT: Checking LiveBroker Requirement
        if broker.is_live:
            raise BrokerTypeError(class_name=type(self).__name__, expected_live_broker=True)

        # IMPORTANT: Setting up Stop Order Elements - Trailing StopPrice by Percent
        self._is_trailed_by_percent = is_trailed_by_percent
        self._trail_percent: float = 0.0
        self._trail_amount: float = 0.0

        if self._is_trailed_by_percent:
            self._trail_percent = trail_percent
            if trail_amount:
                raise InputParameterConflict(class_name=type(self).__name__, provided_input='trail_by_percent',
                                             input_types=('trail_by_percent', 'trail_by_amount'),
                                             expected_corresponding_input='percent',
                                             unexpected_corresponding_input='amount',
                                             corresponding_input_types=('percent', 'amount'))

        else:
            self._trail_amount = trail_amount
            if trail_percent:
                raise InputParameterConflict(class_name=type(self).__name__, provided_input='trail_by_amount',
                                             input_types=('trail_by_percent', 'trail_by_amount'),
                                             expected_corresponding_input='amount',
                                             unexpected_corresponding_input='percent',
                                             corresponding_input_types=('percent', 'amount'))

        # IMPORTANT: Setting up Stop Order Elements - AnchorPrice Increase Threshold by Percent
        self._is_price_increase_by_percent = is_price_increase_by_percent
        self._price_increase_percent: float = 0.0
        self._price_increase_amount: float = 0.0

        if self._is_price_increase_by_percent:
            self._price_increase_percent = price_increase_percent
            if price_increase_amount:
                raise InputParameterConflict(class_name=type(self).__name__, provided_input='price_increase_by_percent',
                                             input_types=('price_increase_by_percent', 'price_increase_by_amount'),
                                             expected_corresponding_input='percent',
                                             unexpected_corresponding_input='amount',
                                             corresponding_input_types=('percent', 'amount'))

        else:
            self._price_increase_amount = price_increase_amount
            if price_increase_percent:
                raise InputParameterConflict(class_name=type(self).__name__, provided_input='price_increase_by_amount',
                                             input_types=('price_increase_by_percent', 'price_increase_by_amount'),
                                             expected_corresponding_input='amount',
                                             unexpected_corresponding_input='percent',
                                             corresponding_input_types=('percent', 'amount'))

        # IMPORTANT: Setting up Stop Order Elements - Gap between StopPrice and LimitPrice for StopLimitOrder by percent
        self._is_slt_price_gap_by_percent = is_slt_price_gap_by_percent
        self._stop_limit_price_gap_percent: float = 0.0
        self._stop_limit_price_gap_amount: float = 0.0

        if self._is_slt_price_gap_by_percent:
            self._stop_limit_price_gap_percent = stop_limit_price_gap_percent
            if stop_limit_price_gap_amount:
                raise InputParameterConflict(class_name=type(self).__name__, provided_input='slt_price_gap_by_percent',
                                             input_types=('slt_price_gap_by_percent', 'slt_price_gap_by_amount'),
                                             expected_corresponding_input='percent',
                                             unexpected_corresponding_input='amount',
                                             corresponding_input_types=('percent', 'amount'))

        else:
            self._price_increase_amount = price_increase_amount
            if price_increase_percent:
                raise InputParameterConflict(class_name=type(self).__name__, provided_input='slt_price_gap_by_amount',
                                             input_types=('price_increase_by_percent', 'price_increase_by_amount'),
                                             expected_corresponding_input='amount',
                                             unexpected_corresponding_input='percent',
                                             corresponding_input_types=('percent', 'amount'))

        # Assigning constructor parameters to class attributes

        self._live_broker = broker
        self._ticker_symbol = ticker_symbol

        self._trailing_stop_order: Optional[StopOrder] = None
        self._initial_onetime_stop_order: Optional[StopOrder] = None
        self._stoploss_count: int = 0

        self.executed_sls: List[StopLoss] = list()
        self.killed_sls: List[StopLoss] = list()

    def __str__(self):
        tojoin = list()
        tojoin.append('ClassType: {}'.format(type(self).__name__))
        tojoin.append('TickerSymbol: {}'.format(self._ticker_symbol))
        tojoin.append('BrokerType: {}'.format(type(self._live_broker).__name__))

        tojoin.append('TrailingStopPriceByPercent: {}'.format(self._is_trailed_by_percent))
        if self._is_trailed_by_percent:
            tojoin.append('TrailPercent: {}'.format(self._trail_percent))
        else:
            tojoin.append('TrailAmount: {}'.format(self._trail_amount))

        tojoin.append('AnchorPriceIncreaseThresholdByPercent: {}'.format(self._is_price_increase_by_percent))
        if self._is_price_increase_by_percent:
            tojoin.append('PriceIncreasePercent: {}'.format(self._price_increase_percent))
        else:
            tojoin.append('PriceIncreaseAmount: {}'.format(self._price_increase_amount))

        tojoin.append('SLTPriceGapByPercent: {}'.format(self._is_slt_price_gap_by_percent))
        if self._is_slt_price_gap_by_percent:
            tojoin.append('SLTPriceGapPercent: {}'.format(self._stop_limit_price_gap_percent))
        else:
            tojoin.append('SLTPriceGapAmount: {}'.format(self._stop_limit_price_gap_percent))

        return ', '.join(tojoin)

    def create_initial_stp(self, isstoplimit: bool, size: int, is_price_required: bool,
                           stop_price: float = 0.0, limit_price: float = 0.0, ref_price: float = 0.0):
        if self._stoploss_count > 0:
            raise ValueError('The initial stop order has already be created')

        if is_price_required:
            if stop_price:
                if isstoplimit:
                    if not limit_price:
                        raise MissingPrice(class_name=type(self).__name__, price_type='limit_price')

            else:
                raise MissingPrice(class_name=type(self).__name__, price_type='stop_price')

        else:
            if not ref_price:
                raise MissingPrice(class_name=type(self).__name__, price_type='ref_price')

            else:
                if self._is_trailed_by_percent:
                    stop_price = round(ref_price * (1 - self._trail_percent), 2)

                    if isstoplimit:
                        if self._is_slt_price_gap_by_percent:
                            limit_price = round(stop_price * (1 - self._stop_limit_price_gap_percent), 2)
                        else:
                            limit_price = round(stop_price - self._stop_limit_price_gap_amount, 2)
                    else:
                        limit_price = 0.0

                else:
                    stop_price = round(ref_price - self._trail_amount, 2)

                    if isstoplimit:
                        if self._is_slt_price_gap_by_percent:
                            limit_price = round(stop_price * (1 - self._stop_limit_price_gap_percent), 2)
                        else:
                            limit_price = round(stop_price - self._stop_limit_price_gap_amount, 2)
                    else:
                        limit_price = 0.0

        isbuy = False  # stop loss is a sell

        stop_order = StopOrder(self._ticker_symbol, size=size, isbuy=isbuy, isstoplimit=isstoplimit,
                               stop_price=stop_price, limit_price=limit_price, ref_price=ref_price)
        if isstoplimit:
            stop_order = self._live_broker.stop_limit_sell(order=stop_order)
        else:
            stop_order = self._live_broker.stop_loss(order=stop_order)

        self._stoploss_count += 1
        self._initial_onetime_stop_order = stop_order

        return stop_order

    def remove_stp(self):
        if self._initial_onetime_stop_order:
            pass