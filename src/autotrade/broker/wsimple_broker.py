# Copyright (C) 2021-2030 StockRead Inc.
# Author: Thanh Tung Nguyen
# Contact: tungstudies@gmail.com

import datetime
from typing import Optional, List, Union
from typing import TYPE_CHECKING

from dateutil import tz

from src.autotrade.artifacts.order import Order, OrderAction, OrderType, OrderStatus, RegularOrder, StopOrder
from src.autotrade.artifacts.position import Position
from src.autotrade.broker.base_broker import BaseLiveBroker
from src.autotrade.broker.base_broker import IBroker, ILiveBroker
from src.autotrade.broker_conn.wsimple_conn import WSimpleConnection
from src.errors import MissingRequiredTradingElement, TickerIDNotFoundError

if TYPE_CHECKING:
    from src.autotrade.trade import Trade


# DIVIDER: --------------------------------------
# INFO: WSimpleBroker Concrete Class

class WSimpleBroker(BaseLiveBroker, IBroker, ILiveBroker):

    def __init__(self, wsimple_conn: WSimpleConnection = WSimpleConnection(), local_timezone: str = 'America/Montreal'):
        super().__init__()
        self._local_tz = local_timezone
        self._conn = wsimple_conn

    def bind_to_trade(self, trade: 'Trade'):
        """
        :param trade: Trade instance is used to get trading ticker symbol and currency
        :type trade: Trade
        """
        self._trade = trade
        self._trading_symbol = self._trade.trading_symbol
        self._currency = self._trade.currency
        self._find_ticker_id()

    @property
    def is_live(self):
        return self._is_live

    @property
    def auth(self):
        return self._conn.auth

    @property
    def ticker_symbol(self):
        if not self._trading_symbol:
            raise MissingRequiredTradingElement(class_name=type(self).__name__, element_type='trading_symbol')
        else:
            return self._trading_symbol

    def _find_ticker_id(self):
        if not self._ticker_id:
            resp = self.auth.find_securities(ticker=self._trading_symbol, fuzzy=True)
            results = resp['results']
            for each in results:
                if each and each['stock']['symbol'] == self._trading_symbol and each['currency'] == self._currency:
                    self._ticker_id = each['id']
                    return self._ticker_id

            raise TickerIDNotFoundError(class_name=type(self).__name__, ticker_symbol=self.ticker_symbol)
        else:
            return self._ticker_id

    @property
    def trading_account(self):
        if self._trading_account_id:
            return self._trading_account_id
        else:
            raise MissingRequiredTradingElement()



    @trading_account.setter
    def trading_account(self, trading_account_id: str = "tfsa-hyrnpbqo"):
        self._trading_account_id = trading_account_id

        accounts = self.auth.get_accounts()
        trading_account = [account for account in accounts['results'] if account['id'] == self._trading_account_id][0]
        account_cash_available = trading_account['buying_power']['amount']

        self._account_cash_available = account_cash_available

    @property
    def buying_power(self):
        if not self._trading_account_id:
            raise Exception(f'The trading account has not been set. '
                            f'It is required to set trading account at the very beginning')

        return self._account_cash_available

    def get_position(self, position: Position) -> Position:
        if self._is_well_setup() and position.ticker_symbol == self._trading_symbol:
            try:
                resp = self.auth.get_positions(sec_id=self._ticker_id, account_id=self._trading_account_id)

                if resp['results']:
                    quantity = resp['results'][0]['sellable_quantity']
                    book_value = resp['results'][0]['book_value']['amount']
                    price = 0 if quantity == 0 else round(book_value / quantity, 2)
                    position.retrieve(quantity, price)
                    position.set_ticker_id(resp['results'][0]['id'])
                    position.set_currency(resp['results'][0]['currency'])

                return position
            except Exception as err:
                raise Exception(f'PositionRequestError: {err}')

    def market_buy(self, order: Order) -> Order:
        if self._is_well_setup() and order.trading_symbol == self._trading_symbol:
            order.set_ticker_id(self._ticker_id)
            try:
                resp = self.auth.market_buy_order(security_id=order.ticker_id,
                                                  quantity=order.size,
                                                  account_id=self._trading_account_id)

                order = self.read_resp_order(order, resp)

                print(f'The MARKET BUY order has been made.\n'
                      f'Order details: {order}')
                return order

            except Exception as err:
                raise Exception(f'OrderPlacingError: {err}')

    def market_sell(self, order: Order) -> Order:
        if self._is_well_setup() and order.trading_symbol == self._trading_symbol:
            order.set_ticker_id(self._ticker_id)

            try:
                resp = self.auth.market_sell_order(security_id=order.ticker_id,
                                                   quantity=order.size,
                                                   account_id=self._trading_account_id)

                order = self.read_resp_order(order, resp)

                print(f'The MARKET SELL order has been made.\n'
                      f'Order details: {order}')
                return order

            except Exception as err:
                raise Exception(f'OrderPlacingError: {err}')

    def limit_buy(self, order: Order) -> Order:

        if self._is_well_setup() and order.trading_symbol == self._trading_symbol:
            order.set_ticker_id(self._ticker_id)

            try:
                resp = self.auth.limit_buy_order(security_id=order.ticker_id,
                                                 limit_price=order.limit_price,
                                                 quantity=order.size,
                                                 account_id=self._trading_account_id)
                # response example
                '''
                {'object': 'order', 'id': 'order-4c6a2c51-226f-4ec3-bee4-0aed36ac1c83', 
                'account_hold_value': {'amount': 1, 'currency': 'CAD'}, 'account_id': 'tfsa-hyrnpbqo', 'account_value': None, 
                'completed_at': None, 'created_at': '2021-07-23T00:40:27.468Z', 'fill_fx_rate': None, 'fill_quantity': None, 
                'filled_at': None, 'market_value': None, 'order_id': 'order-4c6a2c51-226f-4ec3-bee4-0aed36ac1c83', 
                'order_sub_type': 'limit', 'order_type': 'buy_quantity', 'perceived_filled_at': None, 'quantity': 1, 
                'security_id': 'sec-s-93a8e20409f34e01a053525c981f1ef1', 'security_name': 'Shopify Inc (Class A)', 
                'settled': False, 'status': 'new', 'stop_price': None, 'symbol': 'SHOP', 'time_in_force': 'day', 
                'updated_at': '2021-07-23T00:40:27.468Z', 'limit_price': {'amount': 1, 'currency': 'CAD'}, 
                'external_order_id': 'order-4c6a2c51-226f-4ec3-bee4-0aed36ac1c83', 
                'external_order_batch_id': 'order-batch-4c6a2c51-226f-4ec3-bee4-0aed36ac1c83', 
                'external_security_id': 'sec-s-93a8e20409f34e01a053525c981f1ef1', 'account_currency': 'CAD', 
                'market_currency': 'CAD'}
        
                '''
                order = self.read_resp_order(order, resp)

                print(f'The LIMIT BUY order has been made.\n'
                      f'Order details: {order}')
                return order

            except Exception as err:
                raise Exception(f'OrderPlacingError: {err}')

        return order

    def limit_sell(self, order: Order) -> Order:
        if self._is_well_setup() and order.trading_symbol == self._trading_symbol:
            order.set_ticker_id(self._ticker_id)

            try:
                resp = self.auth.limit_sell_order(security_id=order.ticker_id,
                                                  limit_price=order.limit_price,
                                                  quantity=order.size,
                                                  account_id=self._trading_account_id)
                order = self.read_resp_order(order, resp)

                print(f'The LIMIT SELL order has been made.\n'
                      f'Order details: {order}')
                return order

            except Exception as err:
                raise Exception(f'OrderPlacingError: {err}')

    def stop_limit_buy(self, order: Order) -> Order:
        if self._is_well_setup() and order.trading_symbol == self._trading_symbol:
            order.set_ticker_id(self._ticker_id)

        try:
            resp = self.auth.stop_limit_buy_order(security_id=order.ticker_id,
                                                  stop_price=order.stop_price,
                                                  limit_price=order.limit_price,
                                                  quantity=order.size,
                                                  account_id=self._trading_account_id)
            order = self.read_resp_order(order, resp)

            print(f'The STOP LIMIT BUY order has been made.\n'
                  f'Order details: {order}')
            return order

        except Exception as err:
            raise Exception(f'OrderPlacingError: {err}')

    def stop_limit_sell(self, order: Order) -> Order:
        if self._is_well_setup() and order.trading_symbol == self._trading_symbol:
            order.set_ticker_id(self._ticker_id)

        try:
            resp = self.auth.stop_limit_sell_order(security_id=order.ticker_id,
                                                   stop_price=order.stop_price,
                                                   limit_price=order.limit_price,
                                                   quantity=order.size,
                                                   account_id=self._trading_account_id)

            order = self.read_resp_order(order, resp)

            print(f'The STOP LIMIT SELL order has been made.\n'
                  f'Order details: {order}')
            return order

        except Exception as err:
            raise Exception(f'OrderPlacingError: {err}')

    def cancel_order(self, order: Order) -> Order:
        try:
            self.auth.cancel_order(order.broker_ref_id)  # this request will return an empty dict {}
            order.status = OrderStatus.PENDING

            print(f'The CANCELLING REQUEST has been made.\n'
                  f'Order details: {order}')
            return order

        except Exception as err:
            raise Exception(f'OrderPlacingError: {err}')

    def update_order_info(self, order: Order) -> Order:
        if order.isbuy == OrderAction.BUY:
            resp = self.auth.get_activities(type='buy', sec_id=order.ticker_id,
                                            account_id=self._trading_account_id)
        else:
            resp = self.auth.get_activities(type='sell', sec_id=order.ticker_id,
                                            account_id=self._trading_account_id)
        for each in resp['results']:
            if each['id'] == order.broker_ref_id:

                order = self.read_resp_order(order, each)

                order.stop_price = each['stop_price']['amount'] if each['stop_price'] else 0
                order.limit_price = each['limit_price']['amount'] if each['limit_price'] else 0

                if each['filled_at']:
                    datetime_utc = datetime.datetime.strptime(each['filled_at'], '%Y-%m-%dT%H:%M:%S.%fZ')
                    datetime_filled_at = datetime_utc.replace(tzinfo=tz.gettz('UTC')).astimezone(
                        tz.gettz(self._local_tz))
                    filled_at = datetime_filled_at.isoformat()
                    filled_timestamp = round(datetime_utc.timestamp())
                    order.filled_at = filled_at
                    order.filled_timestamp = filled_timestamp
                    order.fill_quantity = each['fill_quantity']
                    market_value = each['market_value']['amount'] if each['market_value'] else 0
                    order.transaction_value = market_value
                    order.filled_price = order.transaction_value / order.fill_quantity

                return order

    def get_pending_orders(self, order_action: Optional[OrderAction] = None):
        if order_action == OrderAction.SELL:
            resp = self.auth.get_activities(type='sell', sec_id=self._ticker_id,
                                            account_id=self._trading_account_id)
            order_infos = resp['results']
        elif order_action == OrderAction.BUY:
            resp = self.auth.get_activities(type='buy', sec_id=self._ticker_id,
                                            account_id=self._trading_account_id)
            order_infos = resp['results']
        else:
            resp_buy = self.auth.get_activities(type='buy', sec_id=self._ticker_id,
                                                account_id=self._trading_account_id)

            resp_sell = self.auth.get_activities(type='sell', sec_id=self._ticker_id,
                                                 account_id=self._trading_account_id)

            order_infos = resp_buy['results'] + resp_sell['results']

        pending_orders: List[Order] = list()
        for resp in order_infos:
            if not resp['settled'] and not (resp['status'] == 'cancelled' or resp['status'] == 'expired'):

                action = OrderAction.BUY if str(resp['order_type']).split('_')[0].strip() == 'buy' else OrderAction.SELL

                stop_price = resp['stop_price']['amount'] if resp['stop_price'] else 0
                limit_price = resp['limit_price']['amount'] if resp['limit_price'] else 0
                order_sub_type = resp['order_sub_type']
                if order_sub_type == 'stop_limit':
                    order_type = OrderType.STOP_LIMIT
                elif order_sub_type == 'limit':
                    order_type = OrderType.LIMIT

                elif order_sub_type == 'market':
                    order_type = OrderType.MARKET
                else:
                    order_type = OrderType.STOP

                order = Order(isbuy=action, order_type=order_type, size=resp['quantity'],
                              trading_symbol=resp['symbol'], ticker_id=resp['security_id'],
                              stop_price=stop_price, limit_price=limit_price)

                # get 'created at' and 'created_timestamp'
                order = self.read_resp_order(order, resp)
                pending_orders.append(order)

        if pending_orders:
            return pending_orders[0] if len(pending_orders) == 1 else pending_orders

    def read_resp_order(self, order, resp) -> Order:
        order.broker_ref_id = resp['order_id'] if 'order_id' in resp else resp['id']
        order.is_broker_settled = resp['settled']
        order.status = self.translate_order_status(resp['status'])
        order.broker_traded_symbol = resp['symbol']
        order.size = resp['quantity']
        order.ticker_id = resp['security_id']

        # get 'created at' and 'created_timestamp'
        if order.created_at != resp['created_at']:
            utc_created_at = resp['created_at']
            datetime_utc = datetime.datetime.strptime(utc_created_at, '%Y-%m-%dT%H:%M:%S.%fZ')
            datetime_created_at = datetime_utc.replace(tzinfo=tz.gettz('UTC')).astimezone(
                tz.gettz(self._local_tz))
            created_at = datetime_created_at.isoformat()
            created_timestamp = round(datetime_utc.timestamp())
            order.created_at = created_at
            order.created_timestamp = created_timestamp

        return order

    @staticmethod
    def translate_order_status(broker_order_status: str):
        if broker_order_status == 'submitted':
            return OrderStatus.SUBMITTED
        elif broker_order_status == 'expired':
            return OrderStatus.EXPIRED
        elif broker_order_status == 'posted':
            return OrderStatus.FILLED
        elif broker_order_status == 'cancelled':
            return OrderStatus.CANCELED

        # unorthodox status
        elif broker_order_status == 'new':
            return OrderStatus.NEW
        elif broker_order_status == 'cancelling':
            return OrderStatus.PENDING
        else:
            return OrderStatus.OTHERS

    def update_orders(self, ref_price: float):
        pass

    def stop_loss(self, order: StopOrder) -> StopOrder:
        pass

    def take_profit(self, order: StopOrder) -> StopOrder:
        pass

    def update_order(self, order: Union[RegularOrder, StopOrder], ref_price: float):
        pass


if __name__ == '__main__':
    # pass
    from src.autotrade.broker_conn.wsimple_conn import ConnectionWST, WSimpleConnection

    conn_wst = ConnectionWST()
    conn_wst.connect()
    wst_auth = conn_wst.wst_auth
    brok_wst = WSimpleBroker()
    brok_wst.set_trading_account("tfsa-hyrnpbqo")
    brok_wst._trading_symbol = 'CGX'
    brok_wst._currency = 'CAD'
    brok_wst._find_ticker_id()
    print(brok_wst._ticker_id)
    # market_buy_order = Order(action=OrderAction.BUY, order_type=OrderType.MARKET, size=1,
    #                          trading_symbol='CGX', ref_price=10.80)
    # market_buy_order.ref_id = 'order-1d0ddd9c-13d6-4aef-bd44-daee12f1ba33'

    # update = brok_wst.update_order_info(market_buy_order)
    # print(update)

    position = Position('CGX')
    updated_position = brok_wst.get_position(position)
    print(updated_position)

    # market_buy_order = brok_wst.market_buy(order=market_buy_order)
    # cancel = brok_wst.cancel_order(market_buy_order)
    # print(cancel)
