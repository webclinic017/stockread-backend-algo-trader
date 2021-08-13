from src.autotrade.artifacts.order import Order


class StopLoss:
    def __init__(self, anchor_price: float, is_trailing: bool, trigger_percentage: float, threshold_percentage: float):
        self.is_trailing = is_trailing
        self.anchor_price = anchor_price
        self.trigger_percentage = trigger_percentage
        self.stop_price = self.anchor_price * (1 - self.trigger_percentage)

        if is_trailing:
            self.active_trailing_order = None
            self.inactive_trailing_orders = list()
            self.threshold_percentage = threshold_percentage
            self.next_anchor_price = self.anchor_price * (1 + self.threshold_percentage)
        else:
            self.one_time_order = None

    def set_percentage(self, trigger_percentage: float):
        self.trigger_percentage = trigger_percentage

    def is_triggered(self, current_price: float):
        return self.stop_price >= current_price

    def update_stop_loss(self, new_anchor_price: float):
        if self.is_trailing and self.next_anchor_price < new_anchor_price:
            self.anchor_price = new_anchor_price
            self.stop_price = self.anchor_price * (1 - self.trigger_percentage)
            self.next_anchor_price = self.anchor_price * (1 + self.threshold_percentage)

    def add_stop_loss_order(self, order: Order):
        if self.is_trailing:
            self.inactive_trailing_orders.append(self.active_trailing_order)
            self.active_trailing_order = order
        else:
            self.one_time_order = order
