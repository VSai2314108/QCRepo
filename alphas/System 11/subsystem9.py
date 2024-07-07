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
            "VIXY", "BND", "BIL", "QLD", "SVXY", "BTAL", "SPY", "GLD", "XLP", "SHY"
        ]
        indicators = [(CumulativeReturnQM, 60), (VolatilityQM, 21)]
        AlphaQM.__init__(self, customAlgo, (14,4,10,-10), symbols, indicators)

    def calculate(self):
        if self.customAlgo.indicators["SPY"]["VolatilityQM_21"].temp_value < 1.25:
            if self.customAlgo.indicators["BND"]["CumulativeReturnQM_60"].temp_value > self.customAlgo.indicators["BIL"]["CumulativeReturnQM_60"].temp_value:
                return self.allocate([("QLD",1)])
            else:
                return self.allocate([("SVXY",0.55), ("BTAL",0.45)])
        else:
            return self.allocate([("SPY",0.2), ("BTAL",0.2), ("GLD",0.2), ("XLP",0.2), ("SHY",0.2)]) 
        
        
