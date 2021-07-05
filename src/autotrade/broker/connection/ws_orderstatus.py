from src.autotrade.broker.connection.ws_order import Order, OrderType
from src.autotrade import WealthSimpleTickerClient


class OrderStatus:

    def __init__(self, ticker_client: WealthSimpleTickerClient, order_id: str, order_type: OrderType) -> None:

        self.ticker_client = ticker_client
        self.order_id = order_id
        self.order_type: str = order_type.name
        self.order: Order = self._get_order()

    def _get_order(self):
        if self.order_type == "BUY":
            orders = self.ticker_client.get_buy_orders()
        elif self.order_type == "SELL":
            orders = self.ticker_client.get_sell_orders()
        else:
            orders = self.ticker_client.get_buy_orders().extend(self.ticker_client.get_buy_orders())

        for order in orders:
            if order['order_id'] == self.order_id:
                self.order = Order(order)
                return self.order

    def _update_order_status(self):
        self._get_order()
        return self.order.status

    @property
    def is_cancelled(self, refresh_order_info: bool = True) -> bool:
        """Specifies whether the order was cancelled or not.
        Arguments:
        ----
        refresh_order_info {bool} -- Specifies whether you want
            to refresh the order data from the TD API before
            checking. If `True` a request will be made to the
            TD API to grab the latest Order Info.
        Returns
        -------
        bool
            `True` if the order status is `cancelled`, `False`
            otherwise.
        """

        if refresh_order_info:
            self._update_order_status()

        if self.order.status == 'cancelled':
            return True
        else:
            return False

    @property
    def is_new(self, refresh_order_info: bool = True) -> bool:
        """Specifies whether the order was new (submitting or just-submitted) or not.
        Arguments:
        ----
        refresh_order_info {bool} -- Specifies whether you want
            to refresh the order data from the TD API before
            checking. If `True` a request will be made to the
            TD API to grab the latest Order Info.
        Returns
        -------
        bool
            `True` if the order status is `new`, `False`
            otherwise.
        """

        if refresh_order_info:
            self._update_order_status()

        if self.order.status == 'new':
            return True
        else:
            return False

    @property
    def is_expired(self, refresh_order_info: bool = True) -> bool:
        """Specifies whether the order was expired or not.
        Arguments:
        ----
        refresh_order_info {bool} -- Specifies whether you want
            to refresh the order data from the TD API before
            checking. If `True` a request will be made to the
            TD API to grab the latest Order Info.
        Returns
        -------
        bool
            `True` if the order status is `expired`, `False`
            otherwise.
        """

        if refresh_order_info:
            self._update_order_status()

        if self.order.status == 'expired':
            return True
        else:
            return False

    @property
    def is_filled(self, refresh_order_info: bool = True) -> bool:
        """Specifies whether the order has filled or not.
        Arguments:
        ----
        refresh_order_info {bool} -- Specifies whether you want
            to refresh the order data from the TD API before
            checking. If `True` a request will be made to the
            TD API to grab the latest Order Info.
        Returns
        -------
        bool
            `True` if the order status is `posted`, `False`
            otherwise.
        """

        if refresh_order_info:
            self._update_order_status()

        if self.order.status == 'posted':
            return True
        else:
            return False

    @property
    def is_submitted(self, refresh_order_info: bool = True) -> bool:
        """Specifies whether the order has submitted or not.
        Arguments:
        ----
        refresh_order_info {bool} -- Specifies whether you want
            to refresh the order data from the TD API before
            checking. If `True` a request will be made to the
            TD API to grab the latest Order Info.
        Returns
        -------
        bool
            `True` if the order status is `submitted`, `False`
            otherwise.
        """

        if refresh_order_info:
            self._update_order_status()

        if self.order.status == 'submitted':
            return True
        else:
            return False

    @property
    def is_pending_cancel(self, refresh_order_info: bool = True) -> bool:
        """Specifies whether the order has pending cancelling or not.
        Arguments:
        ----
        refresh_order_info {bool} -- Specifies whether you want
            to refresh the order data from the TD API before
            checking. If `True` a request will be made to the
            TD API to grab the latest Order Info.
        Returns
        -------
        bool
            `True` if the order status is `cancelling`, `False`
            otherwise.
        """

        if refresh_order_info:
            self._update_order_status()

        if self.order.status == 'cancelling':
            return True
        else:
            return False


if __name__ == '__main__':
    pass
