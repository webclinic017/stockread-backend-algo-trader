# Copyright (C) 2021-2030 StockRead Inc.
# Author: Thanh Tung Nguyen
# Contact: tungstudies@gmail.com

from typing import Optional, Union, Dict

from src.autotrade.bars.bar import Bar
from src.errors import DependentSignalConflict, ValueNotPresentException, SignalNotRequiredException, \
    MissingDependentSignalError


# DIVIDER: --------------------------------------
# INFO: Signal Concrete Class

class Signal:

    def __init__(self, isbuy: bool, codename: str, sequence: str,
                 sequence_types: tuple = ('only', 'first', 'middle', 'last'), leading_dependent_signal=None):

        if sequence.lower() not in sequence_types:
            raise ValueNotPresentException(provided_value=sequence.lower(),
                                           value_list=sequence_types)
        self._isbuy = isbuy
        self._codename = codename
        self._sequence = sequence
        self._notes = dict()

        if not self.is_leading_dependent_required():
            self._sequential = 1
            if leading_dependent_signal:
                raise SignalNotRequiredException(signal_type='leading')
        else:
            if not leading_dependent_signal:
                raise MissingDependentSignalError(signal_type='leading')
            if not isinstance(leading_dependent_signal, Signal):
                raise TypeError('Signal class instance required')
            if leading_dependent_signal.isbuy != self._isbuy:
                raise DependentSignalConflict(isbuy=self._isbuy)

            self._leading_dependent_signal: Signal = leading_dependent_signal
            self._leading_dependent_signal.set_trailing_dependent_signal(self)
            self._sequential = self._leading_dependent_signal._sequential + 1

        if self.is_trailing_dependent_required():
            self._trailing_dependent_signal: Union[Signal, None] = None

        self._is_up: Optional[bool] = None
        self._signal_up_timestamp: Optional[int] = None
        self._signal_up_datetime: Optional[str] = None
        self._price_at_signal: Optional[float] = None
        self._volume_at_signal: Optional[int] = None
        self._indicator_value_at_signal = None

    # DIVIDER: Required Class Construction Methods --------------------------------------------------------

    def __str__(self):
        tojoin = list()
        tojoin.append('ClassType: {}'.format(type(self).__name__))
        tojoin.append('CodeName: {}'.format(self._codename))
        tojoin.append('Sequence: {}'.format(self._sequence))
        tojoin.append('Sequential: {}'.format(self._sequential))
        tojoin.append('CodeName: {}'.format(self._codename))
        tojoin.append('IsLeadingDependentRequired: {}'.format(self.is_leading_dependent_required()))
        tojoin.append('IsTrailingDependentRequired: {}'.format(self.is_trailing_dependent_required()))
        tojoin.append('IsTrailingDependentAttached: {}'.format(self.is_trailing_dependent_required()))
        tojoin.append('IsSignalUp: {}'.format(self._is_up))
        tojoin.append('SignalUpTimestamp: {}'.format(self._signal_up_timestamp))
        tojoin.append('PriceAtSignal: {}'.format(self._price_at_signal))
        tojoin.append('IndicatorValueAtSignal: {}'.format(self._indicator_value_at_signal))

        return ', '.join(tojoin)

    def set_trailing_dependent_signal(self, trailing_dependent_signal):
        if self.is_trailing_dependent_required():

            if not isinstance(trailing_dependent_signal, Signal):
                raise TypeError('Signal class instance required')

            if trailing_dependent_signal.isbuy != self._isbuy:
                raise DependentSignalConflict(isbuy=self._isbuy)

            self._trailing_dependent_signal = trailing_dependent_signal

        else:
            raise SignalNotRequiredException(signal_type='trailing')

    # DIVIDER: Publicly Accessible Method Properties ----------------------------------------------

    @property
    def sequential(self):
        return self._sequential

    @property
    def codename(self):
        return self._codename

    @property
    def notes(self):
        return self._notes

    @property
    def sequence(self):
        return self._sequence

    @property
    def signal_up_timestamp(self):
        return self._signal_up_timestamp

    @property
    def signal_up_datetime(self):
        return self._signal_up_datetime

    @property
    def price_at_signal(self):
        return self._price_at_signal

    @property
    def volume_at_signal(self):
        return self._volume_at_signal

    @property
    def indicator_value_at_signal(self):
        return self._indicator_value_at_signal

    @property
    def isbuy(self):
        return self._isbuy

    @property
    def is_up(self):
        if self.is_leading_dependent_required():
            if self._leading_dependent_signal:
                return self._is_up and self._leading_dependent_signal.is_up
            else:
                raise MissingDependentSignalError(signal_type='leading')
        else:
            return self._is_up

    # DIVIDER: Publicly Accessible Methods --------------------------------------------------------

    def is_trailing_dependent_required(self):
        return self._sequence in {'first', 'middle'}

    def is_leading_dependent_required(self):
        return self._sequence in {'middle', 'last'}

    def is_trailing_dependent_attached(self):
        if self._trailing_dependent_signal:
            return True
        else:
            return False

    def is_first(self):
        return self._sequence == 'first'

    def is_last(self):
        return self._sequence == 'last'

    def is_only(self):
        return self._sequence == 'only'

    def is_middle(self):
        return self._sequence == 'middle'

    def up_signal(self, ref_bar: Bar, ref_indicator_value=None):
        if self.is_up:
            self.down_signal()

        self._is_up = True
        self._signal_up_timestamp = ref_bar.timestamp
        self._signal_up_datetime = ref_bar.datetime
        self._price_at_signal = ref_bar.close
        self._volume_at_signal = ref_bar.volume
        self._indicator_value_at_signal = ref_indicator_value

        if self.is_leading_dependent_required():
            if self._leading_dependent_signal:
                if not self._leading_dependent_signal.is_up:
                    self.down_signal()
            else:
                raise MissingDependentSignalError(signal_type='leading')

    def down_signal(self):
        self._is_up = False
        self._signal_up_timestamp = None
        self._signal_up_datetime = None
        self._price_at_signal = None
        self._volume_at_signal = None
        self._indicator_value_at_signal = None

        if self.is_trailing_dependent_required():
            if self._trailing_dependent_signal:
                self._trailing_dependent_signal.down_signal()
            else:
                raise MissingDependentSignalError(signal_type='trailing')

    def set_codename(self, codename: str):
        self._codename = codename

    def upsert_notes(self, note_id_name: str, note_desc: str):
        if note_id_name in self.notes:
            self._notes[note_id_name] = note_desc
        else:
            self._notes[note_id_name] = note_desc


