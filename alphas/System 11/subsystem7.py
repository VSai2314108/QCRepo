# region imports
from AlgorithmImports import *
from QuantConnect.Algorithm import QCAlgorithm

from AlphaQM import AlphaQM
from utils.indicators.RelativeStrengthIndexQM import RelativeStrengthIndexQM
from utils.indicators.MovingAverageQM import MovingAverageQM
from utils.indicators.CumulativeReturnQM import CumulativeReturnQM
from utils.indicators.MaxDrawdownQM import MaxDrawdownQM
# endregion

class BlackSwanCatcher(AlphaQM):
    def __init__(self, customAlgo:QCAlgorithm) -> None:
        symbols = [
            "SPY", "TQQQ", "UVXY", "QQQ", "TMF", "IEF", "TLT", "BND", "USDU", "GLD", "XLP"
        ]
        indicators = [
            (RelativeStrengthIndexQM, 10),
            (RelativeStrengthIndexQM, 45),
            (RelativeStrengthIndexQM, 60),
            (RelativeStrengthIndexQM, 200),
            (MovingAverageQM, 25),
            (CumulativeReturnQM, 1),
            (CumulativeReturnQM, 6),
            (MaxDrawdownQM, 10)
        ]
        AlphaQM.__init__(self, customAlgo, (11,1,1,-1), symbols, indicators)

    def calculate(self):
        if self.customAlgo.indicators["TQQQ"]["RelativeStrengthIndexQM_10"].temp_value > 79:
            return self.allocate([("UVXY", 1)])
        elif self.customAlgo.indicators["TQQQ"]["CumulativeReturnQM_6"].temp_value < -12:
            if self.customAlgo.indicators["TQQQ"]["CumulativeReturnQM_1"].temp_value > 5.5:
                return self.allocate([("UVXY", 1)])
            elif self.customAlgo.indicators["TQQQ"]["RelativeStrengthIndexQM_10"].temp_value < 32:
                return self.allocate([("TQQQ", 1)])
            elif self.customAlgo.indicators["TMF"]["MaxDrawdownQM_10"].temp_value < 7:
                return self.allocate([("TQQQ", 1)])
            else:
                return self.allocate([("USDU", 1/3), ("GLD", 1/3), ("XLP", 1/3)])
        else:
            if self.customAlgo.indicators["QQQ"]["MaxDrawdownQM_10"].temp_value > 6 or self.customAlgo.indicators["TMF"]["MaxDrawdownQM_10"].temp_value > 7:
                return self.allocate([("USDU", 1/3), ("GLD", 1/3), ("XLP", 1/3)])
            elif self.customAlgo.indicators["QQQ"]["tempBar"].close > self.customAlgo.indicators["QQQ"]["MovingAverageQM_25"].temp_value:
                return self.allocate([("TQQQ", 1)])
            elif self.customAlgo.indicators["SPY"]["RelativeStrengthIndexQM_60"].temp_value > 50:
                if self.customAlgo.indicators["BND"]["RelativeStrengthIndexQM_45"].temp_value > self.customAlgo.indicators["SPY"]["RelativeStrengthIndexQM_45"].temp_value:
                    return self.allocate([("TQQQ", 1)])
                else:
                    return self.allocate([("USDU", 1/3), ("GLD", 1/3), ("XLP", 1/3)])
            elif self.customAlgo.indicators["IEF"]["RelativeStrengthIndexQM_200"].temp_value < self.customAlgo.indicators["TLT"]["RelativeStrengthIndexQM_200"].temp_value:
                if self.customAlgo.indicators["BND"]["RelativeStrengthIndexQM_45"].temp_value > self.customAlgo.indicators["SPY"]["RelativeStrengthIndexQM_45"].temp_value:
                    return self.allocate([("TQQQ", 1)])
                else:
                    return self.allocate([("USDU", 1/3), ("GLD", 1/3), ("XLP", 1/3)])
            else:
                return self.allocate([("USDU", 1/3), ("GLD", 1/3), ("XLP", 1/3)])