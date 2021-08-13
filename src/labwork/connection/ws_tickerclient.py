from typing import Optional, List


from src.autotrade.broker_conn.wsimple_conn import ConnectionWST
from src.labwork.connection.ws_order import Order, OrderType

class WealthSimpleTickerClient:
    def __init__(self, ws_connector: ConnectionWST, ticker_symbol: str, account_id: str):
        self.ws_connector = ws_connector
        self.ticker_symbol = ticker_symbol
        self.sec_id = self._find_security()
        self.account_id = account_id
        self.pending_buy_orders: Optional[List[Order]] = self._get_pending_buy_orders()
        self.pending_sell_orders: Optional[List[Order]] = self._get_pending_sell_orders()
        self.positions: dict = self.get_positions()

    def _find_security(self):
        resp = self.ws_connector.wst_auth.find_securities(ticker=self.ticker_symbol)
        print(resp)
        if resp['stock']['symbol'] == self.ticker_symbol and resp['stock']['primary_exchange'] == 'TSX':
            return resp['id']

    def _get_pending_buy_orders(self):
        recent_buy_orders = self.get_buy_orders()
        self.pending_buy_orders = [Order(order) for order in recent_buy_orders if order['status'] == "submitted"]
        return self.pending_buy_orders

    def _get_pending_sell_orders(self):
        recent_sell_orders = self.get_sell_orders()
        self.pending_sell_orders = [Order(order) for order in recent_sell_orders if order['status'] == "submitted"]
        return self.pending_sell_orders

    def get_positions(self):
        resp = self.ws_connector.wst_auth.get_positions(sec_id=self.sec_id, account_id=account_id)
        positions_dict = dict()
        quantity = resp['results'][0]['quantity']
        positions_dict['quantity'] = quantity
        positions_dict['sellable_quantity'] = resp['results'][0]['sellable_quantity']
        book_value = resp['results'][0]['book_value']['amount']
        positions_dict['book_value'] = book_value
        unit_book_value = round(book_value / quantity, 2)
        positions_dict['unit_book_value'] = unit_book_value
        self.positions = positions_dict
        return self.positions

    def get_buy_orders(self) -> list:
        resp = self.ws_connector.wst_auth.get_activities(type='buy', sec_id=self.sec_id, account_id=self.account_id)
        return resp['results']

    def get_sell_orders(self) -> list:
        resp = self.ws_connector.wst_auth.get_activities(type='sell', sec_id=self.sec_id, account_id=self.account_id)
        return resp['results']

    def make_limit_buy_order(self, limit_price: float, quantity: int):
        try:
            resp = self.ws_connector.wst_auth.limit_buy_order(security_id=self.sec_id,
                                                              limit_price=limit_price,
                                                              quantity=quantity,
                                                              account_id=self.account_id)
            order = Order(result=resp)
            self.pending_buy_orders.append(order)
            print(f'The limit buy order has been made. Order ID received: {order.order_id}')
            return order

        except Exception as err:
            print("Security ID used: {}".format(self.sec_id))
            raise Exception(f'InvalidSecurityIdError: {err}')

    def make_target_buy_order(self, stop_price: float, limit_price: float, quantity: int):
        try:
            resp = self.ws_connector.wst_auth.stop_limit_buy_order(security_id=self.sec_id,
                                                                   stop_price=stop_price,
                                                                   limit_price=limit_price,
                                                                   quantity=quantity,
                                                                   account_id=self.account_id)
            order = Order(result=resp)
            self.pending_buy_orders.append(order)
            print(f'The stop limit buy/TARGET order has been made. Order ID received: {order.order_id}')
            return order

        except Exception as err:
            print("Security ID used: {}".format(self.sec_id))
            raise Exception(f'InvalidSecurityIdError: {err}')

    def make_market_buy_order(self, quantity: int):
        try:
            resp = self.ws_connector.wst_auth.market_buy_order(security_id=self.sec_id,
                                                               quantity=quantity,
                                                               account_id=self.account_id)
            order = Order(result=resp)
            self.pending_buy_orders.append(order)
            print(f'The market buy order has been made. Order ID received: {order.order_id}')
            return order


        except Exception as err:

            print("Security ID used: {}".format(self.sec_id))

            raise Exception(f'InvalidSecurityIdError: {err}')

    def make_limit_sell_order(self, limit_price: float, quantity: int):
        try:
            resp = self.ws_connector.wst_auth.limit_sell_order(security_id=self.sec_id,
                                                               limit_price=limit_price,
                                                               quantity=quantity,
                                                               account_id=self.account_id)
            order = Order(result=resp)
            self.pending_sell_orders.append(order)
            print(f'The limit sell order has been made. Order ID received: {order.order_id}')
            return order


        except Exception as err:

            print("Security ID used: {}".format(self.sec_id))

            raise Exception(f'InvalidSecurityIdError: {err}')

    def make_stop_loss_order(self, stop_price: float, limit_price: float, quantity: int):
        try:
            resp = self.ws_connector.wst_auth.stop_limit_sell_order(security_id=self.sec_id,
                                                                    stop_price=stop_price,
                                                                    limit_price=limit_price,
                                                                    quantity=quantity,
                                                                    account_id=self.account_id)
            order = Order(result=resp)
            self.pending_sell_orders.append(order)
            print(f'The stop limit sell/STOP-LOSS order has been made. Order ID received: {order.order_id}')
            return order


        except Exception as err:

            print("Security ID used: {}".format(self.sec_id))

            raise Exception(f'InvalidSecurityIdError: {err}')

    def make_market_sell_order(self, quantity: int):
        try:
            resp = self.ws_connector.wst_auth.market_sell_order(security_id=self.sec_id,
                                                                quantity=quantity,
                                                                account_id=self.account_id)
            order = Order(result=resp)
            self.pending_sell_orders.append(order)
            print(f'The market sell order has been made. Order ID received: {order.order_id}')
            return order


        except Exception as err:

            print("Security ID used: {}".format(self.sec_id))

            raise Exception(f'InvalidSecurityIdError: {err}')

    def cancel_pending_orders(self, order_type: OrderType):
        if order_type.name == 'BUY':
            pending_orders = self.pending_buy_orders
        elif order_type.name == 'SELL':
            pending_orders = self.pending_sell_orders
        else:
            pending_orders = self.pending_buy_orders.extend(self.pending_sell_orders)

        for order in pending_orders:
            self.ws_connector.wst_auth.cancel_order(order.order_id)

    def cancel_order(self, order: Order):
        self.ws_connector.wst_auth.cancel_order(order.order_id)


if __name__ == '__main__':
    ws_connector = ConnectionWST()
    ws_connector.connect()
    account_id = "tfsa-hyrnpbqo"


    aapl_wtc = WealthSimpleTickerClient(ws_connector, 'AAPL', account_id=account_id)
    aapl_wtc._find_security()


    #
    # orders = SHOP_wtc.get_buy_orders()
    # print(orders)
    # positions = SHOP_wtc.get_positions()
    # print(positions)

