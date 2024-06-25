# region imports
from AlgorithmImports import *
from QuantConnect.Algorithm import QCAlgorithm
from QuantConnect.Algorithm.Framework.Alphas import Insight
from QuantConnect.Data import Slice

from AlphaQM import AlphaQM
from FullProjectMB.utils.indicators.CumulativeReturnQM import CumulativeReturnQM
from utils.indicators.VolatilityQM import VolatilityQM

# from main import ManagementAlgorithm

# endregion
class SVIX10(AlphaQM):
    def __init__(self, customAlgo:QCAlgorithm) -> None:
        symbols = [
            "IEI"
        ]
        indicators = []
        AlphaQM.__init__(self, customAlgo, (14,4,10,-10), symbols, indicators)

    def calculate(self):
        return self.allocate([("IEI",1)])
        
        
