# Copyright (C) 2021-2030 StockRead Inc.
# Author: Thanh Tung Nguyen
# Contact: tungstudies@gmail.com

# DIVIDER: --------------------------------------
# INFO: Commission Concrete Class
from src.errors import InputParameterConflict


class Commission:

    def __init__(self, is_fixed: bool = True, fixed_comm: float = 0.0, percent: float = 0.0, floor: float = 0.0,
                 ceiling: float = 0.0):

        self._is_fixed = is_fixed
        self._percent: float = 0.0
        self._fixed_comm: float = 0.0
        self._floor = floor
        self._ceiling = ceiling

        if self._is_fixed:
            self._is_fixed = fixed_comm
            if percent:
                raise InputParameterConflict(provided_input='by_fixed_amount',
                                             input_types=('by_fixed_amount', 'by_percentage'),
                                             expected_corresponding_input='fixed_comm',
                                             unexpected_corresponding_input='percent',
                                             corresponding_input_types=('fixed_comm', 'percent'))

        else:
            self._percent = percent
            if fixed_comm:
                raise InputParameterConflict(provided_input='by_percentage',
                                             input_types=('by_fixed_amount', 'by_percentage'),
                                             expected_corresponding_input='percent',
                                             unexpected_corresponding_input='fixed_comm',
                                             corresponding_input_types=('fixed_comm', 'percent'))

    def __str__(self):
        tojoin = list()
        tojoin.append('ClassType: {}'.format(type(self).__name__))
        tojoin.append('IsFixedCommission: {}'.format(self._is_fixed))
        if self._is_fixed:
            tojoin.append('PercentCommission: {}'.format(self._percent))
            tojoin.append('FloorAmount: {}'.format(self._floor))
            tojoin.append('CeilingAmount: {}'.format(self._ceiling))
        else:
            tojoin.append('FixedCommission: {}'.format(self._fixed_comm))

        return ', '.join(tojoin)

    # DIVIDER: Publicly Accessible Method Properties ----------------------------------------------
    @property
    def is_fixed(self):
        return self._is_fixed

    @property
    def percent(self):
        if self._is_fixed:
            raise InputParameterConflict(provided_input='by_fixed_amount',
                                         input_types=('by_fixed_amount', 'by_percentage'),
                                         expected_corresponding_input='fixed_comm',
                                         unexpected_corresponding_input='percent',
                                         corresponding_input_types=('fixed_comm', 'percent'))
        else:
            return self._percent

    @property
    def fixed_comm(self):
        if self._is_fixed:
            return self._fixed_comm
        else:
            raise InputParameterConflict(provided_input='by_percentage',
                                         input_types=('by_fixed_amount', 'by_percentage'),
                                         expected_corresponding_input='percent',
                                         unexpected_corresponding_input='fixed_comm',
                                         corresponding_input_types=('fixed_comm', 'percent'))

    # DIVIDER: Publicly Accessible Methods --------------------------------------------------------
    def percent_comm(self, transaction_value: float):
        if self._is_fixed:
            raise InputParameterConflict(provided_input='by_fixed_amount',
                                         input_types=('by_fixed_amount', 'by_percentage'),
                                         expected_corresponding_input='fixed_comm',
                                         unexpected_corresponding_input='percent',
                                         corresponding_input_types=('fixed_comm', 'percent'))
        else:
            comm_amount = transaction_value * self._percent
            if self._floor and comm_amount < self._floor:
                return self._floor
            elif self._ceiling and comm_amount > self._ceiling:
                return self._ceiling
            else:
                return comm_amount

    def estimate_commission(self, transaction_value: float):
        if self._is_fixed:
            return self._fixed_comm
        else:
            return self.percent_comm(transaction_value)


# DIVIDER: --------------------------------------
# INFO: Usage Examples

if __name__ == '__main__':
    comm = Commission(is_fixed=False, fixed_comm=0, percent=0.005, ceiling=10, floor=5)
    commission_amount = comm.estimate_commission(transaction_value=1000000)
    print(commission_amount)
