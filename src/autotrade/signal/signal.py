# Copyright (C) 2021-2030 StockRead Inc.
# Author: Thanh Tung Nguyen
# Contact: tungstudies@gmail.com
from abc import ABC, abstractmethod
from typing import Optional, Union, Dict

from src.autotrade.bars.bar import Bar
from src.errors import DependentSignalConflict, ValueNotPresentException, SignalNotRequiredException, \
    MissingDependentSignalError


# DIVIDER: --------------------------------------
# INFO: ISignalChaining Interface (SignalChaining - Interface)

class ISignalChaining(ABC):

    @abstractmethod
    def is_trailing_dependent_required(self):
        raise NotImplementedError()

    @abstractmethod
    def is_leading_dependent_required(self):
        raise NotImplementedError()

    @abstractmethod
    def is_trailing_dependent_attached(self):
        raise NotImplementedError()

    @abstractmethod
    def is_first(self):
        raise NotImplementedError()

    @abstractmethod
    def is_last(self):
        raise NotImplementedError()

    @abstractmethod
    def is_only(self):
        raise NotImplementedError()

    @abstractmethod
    def is_middle(self):
        raise NotImplementedError()


# DIVIDER: --------------------------------------
# INFO: ISignal Interface (Signal - Interface)

class ISignal(ABC):

    @property
    @abstractmethod
    def isbuy(self):
        raise NotImplementedError()

    @property
    @abstractmethod
    def is_up(self):
        raise NotImplementedError()

    @property
    @abstractmethod
    def is_down(self):
        raise NotImplementedError()

    @property
    @abstractmethod
    def signal_up_price(self):
        raise NotImplementedError()

    @property
    @abstractmethod
    def signal_up_timestamp(self):
        raise NotImplementedError()

    @property
    @abstractmethod
    def signal_up_datetime(self):
        raise NotImplementedError()

    @property
    @abstractmethod
    def signal_up_volume(self):
        raise NotImplementedError()

    @property
    @abstractmethod
    def signal_up_bar(self):
        raise NotImplementedError()

    @property
    @abstractmethod
    def signal_up_indicator_value(self):
        raise NotImplementedError()

    @abstractmethod
    def down_signal(self):
        raise NotImplementedError()


# DIVIDER: --------------------------------------
# INFO: Signal Concrete Class

class Signal(ISignal):

    def __init__(self, isbuy: bool, codename: str, sequence: str,
                 sequence_types: tuple = ('only', 'first', 'middle', 'last'), leading_dependent_signal=None):

        if sequence.lower() not in sequence_types:
            raise ValueNotPresentException(provided_value=sequence.lower(),
                                           value_list=sequence_types)
        self._isbuy = isbuy
        self._codename = codename
        self._sequence = sequence
        self._note: Optional[str] = None

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
        self._signal_up_bar: Optional[Bar] = None
        self._signal_up_timestamp: Optional[int] = None
        self._signal_up_datetime: Optional[str] = None
        self._signal_up_price: Optional[float] = None
        self._signal_up_volume: Optional[int] = None
        self._signal_up_indicator_value = None

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
        tojoin.append('PriceAtSignal: {}'.format(self._signal_up_price))
        tojoin.append('IndicatorValueAtSignal: {}'.format(self._signal_up_indicator_value))

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
    def note(self):
        return self._note

    @property
    def sequence(self):
        return self._sequence

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

    @property
    def is_down(self):
        return not self.is_up()

    @property
    def signal_up_bar(self):
        return self._signal_up_bar

    @property
    def signal_up_timestamp(self):
        return self._signal_up_timestamp

    @property
    def signal_up_datetime(self):
        return self._signal_up_datetime

    @property
    def signal_up_price(self):
        return self._signal_up_price

    @property
    def signal_up_volume(self):
        return self._signal_up_volume

    @property
    def signal_up_indicator_value(self):
        return self._signal_up_indicator_value

    # DIVIDER: Publicly Accessible Setters --------------------------------------------------------

    def set_codename(self, codename: str):
        self._codename = codename

    def set_note(self, note: str):
        self._note = note

    def set_sequential(self, sequential: int):
        if self.is_only():
            self._sequential = sequential
        else:
            raise Exception('DependentSignalSequentialException: Sequential of dependent signal is not settable')

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
        self._signal_up_price = ref_bar.close
        self._signal_up_volume = ref_bar.volume
        self._signal_up_indicator_value = ref_indicator_value

        if self.is_leading_dependent_required():
            if self._leading_dependent_signal:
                if not self._leading_dependent_signal.is_up:
                    self.down_signal()
            else:
                raise MissingDependentSignalError(signal_type='leading')

    def down_signal(self):
        self._is_up = False
        self._signal_up_bar = None
        self._signal_up_timestamp = None
        self._signal_up_datetime = None
        self._signal_up_price = None
        self._signal_up_volume = None
        self._signal_up_indicator_value = None

        if self.is_trailing_dependent_required():
            if self._trailing_dependent_signal:
                self._trailing_dependent_signal.down_signal()
            else:
                raise MissingDependentSignalError(signal_type='trailing')


