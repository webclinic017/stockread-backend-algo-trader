# Copyright (C) 2021-2030 StockRead Inc.
# Author: Thanh Tung Nguyen
# Contact: tungstudies@gmail.com

# DIVIDER: --------------------------------------
# INFO: GainLossTracker Concrete Class

class GainLossTracker:
    def __init__(self, cash: float = 0.0):
        self._cash: float = cash

        self._holding_volume: int = 0
        self._total_sale_volume: int = 0

        self._holding_value: float = 0.0
        self._total_cost_of_sale: float = 0.0
        self._total_commission: float = 0.0
        self._total_sale: float = 0.0

        self._purchase_count: int = 0
        self._sale_count: int = 0

    # DIVIDER: Publicly Accessible Method Properties ----------------------------------------------
    @property
    def sale(self):
        return self._total_sale

    @property
    def cost_of_sale(self):
        return self._total_cost_of_sale

    @property
    def commission(self):
        return self._total_commission

    # DIVIDER: Publicly Accessible Methods --------------------------------------------------------
    def add_cash(self, cash_value: float):
        self._cash += cash_value

    def remove_cash(self, cash_value: float):
        self._cash -= cash_value

    def add_holding(self, purchase_value: float, purchase_volume: int, commission: float = 0.0):
        self._holding_value += purchase_value
        self._holding_volume += purchase_volume
        self._purchase_count += 1
        self._total_commission += commission

        if self._cash:
            self._cash -= purchase_value

    def make_sale(self, sale_value: float, sale_volume: int, commission: float = 0.0):
        self._total_sale += sale_value
        transaction_cost_of_sale = sale_volume * (self._holding_value / self._holding_volume)
        self._total_cost_of_sale += transaction_cost_of_sale
        self._holding_value -= transaction_cost_of_sale

        self._total_sale_volume += sale_volume
        self._holding_volume -= sale_volume

        self._sale_count += 1
        self._total_commission += commission

        self._cash += (sale_value - commission)

    def get_realized_gain_loss(self):
        return round(self._total_sale - self._total_cost_of_sale - self._total_commission, 2)

    def get_unrealized_gain_loss(self, market_price: float):
        if self._holding_volume:
            return round(self._holding_volume * market_price - self._holding_value, 2)
        else:
            return 0.0


# DIVIDER: --------------------------------------
# INFO: Usage Examples

if __name__ == '__main__':
    pass
