# Copyright (C) 2021-2030 StockRead Inc.
# Author: Thanh Tung Nguyen
# Contact: tungstudies@gmail.com

from typing import Optional
from src.errors import MissingPrice, ItemAlreadyExistError, ItemNonExistenceError


# DIVIDER: --------------------------------------
# INFO: Position Concrete Class

class Position:

    def __init__(self, ticker_symbol: str):
        self._ticker_symbol = ticker_symbol
        self._size: Optional[int] = 0
        self._average_buy_price: Optional[float] = 0.0
        self._ticker_id = None
        self._currency = None

    def __str__(self):
        tojoin = list()
        tojoin.append('ClassType: {}'.format(type(self).__name__))
        tojoin.append('TickerSymbol: {}'.format(self._ticker_symbol))
        tojoin.append('TickerID: {}'.format(self._ticker_id))
        tojoin.append('Currency: {}'.format(self._currency))
        tojoin.append('Size: {}'.format(self.size))
        tojoin.append('AverageBuyPrice: {}'.format(self._average_buy_price))

        return ', '.join(tojoin)

    # DIVIDER: Publicly Accessible Method Properties ----------------------------------------------
    @property
    def size(self):
        return self._size

    @property
    def ticker_symbol(self):
        return self._ticker_symbol

    @property
    def ticker_id(self):
        return self._ticker_id

    @property
    def currency(self):
        return self._currency

    @property
    def average_buy_price(self):
        return self._average_buy_price

    def has_position(self):
        return True if self._size else False

    # DIVIDER: Publicly Accessible Methods --------------------------------------------------------
    def set_ticker_id(self, ticker_id: str):
        self._ticker_id = ticker_id

    def set_currency(self, currency: str):
        self._currency = currency

    def retrieve(self, quantity: int, price: float):

        self._size = quantity
        self._average_buy_price = price

    def open(self, quantity: int, buy_price: float):
        if self._size:
            raise ItemAlreadyExistError(item_type='size')
        self._average_buy_price = buy_price
        self._size = quantity

    def close(self):
        self._average_buy_price = 0
        self._size = 0

    def update(self, isbuy: bool, quantity: int, buy_price: float):
        if isbuy:
            if buy_price:
                self._add(quantity=quantity, buy_price=buy_price)
            else:
                raise MissingPrice(price_type='buy_price')
        else:
            self._remove(quantity=quantity)

    # DIVIDER: Class Private Methods to Process Data Internally -----------------------------------
    def _add(self, quantity: int, buy_price: float):
        self._average_buy_price = round((self._average_buy_price * self._size + quantity * buy_price) / (
                self._size + quantity), 2)
        self._size += quantity

    def _remove(self, quantity: int):
        if not self._size:
            raise ItemNonExistenceError(item_type='size')

        if quantity > self._size:
            quantity = self._size

        self._size -= quantity


# DIVIDER: --------------------------------------
# INFO: Usage Examples
if __name__ == '__main__':
    pass
