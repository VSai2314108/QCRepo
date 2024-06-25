# region imports
from AlgorithmImports import *
from QuantConnect.Algorithm import QCAlgorithm
from QuantConnect.Algorithm.Framework.Alphas import Insight
from QuantConnect.Data import Slice

from AlphaQM import AlphaQM
from utils.indicators.RelativeStrengthIndexQM import RelativeStrengthIndexQM

# from main import ManagementAlgorithm

# endregion
class SVIX10(AlphaQM):
    def __init__(self, customAlgo:QCAlgorithm) -> None:
        symbols = [
            "IEF", "TIP", "LQD", "HYG"
        ]
        indicators = []
        AlphaQM.__init__(self, customAlgo, (14,4,10,-10), symbols, indicators)

    def calculate(self):
        return self.allocate([("IEF",0.25),("TIP",0.25),("LQD",0.25),("HYG",0.25)])
