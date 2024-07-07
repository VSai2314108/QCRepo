# region imports
from AlgorithmImports import *
from QuantConnect.Algorithm import QCAlgorithm
from QuantConnect.Algorithm.Framework.Alphas import Insight
from QuantConnect.Data import Slice

from AlphaQM import AlphaQM
from utils.indicators.CumulativeReturnQM import CumulativeReturnQM
from utils.indicators.VolatilityQM import VolatilityQM

# from main import ManagementAlgorithm

# endregion
class SVIX10(AlphaQM):
    def __init__(self, customAlgo:QCAlgorithm) -> None:
        symbols = [
            "SHV", "TLT", "HYG", "GLD", "UUP"
        ]
        indicators = [(CumulativeReturnQM, 90), (CumulativeReturnQM, 120)]
        AlphaQM.__init__(self, customAlgo, (14,4,10,-10), symbols, indicators)

    def calculate(self):
        indicators = ["CumulativeReturnQM"]
        periods = [90, 120]
        allocations = self.selection_helper(self.symbols, indicators, periods, mx=True, k_top=2)
        return self.allocate(allocations)
        
        