# DIVIDER: --------------------------------------
# INFO: SignalSet Concrete Class

class SignalSet:
    def __init__(self, isbuy: bool, signal_count: int):
        # setup signal set
        self._isbuy = isbuy
        self._signal_count = signal_count
        self._signal_dict: Dict[int, Signal] = dict()

    # DIVIDER: Publicly Accessible Method Properties ----------------------------------------------

    @property
    def signal_count(self):
        return self._signal_count

    @property
    def signal_up_count(self):
        signal_up_count = 0
        for sgn in self._signal_dict.values():
            if sgn.is_up:
                signal_up_count += 1
        return signal_up_count

    @property
    def signal_down_count(self):
        signal_down_count = 0
        for sgn in self._signal_dict.values():
            if not sgn.is_up:
                signal_down_count += 1
        return signal_down_count

    @property
    def fist_signal(self):
        return self._signal_dict[1]

    @property
    def last_signal(self):
        if not self._signal_count == len(self._signal_dict):
            raise Exception(
                f'Missing {self._signal_count - len(self._signal_dict)} signal(s) out of {self._signal_count}')
        return self._signal_dict[self._signal_count]

    @property
    def allup_timestamp(self):
        return self.last_signal.signal_up_timestamp

    @property
    def allup_price(self):
        return self.last_signal.price_at_signal

    @property
    def allup_volume(self):
        return self.last_signal.volume_at_signal

    @property
    def allup_datetime(self):
        return self.last_signal.signal_up_datetime

    # DIVIDER: Publicly Accessible Methods --------------------------------------------------------

    def add_signals(self, *args: Signal):
        adding_signals = list()
        adding_signals.extend(args)
        for sgn in adding_signals:
            if len(self._signal_dict) < self.signal_count:
                if sgn.sequential in self._signal_dict:
                    raise Exception("The signal being added already exists")
                if sgn.isbuy != self._isbuy:
                    raise DependentSignalConflict(isbuy=self._isbuy)
                self._signal_dict[sgn.sequential] = sgn
            else:
                raise Exception("The signal being added exceeds the number of signals registered")

        if not sorted(list(self._signal_dict.keys())) == list(range(min(list(self._signal_dict.keys())),
                                                                    max(list(self._signal_dict.keys())) + 1)):
            raise Exception("The signals added are not consecutively linked")

    def remove_signals(self, *args: Signal):
        removing_signals = list()
        removing_signals.extend(args)
        for sgn in removing_signals:
            if sgn.sequential in self._signal_dict:
                self._signal_dict.pop(sgn.sequential)
            else:
                raise KeyError("The signal being removed does not exist")

    def down_signal(self):
        self.fist_signal.down_signal()

    def is_alldown(self):
        return not self.fist_signal.is_up

    def is_allup(self):
        return self.last_signal.is_up


