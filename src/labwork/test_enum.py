from collections import deque
from enum import Enum


class Exchange(Enum):
    """Exchanges available and supported by 'pandas_market_calendars' library"""
    TSX = ('TSX', 'CAD', 'CA')
    NYSE = ('NYSE', 'USD', 'US')

    @classmethod
    def currencies(cls):
        return [member.value[1] for member in cls]

    @classmethod
    def exchanges(cls):
        return [member.value[0] for member in cls]

    @classmethod
    def get_currency(cls, currency: str):
        for member in cls:
            if member.value[1] == currency.upper():
                return member


print(Exchange.get_currency('CAD'))

print(1.2 == 1.3 == 1.2)

print(type(deque([])))


def test_args(*args: int):
    int_list = []
    int_list.extend(args)
    print(int_list)

test_args()

a_dict = {1: 'a', 2: 'b'}
print(a_dict)
print(len([]))

t = 0.0
if not t:
    print(False)