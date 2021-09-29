# Copyright (C) 2021-2030 StockRead Inc.
# Author: Thanh Tung Nguyen
# Contact: tungstudies@gmail.com

import datetime
from typing import Optional, Union

from dateutil import tz

from src.autotrade.artifacts.order import OrderStatus, RegularOrder, StopOrder
from src.autotrade.artifacts.position import Position
from src.autotrade.broker.base_broker import BaseLiveBroker
from src.autotrade.broker.base_broker import IBroker, ILiveBroker
from src.autotrade.broker_conn.wsimple_conn import WSimpleConnection
from src.errors import MissingRequiredTradingElement, TickerIDNotFoundError, OrderPlacingError, \
    PendingOrderNotInPendingListError, PositionRequestError


# DIVIDER: --------------------------------------
# INFO: WSimpleBroker Concrete Class

class WSimpleBroker(BaseLiveBroker, IBroker, ILiveBroker):

    def __init__(self, wsimple_conn: WSimpleConnection = WSimpleConnection(), local_timezone: str = 'America/Montreal'):
        super().__init__()
        self._local_tz = local_timezone
        self._conn = wsimple_conn

    # DIVIDER: Publicly Accessible Method Properties ----------------------------------------------

    @property
    def is_live(self):
        return self._is_live

    @property
    def auth(self):
        return self._conn.auth

    @property
    def trading_account(self):
        if not self._trading_account_id:
            raise MissingRequiredTradingElement(element_type='trading_account')
        else:
            return self._trading_account_id

    def set_trading_account(self, trading_account_id: str = "tfsa-hyrnpbqo"):
        self._trading_account_id = trading_account_id

        accounts = self.auth.get_accounts()
        trading_account = [account for account in accounts['results'] if account['id'] == self._trading_account_id][0]
        account_cash_available = trading_account['buying_power']['amount']

        self._buying_power = account_cash_available

    @property
    def buying_power(self):
        if not self._trading_account_id:
            raise MissingRequiredTradingElement(element_type='trading_account')

        return self._buying_power

    def _find_ticker_id(self):
        if not self._ticker_id:
            resp = self.auth.find_securities(ticker=self._trading_symbol, fuzzy=True)
            results = resp['results']
            for each in results:
                if each and each['stock']['symbol'] == self._trading_symbol and each['currency'] == self._currency:
                    self._ticker_id = each['id']
                    return self._ticker_id

            raise TickerIDNotFoundError(ticker_symbol=self._trading_symbol)
        else:
            return self._ticker_id

    def initialize(self, trading_symbol: str, currency: str):
        """
        Initialize key attributes of the broker
        """

        self._trading_symbol = trading_symbol
        self._currency = currency
        self._find_ticker_id()

        self._position = Position(self._trading_symbol)
        self._position.set_ticker_id(ticker_id=self._ticker_id)
        self._position.set_currency(currency=self._currency)

    def market_buy(self, order: RegularOrder) -> RegularOrder:
        if self._is_well_setup() and order.trading_symbol == self._trading_symbol:
            order.set_ticker_id(ticker_id=self._ticker_id)
            try:
                resp = self.auth.market_buy_order(security_id=order.ticker_id,
                                                  ref_price=order.ref_price,
                                                  quantity=order.size,
                                                  account_id=self._trading_account_id)
                # print(resp)

                order = self._write_order_resp(order, resp)

                print(f'The MARKET BUY order has been made.\n'
                      f'Order details: {order}')
                return order

            except Exception as err:
                raise OrderPlacingError(order=order, error=err)

    def market_sell(self, order: RegularOrder) -> RegularOrder:
        if self._is_well_setup() and order.trading_symbol == self._trading_symbol:
            order.set_ticker_id(ticker_id=self._ticker_id)

            try:
                resp = self.auth.market_sell_order(security_id=order.ticker_id,
                                                   ref_price=order.ref_price,
                                                   quantity=order.size,
                                                   account_id=self._trading_account_id)

                order = self._write_order_resp(order, resp)

                print(f'The MARKET SELL order has been made.\n'
                      f'Order details: {order}')
                return order

            except Exception as err:
                raise OrderPlacingError(order=order, error=err)

    def limit_buy(self, order: RegularOrder) -> RegularOrder:
        if self._is_well_setup() and order.trading_symbol == self._trading_symbol:
            print(self._ticker_id)
            print(self._trading_symbol)
            order.set_ticker_id(ticker_id=self._ticker_id)

            try:
                resp = self.auth.limit_buy_order(security_id=order.ticker_id,
                                                 limit_price=order.limit_price,
                                                 quantity=order.size,
                                                 account_id=self._trading_account_id)

                order = self._write_order_resp(order, resp)

                print(f'The LIMIT BUY order has been made.\n'
                      f'Order details: {order}')
                return order

            except Exception as err:
                raise OrderPlacingError(order=order, error=err)

        return order

    def limit_sell(self, order: RegularOrder) -> RegularOrder:
        if self._is_well_setup() and order.trading_symbol == self._trading_symbol:
            order.set_ticker_id(ticker_id=self._ticker_id)

            try:
                resp = self.auth.limit_sell_order(security_id=order.ticker_id,
                                                  limit_price=order.limit_price,
                                                  quantity=order.size,
                                                  account_id=self._trading_account_id)
                order = self._write_order_resp(order, resp)

                print(f'The LIMIT SELL order has been made.\n'
                      f'Order details: {order}')
                return order

            except Exception as err:
                raise OrderPlacingError(order=order, error=err)

    def stop_limit_buy(self, order: StopOrder) -> StopOrder:
        if self._is_well_setup() and order.trading_symbol == self._trading_symbol:
            order.set_ticker_id(ticker_id=self._ticker_id)

        try:
            resp = self.auth.stop_limit_buy_order(security_id=order.ticker_id,
                                                  stop_price=order.stop_price,
                                                  limit_price=order.limit_price,
                                                  quantity=order.size,
                                                  account_id=self._trading_account_id)
            order = self._write_order_resp(order, resp)

            print(f'The STOP LIMIT BUY order has been made.\n'
                  f'Order details: {order}')
            return order

        except Exception as err:
            raise OrderPlacingError(order=order, error=err)

    def stop_limit_sell(self, order: StopOrder) -> StopOrder:
        if self._is_well_setup() and order.trading_symbol == self._trading_symbol:
            order.set_ticker_id(ticker_id=self._ticker_id)

        try:
            resp = self.auth.stop_limit_sell_order(security_id=order.ticker_id,
                                                   stop_price=order.stop_price,
                                                   limit_price=order.limit_price,
                                                   quantity=order.size,
                                                   account_id=self._trading_account_id)

            order = self._write_order_resp(order, resp)

            print(f'The STOP LIMIT SELL order has been made.\n'
                  f'Order details: {order}')
            return order

        except Exception as err:
            raise OrderPlacingError(order=order, error=err)

    def cancel_order(self, order: Union[RegularOrder, StopOrder]) -> Union[RegularOrder, StopOrder]:
        if not order.is_settled():
            try:
                self.auth.cancel_order(order.broker_ref_id)  # this request will return an empty dict {}
                order.set_status(status=OrderStatus.PENDING)

                print(f'The CANCELLING REQUEST has been made.\n'
                      f'Order details: {order}')
                return order

            except Exception as err:
                raise OrderPlacingError(order=order, error=err)

    def update_order(self, order: Union[RegularOrder, StopOrder],
                     ref_price: Optional[float] = None) -> Union[RegularOrder, StopOrder]:
        """
        Update an order if its status is still unsettled
        """
        if not order.is_settled():
            if order.broker_ref_id not in self._pending_orders:
                raise PendingOrderNotInPendingListError(order=order)
            else:
                if order.isbuy:
                    resp = self.auth.get_activities(type='buy', sec_id=order.ticker_id,
                                                    account_id=self._trading_account_id)
                else:
                    resp = self.auth.get_activities(type='sell', sec_id=order.ticker_id,
                                                    account_id=self._trading_account_id)

                for ord_resp in resp['results']:
                    if ord_resp['id'] == order.broker_ref_id:
                        order = self._write_order_resp(order, ord_resp)
                        return order

    def get_pending_orders(self, isbuy: Optional[bool] = None):
        if isbuy is None:
            resp_buy = self.auth.get_activities(type='buy', sec_id=self._ticker_id,
                                                account_id=self._trading_account_id)

            resp_sell = self.auth.get_activities(type='sell', sec_id=self._ticker_id,
                                                 account_id=self._trading_account_id)

            order_responses = resp_buy['results'] + resp_sell['results']

        elif isbuy:
            resp = self.auth.get_activities(type='buy', sec_id=self._ticker_id,
                                            account_id=self._trading_account_id)
            order_responses = resp['results']
        else:
            resp = self.auth.get_activities(type='sell', sec_id=self._ticker_id,
                                            account_id=self._trading_account_id)
            order_responses = resp['results']

        for resp in order_responses:
            if not resp['settled'] and not (resp['status'] == 'cancelled' or resp['status'] == 'expired'):
                if resp['symbol'] == self._trading_symbol:

                    is_a_buy = True if str(resp['order_type']).split('_')[0].strip() == 'buy' else False

                    stop_price = resp['stop_price']['amount'] if resp['stop_price'] else 0
                    limit_price = resp['limit_price']['amount'] if resp['limit_price'] else 0
                    order_sub_type = resp['order_sub_type']
                    if order_sub_type == 'stop_limit':
                        order = StopOrder(trading_symbol=self._trading_symbol, size=resp['quantity'], isbuy=is_a_buy,
                                          isstoplimit=True, limit_price=limit_price, stop_price=stop_price)
                        # get 'created at' and 'created_timestamp'
                        self._write_order_resp(order, resp)

                    elif order_sub_type == 'limit':
                        order = RegularOrder(trading_symbol=self._trading_symbol, size=resp['quantity'], isbuy=is_a_buy,
                                             islimit=True, limit_price=limit_price)

                        # get 'created at' and 'created_timestamp'
                        self._write_order_resp(order, resp)

                    elif order_sub_type == 'market':
                        order = RegularOrder(trading_symbol=self._trading_symbol, size=resp['quantity'], isbuy=is_a_buy,
                                             islimit=False, limit_price=0.0)

                        # get 'created at' and 'created_timestamp'
                        self._write_order_resp(order, resp)

                    else:
                        raise Exception('Unrecognizable order response from the broker.')

        return self._pending_orders

    def update_pending_orders(self, ref_price: Optional[float] = None):
        if self._pending_orders:
            buy_count = 0
            sell_count = 0
            for _ord in self._pending_orders.values():
                if _ord.isbuy:
                    buy_count += 1
                else:
                    sell_count += 1
            if buy_count and not sell_count:
                resp = self.auth.get_activities(type='buy', sec_id=self._ticker_id,
                                                account_id=self._trading_account_id)
                order_responses = resp['results']
            elif sell_count and not buy_count:
                resp = self.auth.get_activities(type='sell', sec_id=self._ticker_id,
                                                account_id=self._trading_account_id)
                order_responses = resp['results']
            else:
                resp_buy = self.auth.get_activities(type='buy', sec_id=self._ticker_id,
                                                    account_id=self._trading_account_id)

                resp_sell = self.auth.get_activities(type='sell', sec_id=self._ticker_id,
                                                     account_id=self._trading_account_id)

                order_responses = resp_buy['results'] + resp_sell['results']
            for _ord in list(self._pending_orders.values()):
                for ord_resp in order_responses:
                    if ord_resp['id'] == _ord.broker_ref_id:
                        _ord = self._write_order_resp(_ord, ord_resp)
                        break

    def _write_order_resp(self, order: Union[RegularOrder, StopOrder],
                          ord_resp: dict) -> Union[RegularOrder, StopOrder]:
        order.set_broker_ref_id(broker_ref_id=ord_resp['order_id'] if 'order_id' in ord_resp else ord_resp['id'])

        order.set_is_broker_settled(is_broker_settled=ord_resp['settled'])
        order.set_status(status=self._translate_order_status(ord_resp['status']))
        order.set_broker_traded_symbol(broker_traded_symbol=ord_resp['symbol'])

        # get 'created at' and 'created_timestamp'
        utc_created_at = ord_resp['created_at']
        datetime_utc = datetime.datetime.strptime(utc_created_at, '%Y-%m-%dT%H:%M:%S.%fZ')
        datetime_created_at = datetime_utc.replace(tzinfo=tz.gettz('UTC')).astimezone(
            tz.gettz(self._local_tz))
        order.set_created_at(created_at=datetime_created_at.isoformat())
        order.set_created_timestamp(created_timestamp=round(datetime_utc.timestamp()))

        if order.is_settled() or order.is_broker_settled:
            if order.is_filled():
                if ord_resp['filled_at']:  # if the order has been filled
                    datetime_utc = datetime.datetime.strptime(ord_resp['filled_at'], '%Y-%m-%dT%H:%M:%S.%fZ')
                    datetime_filled_at = datetime_utc.replace(tzinfo=tz.gettz('UTC')).astimezone(
                        tz.gettz(self._local_tz))
                    order.set_filled_at(filled_at=datetime_filled_at.isoformat())
                    order.set_filled_timestamp(filled_timestamp=round(datetime_utc.timestamp()))
                    order.set_fill_quantity(fill_quantity=ord_resp['fill_quantity'])
                    broker_transaction_value = ord_resp['market_value']['amount'] if ord_resp['market_value'] else 0
                    order.set_transaction_value(transaction_value=broker_transaction_value)
                    order.set_filled_price(filled_price=round(order.transaction_value / order.fill_quantity, 2))
                    # IMPORTANT: Update position when order get filled
                    self._position.update(order.isbuy, order.fill_quantity, order.filled_price)

            # IMPORTANT: Upsert settled orders -> add to the broker's settled list and remove it from pending
            self._upsert_settled(order)

        else:
            # IMPORTANT: Upsert pending orders -> add to the broker's pending order list
            self._upsert_pending(order)

        return order

    def get_position(self, is_live_position: bool) -> Position:
        if self._is_well_setup():
            if is_live_position:
                try:
                    resp = self.auth.get_positions(sec_id=self._ticker_id, account_id=self._trading_account_id)

                    if resp['results']:
                        if resp['results'][0]['id'] == self._position.ticker_id:
                            quantity = resp['results'][0]['sellable_quantity']
                            book_value = resp['results'][0]['book_value']['amount']
                            price = 0.0 if quantity == 0 else round(book_value / quantity, 2)
                            self._position.retrieve(quantity, price)
                            return self._position

                except Exception as err:
                    raise PositionRequestError(position=self._position, error=err)
            else:
                return self._position

    @staticmethod
    def _translate_order_status(broker_order_status: str):
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

    def stop_loss(self, order: StopOrder) -> StopOrder:
        pass

    def take_profit(self, order: StopOrder) -> StopOrder:
        pass


if __name__ == '__main__':
    # pass
    import time

    wsimple_broker = WSimpleBroker()
    wsimple_broker.initialize(trading_symbol='CTS', currency='CAD')
    wsimple_broker.set_trading_account(trading_account_id='tfsa-hyrnpbqo')
    print(wsimple_broker.ticker_id)
    print(wsimple_broker.position)

    market_buy_order = RegularOrder(isbuy=True, islimit=False, size=1, trading_symbol='CTS', ref_price=11.11, limit_price=11.11)

    print(market_buy_order.ref_price)

    order_info = wsimple_broker.market_buy(market_buy_order)
    print(order_info)
    # time.sleep(3)
    # wsimple_broker.update_pending_orders()
    # print(wsimple_broker.pending_orders)
    # wsimple_broker.get_pending_orders()
    # print(wsimple_broker.pending_orders)
    # wsimple_broker.update_pending_orders()
    # print(wsimple_broker.pending_orders)
    # wsimple_broker.cancel_order(list(wsimple_broker.pending_orders.values())[0])
    # time.sleep(3)
    # wsimple_broker.update_pending_orders()
    # print(wsimple_broker.pending_orders)
    # print(wsimple_broker.settled_orders)