# DIVIDER: --------------------------------------
# INFO: SignalSet Concrete Class

class SignalSet(ISignal):

    def __init__(self, isbuy: bool, signal_count: int):
        # setup signal set
        self._isbuy = isbuy
        self._signal_count = signal_count
        self._signal_dict: Dict[int, Signal] = dict()

    # DIVIDER: Publicly Accessible Method Properties ----------------------------------------------

    @property
    def isbuy(self):
        return self._isbuy

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
    def is_down(self):
        return len([sgn for sgn in self._signal_dict.values() if not sgn.is_up]) == self.signal_count

    @property
    def is_up(self):
        return len([sgn for sgn in self._signal_dict.values() if sgn.is_up]) == self.signal_count

    @property
    def signal_up_bar(self):
        allup_info = self._get_allup_info()
        if allup_info:
            return allup_info['allup_bar']

    @property
    def signal_up_timestamp(self):
        allup_info = self._get_allup_info()
        if allup_info:
            return allup_info['allup_timestamp']

    @property
    def signal_up_price(self):
        allup_info = self._get_allup_info()
        if allup_info:
            return allup_info['allup_price']

    @property
    def signal_up_volume(self):
        allup_info = self._get_allup_info()
        if allup_info:
            return allup_info['allup_volume']

    @property
    def signal_up_datetime(self):
        allup_info = self._get_allup_info()
        if allup_info:
            return allup_info['allup_datetime']

    @property
    def signal_up_indicator_value(self):
        allup_info = self._get_allup_info()
        if allup_info:
            return allup_info['allup_indicator_value']

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
        for sgn in self._signal_dict.values():
            if sgn.is_up:
                sgn.down_signal()

    def _get_allup_info(self):
        signal_up_count = 0
        allup_timestamp = 0
        allup_price: float = 0.0
        allup_volume: int = 0
        allup_datetime = None
        allup_indicator_value = None
        allup_bar = None

        for sgn in self._signal_dict.values():
            if sgn.is_up:
                signal_up_count += 1
                if sgn.signal_up_timestamp > allup_timestamp:
                    allup_timestamp = sgn.signal_up_timestamp
                    allup_price = sgn.signal_up_price
                    allup_volume = sgn.signal_up_volume
                    allup_datetime = sgn.signal_up_datetime
                    allup_indicator_value = sgn.signal_up_indicator_value
                    allup_bar = sgn.signal_up_bar

        if signal_up_count == self.signal_count:
            return {'is_allup': True,
                    'greatest_timestamp': allup_timestamp,
                    'allup_price': allup_price,
                    'allup_volume': allup_volume,
                    'allup_indicator_value': allup_indicator_value,
                    'allup_bar': allup_bar,
                    'allup_datetime': allup_datetime}


