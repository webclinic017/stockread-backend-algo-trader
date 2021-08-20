# Copyright (C) 2021-2030 StockRead Inc.
# Author: Thanh Tung Nguyen
# Contact: tungstudies@gmail.com

# DIVIDER: --------------------------------------
# INFO: GainLossTracker Concrete Class

class GainLossTracker:
    def __init__(self):

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

    def add_holding(self, purchase_value: float, purchase_volume: int, commission: float = 0.0):
        self._holding_value += purchase_value
        self._holding_volume += purchase_volume
        self._purchase_count += 1
        self._total_commission += commission

    def make_sale(self, sale_value: float, sale_volume: int, commission: float = 0.0):
        self._total_sale += sale_value
        transaction_cost_of_sale = sale_volume * (self._holding_value / self._holding_volume)
        self._total_cost_of_sale += transaction_cost_of_sale
        self._holding_value -= transaction_cost_of_sale

        self._total_sale_volume += sale_volume
        self._holding_volume -= sale_volume

        self._sale_count += 1
        self._total_commission += commission

    @property
    def realized_gain_loss(self):
        return round(self._total_sale - self._total_cost_of_sale - self._total_commission, 2)

    def estimate_unrealized_gls(self, market_price: float):
        if self._holding_volume:
            return round(self._holding_volume * market_price - self._holding_value, 2)
        else:
            return self._holding_volume


# DIVIDER: --------------------------------------
# INFO: Usage Examples

if __name__ == '__main__':
    pass
