from abc import ABC, abstractmethod
from typing import Optional

from wsimple import Wsimple


class BrokerAccount(ABC):

    def __init__(self):
        self._id: Optional[str] = None
        self._account_type: Optional[str] = None
        self._base_currency: Optional[str] = None
        self._net_deposits: Optional[float] = None
        self._current_balance: Optional[float] = None
        self._available_to_trade: Optional[float] = None
        self._available_to_withdraw: Optional[float] = None
        self._position_quantities: Optional[int] = None

    @abstractmethod
    def set_account(self, account_info: dict):
        raise NotImplementedError()

    @abstractmethod
    def id(self):
        raise NotImplementedError()

    @abstractmethod
    def available_to_trade(self):
        raise NotImplementedError()


class AccountWST(BrokerAccount):

    def __init__(self):
        super().__init__()
        self._connection: Optional[Wsimple] = None

    def set_account(self, account_info: dict):
        self._id = account_info['id']
        self._account_type = account_info['account_type']
        self._base_currency = account_info['base_currency']
        self._net_deposits = account_info['net_deposits']['amount']
        self._current_balance = account_info['current_balance']['amount']
        self._available_to_trade = account_info['available_to_withdraw']['amount']
        self._available_to_withdraw = account_info['available_to_withdraw']['amount']
        self._position_quantities = account_info['position_quantities']

    @property
    def id(self):
        return self._id

    @property
    def available_to_trade(self):
        return self._available_to_trade
