from abc import ABC, abstractmethod
from typing import Optional


class Instrument(ABC):
    def __init__(self):
        self._id: Optional[str] = None
        self._ticker_symbol: Optional[str] = None
        self._name: Optional[str] = None
        self._primary_exchange: Optional[str] = None
        self._currency: Optional[str] = None
        self._instrument_type: Optional[str] = None

    @abstractmethod
    def set_instrument(self, instrument_info: dict):
        raise NotImplementedError()

    @abstractmethod
    def id(self):
        raise NotImplementedError()


class InstrumentWST(Instrument):

    def __init__(self):
        super().__init__()

    def set_instrument(self, instrument_info: dict):
        self._id = instrument_info['id']
        self._ticker_symbol = instrument_info['stock']['symbol']
        self._name = instrument_info['stock']['name']
        self._primary_exchange = instrument_info['stock']['primary_exchange']
        self._currency = instrument_info['currency']
        self._instrument_type = instrument_info['security_type']

    @property
    def id(self):
        return self._id


# 'id': 'sec-s-19dda65d393d4260af25087824e2ee0b'
# 'account_id': 'tfsa-hyrnpbqo'