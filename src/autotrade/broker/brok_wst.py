import datetime
from typing import Optional, List

from dateutil import tz
from wsimple import Wsimple

from src.autotrade.broker.brok_base import BaseLiveBroker
from src.autotrade.broker.brok_base import IBroker, IBrokerLive
from src.autotrade.broker.order import Order, OrderAction, OrderType, OrderStatus

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.autotrade.tradebot import TradeBot


class BrokerWST(BaseLiveBroker, IBroker, IBrokerLive):

    def __init__(self):
        super().__init__()
        self._local_tz = None
        self._connection: Optional[Wsimple] = None
        self.set_timezone()

    def set_timezone(self, local_tz='America/Montreal'):
        self._local_tz = local_tz

    def set_connection(self, wst_auth: Wsimple):
        self._connection = wst_auth

    def bind_to_trade(self, trade_bot: 'TradeBot'):
        """
        :type trade_bot: TradeBot
        """
        self._trade_bot = trade_bot
        self._trading_symbol = self._trade_bot.trading_symbol
        self._currency = self._trade_bot.currency
        self.find_instrument()
        self._position = self._trade_bot.position

    @property
    def is_live(self):
        return self._is_live

    @property
    def connection(self):
        return self._connection

    def find_instrument(self):
        if self._ticker_id:
            return self._ticker_id
        else:
            resp = self._connection.find_securities(ticker=self._trading_symbol, fuzzy=True)
            results = resp['results']
            for each in results:
                if each and each['stock']['symbol'] == self._trading_symbol and each['currency'] == self._currency:
                    self._ticker_id = each['id']
                    return self._ticker_id

            raise Exception(f'TickerNotFoundError: there is no corresponding ticker_id for {self._trading_symbol}')

    def set_trading_account(self, trading_account_id: str = "tfsa-hyrnpbqo"):
        self._trading_account_id = trading_account_id

        accounts = self._connection.get_accounts()
        trading_account = [account for account in accounts['results'] if account['id'] == self._trading_account_id][0]
        account_cash_available = trading_account['buying_power']['amount']

        self._account_cash_available = account_cash_available

    @property
    def buying_power(self):
        if not self._trading_account_id:
            raise Exception(f'The trading account has not been set. '
                            f'It is required to set trading account at the very beginning')
        return self._account_cash_available

    def get_position(self):
        if not self._trading_account_id:
            raise Exception(f'The trading account has not been set. '
                            f'It is required to set trading account at the very beginning')

        resp = self._connection.get_positions(sec_id=self._ticker_id, account_id=self._trading_account_id)
        if resp['results']:
            quantity = resp['results'][0]['sellable_quantity']
            book_value = resp['results'][0]['book_value']['amount']
            price = 0 if quantity == 0 else round(book_value / quantity, 2)
            self._position.retrieve(quantity, price)
        return self._position

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

    def market_buy(self, quantity):
        new_order = Order(action=OrderAction.SELL, order_type=OrderType.MARKET, size=quantity,
                          trading_symbol=self._trading_symbol, ticker_id=self._ticker_id)

        try:
            resp = self._connection.market_buy_order(security_id=new_order.ticker_id,
                                                     quantity=new_order.size,
                                                     account_id=self._trading_account_id)

            new_order.ref_id = resp['order_id']
            new_order.is_broker_settled = resp['settled']
            new_order.state = self.translate_order_status(resp['status'])
            new_order.broker_traded_symbol = resp['symbol']

            # get 'created at' and 'created_timestamp'
            if new_order.created_at != resp['created_at']:
                utc_created_at = resp['created_at']
                datetime_utc = datetime.datetime.strptime(utc_created_at, '%Y-%m-%dT%H:%M:%S.%fZ')
                datetime_created_at = datetime_utc.replace(tzinfo=tz.gettz('UTC')).astimezone(
                    tz.gettz(self._local_tz))
                created_at = datetime_created_at.isoformat()
                created_timestamp = round(datetime_utc.timestamp())
                new_order.created_at = created_at
                new_order.created_timestamp = created_timestamp

            print(f'The MARKET BUY order has been made.\n'
                  f'Order details: {new_order}')
            return new_order

        except Exception as err:
            raise Exception(f'OrderPlacingError: {err}')

    def market_sell(self, quantity):
        new_order = Order(action=OrderAction.SELL, order_type=OrderType.MARKET, size=quantity,
                          trading_symbol=self._trading_symbol, ticker_id=self._ticker_id)

        try:
            resp = self._connection.market_sell_order(security_id=new_order.ticker_id,
                                                      quantity=new_order.size,
                                                      account_id=self._trading_account_id)

            new_order.ref_id = resp['order_id']
            new_order.is_broker_settled = resp['settled']
            new_order.state = self.translate_order_status(resp['status'])
            new_order.broker_traded_symbol = resp['symbol']

            # get 'created at' and 'created_timestamp'
            if new_order.created_at != resp['created_at']:
                utc_created_at = resp['created_at']
                datetime_utc = datetime.datetime.strptime(utc_created_at, '%Y-%m-%dT%H:%M:%S.%fZ')
                datetime_created_at = datetime_utc.replace(tzinfo=tz.gettz('UTC')).astimezone(
                    tz.gettz(self._local_tz))
                created_at = datetime_created_at.isoformat()
                created_timestamp = round(datetime_utc.timestamp())
                new_order.created_at = created_at
                new_order.created_timestamp = created_timestamp

            print(f'The MARKET SELL order has been made.\n'
                  f'Order details: {new_order}')
            return new_order

        except Exception as err:
            raise Exception(f'OrderPlacingError: {err}')

    def limit_buy(self, limit_price, quantity):
        new_order = Order(action=OrderAction.BUY, order_type=OrderType.LIMIT, size=quantity,
                          trading_symbol=self._trading_symbol, ticker_id=self._ticker_id, limit_price=limit_price)
        try:
            resp = self._connection.limit_buy_order(security_id=new_order.ticker_id,
                                                    limit_price=new_order.limit_price,
                                                    quantity=new_order.size,
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
            new_order.ref_id = resp['order_id']
            new_order.is_broker_settled = resp['settled']
            new_order.state = self.translate_order_status(resp['status'])
            new_order.broker_traded_symbol = resp['symbol']

            # get 'created at' and 'created_timestamp'
            if new_order.created_at != resp['created_at']:
                utc_created_at = resp['created_at']
                datetime_utc = datetime.datetime.strptime(utc_created_at, '%Y-%m-%dT%H:%M:%S.%fZ')
                datetime_created_at = datetime_utc.replace(tzinfo=tz.gettz('UTC')).astimezone(
                    tz.gettz(self._local_tz))
                created_at = datetime_created_at.isoformat()
                created_timestamp = round(datetime_utc.timestamp())
                new_order.created_at = created_at
                new_order.created_timestamp = created_timestamp

            print(f'The LIMIT BUY order has been made.\n'
                  f'Order details: {new_order}')
            return new_order

        except Exception as err:
            raise Exception(f'OrderPlacingError: {err}')

    def limit_sell(self, limit_price, quantity):
        new_order = Order(action=OrderAction.SELL, order_type=OrderType.LIMIT, size=quantity,
                          trading_symbol=self._trading_symbol, ticker_id=self._ticker_id, limit_price=limit_price)
        try:
            resp = self._connection.limit_sell_order(security_id=new_order.ticker_id,
                                                     limit_price=new_order.limit_price,
                                                     quantity=new_order.size,
                                                     account_id=self._trading_account_id)
            new_order.ref_id = resp['order_id']
            new_order.is_broker_settled = resp['settled']
            new_order.state = self.translate_order_status(resp['status'])
            new_order.broker_traded_symbol = resp['symbol']

            # get 'created at' and 'created_timestamp'
            if new_order.created_at != resp['created_at']:
                utc_created_at = resp['created_at']
                datetime_utc = datetime.datetime.strptime(utc_created_at, '%Y-%m-%dT%H:%M:%S.%fZ')
                datetime_created_at = datetime_utc.replace(tzinfo=tz.gettz('UTC')).astimezone(
                    tz.gettz(self._local_tz))
                created_at = datetime_created_at.isoformat()
                created_timestamp = round(datetime_utc.timestamp())
                new_order.created_at = created_at
                new_order.created_timestamp = created_timestamp

            print(f'The LIMIT SELL order has been made.\n'
                  f'Order details: {new_order}')
            return new_order

        except Exception as err:
            raise Exception(f'OrderPlacingError: {err}')

    def stop_limit_buy(self, stop_price, limit_price, quantity):
        new_order = Order(action=OrderAction.BUY, order_type=OrderType.STOP_LIMIT, size=quantity,
                          trading_symbol=self._trading_symbol, ticker_id=self._ticker_id, limit_price=limit_price,
                          stop_price=stop_price)

        try:
            resp = self._connection.stop_limit_buy_order(security_id=new_order.ticker_id,
                                                         stop_price=new_order.stop_price,
                                                         limit_price=new_order.limit_price,
                                                         quantity=new_order.size,
                                                         account_id=self._trading_account_id)
            new_order.ref_id = resp['order_id']
            new_order.is_broker_settled = resp['settled']
            new_order.state = self.translate_order_status(resp['status'])
            new_order.broker_traded_symbol = resp['symbol']

            # get 'created at' and 'created_timestamp'
            if new_order.created_at != resp['created_at']:
                utc_created_at = resp['created_at']
                datetime_utc = datetime.datetime.strptime(utc_created_at, '%Y-%m-%dT%H:%M:%S.%fZ')
                datetime_created_at = datetime_utc.replace(tzinfo=tz.gettz('UTC')).astimezone(
                    tz.gettz(self._local_tz))
                created_at = datetime_created_at.isoformat()
                created_timestamp = round(datetime_utc.timestamp())
                new_order.created_at = created_at
                new_order.created_timestamp = created_timestamp

            print(f'The STOP LIMIT BUY order has been made.\n'
                  f'Order details: {new_order}')
            return new_order

        except Exception as err:
            raise Exception(f'OrderPlacingError: {err}')

    def stop_limit_sell(self, stop_price, limit_price, quantity):
        new_order = Order(action=OrderAction.SELL, order_type=OrderType.STOP_LIMIT, size=quantity,
                          trading_symbol=self._trading_symbol, ticker_id=self._ticker_id, limit_price=limit_price,
                          stop_price=stop_price)

        try:
            resp = self._connection.stop_limit_sell_order(security_id=new_order.ticker_id,
                                                          stop_price=new_order.stop_price,
                                                          limit_price=new_order.limit_price,
                                                          quantity=new_order.size,
                                                          account_id=self._trading_account_id)
            new_order.ref_id = resp['order_id']
            new_order.is_broker_settled = resp['settled']
            new_order.state = self.translate_order_status(resp['status'])
            new_order.broker_traded_symbol = resp['symbol']

            # get 'created at' and 'created_timestamp'
            if new_order.created_at != resp['created_at']:
                utc_created_at = resp['created_at']
                datetime_utc = datetime.datetime.strptime(utc_created_at, '%Y-%m-%dT%H:%M:%S.%fZ')
                datetime_created_at = datetime_utc.replace(tzinfo=tz.gettz('UTC')).astimezone(
                    tz.gettz(self._local_tz))
                created_at = datetime_created_at.isoformat()
                created_timestamp = round(datetime_utc.timestamp())
                new_order.created_at = created_at
                new_order.created_timestamp = created_timestamp


            print(f'The STOP LIMIT SELL order has been made.\n'
                  f'Order details: {new_order}')
            return new_order

        except Exception as err:
            raise Exception(f'OrderPlacingError: {err}')

    def cancel_order(self, order: Order):
        self._connection.cancel_order(order.ref_id)

    def update_order_info(self, order: Order):
        if order.action == OrderAction.BUY:
            resp = self._connection.get_activities(type='buy', sec_id=order.ticker_id,
                                                   account_id=self._trading_account_id)
        else:
            resp = self._connection.get_activities(type='sell', sec_id=order.ticker_id,
                                                   account_id=self._trading_account_id)
        for each in resp['results']:
            if each['id'] == order.ref_id:
                state = self.translate_order_status(each['status'])
                order.state = state
                order.is_broker_settled = each['settled']
                order.size = each['quantity']
                order.ticker_id = each['security_id']
                order.broker_traded_symbol = each['symbol']
                order.stop_price = each['stop_price']['amount'] if each['stop_price'] else 0
                order.limit_price = each['limit_price']['amount'] if each['limit_price'] else 0

                # get 'created at' and 'created_timestamp'
                if order.created_at != each['created_at']:
                    utc_created_at = each['created_at']
                    datetime_utc = datetime.datetime.strptime(utc_created_at, '%Y-%m-%dT%H:%M:%S.%fZ')
                    datetime_created_at = datetime_utc.replace(tzinfo=tz.gettz('UTC')).astimezone(
                        tz.gettz(self._local_tz))
                    created_at = datetime_created_at.isoformat()
                    created_timestamp = round(datetime_utc.timestamp())
                    order.created_at = created_at
                    order.created_timestamp = created_timestamp

                if each['filled_at']:
                    datetime_utc = datetime.datetime.strptime(each['filled_at'], '%Y-%m-%dT%H:%M:%S.%fZ')
                    datetime_filled_at = datetime_utc.replace(tzinfo=tz.gettz('UTC')).astimezone(
                        tz.gettz(self._local_tz))
                    filled_at = datetime_filled_at.isoformat()
                    filled_timestamp = round(datetime_utc.timestamp())
                    order.filled_at = filled_at
                    order.filled_timestamp = filled_timestamp
                    order.fill_quantity = each['fill_quantity']
                    order.fill_quantity = each['fill_quantity']
                    market_value = each['market_value']['amount'] if each['market_value'] else 0
                    order.market_value = market_value
                    order.filled_price = order.market_value / order.fill_quantity

                return order

    def get_pending_orders(self, order_action: Optional[OrderAction] = None):
        if order_action == OrderAction.SELL:
            resp = self._connection.get_activities(type='sell', sec_id=self._ticker_id,
                                                   account_id=self._trading_account_id)
            order_infos = resp['results']
        elif order_action == OrderAction.BUY:
            resp = self._connection.get_activities(type='buy', sec_id=self._ticker_id,
                                                   account_id=self._trading_account_id)
            order_infos = resp['results']
        else:
            resp_buy = self._connection.get_activities(type='buy', sec_id=self._ticker_id,
                                                       account_id=self._trading_account_id)

            resp_sell = self._connection.get_activities(type='sell', sec_id=self._ticker_id,
                                                        account_id=self._trading_account_id)

            order_infos = resp_buy['results'] + resp_sell['results']

        pending_orders: List[Order] = list()
        for each in order_infos:
            if not each['settled'] and not (each['status'] == 'cancelled' or each['status'] == 'expired'):

                action = OrderAction.BUY if str(each['order_type']).split('_')[0].strip() == 'buy' else OrderAction.SELL

                stop_price = each['stop_price']['amount'] if each['stop_price'] else 0
                limit_price = each['limit_price']['amount'] if each['limit_price'] else 0
                order_sub_type = each['order_sub_type']
                if order_sub_type == 'stop_limit':
                    order_type = OrderType.STOP_LIMIT
                elif order_sub_type == 'limit':
                    order_type = OrderType.LIMIT

                elif order_sub_type == 'market':
                    order_type = OrderType.MARKET
                else:
                    order_type = OrderType.STOP

                order = Order(action=action, order_type=order_type, size=each['quantity'],
                              trading_symbol=each['symbol'], ticker_id=each['security_id'],
                              stop_price=stop_price, limit_price=limit_price)

                # get 'created at' and 'created_timestamp'
                utc_created_at = each['created_at']
                datetime_utc = datetime.datetime.strptime(utc_created_at, '%Y-%m-%dT%H:%M:%S.%fZ')
                datetime_created_at = datetime_utc.replace(tzinfo=tz.gettz('UTC')).astimezone(tz.gettz(self._local_tz))
                created_at = datetime_created_at.isoformat()
                created_timestamp = round(datetime_utc.timestamp())
                order.created_at = created_at
                order.created_timestamp = created_timestamp

                state = self.translate_order_status(each['status'])
                order.state = state
                order.is_broker_settled = each['settled']
                order.broker_traded_symbol = each['symbol']
                order.ref_id = each['id']
                pending_orders.append(order)

        if pending_orders:
            return pending_orders[0] if len(pending_orders) == 1 else pending_orders


if __name__ == '__main__':
    pass
