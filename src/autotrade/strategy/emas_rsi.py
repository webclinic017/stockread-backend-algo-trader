import math

from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator
from ta.volume import MFIIndicator

from src.autotrade.indicator.insignal import IndicatorSignal
from src.autotrade.signal.signal import Signal, SignalSet
from src.autotrade.strategy.base_strategy import BaseStrategy


class EMASAndRSIStrategy(BaseStrategy):

    def __init__(self):

        super().__init__()
        # INFO: Signal Preparation

        self.rsi_buy_signal = Signal(isbuy=True, codename='RSIBuy', sequence='only')
        self.mfi_buy_signal = Signal(isbuy=True, codename='MFIBuy', sequence='only')
        self.mfi_buy_signal.set_sequential(sequential=2)

        self.rsi_sell_signal = Signal(isbuy=False, codename='RSISell', sequence='only')
        self.mfi_sell_signal = Signal(isbuy=False, codename='MFISell', sequence='only')
        self.mfi_sell_signal.set_sequential(sequential=2)

        self.buy_sgnl_set = SignalSet(isbuy=True, signal_count=2)
        self.buy_sgnl_set.add_signals(self.rsi_buy_signal, self.mfi_buy_signal)

        self.sell_sgnl_set = SignalSet(isbuy=False, signal_count=2)
        self.sell_sgnl_set.add_signals(self.rsi_sell_signal, self.mfi_sell_signal)

    def prepare(self):
        # INFO: Indicators preparation
        self._barfeed.add_fields(rsi=RSIIndicator(self._barfeed.close).rsi())
        self._barfeed.add_fields(ema20=EMAIndicator(self._barfeed.close, window=20).ema_indicator())
        self._barfeed.add_fields(ema50=EMAIndicator(self._barfeed.close, window=50).ema_indicator())
        self._barfeed.add_fields(ema100=EMAIndicator(self._barfeed.close, window=100).ema_indicator())
        self._barfeed.add_fields(ema200=EMAIndicator(self._barfeed.close, window=200).ema_indicator())

        self._barfeed.add_fields(rsi_uphit_30=IndicatorSignal(self._barfeed.frame['rsi']).is_up_hit(30))
        self._barfeed.add_fields(rsi_downhit_70=IndicatorSignal(self._barfeed.frame['rsi']).is_down_hit(70))




        self._barfeed.add_fields(mfi=MFIIndicator(self._barfeed.high, self._barfeed.low,
                                                  self._barfeed.close, self._barfeed.volume).money_flow_index())
        self._barfeed.add_fields(mfi_downhit_80=IndicatorSignal(self._barfeed.frame['mfi']).is_down_hit(80))
        self._barfeed.add_fields(mfi_uphit_20=IndicatorSignal(self._barfeed.frame['mfi']).is_up_hit(20))


    def print_bar(self):
        if not math.isnan(self.bars[0].rsi) or not math.isnan(self.bars[0].mfi):
            tojoin = list()
            tojoin.append('TickerSymbol: {}'.format(self.bars[0].ticker_symbol))
            tojoin.append('IsLiveBar: {}'.format(self.bars[0].is_live_bar))
            tojoin.append('Datetime: {}'.format(self.bars[0].datetime))
            tojoin.append('ClosePrice: {}'.format(self.bars[0].close))
            tojoin.append('RSI: {}'.format(self.bars[0].rsi))
            tojoin.append('MFI: {}'.format(self.bars[0].mfi))
            bar_text = ', '.join(tojoin)
            print(bar_text)

    def next(self):

        if abs(self.bars[0].rsi_uphit_30) == 1:
            self.rsi_buy_signal.set_note(note_id_name='RSIUpHit30', note_desc='RSI up hits 30')
            if not self.position.has_position():
                self.rsi_buy_signal.up_signal(ref_bar=self.bars[0], ref_indicator_value={'rsi': self.bars[0].rsi})
                self.notify_signal(self.rsi_buy_signal)

        if abs(self.bars[0].mfi_uphit_20) == 1:
            self.mfi_buy_signal.set_note(note_id_name='MFIUpHit20', note_desc='MFI up hits 20')
            if not self.position.has_position():
                self.mfi_buy_signal.up_signal(ref_bar=self.bars[0], ref_indicator_value={'mfi': self.bars[0].mfi})
                self.notify_signal(self.mfi_buy_signal)

        if abs(self.bars[0].rsi_downhit_70) == 1:
            self.rsi_sell_signal.set_note(note_id_name='RSIDownHit70', note_desc='RSI down hits 70')
            if self.position.has_position():
                self.rsi_sell_signal.up_signal(ref_bar=self.bars[0], ref_indicator_value={'rsi': self.bars[0].rsi})
                self.notify_signal(self.rsi_sell_signal)

        if abs(self.bars[0].mfi_downhit_80) == 1:
            self.mfi_sell_signal.set_note(note_id_name='MFIDownHit80', note_desc='MFI down hits 80')
            if self.position.has_position():
                self.mfi_sell_signal.up_signal(ref_bar=self.bars[0], ref_indicator_value={'mfi': self.bars[0].mfi})
                self.notify_signal(self.mfi_sell_signal)

        if self.buy_sgnl_set.is_allup():
            if not self.position.has_position():
                self.buy(islimit=False, ref_price=self.bars[0].close)
                self.buy_sgnl_set.down_signals()
                self.update_pending_orders(is_multiple_update=False)

            if self.position.has_position():
                prices = self.stp_pricer.get_stop_limit_prices(ref_price=self.bars[0].close, is_to_trail=False)

                if prices:
                    self.stoploss(isstoplimit=True, stop_price=prices['stop_price'],
                                  ref_price=self.bars[0].close, limit_price=prices['limit_price'])
                    self.stp_pricer.set_trailing(ref_price=self.bars[0].close, stop_price=prices['stop_price'])

        if self.position.has_position():
            self.trail_stoploss(isstoplimit=True)

        if self.sell_sgnl_set.is_allup():
            if self.position.has_position():
                self.sell(islimit=False, ref_price=self.bars[0].close)
                self.sell_sgnl_set.down_signals()
