import datetime
from abc import abstractmethod, ABC
from typing import Optional, TYPE_CHECKING, Union, Dict

from src.autotrade.artifacts.order import RegularOrder, StopOrder
from src.autotrade.artifacts.position import Position
from src.errors import MissingRequiredTradingElement, InvalidOrderListCUD

if TYPE_CHECKING:
    from src.autotrade.trade import Trade


# DIVIDER: --------------------------------------
# INFO: BaseBroker Abstract Class (Broker - BaseClass)

class BaseBroker:
    def __init__(self):
        self._is_live = None
        self._trade: Optional['Trade'] = None
        self._comm_amount: float = 0
        self._position: Optional[Position] = None

        # trading instruments to be added
        self._trading_symbol = None
        self._ticker_id = None
        self._currency = None

        # IMPORTANT: Order Management
        self._pending_orders: Dict[str, Union[RegularOrder, StopOrder]] = dict()
        self._settled_orders: Dict[str, Union[RegularOrder, StopOrder]] = dict()

    def __repr__(self):
        tojoin = list()
        tojoin.append('ClassType: {}'.format(type(self).__name__))
        tojoin.append('IsLive: {}'.format(self._is_live))
        tojoin.append('TradingSymbol: {}'.format(self._trading_symbol))
        tojoin.append('TickerID: {}'.format(self._ticker_id))
        tojoin.append('Currency: {}'.format(self._currency))

    def _update_position(self, order: Union[RegularOrder, StopOrder]):
        if order.is_filled():
            self._position.update(order.isbuy, order.fill_quantity, buy_price=order.filled_price)

    def _upsert_pending(self, order: Union[RegularOrder, StopOrder], is_insert=True):

        if order.broker_ref_id in self._pending_orders:
            if is_insert:
                raise InvalidOrderListCUD(class_name=type(self).__name__, operation='insert', order_list_type='pending',
                                          additional_msg='The order already exists. Please review Broker code logic')
            else:
                if order.is_settled():
                    raise InvalidOrderListCUD(class_name=type(self).__name__, operation='update',
                                              order_list_type='pending', expected_order='pending',
                                              unexpected_order='settled',
                                              additional_msg='Please review Broker code logic')

                else:
                    self._pending_orders[order.broker_ref_id] = order
                    print(f"{type(self).__name__}: Order {order.broker_ref_id} has been updated in PENDING list")

        else:
            if is_insert:
                self._pending_orders[order.broker_ref_id] = order
                print(f"{type(self).__name__}: Order {order.broker_ref_id} has been added to PENDING list")

            else:
                raise InvalidOrderListCUD(class_name=type(self).__name__, operation='update',
                                          order_list_type='pending',
                                          additional_msg='The order doest not already exists. '
                                                         'Please review Broker code logic')

    def _upsert_settled(self, order: Union[RegularOrder, StopOrder, None] = None):
        if order:
            if order.is_settled():
                if order.broker_ref_id in self._settled_orders:
                    raise InvalidOrderListCUD(class_name=type(self).__name__, operation='insert',
                                              order_list_type='settled',
                                              additional_msg='The order already exists. Please review Broker code logic')

                else:
                    if order.broker_ref_id in self._pending_orders:
                        self._settled_orders[order.broker_ref_id] = self._pending_orders.pop(order.broker_ref_id)
                        print(f"{type(self).__name__}: Order {order.broker_ref_id} has been removed from PENDING and "
                              f"inserted to SETTLED order list")

                    else:
                        InvalidOrderListCUD(class_name=type(self).__name__, operation='insert',
                                            order_list_type='settled',
                                            additional_msg='The order does not exists in pending list. '
                                                           'Please review Broker code logic')

        else:
            for key, value in self._pending_orders.items():
                if value.is_settled():
                    # remove settled orders out of the pending list and add it to settled list:
                    self._settled_orders[value.broker_ref_id] = self._pending_orders.pop(key)
                    print(f"{type(self).__name__}: Order {order.broker_ref_id} has been moved from PENDING to SETTLED")

    def remove_settled(self, hours_ago=None):
        if hours_ago:
            current_date = datetime.datetime.now().replace(microsecond=0)
            past_date = current_date - datetime.timedelta(hours=hours_ago)
            # remove long lasting settled orders which older than a given timestamp
            for key, value in self._settled_orders.items():
                if value.created_timestamp < past_date.timestamp():
                    self._settled_orders.pop(key)
                    print(f"{type(self).__name__}: The aged order {value.broker_ref_id} has been removed from SETTLED")


