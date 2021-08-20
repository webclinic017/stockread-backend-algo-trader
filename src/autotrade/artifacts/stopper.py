# Copyright (C) 2021-2030 StockRead Inc.
# Author: Thanh Tung Nguyen
# Contact: tungstudies@gmail.com


from typing import Optional, List, Union

from src.autotrade.artifacts.order import StopOrder
from src.autotrade.broker.base_broker import IBroker, BaseBroker
from src.errors import BrokerTypeError, InputParameterConflict, MissingPrice


# TODO: Allow reset counter for new trade reps if there is no stop loss executed
# TODO: Allow strategy to check if there is any stop loss executed before (prenext) processing next bar
# TODO: Check if strategy required stop loss or not before creating TrailingStopOrderController instance in strategy (if add else no)
# TODO: Implement system stoploss

# DIVIDER: --------------------------------------
# INFO: TrailingStopOrderController Concrete Class


class StopOrderPricer:
    """Compute stop orders stop and limit prices"""

    def __init__(self, is_trailed_by_percent: bool, is_price_increase_by_percent: bool,
                 is_slt_price_gap_by_percent=False, trail_percent=None, trail_amount=None,
                 price_increase_percent=None, price_increase_amount=None,
                 stop_limit_price_gap_percent=None, stop_limit_price_gap_amount=None):

        """

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

        # IMPORTANT: Setting up Stop Order Elements - Trailing StopPrice by Percent
        self._is_trailed_by_percent = is_trailed_by_percent
        self._trail_percent: float = 0.0
        self._trail_amount: float = 0.0

        if self._is_trailed_by_percent:
            if trail_percent:
                self._trail_percent = trail_percent
            else:
                raise ValueError("Missing TrailPercent")
            if trail_amount:
                raise InputParameterConflict(provided_input='trail_by_percent',
                                             input_types=('trail_by_percent', 'trail_by_amount'),
                                             expected_corresponding_input='percent',
                                             unexpected_corresponding_input='amount',
                                             corresponding_input_types=('percent', 'amount'))

        else:
            if trail_amount:
                self._trail_amount = trail_amount
            else:
                raise ValueError("Missing TrailAmount")
            if trail_percent:
                raise InputParameterConflict(provided_input='trail_by_amount',
                                             input_types=('trail_by_percent', 'trail_by_amount'),
                                             expected_corresponding_input='amount',
                                             unexpected_corresponding_input='percent',
                                             corresponding_input_types=('percent', 'amount'))

        # IMPORTANT: Setting up Stop Order Elements - AnchorPrice Increase Threshold by Percent
        self._is_price_increase_by_percent = is_price_increase_by_percent
        self._price_increase_percent: float = 0.0
        self._price_increase_amount: float = 0.0

        if self._is_price_increase_by_percent:
            if price_increase_percent:
                self._price_increase_percent = price_increase_percent
            else:
                raise ValueError("Missing PriceIncreasePercent")

            if price_increase_amount:
                raise InputParameterConflict(provided_input='price_increase_by_percent',
                                             input_types=('price_increase_by_percent', 'price_increase_by_amount'),
                                             expected_corresponding_input='percent',
                                             unexpected_corresponding_input='amount',
                                             corresponding_input_types=('percent', 'amount'))

        else:
            if price_increase_amount:
                self._price_increase_amount = price_increase_amount
            else:
                raise ValueError("Missing PriceIncreaseAmount")
            if price_increase_percent:
                raise InputParameterConflict(provided_input='price_increase_by_amount',
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
                raise InputParameterConflict(provided_input='slt_price_gap_by_percent',
                                             input_types=('slt_price_gap_by_percent', 'slt_price_gap_by_amount'),
                                             expected_corresponding_input='percent',
                                             unexpected_corresponding_input='amount',
                                             corresponding_input_types=('percent', 'amount'))

        else:
            self._stop_limit_price_gap_amount = stop_limit_price_gap_amount

            if stop_limit_price_gap_percent:
                raise InputParameterConflict(provided_input='slt_price_gap_by_amount',
                                             input_types=('slt_price_gap_by_percent', 'slt_price_gap_by_amount'),
                                             expected_corresponding_input='amount',
                                             unexpected_corresponding_input='percent',
                                             corresponding_input_types=('percent', 'amount'))

        self._latest_ref_price: float = 0.0
        self._latest_stop_price: float = 0.0
        self._latest_limit_price: float = 0.0

    def __str__(self):
        tojoin = list()
        tojoin.append('ClassType: {}'.format(type(self).__name__))

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

    def get_stop_limit_prices(self, ref_price: float, is_to_trail=True):
        if not is_to_trail:
            if self._is_trailed_by_percent:
                estimated_stop_price = round(ref_price * (1 - self._trail_percent), 2)
            else:
                estimated_stop_price = round(ref_price - self._trail_amount, 2)

            if self._is_slt_price_gap_by_percent:
                estimated_limit_price = round(estimated_stop_price * (1 - (self._stop_limit_price_gap_percent if
                                                                           self._stop_limit_price_gap_percent else 0)), 2)
            else:
                estimated_limit_price = round(estimated_stop_price - (self._stop_limit_price_gap_amount if
                                                                      self._stop_limit_price_gap_amount else 0), 2)

                return {'stop_price': estimated_limit_price, 'limit_price': estimated_limit_price}

        else:
            if self._latest_ref_price:
                if self._is_price_increase_by_percent:
                    if (ref_price / self._latest_ref_price - 1) >= self._price_increase_percent:
                        self._latest_ref_price = ref_price
                    else:
                        return
                else:
                    if ref_price - self._latest_ref_price >= self._price_increase_amount:
                        self._latest_ref_price = ref_price
                    else:
                        return
            else:
                self._latest_ref_price = ref_price

            # compute stop price
            if self._is_trailed_by_percent:
                estimated_stop_price = round(self._latest_ref_price * (1 - self._trail_percent), 2)
            else:
                estimated_stop_price = round(self._latest_ref_price - self._trail_amount, 2)

            if estimated_stop_price > self._latest_stop_price:
                self._latest_stop_price = estimated_stop_price
            else:
                return

            # compute limit price
            if self._is_slt_price_gap_by_percent:
                if self._stop_limit_price_gap_percent:
                    self._latest_limit_price = round(self._latest_stop_price * (1 - self._stop_limit_price_gap_percent), 2)
                else:
                    self._latest_limit_price = self._latest_stop_price
            else:
                if self._stop_limit_price_gap_amount:
                    self._latest_limit_price = round(self._latest_stop_price - self._stop_limit_price_gap_amount, 2)
                else:
                    self._latest_limit_price = self._latest_stop_price

            return {'stop_price': self._latest_stop_price, 'limit_price': self._latest_limit_price}

    def reset_trailing(self):
        self._latest_ref_price = 0.0
        self._latest_stop_price = 0.0
        self._latest_limit_price = 0.0

    def set_trailing(self, ref_price: float, stop_price: float):
        self._latest_ref_price = ref_price
        self._latest_stop_price = stop_price

    @property
    def latest_ref_price(self):
        return self._latest_ref_price

    @property
    def latest_stop_price(self):
        return self._latest_stop_price

if __name__ == '__main__':
    stp_pricer = StopOrderPricer(is_trailed_by_percent=True, is_price_increase_by_percent=True,
                                 trail_percent=0.007, price_increase_percent=0.005)

    slt_prices = stp_pricer.get_stop_limit_prices(ref_price=23.88)
    print(slt_prices)
    slt_prices = stp_pricer.get_stop_limit_prices(ref_price=24.05, is_to_trail=True)

    print(slt_prices)