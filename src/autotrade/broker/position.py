from typing import Optional


class Position:
    def __init__(self):

        self._size: Optional[int] = 0
        self._average_buy_price: Optional[float] = 0

    def __repr__(self):
        return 'Position(size: {size}, price: {average_buy_price})'.format(
            size=self._size,
            average_buy_price=self._average_buy_price)

    @property
    def size(self):
        return self._size
    def retrieve(self, quantity: int, price: float):

        self._size = quantity
        self._average_buy_price = price

    def open(self, quantity: int, buy_price: float):
        if self._size:
            raise Exception('There is already position. Open operation cannot be performed')
        self._average_buy_price = buy_price
        self._size = quantity

    def add(self, quantity: int, buy_price: float):
        self._average_buy_price = round((self._average_buy_price * self._size + quantity * buy_price) / (
                self._size + quantity), 2)
        self._size += quantity

    def remove(self, quantity: int):
        if not self._size:
            raise Exception('There is no position. Remove operation cannot be performed')

        if quantity > self._size:
            quantity = self._size

        self._size -= quantity

    def close(self):
        self._average_buy_price = 0
        self._size = 0

    @property
    def has_position(self):
        return True if self._size else False