# DIVIDER: --------------------------------------
# INFO: BaseLiveBroker Abstract Class (LiveBroker - BaseClass)

class BaseLiveBroker(BaseBroker):
    def __init__(self):
        super().__init__()
        self._is_live = True
        self._conn = None

        # trading account & cash
        self._trading_account_id: Optional[str] = None
        self._account_cash_available: float = 0

    def _is_well_setup(self):
        """
        safety-check if all required components of a live broker are set
        THIS METHOD IS TO BE PLACED AT THE END OF THE CHILD CLASS CONSTRUCTOR
        """

        if not self._trading_account_id:
            raise MissingRequiredTradingElement(class_name=type(self).__name__, element_type='trading_account_id')

        if not self._ticker_id:
            raise MissingRequiredTradingElement(class_name=type(self).__name__, element_type='ticker_id')

        if not self._trading_symbol:
            raise MissingRequiredTradingElement(class_name=type(self).__name__, element_type='trading_symbol')

        if not self._currency:
            raise MissingRequiredTradingElement(class_name=type(self).__name__, element_type='currency')

        if not self._position:
            raise MissingRequiredTradingElement(class_name=type(self).__name__, element_type='position')

        if not self._conn:
            raise MissingRequiredTradingElement(class_name=type(self).__name__, element_type='connection')

        return True


# DIVIDER: --------------------------------------
# INFO: IBroker Interface (Broker - Interface)

class IBroker(ABC):

    @abstractmethod
    def bind_to_trade(self, trade):
        raise NotImplementedError()

    @property
    @abstractmethod
    def is_live(self):
        raise NotImplementedError()

    @property
    @abstractmethod
    def ticker_symbol(self):
        raise NotImplementedError()

    @abstractmethod
    def market_buy(self, order: RegularOrder) -> RegularOrder:
        raise NotImplementedError()

    @abstractmethod
    def market_sell(self, order: RegularOrder) -> RegularOrder:
        raise NotImplementedError()

    @abstractmethod
    def limit_buy(self, order: RegularOrder) -> RegularOrder:
        raise NotImplementedError()

    @abstractmethod
    def limit_sell(self, order: RegularOrder) -> RegularOrder:
        raise NotImplementedError()

    @abstractmethod
    def stop_limit_buy(self, order: StopOrder) -> StopOrder:
        raise NotImplementedError()

    @abstractmethod
    def stop_limit_sell(self, order: StopOrder) -> StopOrder:
        raise NotImplementedError()

    @abstractmethod
    def stop_loss(self, order: StopOrder) -> StopOrder:
        raise NotImplementedError()

    @abstractmethod
    def take_profit(self, order: StopOrder) -> StopOrder:
        raise NotImplementedError()

    @abstractmethod
    def cancel_order(self, order: Union[RegularOrder, StopOrder]) -> Union[RegularOrder, StopOrder]:
        raise NotImplementedError()

    @abstractmethod
    def update_order(self, order: Union[RegularOrder, StopOrder], ref_price: float):
        raise NotImplementedError()

    @abstractmethod
    def update_pending_orders(self, ref_price: float):
        raise NotImplementedError()

    @abstractmethod
    def get_position(self, position: Position, is_live_position: bool) -> Position:
        raise NotImplementedError()


# DIVIDER: --------------------------------------
# INFO: ILiveBroker Interface (LiveBroker - Interface)

class ILiveBroker(ABC):

    @property
    @abstractmethod
    def trading_account(self):
        """Returns the trading account ID"""
        raise NotImplementedError()

    @abstractmethod
    @trading_account.setter
    def trading_account(self, trading_account_id: str):
        """
        Sets the the account to be used for trading
        :param trading_account_id: account_id of the account used for trading
        :type trading_account_id: str
        """
        raise NotImplementedError()

    @abstractmethod
    def _find_ticker_id(self):
        """Returns the instrument information"""
        raise NotImplementedError()

    @abstractmethod
    def get_pending_orders(self, isbuy: Optional[bool] = None):
        """Get unsettled orders from live broker
        :param isbuy: it is to get pending buy (True) order or sell (Fool) or both (default None)
        :type isbuy: bool/None
        """
        raise NotImplementedError()

    @staticmethod
    @abstractmethod
    def translate_order_status(broker_order_status: str):
        """Translates broker order status to system order status"""
        raise NotImplementedError()

    @property
    @abstractmethod
    def buying_power(self):
        """Returns the cash available to trade"""
        raise NotImplementedError()
