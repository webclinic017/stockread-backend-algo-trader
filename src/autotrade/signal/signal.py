from datetime import datetime
from enum import Enum
from typing import Optional


class SignalAction(Enum):
    BUY = 1
    SELL = 2


class Signal:

    def __init__(self, signal_action: SignalAction, name: str, sequential: int):
        self.signal_action = signal_action
        self._name: Optional[str] = name
        self._sequential: Optional[int] = sequential
        self._is_signal_up: Optional[bool] = None
        self._signal_up_timestamp: Optional[int] = None
        self._price_at_signal: Optional[float] = None
        self._indicator_value_at_signal: Optional[float] = None

    @property
    def is_signal_up(self):
        return self.is_signal_up

    def signal_up(self):
        self._is_signal_up = True
        self._signal_up_timestamp = datetime.utcnow().timestamp()

    def signal_down(self):
        self._is_signal_up = False
        self._signal_up_timestamp = None

    @property
    def sequential(self):
        return self._sequential

    @property
    def name(self):
        return self._name

    @property
    def signal_up_timestamp(self):
        return self._signal_up_timestamp

    def set_price_at_signal(self, price_at_signal: float):
        self._price_at_signal = price_at_signal

    def set_indicator_value_at_signal(self, indicator_value_at_signal: float):
        self._price_at_signal = indicator_value_at_signal

    @property
    def price_at_signal(self):
        return self._price_at_signal

    @property
    def indicator_value_at_signal(self):
        return self._indicator_value_at_signal
