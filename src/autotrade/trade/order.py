from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Optional

from wsimple import Wsimple

from src.autotrade import Instrument, InstrumentWST


class OrderAction(Enum):
    BUY = 1
    SELL = 2


class OrderStatus(Enum):
    CREATED = 1  # BaseOrder has been created.
    SUBMITTED = 2  # BaseOrder has been submitted.
    ACCEPTED = 3  # BaseOrder has been acknowledged by the broker.
    CANCELED = 4  # BaseOrder has been canceled.
    PARTIALLY_FILLED = 5  # BaseOrder has been partially filled.
    FILLED = 6  # BaseOrder has been completely filled.
    EXPIRED = 7  # BaseOrder has been expired.
    REJECTED = 8  # BaseOrder has been rejected.


class OrderType(Enum):
    MARKET = 1
    LIMIT = 2
    STOP = 3


class Order(ABC):

    def __init__(self):
        self._id: Optional[str] = None
        self._instrument: Optional[Instrument] = None
        self._size: Optional[int] = None
        self._limit_price: Optional[float] = None
        self._stop_price: Optional[float] = None
        self._executed_price: Optional[int] = None
        self._state = OrderStatus.CREATED
        self._type: Optional[OrderType] = None
        self._action: Optional[OrderAction] = None
        self._created_at = None
        self._filled_at = None
        self._filled_quantity: int = 0
        self._commissions: Optional[float] = None

    @abstractmethod
    def id(self):
        """
        Returns the order id.
        .. note::
            This will be None if the order was not submitted.
        """
        return self._id

    @abstractmethod
    def order_type(self):
        """Returns the order type. Valid order types are:
         * OrderType.MARKET
         * OrderType.LIMIT
         * OrderType.STOP_LIMIT
        """
        return self._type

    @abstractmethod
    def action(self):
        """Returns the order action. Valid order actions are:
         * OrderAction.BUY
         * OrderAction.SELL
        """
        return self._action

    @abstractmethod
    def state(self):
        """Returns the order state. Valid order states are:
         * OrderStatus.CREATED (the initial state).
         * OrderStatus.SUBMITTED
         * OrderStatus.ACCEPTED
         * OrderStatus.CANCELED
         * OrderStatus.PARTIALLY_FILLED
         * OrderStatus.FILLED
         * OrderStatus.EXPIRED
         * OrderStatus.REJECTED
        """
        return self._state

    @abstractmethod
    def is_settled(self):
        """Returns True if the order is settled."""
        return self._state in [OrderStatus.CANCELED, OrderStatus.FILLED, OrderStatus.REJECTED]

    @abstractmethod
    def is_submitted(self):
        """Returns True if the order state is OrderStatus.SUBMITTED."""
        return self._state == OrderStatus.SUBMITTED

    @abstractmethod
    def is_canceled(self):
        """Returns True if the order state is OrderStatus.CANCELED."""
        return self._state == OrderStatus.CANCELED

    @abstractmethod
    def is_filled(self):
        """Returns True if the order state is OrderStatus.FILLED."""
        return self._state == OrderStatus.FILLED

    @abstractmethod
    def is_expired(self):
        """Returns True if the order state is OrderStatus.EXPIRED."""
        return self._state == OrderStatus.EXPIRED

    @abstractmethod
    def instrument(self):
        """Returns the instrument identifier."""
        return self._instrument

    @abstractmethod
    def size(self):
        """Returns the quantity of securities orders."""
        return self._size

    @abstractmethod
    def filled_quantity(self):
        """Returns the number of shares that have been executed."""
        return self._filled_quantity

    @property
    def commissions(self):
        """Returns the commission fees of the order."""
        return self._commissions

    @abstractmethod
    def set_order(self, order_info: dict):
        raise NotImplementedError()

    @abstractmethod
    def create_market_order(self, instrument: Optional[Instrument], size: int, order_action: OrderAction):
        raise NotImplementedError()

    @abstractmethod
    def create_limit_order(self, instrument: Optional[Instrument], size: int, limit_price: float,
                           order_action: OrderAction):
        raise NotImplementedError()

    @abstractmethod
    def create_stop_limit_order(self, instrument: Optional[Instrument], size: int, stop_price: float,
                                limit_price: float, order_action: OrderAction):
        raise NotImplementedError()

    @abstractmethod
    def update_state(self):
        raise NotImplementedError()


class OrderWST(Order):

    def __init__(self):
        super().__init__()
        self._connection: Optional[Wsimple] = None

    def set_connection(self, ws_access: Wsimple):
        self._connection = ws_access

    @property
    def id(self):
        return self._id

    def create_market_order(self, instrument: Optional[InstrumentWST], size: int, order_action: OrderAction):
        self._instrument = instrument
        self._size = size
        self._action = order_action
        self._type = OrderType.MARKET
        self._created_at = datetime.utcnow().timestamp()

    def create_limit_order(self, instrument: Optional[Instrument], size: int, limit_price: float,
                           order_action: OrderAction):
        self._instrument = instrument
        self._size = size
        self._limit_price = limit_price
        self._action = order_action
        self._type = OrderType.LIMIT
        self._created_at = datetime.utcnow().timestamp()

    def create_stop_limit_order(self, instrument: Optional[Instrument], size: int, stop_price: float,
                                limit_price: float, order_action: OrderAction):
        self._instrument = instrument
        self._size = size
        self._limit_price = limit_price
        self._stop_price = stop_price
        self._action = order_action
        self._type = OrderType.LIMIT
        self._created_at = datetime.utcnow().timestamp()
