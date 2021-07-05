from typing import Optional, List

from src.autotrade import BrokerBase
from src.autotrade.broker.position import PositionWST
from src.autotrade import Strategy


class Trade:
    def __init__(self, is_continuous: bool=False):
        # trading tools setup
        self._strategy: Optional[Strategy] = None
        self._broker: Optional[BrokerBase] = None
        self._data: Optional[List[dict]] = None

        # ticker symbol setup
        self._trading_ticker_symbol: Optional[str] = None
        self._trading_ticker_symbol_alias: Optional[str] = None
        self._primary_exchange: Optional[str] = None

        # cost vs revenue
        self._buy_amount = None
        self._sell_amount = None
        self._commission = None
        self._size = False

        # trade flag
        self._is_continuous = is_continuous
        self._is_closed = False


    def set_trading_ticker_symbol(self, trading_ticker_symbol, primary_exchange="TSX",
                                  trading_ticker_symbol_alias=None):
        self._trading_ticker_symbol = trading_ticker_symbol
        self._primary_exchange = primary_exchange
        self._trading_ticker_symbol_alias = trading_ticker_symbol_alias

    @property
    def trading_security(self):
        return self._trading_security

    @property
    def trading_position(self):
        if not self._trading_security.id:
            raise ValueError('Trading security value has not been set')

        if not self._trading_account_id:
            raise ValueError('Trading account value has not been set')

        sec_id = self._trading_security.id
        account_id = self._trading_account_id

        trading_position_resp = self._connection.get_positions(sec_id=sec_id, account_id=account_id)
        if trading_position_resp['results']:
            position_info = trading_position_resp['results'][0]
            self._trading_position = PositionWST()
            self._trading_position.set_position(position_info=position_info)
            self._has_position = True
        else:
            self._trading_position = None
            self._has_position = False

        return self._trading_position

    @property
    def has_position(self):
        return self._has_position


if __name__ == '__main__':

    # trade_wst = TradeWTS()
    # trade_wst.set_connection(ws_access)
    # trade_wst.set_trading_account('tfsa-hyrnpbqo')
    # trade_wst.set_trading_ticker_symbol('ZWC')
    # print(trade_wst.trading_position.size)
