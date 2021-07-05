from abc import ABC, abstractmethod
from typing import Optional, List

from wsimple import Wsimple

from src.autotrade import BrokerAccount, AccountWST
from src.autotrade import Order, OrderWST, OrderAction
from src.autotrade import InstrumentWST
from src.autotrade.errors import TickerSymbolNotFound
# from autotrade.trade import Trade


class BrokerBaseInterface(ABC):

    @abstractmethod
    def set_cash(self, cash):
        """Sets the cash parameter"""
        raise NotImplementedError()

    @abstractmethod
    def get_cash(self):
        """
        Returns the cash available to trade.
        """
        raise NotImplementedError()

    @abstractmethod
    def add_cash(self, cash):
        """Add/Remove cash to the system (use a negative value to remove)"""
        raise NotImplementedError()

    @abstractmethod
    def get_value(self):
        """Returns the portfolio value"""
        raise NotImplementedError()

    @abstractmethod
    def market_buy(self, ticker_symbol, quantity):
        raise NotImplementedError()

    @abstractmethod
    def market_sell(self, ticker_symbol, quantity):
        raise NotImplementedError()

    @abstractmethod
    def limit_buy(self, ticker_symbol, limit_price, quantity):
        raise NotImplementedError()

    @abstractmethod
    def limit_sell(self, ticker_symbol, stop_price, limit_price, quantity):
        raise NotImplementedError()

    @abstractmethod
    def stop_limit_buy(self, ticker_symbol, stop_price, limit_price, quantity):
        raise NotImplementedError()

    @abstractmethod
    def stop_limit_sell(self, ticker_symbol, stop_price, limit_price, quantity):
        raise NotImplementedError()

    @abstractmethod
    def cancel_order(self, order):
        """Requests an order to be canceled.
        """
        raise NotImplementedError()

    @abstractmethod
    def cancel_all(self):
        raise NotImplementedError()


class BrokerLiveInterface(ABC):
    @abstractmethod
    def set_trading_account(self, trading_account_id: str):
        """
        Sets the the account to be used for trading

        :param trading_account_id:
        :type trading_account_id: str
        """
        raise NotImplementedError()

    @abstractmethod
    def trading_account(self):
        raise NotImplementedError()

    @abstractmethod
    def trading_account_id(self):
        raise NotImplementedError()


class BrokerBase():
    def __init__(self):
        self.IS_LIVE: Optional[bool] = None


class BackBrokerBase(BrokerBase):
    def __init__(self):
        super().__init__()

    def set_back_trader(self):
        self.IS_LIVE = False
        self.set_back_trader()


class LiveBrokerBase(BrokerBase):
    def __init__(self):
        super().__init__()
        self.set_live_trader()

        # cash setup
        self._cash_budget: Optional[float] = None
        self._cash_available_to_trade: Optional[float] = None
        self._value: Optional[float] = None

        # trading account setup
        self._trading_account_id: Optional[str] = None
        self._trading_account: Optional[BrokerAccount] = None

        # order setup
        self.submitted_selL_order: Optional[Order] = None
        self.executed_selL_order: Optional[Trade] = None
        self.submitted_buy_order: Optional[Order] = None
        self.executed_buy_order: Optional[Order] = None
        self.submitted_stop_loss_orders: Optional[List[Order]] = None
        self.executed_stop_order: Optional[Order] = None

    def set_live_trader(self):
        self.IS_LIVE = True


class BrokerWST(LiveBrokerBase, BrokerBaseInterface, BrokerLiveInterface):

    def __init__(self):
        super().__init__()
        self._connection: Optional[Wsimple] = None

    def set_connection(self, ws_access: Wsimple):
        self._connection = ws_access

    def set_cash(self, cash: float):
        if not self._cash_budget:
            self._cash_budget = cash
            self._cash_available_to_trade = cash
        else:
            raise ValueError('Invalid cash budget setup. Cash budget can only be added once before trading.')

    def get_cash(self):
        return self._cash_available_to_trade

    def set_trading_account(self, trading_account_id: str):
        self._trading_account_id = trading_account_id
        accounts_resp = self._connection.get_accounts()

        for account_info in accounts_resp['results']:

            if account_info['id'] == trading_account_id:
                self._trading_account = AccountWST()
                self._trading_account.set_account(account_info)

    @property
    def trading_account_id(self):
        return self._trading_account_id

    @property
    def trading_account(self):
        self.set_trading_account(self._trading_account_id)
        return self.trading_account

    def _find_instrument(self, trading_ticker_symbol, primary_exchange="TSX",
                         trading_ticker_symbol_alias=None):
        resp = self._connection.find_securities(ticker=trading_ticker_symbol)

        ticker_symbol_check = (resp['stock']['symbol'] == trading_ticker_symbol
                               and resp['stock']['primary_exchange'] == primary_exchange)

        ticker_symbol_alias_check = (resp['stock']['symbol'] == trading_ticker_symbol_alias)

        if ticker_symbol_check or ticker_symbol_alias_check:

            instrument = InstrumentWST()
            instrument.set_instrument(instrument_info=resp)

            return instrument

        else:
            raise TickerSymbolNotFound

    def market_buy(self, ticker_symbol, quantity):

        instrument = self._find_instrument(trading_ticker_symbol=ticker_symbol)

        order_wst = OrderWST()
        order_wst.create_market_order(instrument=instrument, size=quantity, order_action=OrderAction.BUY)

        try:

            resp = self._connection.market_buy_order(security_id=instrument.id,
                                                     quantity=quantity,
                                                     account_id=self.trading_account_id)
            order_wst.set_order(order_info=resp)
            self.submitted_buy_order = order_wst
            print(f'The market buy order has been made. Order ID received: {self.submitted_buy_order.id}')
            return order

        except InvalidSecurityIdError:
            print("Security ID used: {}".format(self.sec_id))
            raise InvalidSecurityIdError
