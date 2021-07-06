from abc import ABC, abstractmethod
from typing import Optional

from src.autotrade.broker.instrument import Instrument, InstrumentWST


class Position(ABC):
    def __init__(self):
        self._instrument: Optional[Instrument] = None
        self._size: Optional[int] = None
        self._sellable_size: Optional[int] = None
        self._book_value: Optional[float] = None
        self._average_price: Optional[float] = None

    @abstractmethod
    def set_position(self, position_info: dict):
        raise NotImplementedError()

    @abstractmethod
    def instrument(self):
        raise NotImplementedError()

    @abstractmethod
    def size(self):
        raise NotImplementedError()

    @abstractmethod
    def sellable_size(self):
        raise NotImplementedError()

    @abstractmethod
    def book_value(self):
        raise NotImplementedError()

    @abstractmethod
    def average_price(self):
        raise NotImplementedError()


class PositionWST(Position):

    def __init__(self):
        super().__init__()

    def set_position(self, position_info: dict):
        self._instrument = InstrumentWST()
        self._instrument.set_instrument(instrument_info=position_info)
        self._size = position_info['quantity']
        self._sellable_size = position_info['sellable_quantity']
        self._book_value = position_info['book_value']['amount']
        self._average_price = round(self._book_value / self._sellable_size,2)

    @property
    def instrument(self):
        return self._instrument

    @property
    def size(self):
        return self._size

    @property
    def sellable_size(self):
        return self._sellable_size

    @property
    def book_value(self):
        return self._book_value

    @property
    def average_price(self):
        return self._average_price
