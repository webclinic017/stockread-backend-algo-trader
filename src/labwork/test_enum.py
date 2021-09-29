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

my_list = [1, 2, 3]

import pandas as pd

dict_list1 = [{'tien': 1, 'tinh': '1a', 'tu': '1b', 'toi': '1c'}, {'tien': 2, 'tinh': '2a', 'tu': '2b', 'toi': '2c'},
              {'tien': 3, 'tinh': '3a', 'tu': '3b', 'toi': '3c'}]
dict_list2 = [{'tien': 2, 'tinh': '2a', 'tu': '2b'}, {'tien': 3, 'tinh': '3a', 'tu': '3b'},
              {'tien': 4, 'tinh': '4a', 'tu': '4b'}]
df1 = pd.DataFrame(data=dict_list1)
df2 = pd.DataFrame(data=dict_list2)

print(df1)
print(df2)
df2_columns = list(df2.columns)
print(df2_columns)
df1 = df1[df2.columns]
print(df1[:-1])

df1 = pd.concat([df1[:-1][df2.columns], df2]).drop_duplicates().reset_index(drop=True)
print(df1)
# df_com = pd.concat([df1, df2], ignore_index=True)
# df2 = pd.merge(df2, df1, on=df2.tien, how='outer')
# print(df2)
