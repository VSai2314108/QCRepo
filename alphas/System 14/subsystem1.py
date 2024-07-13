from AlgorithmImports import *
from QuantConnect.Algorithm import QCAlgorithm
from AlphaQM import AlphaQM
from utils.indicators.RelativeStrengthIndexQM import RelativeStrengthIndexQM
from utils.indicators.CumulativeReturnQM import CumulativeReturnQM
from utils.indicators.MovingAverageQM import MovingAverageQM

class HedgedTrinityPop(AlphaQM):
    def __init__(self, customAlgo: QCAlgorithm) -> None:
        symbols = [
            "SPY", "SPXL", "TQQQ", "SOXL", "UVXY", "BIL", "VIXM", "DBC", "SQQQ", "CURE", "UTSL", "SVXY"
        ]
        indicators = [
            (RelativeStrengthIndexQM, 10),
            (CumulativeReturnQM, 1), (CumulativeReturnQM, 5), (CumulativeReturnQM, 100), (CumulativeReturnQM, 200),
            (CumulativeReturnQM, 300), (CumulativeReturnQM, 400), (CumulativeReturnQM, 500), (CumulativeReturnQM, 600),
            (MovingAverageQM, 20)
        ]
        AlphaQM.__init__(self, customAlgo, (14, 4, 10, -10), symbols, indicators, True)
    
    def calculate(self):
        # SPY Pop Bot
        spy_allocation = self.spy_pop_bot()
        if spy_allocation:
            return spy_allocation
        
        # QQQ Pop Bot
        qqq_allocation = self.qqq_pop_bot()
        if qqq_allocation:
            return qqq_allocation
        
        # SMH Pop Bot
        smh_allocation = self.smh_pop_bot()
        if smh_allocation:
            return smh_allocation
        
        # If none of the above conditions are met, allocate to BIL
        return self.allocate([("BIL", 1)])

    def spy_pop_bot(self):
        spxl_rsi = self.customAlgo.indicators["SPXL"]["RelativeStrengthIndexQM_10"].temp_value
        if spxl_rsi > 80:
            return self.allocate([("UVXY", 1)])
        elif spxl_rsi < 30:
            return self.allocate([("SPXL", 1)])
        return None

    def qqq_pop_bot(self):
        tqqq_rsi = self.customAlgo.indicators["TQQQ"]["RelativeStrengthIndexQM_10"].temp_value
        if tqqq_rsi > 80:
            return self.allocate([("UVXY", 1)])
        elif tqqq_rsi < 30:
            return self.allocate([("TQQQ", 1)])
        return None

    def smh_pop_bot(self):
        soxl_rsi = self.customAlgo.indicators["SOXL"]["RelativeStrengthIndexQM_10"].temp_value
        if soxl_rsi < 30:
            return self.allocate([("SOXL", 1)])
        return None

    def trinity_strategy(self):
        vixm_rsi = self.customAlgo.indicators["VIXM"]["RelativeStrengthIndexQM_10"].temp_value
        if vixm_rsi > 70:
            return self.allocate([("BIL", 1)])
        
        for period in [600, 500, 400, 300, 200, 100]:
            spy_return = self.customAlgo.indicators["SPY"][f"CumulativeReturnQM_{period}"].temp_value
            dbc_return = self.customAlgo.indicators["DBC"][f"CumulativeReturnQM_{period}"].temp_value
            
            if spy_return > dbc_return:
                svxy_return = self.customAlgo.indicators["SVXY"]["CumulativeReturnQM_5"].temp_value
                if svxy_return > 0:
                    return self.allocate([("TQQQ", 1/3), ("CURE", 1/3), ("SVXY", 1/3)])
                else:
                    return self.allocate([("TQQQ", 1/3), ("CURE", 1/3), ("UTSL", 1/3)])
            else:
                return self.allocate([("SQQQ", 1/4), ("CURE", 1/4), ("UTSL", 1/4), ("SVXY", 1/4)])
        
        return self.allocate([("BIL", 1)])