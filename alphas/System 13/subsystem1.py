from AlgorithmImports import *
from QuantConnect.Algorithm import QCAlgorithm
from AlphaQM import AlphaQM
from utils.indicators.RelativeStrengthIndexQM import RelativeStrengthIndexQM
from utils.indicators.MaxDrawdownQM import MaxDrawdownQM
from utils.indicators.CumulativeReturnQM import CumulativeReturnQM
from utils.indicators.MovingAverageQM import MovingAverageQM
from utils.indicators.ExponentialMovingAverageQM import ExponentialMovingAverageQM
from utils.indicators.VolatilityQM import VolatilityQM

class BroadMarket(AlphaQM):
    def __init__(self, customAlgo: QCAlgorithm) -> None:
        symbols = ['SVXY', 'TECS', 'SQQQ', 'SOXS', 'FNGD', 'UVXY', 'TECL', 'TQQQ', 'SOXL', 'FNGU', 'UPRO', 'UDOW', 'SPY', 'SGOV', 'VIXM', 'UUP', 'ERX', 'XLP', 'BND', 'SPXU', 'PSQ', 'IEF']

        indicators = [
            (RelativeStrengthIndexQM, 10), (MaxDrawdownQM, 2), (MaxDrawdownQM, 3),
            (CumulativeReturnQM, 5), (VolatilityQM, 5), (MovingAverageQM, 200),
            (ExponentialMovingAverageQM, 10), (MovingAverageQM, 10), (MovingAverageQM, 20),
            (RelativeStrengthIndexQM, 20)
        ]
        
        AlphaQM.__init__(self, customAlgo, (14, 4, 10, -10), symbols, indicators, True)
        
    def calculate(self):
        # Volmageddon I
        if self.customAlgo.indicators["SVXY"]["MaxDrawdownQM_2"].temp_value > 10.0:
            return self.allocate([("SGOV", 1)])

        # Volmageddon II
        if self.customAlgo.indicators["SVXY"]["MaxDrawdownQM_3"].temp_value > 20.0:
            return self.allocate([("SGOV", 1)])

        # Dip Buy conditions
        tqqq_rsi = self.customAlgo.indicators["TQQQ"]["RelativeStrengthIndexQM_10"].temp_value
        tecl_rsi = self.customAlgo.indicators["TECL"]["RelativeStrengthIndexQM_10"].temp_value
        udow_rsi = self.customAlgo.indicators["UDOW"]["RelativeStrengthIndexQM_10"].temp_value
        upro_rsi = self.customAlgo.indicators["UPRO"]["RelativeStrengthIndexQM_10"].temp_value

        dip_buy_conditions = [
            tqqq_rsi < 28.0,
            tecl_rsi < 29.0,
            udow_rsi < 24.0,
            upro_rsi < 26.0
        ]

        if all(dip_buy_conditions):
            return self.allocate(self.long_high_beta(100))
        elif sum(dip_buy_conditions[:3]) == 3:
            return self.allocate(self.long_high_beta(75))
        elif sum(dip_buy_conditions[:2]) == 2:
            return self.allocate(self.long_high_beta(50))
        elif dip_buy_conditions[0]:
            return self.allocate(self.long_high_beta(25))

        # MB Total Market
        vixm_rsi = self.customAlgo.indicators["VIXM"]["RelativeStrengthIndexQM_10"].temp_value
        if vixm_rsi > 70.0:
            return self.allocate([("VIXM", 0.5), ("UUP", 0.5)])

        ief_rsi = self.customAlgo.indicators["IEF"]["RelativeStrengthIndexQM_10"].temp_value
        psq_rsi = self.customAlgo.indicators["PSQ"]["RelativeStrengthIndexQM_20"].temp_value
        if ief_rsi > psq_rsi:
            return self.allocate([("TQQQ", 1)])

        spy_price = self.customAlgo.indicators["SPY"]["tempBar"].Close
        spy_ma_200 = self.customAlgo.indicators["SPY"]["MovingAverageQM_200"].temp_value
        if spy_price > spy_ma_200:
            return self.allocate([("XLP", 0.5)] + self.select_top_rsi([("UUP", 1), ("ERX", 1), ("UPRO", 1)], 0.5))

        spy_ema_10 = self.customAlgo.indicators["SPY"]["ExponentialMovingAverageQM_10"].temp_value
        spy_ma_10 = self.customAlgo.indicators["SPY"]["MovingAverageQM_10"].temp_value
        if spy_ema_10 < spy_ma_10:
            return self.allocate([("SPXU", 1)])

        tqqq_price = self.customAlgo.indicators["TQQQ"]["tempBar"].Close
        tqqq_ma_20 = self.customAlgo.indicators["TQQQ"]["MovingAverageQM_20"].temp_value
        if tqqq_price < tqqq_ma_20:
            return self.allocate([("SQQQ", 1)])

        return self.allocate([("BND", 1)])

    def long_high_beta(self, percentage):
        long_group_svxy = self.select_top([
            ("TECL", 1), ("TQQQ", 1), ("FNGU", 1), ("SOXL", 1), ("SVXY", 1)
        ], 1)
        long_group_no_svxy = self.select_top([
            ("TECL", 1), ("TQQQ", 1), ("SOXL", 1), ("FNGU", 1)
        ], 1)
        long_high_beta = [(ticker, weight * 0.5) for ticker, weight in long_group_svxy + long_group_no_svxy]
        return [(ticker, weight * percentage / 100) for ticker, weight in long_high_beta] + [("SGOV", (100 - percentage) / 100)]

    def select_top(self, tickers_weights, count):
        sorted_tickers = sorted(
            tickers_weights,
            key=lambda x: self.customAlgo.indicators[x[0]]["RelativeStrengthIndexQM_10"].temp_value,
            reverse=True
        )
        return sorted_tickers[:count]

    def select_top_rsi(self, tickers_weights, weight):
        top_ticker = max(
            tickers_weights,
            key=lambda x: self.customAlgo.indicators[x[0]]["RelativeStrengthIndexQM_20"].temp_value
        )
        return [(top_ticker[0], weight)]