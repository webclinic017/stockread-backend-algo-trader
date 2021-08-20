import math

from ta.momentum import RSIIndicator
from ta.trend import IchimokuIndicator
from ta.volatility import BollingerBands

from src.autotrade.indicator.insignal import IndicatorSignal
from src.autotrade.signal.signal import Signal
from src.autotrade.strategy.base_strategy import BaseStrategy


class RSICloudBollStrategy(BaseStrategy):

    def __init__(self):

        super().__init__()
        self.rsi_buy_signal = Signal(isbuy=True, codename='RSIBuy', sequence='first')
        self.mband_buy_signal = Signal(isbuy=True, codename='MiddleBBBuy', sequence='last',
                                       leading_dependent_signal=self.rsi_buy_signal)
        self.hband_sell_signal = Signal(isbuy=False, codename='BollHBandSell', sequence='first')
        self.mband_sell_signal = Signal(isbuy=False, codename='MiddleBBSell', sequence='last',
                                        leading_dependent_signal=self.hband_sell_signal)

    def prepare(self):
        self._barfeed.add_fields(rsi=RSIIndicator(self._barfeed.close).rsi())
        self._barfeed.add_fields(bollinger_hband=BollingerBands(self._barfeed.close).bollinger_hband())
        self._barfeed.add_fields(bollinger_lband=BollingerBands(self._barfeed.close).bollinger_lband())
        self._barfeed.add_fields(bollinger_mavg=BollingerBands(self._barfeed.close).bollinger_mavg())
        self._barfeed.add_fields(
            tenkan=IchimokuIndicator(self._barfeed.high, self._barfeed.low, fillna=True).ichimoku_conversion_line())
        self._barfeed.add_fields(rsi_uphit_70=IndicatorSignal(self._barfeed.frame['rsi']).is_up_hit(70))
        self._barfeed.add_fields(rsi_downhit_25=IndicatorSignal(self._barfeed.frame['rsi']).is_down_hit(25))
        self._barfeed.add_fields(
            price_upcross_mband=IndicatorSignal(self._barfeed.close).cross_up(self._barfeed.frame['bollinger_mavg']))
        self._barfeed.add_fields(
            price_downcross_mband=IndicatorSignal(self._barfeed.close).cross_down(
                self._barfeed.frame['bollinger_mavg']))
        self._barfeed.add_fields(price_downcross_hband=IndicatorSignal(self._barfeed.close).cross_down(
            self._barfeed.frame['bollinger_hband']))

    def print_bar(self):
        if not math.isnan(self.bars[0].rsi):
            print(
                f'>>>> {self.bars[0].datetime} >>>> {self.bars[0].close} >>>> {self.bars[0].rsi} >>> {self.bars[0].price_upcross_mband} ')

    def next(self):

        if abs(self.bars[0].rsi_downhit_25) == 1:
            self.rsi_buy_signal.upsert_notes(note_id_name='RSIDownHit25', note_desc='RSI down hits 25')
            if not self.position.has_position():
                self.rsi_buy_signal.up_signal(ref_bar=self.bars[0], ref_indicator_value={'rsi': self.bars[0].rsi})
                # print(f'rsi: {rsi_buy_signal.is_up} vs tenkan: {tenkan_buy_signal.is_up}')
                self.notify_signal(self.rsi_buy_signal)

        if abs(self.bars[0].price_upcross_mband) == 1:
            if not self.position.has_position():
                self.mband_buy_signal.up_signal(ref_bar=self.bars[0],
                                                ref_indicator_value={'tenkan': self.bars[0].tenkan})

                self.notify_signal(self.mband_buy_signal)

        if abs(self.bars[0].price_downcross_hband) == 1:
            self.hband_sell_signal.upsert_notes(note_id_name='PriceDownCressHBand',
                                                note_desc='Price down crosses High BB')
            if self.position.has_position():
                self.hband_sell_signal.up_signal(ref_bar=self.bars[0],
                                                 ref_indicator_value={'hband': self.bars[0].bollinger_hband})
                self.notify_signal(self.hband_sell_signal)

        if abs(self.bars[0].price_downcross_mband) == 1:
            self.mband_sell_signal.upsert_notes(note_id_name='PriceDownCrossTenkan',
                                                note_desc='Price down crosses Tenkan')
            if self.position.has_position():
                self.mband_sell_signal.up_signal(ref_bar=self.bars[0],
                                                 ref_indicator_value={'tenkan': self.bars[0].tenkan})
                self.notify_signal(self.mband_sell_signal)

        if self.mband_sell_signal.is_up:
            if not self.position.has_position():
                self.buy(islimit=False, ref_price=self.bars[0].close)
                self.rsi_buy_signal.down_signal()
                self.update_pending_orders(is_multiple_update=False)
            if self.position.has_position():
                prices = self.stp_pricer.get_stop_limit_prices(ref_price=self.bars[0].close, is_to_trail=False)

                if prices:
                    self.stoploss(isstoplimit=True, stop_price=prices['stop_price'],
                                  ref_price=self.bars[0].close, limit_price=prices['limit_price'])
                    self.stp_pricer.set_trailing(ref_price=self.bars[0].close, stop_price=prices['stop_price'])

        if self.position.has_position():
            self.trail_stoploss(isstoplimit=True)

        if self.mband_sell_signal.is_up:
            if self.position.has_position():
                self.sell(islimit=False, ref_price=self.bars[0].close)


