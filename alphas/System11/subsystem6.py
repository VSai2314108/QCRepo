# region imports
from AlgorithmImports import *
from QuantConnect.Algorithm import QCAlgorithm
from QuantConnect.Algorithm.Framework.Alphas import Insight
from QuantConnect.Data import Slice

from AlphaQM import AlphaQM
from utils.indicators.CumulativeReturnQM import CumulativeReturnQM
from utils.indicators.RelativeStrengthIndexQM import RelativeStrengthIndexQM

# from main import ManagementAlgorithm

# endregion
class S11_6(AlphaQM):
    def __init__(self, customAlgo:QCAlgorithm) -> None:
        symbols = [
            "VGLT", "VGIT", "TMF", "TMV", "USDU", "BND", "BIL", "TLT"
        ]
        indicators = [(CumulativeReturnQM, 60), (CumulativeReturnQM, 20), (RelativeStrengthIndexQM, 20)]
        AlphaQM.__init__(self, customAlgo, (14,4,10,-10), symbols, indicators)

    def calculate(self):
        if self.customAlgo.indicators["BND"]["CumulativeReturnQM_60"].temp_value > self.customAlgo.indicators["BIL"]["CumulativeReturnQM_60"].temp_value:
            return self.allocate([("VGLT",0.5), ("VGIT",0.5)])
        else:
            if self.customAlgo.indicators["TLT"]["CumulativeReturnQM_20"].temp_value < 0:
                allocations = self.selection_helper(["TMV", "USDU"], ["RelativeStrengthIndexQM"], [20], False, 1)
                allocations = [(symbol, weight*0.5) for symbol, weight in allocations]
                allocations.extend([("USDU",0.5)])
                return self.allocate(allocations)
            else:
                return self.allocate([("TMF",1)])
        
        
