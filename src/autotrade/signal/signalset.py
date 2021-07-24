from datetime import datetime
from enum import Enum
from typing import Optional

from src.autotrade.signal.signal import Signal


class SignalSetAction(Enum):
    BUY = 1
    SELL = 2


class SignalSet:
    def __init__(self, signal_set_action: SignalSetAction, signal_count: int):
        # setup signal set
        self.signal_set_action = signal_set_action
        self._signal_count = signal_count
        self._signal_dict: dict = dict()

        # check first and last signals
        self._first_signal: Optional[Signal]
        self._last_signal: Optional[Signal]

        # check if all signals are up
        self._is_all_up: Optional[bool] = None
        self._signal_up_count = 0
        self._all_up_timestamp: Optional[int] = None

        # check prices at all-up signal
        self._price_at_allup: Optional[float] = None
        self._target_price: Optional[float] = None
        self._target_stop_price: Optional[float] = None

    @property
    def signal_count(self):
        return self._signal_count

    @property
    def is_all_up(self):
        return self._signal_count

    @property
    def all_up_timestamp(self):
        return self._all_up_timestamp

    @property
    def signal_up_count(self):
        return self._signal_up_count

    def set_price_at_allup(self, price_at_allup: float):
        self._price_at_allup = price_at_allup

    @property
    def price_at_allup(self):
        return self._price_at_allup

    def set_target_price(self, target_price: float):
        self._target_price = target_price

    @property
    def target_price(self):
        return self._target_price

    def set_target_stop_price(self, target_stop_price: float):
        self._target_stop_price = target_stop_price

    @property
    def target_stop_price(self):
        return self._target_stop_price

    def add_signals(self, signal: Signal, *args: Signal):
        signals = list()
        signals.append(signal)
        signals.extend(args)
        for sgn in signals:
            if len(self._signal_dict) < self.signal_count:
                if self._signal_dict[sgn.sequential]:
                    raise Exception("The signal being added already exists")
                else:
                    self._signal_dict[sgn.sequential] = sgn
            else:
                raise Exception("The signal being added exceeds the number of signals registered")

        if self._check_all_up():
            self._all_up_timestamp = datetime.utcnow().timestamp()

    def _check_all_up(self):
        for sgn in self._signal_dict.values():
            if sgn.is_signal_up:
                self._signal_count += 1

        if self._signal_count == self._signal_up_count:
            self._is_all_up = True
        else:
            self._is_all_up = False

        return self._is_all_up

    def remove_signals(self, signal: Signal, *args: Signal):
        signals = list()
        signals.append(signal)
        signals.extend(args)
        for sgn in signals:
            if self._signal_dict[sgn.sequential]:
                self._signal_dict.pop(sgn.sequential)
            else:
                raise Exception("The signal being removed does not exist")

    def update_signals(self, signal: Signal, *args: Signal):
        signals = list()
        signals.append(signal)
        signals.extend(args)
        for sgn in signals:
            if self._signal_dict[sgn.sequential]:
                self._signal_dict[sgn.sequential] = sgn

        if self._check_all_up():
            self._all_up_timestamp = datetime.utcnow().timestamp()
