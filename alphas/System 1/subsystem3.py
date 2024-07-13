from AlgorithmImports import *
from QuantConnect.Algorithm import QCAlgorithm
from AlphaQM import AlphaQM
from utils.indicators.RelativeStrengthIndexQM import RelativeStrengthIndexQM
from utils.indicators.MaxDrawdownQM import MaxDrawdownQM
from utils.indicators.CumulativeReturnQM import CumulativeReturnQM
from utils.indicators.MovingAverageQM import MovingAverageQM
from utils.indicators.VolatilityQM import VolatilityQM
from datetime import datetime

class UncorrelatedBonds(AlphaQM):
    def __init__(self, customAlgo: QCAlgorithm) -> None:
        symbols = [
            "SPY", "IEF", "BIL", "SVXY", "TQQQ", "TECL", "UPRO", "SQQQ", "SOXS", "TECS", "UVXY", "TLT", "BND", "PSQ", "QQQ", "VIXY", "SHY", "GLD", "XLP", "BTAL", "SHV", "TMF", "VIXM", "SOXL", "TMV"
        ]
        indicators = [
            (MovingAverageQM, 10), (MovingAverageQM, 40), (MovingAverageQM, 100), (MovingAverageQM, 200),
            (MaxDrawdownQM, 2), (MaxDrawdownQM, 3), (MaxDrawdownQM, 10),
            (RelativeStrengthIndexQM, 5), (RelativeStrengthIndexQM, 10), (RelativeStrengthIndexQM, 50), (RelativeStrengthIndexQM, 60),
            (VolatilityQM, 5), (VolatilityQM, 10), (VolatilityQM, 40),
            (CumulativeReturnQM, 1), (CumulativeReturnQM, 6), (CumulativeReturnQM, 60), (CumulativeReturnQM, 100)
        ]
        AlphaQM.__init__(self, customAlgo, (14, 4, 10, -10), symbols, indicators, True)

    def calculate(self):
        current_month = self.customAlgo.Time.month

        if current_month in [11, 12]:
            return self.allocate([("SPY", 0.6), ("IEF", 0.4)])

        if self.bonds_exciting():
            return self.allocate([("TMV", 1)])

        if self.svxy_drawdown():
            return self.allocate([("BIL", 1)])

        if self.overbought_conditions():
            return self.handle_overbought_condition()

        if self.bsc_conditions():
            return self.handle_bsc_condition()

        return self.handle_bulls_condition()

    def bonds_exciting(self):
        return (self.customAlgo.indicators["TMV"]["MovingAverageQM_10"].temp_value > 
                self.customAlgo.indicators["TMV"]["MovingAverageQM_40"].temp_value and
                self.customAlgo.indicators["TMV"]["tempBar"].close > 
                self.customAlgo.indicators["TMV"]["MovingAverageQM_100"].temp_value)

    def svxy_drawdown(self):
        return (self.customAlgo.indicators["SVXY"]["MaxDrawdownQM_2"].temp_value >= 10 or
                self.customAlgo.indicators["SVXY"]["MaxDrawdownQM_3"].temp_value >= 20)

    def overbought_conditions(self):
        return (self.customAlgo.indicators["TQQQ"]["RelativeStrengthIndexQM_10"].temp_value >= 82 or
                self.customAlgo.indicators["TECL"]["RelativeStrengthIndexQM_10"].temp_value >= 80 or
                self.customAlgo.indicators["UPRO"]["RelativeStrengthIndexQM_10"].temp_value >= 78)

    def bsc_conditions(self):
        return (self.customAlgo.indicators["VIXM"]["RelativeStrengthIndexQM_10"].temp_value >= 70 and
                self.customAlgo.indicators["QQQ"]["VolatilityQM_10"].temp_value >= 3 and
                self.customAlgo.indicators["SPY"]["VolatilityQM_10"].temp_value >= 2.5)

    def handle_overbought_condition(self):
        hedge_tickers = ["TECS", "SQQQ", "SOXS", "UVXY"]
        no_uvxy_tickers = ["TECS", "SQQQ", "SOXS"]
        
        allocation = []
        for group in [hedge_tickers, no_uvxy_tickers]:
            allocation.extend([
                self.select_best_ticker(group, "VolatilityQM_5", True, 0.1),
                self.select_best_ticker(group, "CumulativeReturnQM_1", True, 0.1),
                self.select_best_ticker(group, "RelativeStrengthIndexQM_5", True, 0.1)
            ])
        
        allocation.append(("BIL", 0.4))
        return self.allocate(allocation)

    def handle_bsc_condition(self):
        bsc_weight = self.get_bsc_weight()
        return self.allocate([
            ("TLT", bsc_weight * 0.5),
            ("VIXM", bsc_weight * 0.5),
            ("BIL", 1 - bsc_weight)
        ])

    def get_bsc_weight(self):
        vixm_rsi = self.customAlgo.indicators["VIXM"]["RelativeStrengthIndexQM_10"].temp_value
        qqq_vol = self.customAlgo.indicators["QQQ"]["VolatilityQM_10"].temp_value
        spy_vol = self.customAlgo.indicators["SPY"]["VolatilityQM_10"].temp_value
        
        if vixm_rsi >= 70 and qqq_vol >= 3 and spy_vol >= 2.5:
            return 1
        elif vixm_rsi >= 65 and qqq_vol >= 2.5 and spy_vol >= 2:
            return 0.66
        elif vixm_rsi >= 60 and qqq_vol >= 2 and spy_vol >= 1.5:
            return 0.33
        else:
            return 0

    def handle_bulls_condition(self):
        if self.nbdb_conditions():
            return self.allocate([("SHV", 1)])

        if self.bsmr_conditions():
            return self.handle_bsmr_condition()

        if self.bab_conditions():
            return self.handle_bab_condition()

        if self.wmdyn_conditions():
            return self.handle_wmdyn_condition()

        return self.handle_individual_ticker_condition()

    def nbdb_conditions(self):
        return (self.customAlgo.indicators["QQQ"]["MaxDrawdownQM_10"].temp_value >= 6 or
                self.customAlgo.indicators["TLT"]["MaxDrawdownQM_10"].temp_value >= 3)

    def bsmr_conditions(self):
        return self.customAlgo.indicators["TQQQ"]["RelativeStrengthIndexQM_10"].temp_value >= 79

    def handle_bsmr_condition(self):
        tqqq_rsi = self.customAlgo.indicators["TQQQ"]["RelativeStrengthIndexQM_10"].temp_value
        tqqq_return = self.customAlgo.indicators["TQQQ"]["CumulativeReturnQM_6"].temp_value
        tqqq_daily_return = self.customAlgo.indicators["TQQQ"]["CumulativeReturnQM_1"].temp_value

        if tqqq_rsi >= 79:
            return self.allocate([("UVXY", 1)])
        elif tqqq_return < -12:
            if tqqq_daily_return >= 5.5:
                return self.allocate([("UVXY", 1)])
            elif tqqq_rsi < 32:
                return self.allocate([("TQQQ", 1)])
        
        return self.allocate([("SHV", 1)])

    def bab_conditions(self):
        return (self.customAlgo.indicators["QQQ"]["RelativeStrengthIndexQM_10"].temp_value >= 80 or
                self.customAlgo.indicators["VIXY"]["VolatilityQM_40"].temp_value < 5)

    def handle_bab_condition(self):
        if self.customAlgo.indicators["QQQ"]["RelativeStrengthIndexQM_10"].temp_value >= 80:
            return self.allocate([("UVXY", 0.5), ("BTAL", 0.5)])
        elif self.customAlgo.indicators["VIXY"]["VolatilityQM_40"].temp_value < 5:
            if self.customAlgo.indicators["BND"]["CumulativeReturnQM_60"].temp_value > self.customAlgo.indicators["BIL"]["CumulativeReturnQM_60"].temp_value:
                return self.allocate([("TQQQ", 1)])
            else:
                return self.allocate([("SVXY", 0.55), ("BTAL", 0.45)])
        else:
            return self.allocate([("SHY", 0.2), ("SPY", 0.2), ("BTAL", 0.2), ("GLD", 0.2), ("XLP", 0.2)])

    def wmdyn_conditions(self):
        return (self.customAlgo.indicators["SPY"]["RelativeStrengthIndexQM_5"].temp_value < 25 or
                self.customAlgo.indicators["SPY"]["VolatilityQM_10"].temp_value >= 2.5)

    def handle_wmdyn_condition(self):
        if self.customAlgo.indicators["SPY"]["VolatilityQM_10"].temp_value >= 2.5:
            return self.allocate([("SHV", 1)])
        elif (self.customAlgo.indicators["BIL"]["CumulativeReturnQM_100"].temp_value <= 
              self.customAlgo.indicators["TLT"]["CumulativeReturnQM_100"].temp_value and
              self.customAlgo.indicators["IEF"]["RelativeStrengthIndexQM_10"].temp_value > 
              self.customAlgo.indicators["PSQ"]["RelativeStrengthIndexQM_10"].temp_value):
            return self.allocate([
                ("SOXL", 0.5),
                self.select_best_ticker(["TLT", "SVXY", "SOXL", "TECL"], "RelativeStrengthIndexQM_5", False, 0.5)
            ])
        else:
            return self.allocate([("SHV", 1)])

    def handle_individual_ticker_condition(self):
        for ticker in ["TQQQ", "TECL", "SOXL", "UPRO", "SVXY"]:
            allocation = self.check_ticker_conditions(ticker)
            if allocation:
                return allocation
        return self.allocate([("SHV", 1)])

    def check_ticker_conditions(self, ticker):
        current_price = self.customAlgo.indicators[ticker]["tempBar"].close
        ma = self.customAlgo.indicators[ticker]["MovingAverageQM_200"].temp_value
        rsi = self.customAlgo.indicators[ticker]["RelativeStrengthIndexQM_10"].temp_value
        cumulative_return = self.customAlgo.indicators[ticker]["CumulativeReturnQM_6"].temp_value

        if current_price > ma:
            if rsi < 49:
                if cumulative_return < -2:
                    return self.allocate([("SHV", 1)])
                elif cumulative_return >= 8.5:
                    if rsi < 31:
                        return self.allocate([(ticker, 1)])
                    else:
                        return self.allocate([("SHV", 1)])
                else:
                    return self.allocate([(ticker, 1)])
            elif rsi >= 82:
                return self.allocate([("SHV", 1)])
            elif rsi < 31:
                if cumulative_return < -6:
                    return self.allocate([(ticker, 1)])
                else:
                    return self.allocate([("SHV", 1)])
        
        return None

    def select_best_ticker(self, tickers, indicator, reverse, weight):
        sorted_tickers = sorted(
            tickers,
            key=lambda ticker: self.customAlgo.indicators[ticker][indicator].temp_value,
            reverse=reverse
        )
        return (sorted_tickers[0], weight)