# region imports
from AlgorithmImports import *
from QuantConnect.Algorithm import QCAlgorithm
from QuantConnect.Algorithm.Framework.Alphas import Insight
from QuantConnect.Data import Slice

from AlphaQM import AlphaQM
from utils.indicators.VolatilityQM import VolatilityQM

# from main import ManagementAlgorithm

# endregion
class S11_2(AlphaQM):
    def __init__(self, customAlgo:QCAlgorithm) -> None:
        symbols = [
            "TLT", "TMF", "SHY", "UUP", "GLD", "XLP"
        ]
        indicators = [(VolatilityQM, 60), (VolatilityQM, 40), (VolatilityQM, 20)]
        AlphaQM.__init__(self, customAlgo, (14,4,10,-10), symbols, indicators)

    def calculate(self):
        allocations = []
        if self.customAlgo.indicators["TLT"]["VolatilityQM_60"].temp_value < 1:
            allocations.extend([("TMF",0.5), ("SHY",0.5)])
        else:
            allocations.extend([("SHY", 0.25), ("UUP", 0.25), ("GLD", 0.25), ("XLP", 0.25)])
            
        if self.customAlgo.indicators["TLT"]["VolatilityQM_40"].temp_value < 0.25:
            allocations.extend([("TMF",0.5), ("SHY",0.5)])
        else:
            allocations.extend([("SHY", 0.25), ("UUP", 0.25), ("GLD", 0.25), ("XLP", 0.25)])
            
        if self.customAlgo.indicators["TLT"]["VolatilityQM_20"].temp_value < 0.5:
            allocations.extend([("TMF",0.5), ("SHY",0.5)])
        else:
            allocations.extend([("SHY", 0.25), ("UUP", 0.25), ("GLD", 0.25), ("XLP", 0.25)])
        
        # multiple all weights by 0.333
        allocations = [(symbol, weight*0.333) for symbol, weight in allocations]
        
        return self.allocate(allocations)
        
        
