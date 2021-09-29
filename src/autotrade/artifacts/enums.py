from enum import Enum


# DIVIDER: --------------------------------------
# INFO: Exchange Enum

class Exchange(Enum):
    """Exchanges available and supported by 'pandas_market_calendars' library"""
    TSX = ('TSX', 'CAD', 'CA')
    NYSE = ('NYSE', 'USD', 'US')

    @classmethod
    def currencies(cls):
        return [member.value[1] for member in cls]

    @classmethod
    def exchanges(cls):
        return [member.value[0] for member in cls]

    @classmethod
    def get_currency(cls, currency: str):
        for member in cls:
            if member.value[1] == currency.upper():
                return member

    @classmethod
    def get_exchange(cls, exchange: str):
        for member in cls:
            if member.value[0] == exchange.upper():
                return member


# DIVIDER: --------------------------------------
# INFO: IntervalOption Enum

class IntervalOption(Enum):
    _1M = ('1m', 60)
    _2M = ('2m', 120)
    _5M = ('5m', 300)
    _15M = ('15m', 900)
    _30M = ('30m', 1800)
    _1H = ('1h', 3600)
    _4H = ('4h', 14400)
    _1D = ('1d', 86400)

    @classmethod
    def interval_options(cls):
        return [member.value[0] for member in cls]

    @classmethod
    def get_interval(cls, interval_option: str):
        for member in cls:
            if member.value[0] == interval_option.lower():
                return member


# DIVIDER: --------------------------------------
# INFO: TradeStatus Enum

class TradeStatus(Enum):
    """ TradeStatus: specifies the current status of the trade (ACTIVATED, CANCELLED, STOPPED, RESUMED, CLOSED)."""

    ACTIVATED = 'Activated'
    CANCELLED = 'Cancelled'
    PAUSED = 'Stopped'
    RESUMED = 'Resumed'
    CLOSED = 'Closed'


# DIVIDER: --------------------------------------
# INFO: TradingDurationType Enum

class TradingDurationType(Enum):
    """ TradeDurationType: Trading durations allow you to control how long your trade remains active.
    The following is a list of durations available in a certain trade.

    - DAY: The trade will remain active until the end of the current trading day. The trade is terminated at the end
           of the trading day

    - GTD: Good ‘till date - the trade will remain active until the specified date. The trade will be terminated at
           the end of the chosen day

    - GTC: Good ‘till cancelled - the trade will remain active until it is manually cancelled
    """

    DAY = 'DAY'
    GTD = 'GTD'
    GTC = 'GTC'

    @classmethod
    def duration_options(cls):
        return [member.value for member in cls]


# DIVIDER: --------------------------------------
# INFO: OrderStatus Enum

class OrderStatus(Enum):
    CREATED = 'CREATED'  # BaseOrder has been created at the trader end.
    SUBMITTED = 'SUBMITTED'  # BaseOrder has been submitted.
    ACCEPTED = 'ACCEPTED'  # BaseOrder has been acknowledged by the broker.
    CANCELED = 'CANCELED'  # BaseOrder has been canceled.
    PARTIALLY_FILLED = 'PARTIALLY_FILLED'  # BaseOrder has been partially filled.
    FILLED = 'FILLED'  # BaseOrder has been completely filled.
    EXPIRED = 'EXPIRED'  # BaseOrder has been expired.
    REJECTED = 'REJECTED'  # BaseOrder has been rejected.

    NEW = 'NEW'  # BaseOrder has been created at the broker end.
    PENDING = 'PENDING'
    OTHERS = 'OTHERS'


# DIVIDER: --------------------------------------
# INFO: OrderType Enum

class OrderType(Enum):
    MARKET = 'MARKET'  # Abbreviation: MKT (mkt)
    LIMIT = 'LIMIT'  # Abbreviation: LMT (lmt)
    STOP_LIMIT = 'STOP_LIMIT'  # Abbreviation: SLO (slo)
    STOP = 'STOP'  # Abbreviation: STP (stp)
