from enum import Enum


class SizerType(Enum):
    BY_SIZE = 1
    BY_AMOUNT = 2


class Sizer:
    def __init__(self, sizer_type: SizerType, value):
        self._set_sizer(sizer_type, value)

    def _set_sizer(self, sizer_type: SizerType, value):
        if sizer_type == SizerType.BY_SIZE:
            self._sizer_type = sizer_type
            self._size: int = value

        if sizer_type == SizerType.BY_AMOUNT:
            self._sizer_type = sizer_type
            self._amount: float = value

    def set_new(self, sizer_type: SizerType, value):
        self._set_sizer(sizer_type, value)

    @property
    def size(self):
        if self._sizer_type != SizerType.BY_SIZE:
            raise Exception('The sizer type is not "BY SIZE"')
        return self._size

    @property
    def amount(self):
        if self._sizer_type == SizerType.BY_SIZE:
            raise Exception('The sizer type is not "BY AMOUNT"')
        else:
            return self._amount



