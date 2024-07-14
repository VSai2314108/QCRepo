# region imports
from AlgorithmImports import *
from QuantConnect.Algorithm import QCAlgorithm
from QuantConnect.Algorithm.Framework.Alphas import Insight
from QuantConnect.Data import Slice

from AlphaQM import AlphaQM
from utils.indicators.RelativeStrengthIndexQM import RelativeStrengthIndexQM
from utils.indicators.MovingAverageQM import MovingAverageQM
from utils.indicators.CumulativeReturnQM import CumulativeReturnQM

# endregion

class S11_5(AlphaQM):
    def __init__(self, customAlgo:QCAlgorithm) -> None:
        symbols = [
            "TLT", "GLD", "TMF", "BTAL", "XLP", "UUP", "PSQ", "SH", "TMV"
        ]
        indicators = [
            (MovingAverageQM, 200),
            (MovingAverageQM, 5),
            (RelativeStrengthIndexQM, 14),
            (RelativeStrengthIndexQM, 20),
            (CumulativeReturnQM, 20)
        ]
        AlphaQM.__init__(self, customAlgo, (11,1,1,-1), symbols, indicators)

    def calculate(self):
        if self.customAlgo.indicators["TLT"]["tempBar"].close > self.customAlgo.indicators["TLT"]["MovingAverageQM_200"].temp_value:
            if self.customAlgo.indicators["TLT"]["RelativeStrengthIndexQM_14"].temp_value < 50:
                if self.customAlgo.indicators["TLT"]["tempBar"].close > self.customAlgo.indicators["TLT"]["MovingAverageQM_5"].temp_value:
                    return self.allocate([("TMF", 1)])
                else:
                    if self.customAlgo.indicators["TLT"]["RelativeStrengthIndexQM_14"].temp_value < 20:
                        return self.allocate([("TMF", 1)])
                    else:
                        if self.customAlgo.indicators["TLT"]["CumulativeReturnQM_20"].temp_value < 0:
                            allocations = self.selection_helper(["PSQ", "SH", "UUP", "TMV"], ["RelativeStrengthIndexQM"], [20], mx=False, k_top=1)
                            allocations = [(symbol, weight*0.5) for symbol, weight in allocations]
                            allocations.append(("UUP", 0.5))
                            return self.allocate(allocations)
                        else:
                            return self.allocate([("GLD", 0.25), ("TMF", 0.25), ("BTAL", 0.25), ("XLP", 0.25)])
            else:
                if self.customAlgo.indicators["TLT"]["RelativeStrengthIndexQM_14"].temp_value > 80:
                    return self.allocate([("TMV", 1)])
                else:
                    if self.customAlgo.indicators["TLT"]["CumulativeReturnQM_20"].temp_value < 0:
                        allocations = self.selection_helper(["PSQ", "SH", "UUP", "TMV"], ["RelativeStrengthIndexQM"], [20], mx=False, k_top=1)
                        allocations = [(symbol, weight*0.5) for symbol, weight in allocations]
                        allocations.append(("UUP", 0.5))
                        return self.allocate(allocations)
                    else:
                        return self.allocate([("GLD", 0.25), ("TMF", 0.25), ("BTAL", 0.25), ("XLP", 0.25)])
        else:
            if self.customAlgo.indicators["TLT"]["CumulativeReturnQM_20"].temp_value < 0:
                allocations = self.selection_helper(["PSQ", "SH", "UUP", "TMV"], ["RelativeStrengthIndexQM"], [20], mx=False, k_top=1)
                allocations = [(symbol, weight*0.5) for symbol, weight in allocations]
                allocations.append(("UUP", 0.5))
                return self.allocate(allocations)
            else:
                return self.allocate([("GLD", 0.25), ("TMF", 0.25), ("BTAL", 0.25), ("XLP", 0.25)])