# DIVIDER: --------------------------------------
# INFO: Usage Examples

if __name__ == '__main__':

    is_to_test_run = True

    if is_to_test_run:

        rsi_buy_signal = Signal(isbuy=True, codename='RSIBuy', sequence='only')
        mfi_buy_signal = Signal(isbuy=True, codename='MFIBuy', sequence='only')

        mfi_buy_signal.set_sequential(sequential=2)

        sgnl_set = SignalSet(isbuy=True, signal_count=2)
        sgnl_set.add_signals(rsi_buy_signal, mfi_buy_signal)

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

        print(rsi_buy_signal)
        print(mfi_buy_signal)

        rsi_buy_signal.up_signal(ref_bar=first_bar, ref_indicator_value=29)
        mfi_buy_signal.up_signal(ref_bar=middle_bar, ref_indicator_value=71)

        print(sgnl_set.fist_signal)
        print(sgnl_set.last_signal)
        print(sgnl_set.signal_up_count)
        print(sgnl_set.is_up)
        sgnl_set.down_signal()
        print(sgnl_set.is_down)

    else:
        pass

    # is_to_test_run = True
    #
    # if is_to_test_run:
    #
    #     first_signal = Signal(isbuy=True, codename='TheFirstSignal', sequence='first')
    #
    #     middle_signal = Signal(isbuy=True, codename='TheMiddleSignal', sequence='middle',
    #                            leading_dependent_signal=first_signal)
    #
    #     last_signal = Signal(isbuy=True, codename='TheLastSignal', sequence='last',
    #                          leading_dependent_signal=middle_signal)
    #
    #     first_bar_dict = {'timestamp': 1569297600,
    #                       'datetime': '9/24/2019, 12:00:00 AM',
    #                       'open': 221.03,
    #                       'high': 221.03,
    #                       'low': 217.19,
    #                       'close': 217.68,
    #                       'volume': 33463820,
    #                       'interval': '1d',
    #                       'ticker_symbol': 'AAPL'}
    #
    #     first_bar = Bar(bar_dict=first_bar_dict)
    #
    #     middle_bar_dict = {'timestamp': 1569384000,
    #                        'datetime': '9/25/2019, 12:00:00 AM',
    #                        'open': 218.55,
    #                        'high': 221.50,
    #                        'low': 217.14,
    #                        'close': 221.03,
    #                        'volume': 24018876,
    #                        'interval': '1d',
    #                        'ticker_symbol': 'AAPL'}
    #
    #     middle_bar = Bar(bar_dict=middle_bar_dict)
    #
    #     last_bar_dict = {'timestamp': 1569470400,
    #                      'datetime': '9/26/2019, 12:00:00 AM',
    #                      'open': 220.13,
    #                      'high': 220.94,
    #                      'low': 218.83,
    #                      'close': 219.89,
    #                      'volume': 20730608,
    #                      'interval': '1d',
    #                      'ticker_symbol': 'AAPL'}
    #
    #     last_bar = Bar(bar_dict=last_bar_dict)
    #
    #     print(first_signal)
    #     print(middle_signal)
    #     print(last_signal)
    #
    #     sgnl_set = SignalSet(isbuy=True, signal_count=3)
    #     sgnl_set.add_signals(first_signal, last_signal, middle_signal)
    #
    #     first_signal.up_signal(ref_bar=first_bar, ref_indicator_value=29)
    #     middle_signal.up_signal(ref_bar=middle_bar, ref_indicator_value=71)
    #     last_signal.up_signal(ref_bar=last_bar, ref_indicator_value=31)
    #
    #     print(sgnl_set.last_signal)
    #     first_signal.up_signal(ref_bar=first_bar, ref_indicator_value=29)
    #     print(sgnl_set.signal_up_count)
    #     print(sgnl_set.is_allup())
    #     sgnl_set.down_signal()
    #     print(sgnl_set.is_alldown())
    #
    # else:
    #     pass
