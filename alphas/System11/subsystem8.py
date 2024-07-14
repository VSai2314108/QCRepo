# region imports
from AlgorithmImports import *
from QuantConnect.Algorithm import QCAlgorithm
from QuantConnect.Algorithm.Framework.Alphas import Insight
from QuantConnect.Data import Slice

from AlphaQM import AlphaQM
from utils.indicators.RelativeStrengthIndexQM import RelativeStrengthIndexQM
from utils.indicators.MovingAverageQM import MovingAverageQM

# endregion

class S11_8(AlphaQM):
    def __init__(self, customAlgo:QCAlgorithm) -> None:
        symbols = [
            "SPY", "TQQQ", "UVXY", "SQQQ", "BSV", "SPXL", "TECL"
        ]
        indicators = [
            (RelativeStrengthIndexQM, 10),
            (MovingAverageQM, 200),
            (MovingAverageQM, 20)
        ]
        AlphaQM.__init__(self, customAlgo, (11,1,1,-1), symbols, indicators)

    def calculate(self):
        if self.customAlgo.indicators["SPY"]["MovingAverageQM_200"].temp_value < self.customAlgo.indicators["SPY"]["tempBar"].close:
            if self.customAlgo.indicators["TQQQ"]["RelativeStrengthIndexQM_10"].temp_value > 79 :
                return self.allocate([("UVXY", 1)])
            elif self.customAlgo.indicators["SPXL"]["RelativeStrengthIndexQM_10"].temp_value > 80:
                return self.allocate([("UVXY", 1)])
            else:
                return self.allocate([("TQQQ", 1)])
        else:
            if self.customAlgo.indicators["TQQQ"]["RelativeStrengthIndexQM_10"].temp_value < 31:
                return self.allocate([("TECL", 1)])
            elif self.customAlgo.indicators["SPY"]["RelativeStrengthIndexQM_10"].temp_value > 30:
                return self.allocate([("SPXL", 1)])
            elif self.customAlgo.indicators["UVXY"]["RelativeStrengthIndexQM_10"].temp_value > 74:
                if 84 < self.customAlgo.indicators["UVXY"]["RelativeStrengthIndexQM_10"].temp_value:
                    if self.customAlgo.indicators["TQQQ"]["tempBar"].close > self.customAlgo.indicators["TQQQ"]["MovingAverageQM_20"].temp_value:
                        return self.allocate([("TQQQ", 1)])
                    else:
                        allocations = self.selection_helper(["SQQQ", "BSV"], ["RelativeStrengthIndexQM"], [10], mx=True, k_top=1)
                        return allocations
                else:
                    return self.allocate([("UVXY", 1)])
            else:
                if self.customAlgo.indicators["TQQQ"]["tempBar"].close > self.customAlgo.indicators["TQQQ"]["MovingAverageQM_20"].temp_value:
                    return self.allocate([("TQQQ", 1)])
                else:
                    allocations = self.selection_helper(["SQQQ", "BSV"], ["RelativeStrengthIndexQM"], [10], mx=True, k_top=1)
                    return allocations