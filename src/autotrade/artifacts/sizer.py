# Copyright (C) 2021-2030 StockRead Inc.
# Author: Thanh Tung Nguyen
# Contact: tungstudies@gmail.com

import math
from src.errors import InputParameterConflict


# DIVIDER: --------------------------------------
# INFO: Sizer Concrete Class

class Sizer:
    def __init__(self, isbysize: bool, size: int = 0, amount: float = 0.0):
        self._isbysize = isbysize
        self._size: int = 0
        self._amount: float = 0.0

        if self._isbysize:
            self._size = size
            if amount:
                raise InputParameterConflict(class_name=type(self).__name__, provided_input='by_size',
                                             input_types=('by_size', 'by_amount'),
                                             expected_corresponding_input='size',
                                             unexpected_corresponding_input='amount',
                                             corresponding_input_types=('size', 'amount'))

        else:
            self._amount = amount
            if size:
                raise InputParameterConflict(class_name=type(self).__name__, provided_input='by_amount',
                                             input_types=('by_size', 'by_amount'),
                                             expected_corresponding_input='amount',
                                             unexpected_corresponding_input='size',
                                             corresponding_input_types=('size', 'amount'))

    def __str__(self):
        tojoin = list()
        tojoin.append('ClassType: {}'.format(type(self).__name__))
        tojoin.append('IsBySize: {}'.format(self._isbysize))
        if self._isbysize:
            tojoin.append('Size: {}'.format(self._size))
        else:
            tojoin.append('Amount: {}'.format(self._amount))

        return ', '.join(tojoin)

    # DIVIDER: Publicly Accessible Method Properties ----------------------------------------------
    @property
    def isbysize(self):
        return self._isbysize

    @property
    def size(self):
        if not self._isbysize:
            raise InputParameterConflict(class_name=type(self).__name__, provided_input='by_amount',
                                         input_types=('by_size', 'by_amount'),
                                         expected_corresponding_input='amount',
                                         unexpected_corresponding_input='size',
                                         corresponding_input_types=('size', 'amount'))
        return self._size

    @property
    def amount(self):
        if self._isbysize:
            raise InputParameterConflict(class_name=type(self).__name__, provided_input='by_size',
                                         input_types=('by_size', 'by_amount'),
                                         expected_corresponding_input='size',
                                         unexpected_corresponding_input='amount',
                                         corresponding_input_types=('size', 'amount'))

        else:
            return self._amount

    # DIVIDER: Publicly Accessible Methods --------------------------------------------------------
    def sizebyamount(self, ref_price: float, buy_power_ratio: float = 0.95):
        if self._isbysize:
            raise InputParameterConflict(class_name=type(self).__name__, provided_input='by_amount',
                                         input_types=('by_size', 'by_amount'),
                                         expected_corresponding_input='amount',
                                         unexpected_corresponding_input='size',
                                         corresponding_input_types=('size', 'amount'))
        else:
            if buy_power_ratio > 1.0:
                raise ValueError('Unable to buy more than the pre-set amount. Buy power ratio must be <= 1.0.')
            else:
                return math.floor((self._amount * buy_power_ratio) / ref_price)


# DIVIDER: --------------------------------------
# INFO: Usage Examples

if __name__ == '__main__':
    szr = Sizer(isbysize=False, size=0, amount=100)
    print(szr.sizebyamount(ref_price=10))
