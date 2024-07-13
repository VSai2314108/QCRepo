from AlgorithmImports import *
from AlphaQM import AlphaQM
from utils.indicators.RelativeStrengthIndexQM import RelativeStrengthIndexQM
from utils.indicators.CumulativeReturnQM import CumulativeReturnQM
from utils.indicators.MovingAverageQM import MovingAverageQM
from utils.indicators.VolatilityQM import VolatilityQM
from utils.indicators.MaxDrawdownQM import MaxDrawdownQM

class VixationUVIX(AlphaQM):
    def __init__(self, customAlgo: QCAlgorithm) -> None:
        symbols = [
            "TQQQ", "TECL", "UPRO", "FNGU", "UDOW", "VIXM", "QQQ", "SPY", "SVXY", 
            "BND", "TLT", "PSQ", "IEF", "TBX", "SH", "UVXY", "SPXL", "BSV", "SVIX", "SVOL"
        ]
        indicators = [
            (RelativeStrengthIndexQM, 10), (RelativeStrengthIndexQM, 15), (RelativeStrengthIndexQM, 20),
            (CumulativeReturnQM, 1), (CumulativeReturnQM, 6), (CumulativeReturnQM, 10),
            (VolatilityQM, 5), (VolatilityQM, 10),
            (MaxDrawdownQM, 4), (MaxDrawdownQM, 5), (MaxDrawdownQM, 6), 
            (MaxDrawdownQM, 7), (MaxDrawdownQM, 8), (MaxDrawdownQM, 9)
        ]
        AlphaQM.__init__(self, customAlgo, (14, 4, 10, -10), symbols, indicators, True)

    def calculate(self):
        if self.check_overbought():
            return self.allocate([("UVXY", 1)])
        
        if self.check_oversold():
            return self.allocate([("SPXL", 1)])
        
        if self.check_bsc_conditions():
            return self.bsc_logic()
        
        allocations = []
        
        allocations.extend(self.check_bond_conditions())
        allocations.extend(self.check_max_drawdown_conditions())
        
        if not allocations:
            allocations = self.volatility_harvester()
        
        return self.allocate(allocations)

    def check_overbought(self):
        return (
            self.customAlgo.indicators["TQQQ"]["RelativeStrengthIndexQM_10"].temp_value > 82 or
            self.customAlgo.indicators["TECL"]["RelativeStrengthIndexQM_10"].temp_value > 80 or
            self.customAlgo.indicators["UPRO"]["RelativeStrengthIndexQM_10"].temp_value > 78
        )

    def check_oversold(self):
        return (
            self.customAlgo.indicators["TQQQ"]["RelativeStrengthIndexQM_10"].temp_value < 28 or
            self.customAlgo.indicators["TECL"]["RelativeStrengthIndexQM_10"].temp_value < 29 or
            self.customAlgo.indicators["FNGU"]["RelativeStrengthIndexQM_10"].temp_value < 26 or
            self.customAlgo.indicators["UDOW"]["RelativeStrengthIndexQM_10"].temp_value < 24 or
            self.customAlgo.indicators["UPRO"]["RelativeStrengthIndexQM_10"].temp_value < 26
        )

    def check_bsc_conditions(self):
        tqqq_cr6 = self.customAlgo.indicators["TQQQ"]["CumulativeReturnQM_6"].temp_value
        vixm_rsi = self.customAlgo.indicators["VIXM"]["RelativeStrengthIndexQM_10"].temp_value
        qqq_vol = self.customAlgo.indicators["QQQ"]["VolatilityQM_10"].temp_value
        spy_vol = self.customAlgo.indicators["SPY"]["VolatilityQM_5"].temp_value
        svxy_rsi = self.customAlgo.indicators["SVXY"]["RelativeStrengthIndexQM_10"].temp_value

        return (tqqq_cr6 < -11 or
                (vixm_rsi > 70 and qqq_vol > 3 and spy_vol > 2.5) or
                svxy_rsi < 30)

    def bsc_logic(self):
        tqqq_cr1 = self.customAlgo.indicators["TQQQ"]["CumulativeReturnQM_1"].temp_value
        if tqqq_cr1 > 5.5:
            return self.allocate([("UVXY", 1)])
        else:
            return self.allocate([("SVIX", 1)])

    def check_bond_conditions(self):
        conditions = [
            (self.customAlgo.indicators["BND"]["RelativeStrengthIndexQM_15"].temp_value >
             self.customAlgo.indicators["QQQ"]["RelativeStrengthIndexQM_15"].temp_value),
            (self.customAlgo.indicators["TLT"]["RelativeStrengthIndexQM_20"].temp_value >
             self.customAlgo.indicators["PSQ"]["RelativeStrengthIndexQM_20"].temp_value),
            (self.customAlgo.indicators["IEF"]["RelativeStrengthIndexQM_10"].temp_value >
             self.customAlgo.indicators["PSQ"]["RelativeStrengthIndexQM_20"].temp_value),
            (self.customAlgo.indicators["BND"]["CumulativeReturnQM_10"].temp_value >
             self.customAlgo.indicators["TBX"]["CumulativeReturnQM_10"].temp_value)
        ]
        
        if any(conditions):
            return [("TECL", 0.5), ("TQQQ", 0.5)]
        return []

    def check_max_drawdown_conditions(self):
        for days in range(4, 10):
            if self.customAlgo.indicators["SH"][f"MaxDrawdownQM_{days}"].temp_value <= 0.1:
                return [("TECL", 0.5), ("TQQQ", 0.5)]
        return []

    def volatility_harvester(self):
        volatilities = {
            "SVXY": self.customAlgo.indicators["SVXY"]["VolatilityQM_5"].temp_value,
            "VIXM": self.customAlgo.indicators["VIXM"]["VolatilityQM_5"].temp_value,
            "SVOL": self.customAlgo.indicators["SVOL"]["VolatilityQM_5"].temp_value
        }
        sorted_tickers = sorted(volatilities, key=volatilities.get)
        return [(ticker, 0.5) for ticker in sorted_tickers[:2]]

    def tech_allocation(self):
        tecl_rsi = self.customAlgo.indicators["TECL"]["RelativeStrengthIndexQM_10"].temp_value
        tqqq_rsi = self.customAlgo.indicators["TQQQ"]["RelativeStrengthIndexQM_10"].temp_value
        bsv_rsi = self.customAlgo.indicators["BSV"]["RelativeStrengthIndexQM_10"].temp_value
        
        if min(tecl_rsi, tqqq_rsi) < bsv_rsi:
            return [("TECL", 0.5), ("TQQQ", 0.5)]
        else:
            return [("BSV", 1)]