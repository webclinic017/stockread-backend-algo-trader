from datetime import datetime
from enum import Enum
from typing import Optional


class SignalAction(Enum):
    BUY = 1
    SELL = 2


class Signal:

    def __init__(self, signal_action: SignalAction, name: str, sequential: int, has_dependent_signal: bool = True):
        self.signal_action = signal_action
        self._name = name
        self._sequential = sequential
        self._is_signal_up: Optional[bool] = None
        self._signal_up_timestamp: Optional[int] = None
        self._price_at_signal: Optional[float] = None
        self._indicator_value_at_signal: Optional[float] = None
        self._has_dependent_signal = has_dependent_signal
        self._dependent_signal: Optional[Signal] = None

    @property
    def is_signal_up(self):
        if self._has_dependent_signal:
            if self._dependent_signal:
                return self.is_signal_up
            else:
                raise Exception('You have missed setting up dependent signal')
        else:
            return self.is_signal_up

    def set_dependent_signal(self, dependent_signal=None):
        if self._has_dependent_signal:
            if dependent_signal and isinstance(dependent_signal, Signal):
                self._dependent_signal = self.is_signal_up
            else:
                raise Exception('It is required to provide an instance of Signal class as the input')
        else:
            raise Exception('This Signal instance has no dependent signal. Setting dependent signal is not required')

    def signal_up(self):
        if self._dependent_signal.is_signal_up:
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