'''
class RSICloudBollStrategy(BaseStrategy):
    def __init__(self):

        super().__init__()
        self.rsi_buy_signal = Signal(isbuy=True, codename='RSIBuy', sequence='first')
        self.tenkan_buy_signal = Signal(isbuy=True, codename='TenkanBuy', sequence='last',
                                        leading_dependent_signal=self.rsi_buy_signal)
        self.hband_sell_signal = Signal(isbuy=False, codename='BollHBandSell', sequence='first')
        self.tenkan_sell_signal = Signal(isbuy=False, codename='TenkanSell', sequence='last',
                                         leading_dependent_signal=self.hband_sell_signal)

        self.bar_count = 0

    def prepare(self):
        self._barfeed.add_fields(rsi=RSIIndicator(self._barfeed.close, window=14, fillna=True).rsi())
        self._barfeed.add_fields(bollinger_hband=BollingerBands(self._barfeed.close, fillna=True).bollinger_hband())
        self._barfeed.add_fields(bollinger_lband=BollingerBands(self._barfeed.close, fillna=True).bollinger_lband())
        self._barfeed.add_fields(bollinger_mavg=BollingerBands(self._barfeed.close, fillna=True).bollinger_mavg())
        self._barfeed.add_fields(
            tenkan=IchimokuIndicator(self._barfeed.high, self._barfeed.low, fillna=True).ichimoku_conversion_line())
        self._barfeed.add_fields(rsi_uphit_70=IndicatorSignal(self._barfeed.frame['rsi']).is_up_hit(70))
        self._barfeed.add_fields(rsi_downhit_25=IndicatorSignal(self._barfeed.frame['rsi']).is_down_hit(25))
        self._barfeed.add_fields(
            price_upcross_tenkan=IndicatorSignal(self._barfeed.close).cross_up(self._barfeed.frame['tenkan']))
        self._barfeed.add_fields(
            price_downcross_tenkan=IndicatorSignal(self._barfeed.close).cross_down(self._barfeed.frame['tenkan']))
        self._barfeed.add_fields(price_downcross_hband=IndicatorSignal(self._barfeed.close).cross_down(
            self._barfeed.frame['bollinger_hband']))

    def next(self):
        self.bar_count += 1
        print(
            f'>>>> {self.bars[0].datetime} >>>> {self.bars[0].close} >>>> {self.bars[0].rsi} >>> {self.bars[0].price_upcross_tenkan} ')

        if abs(self.bars[0].rsi_downhit_25) == 1 and self.bar_count > 14:
            self.rsi_buy_signal.upsert_notes(note_id_name='RSIDownHit25', note_desc='RSI down hits 25')
            if not self.position.has_position():
                self.rsi_buy_signal.up_signal(ref_bar=self.bars[0], ref_indicator_value={'rsi': self.bars[0].rsi})
                # print(f'rsi: {rsi_buy_signal.is_up} vs tenkan: {tenkan_buy_signal.is_up}')
                self.notify_signal(self.rsi_buy_signal)

        if abs(self.bars[0].price_upcross_tenkan) == 1 and self.bar_count > 14:
            self.tenkan_buy_signal.upsert_notes(note_id_name='PriceUpCrossTenkan', note_desc='Price up crosses Tenkan')
            if not self.position.has_position():
                self.tenkan_buy_signal.up_signal(ref_bar=self.bars[0],
                                                 ref_indicator_value={'tenkan': self.bars[0].tenkan})

                self.notify_signal(self.tenkan_buy_signal)

        if abs(self.bars[0].price_downcross_hband) == 1 and self.bar_count > 14:
            self.hband_sell_signal.upsert_notes(note_id_name='PriceDownCressHBand',
                                                note_desc='Price down crosses High BB')
            if self.position.has_position():
                self.hband_sell_signal.up_signal(ref_bar=self.bars[0],
                                                 ref_indicator_value={'hband': self.bars[0].bollinger_hband})
                self.notify_signal(self.hband_sell_signal)

        if abs(self.bars[0].price_downcross_tenkan) == 1 and self.bar_count > 14:
            self.tenkan_sell_signal.upsert_notes(note_id_name='PriceDownCrossTenkan',
                                                 note_desc='Price down crosses Tenkan')
            if self.position.has_position():
                self.tenkan_sell_signal.up_signal(ref_bar=self.bars[0],
                                                  ref_indicator_value={'tenkan': self.bars[0].tenkan})
                self.notify_signal(self.tenkan_sell_signal)

        if self.tenkan_buy_signal.is_up:
            if not self.position.has_position():
                self.buy(islimit=False, ref_price=self.bars[0].close)
                self.rsi_buy_signal.down_signal()
                self.update_pending_orders(is_multiple_update=False)
            if self.position.has_position():
                prices = self.stp_pricer.get_stop_limit_prices(ref_price=self.bars[0].close, is_to_trail=False)

                if prices:
                    self.stoploss(isstoplimit=True, stop_price=prices['stop_price'],
                                  ref_price=self.bars[0].close, limit_price=prices['limit_price'])
                    self.stp_pricer.set_trailing(ref_price=self.bars[0].close, stop_price=prices['stop_price'])

        if self.position.has_position():
            self.trail_stoploss(isstoplimit=True)

        if self.tenkan_sell_signal.is_up:
            if self.position.has_position():
                self.sell(islimit=False, ref_price=self.bars[0].close)
'''
'''
class RSIStrategy(BaseStrategy):

    def prepare(self):
        self._barfeed.add_fields(rsi=RSIIndicator(self._barfeed.close, window=14, fillna=True).rsi())
        self._barfeed.add_fields(rsi_downhit_70=IndicatorSignal(self._barfeed.frame['rsi']).is_down_hit(70))
        self._barfeed.add_fields(rsi_uphit_25=IndicatorSignal(self._barfeed.frame['rsi']).is_up_hit(25))

    def next(self):
        print(f'>>>> {self.bars[0].datetime} >>>> {self.bars[0].close} >>>> {self.bars[0].rsi} ')
        rsi_buy_signal = Signal(isbuy=True, codename='RSIBuy', sequence='only')
        rsi_sell_signal = Signal(isbuy=False, codename='RSISell', sequence='only')

        if abs(self.bars[0].rsi_downhit_70) == 1:
            rsi_sell_signal.upsert_notes(note_id_name='RSIDownHit70', note_desc='RSI downhits 70')
            if self.position.has_position():
                rsi_sell_signal.up_signal(ref_bar=self.bars[0], ref_indicator_value={'rsi': self.bars[0].rsi})
                self.notify_signal(rsi_sell_signal)

        if abs(self.bars[0].rsi_uphit_25) == 1:
            rsi_buy_signal.upsert_notes(note_id_name='RSIUpHit25', note_desc='RSI uphits 70')
            if not self.position.has_position():
                rsi_buy_signal.up_signal(ref_bar=self.bars[0], ref_indicator_value={'rsi': self.bars[0].rsi})
                self.notify_signal(rsi_buy_signal)

        if rsi_buy_signal.is_up:
            self.buy(islimit=False, ref_price=self.bars[0].close)
            self.update_pending_orders(is_multiple_update=False)
            if self.position.has_position():
                prices = self.stp_pricer.get_stop_limit_prices(ref_price=self.bars[0].close, is_to_trail=False)

                if prices:
                    self.stoploss(isstoplimit=True, stop_price=prices['stop_price'],
                                  ref_price=self.bars[0].close, limit_price=prices['limit_price'])
                    self.stp_pricer.set_trailing(ref_price=self.bars[0].close, stop_price=prices['stop_price'])

        if self.position.has_position():
            self.trail_stoploss(isstoplimit=True)

        if rsi_sell_signal.is_up:
            self.sell(islimit=False, ref_price=self.bars[0].close)

# class RSIStrategy(BaseStrategy):
#
#     def prepare(self):
#         self._bar_frame.add_fields(rsi=RSIIndicator(self._bar_frame.close, window=14, fillna=True).rsi())
#         self._bar_frame.add_fields(rsi_uphit_70=Indicator(self._bar_frame.frame['rsi']).is_up_hit(70))
#
#     def next(self):
#     #     print('bar 0:', self.bars[0])
#     #     print('bar -1:', self.bars[-1])
#         rsi = self.bars[0].rsi
#         price = self.bars[0].close
#         if rsi and self.bars[0].rsi_uphit_70 == 1:
#             # pass
#             print(f'RSI: {self.bars[0].rsi} and close price: {price}')

# cloud_buy_signal = Signal(isbuy=True, codename='IchimokuCloudBuy', sequence='last',
#                                  leading_dependent_signal=rsi_buy_signal)
#
#        buy_ss = SignalSet(isbuy=True, signal_count=2)
#        sgnl_set.add_signals(first_signal, last_signal, middle_signal)
'''