# DIVIDER: --------------------------------------
# INFO: Usage Examples

if __name__ == '__main__':

    is_to_test_run = True

    if is_to_test_run:
        first_signal = Signal(isbuy=True, codename='TheFirstSignal', sequence='first')

        middle_signal = Signal(isbuy=True, codename='TheMiddleSignal', sequence='middle',
                               leading_dependent_signal=first_signal)

        last_signal = Signal(isbuy=True, codename='TheLastSignal', sequence='last',
                             leading_dependent_signal=middle_signal)

        first_bar_dict = {'timestamp': 1569297600,
                          'datetime': '9/24/2019, 12:00:00 AM',
                          'open': 221.03,
                          'high': 221.03,
                          'low': 217.19,
                          'close': 217.68,
                          'volume': 33463820,
                          'interval': '1d',
                          'ticker_symbol': 'AAPL'}

        first_bar = Bar(bar_dict=first_bar_dict)

        middle_bar_dict = {'timestamp': 1569384000,
                           'datetime': '9/25/2019, 12:00:00 AM',
                           'open': 218.55,
                           'high': 221.50,
                           'low': 217.14,
                           'close': 221.03,
                           'volume': 24018876,
                           'interval': '1d',
                           'ticker_symbol': 'AAPL'}

        middle_bar = Bar(bar_dict=middle_bar_dict)

        last_bar_dict = {'timestamp': 1569470400,
                         'datetime': '9/26/2019, 12:00:00 AM',
                         'open': 220.13,
                         'high': 220.94,
                         'low': 218.83,
                         'close': 219.89,
                         'volume': 20730608,
                         'interval': '1d',
                         'ticker_symbol': 'AAPL'}

        last_bar = Bar(bar_dict=last_bar_dict)

        print(first_signal)
        print(middle_signal)
        print(last_signal)

        sgnl_set = SignalSet(isbuy=True, signal_count=3)
        sgnl_set.add_signals(first_signal, last_signal, middle_signal)

        first_signal.up_signal(ref_bar=first_bar, ref_indicator_value=29)
        middle_signal.up_signal(ref_bar=middle_bar, ref_indicator_value=71)
        last_signal.up_signal(ref_bar=last_bar, ref_indicator_value=31)

        print(sgnl_set.last_signal)
        first_signal.up_signal(ref_bar=first_bar, ref_indicator_value=29)
        print(sgnl_set.signal_up_count)
        print(sgnl_set.is_allup())
        sgnl_set.down_signal()
        print(sgnl_set.is_alldown())

    else:
        pass
