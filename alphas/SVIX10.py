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
            "SOXL", "TQQQ", "UVIX", "QQQE", "VTV", "VOX", "TECL", "VOOG", "XLP", "XLV", "XLY", "FAS", "SPXL", "SPY", "VOOV", "SVIX"
        ]
        indicators = [(RelativeStrengthIndexQM, 10)]
        AlphaQM.__init__(self, customAlgo, (14,4,10,-10), symbols, indicators)

    def calculate(self):
        if self.customAlgo.indicators["SOXL"]["RelativeStrengthIndexQM_10"].temp_value < 30:
            return self.allocate([("SOXL",1)])
        elif self.customAlgo.indicators["SPXL"]["RelativeStrengthIndexQM_10"].temp_value < 30:
            return self.allocate([("SPXL",1)])
        elif self.customAlgo.indicators["TQQQ"]["RelativeStrengthIndexQM_10"].temp_value < 30:
            return self.allocate([("TQQQ",1)])
        else:
            rsi_conditions = [
                ("QQQE", 79), ("VTV", 79), ("VOX", 79), ("TECL", 79), 
                ("VOOG", 79), ("VOOV", 79), ("XLP", 75), ("TQQQ", 79), ("XLY", 80), ("FAS", 80), ("SPY", 80)
            ]

            for symbol, rsi_threshold in rsi_conditions:
                rsi = self.customAlgo.indicators[symbol]["RelativeStrengthIndexQM_10"].temp_value
                if rsi > rsi_threshold:
                    return self.allocate([("UVIX",1)])
            
            if self.customAlgo.indicators["TQQQ"]["bars"].count >= 6:
                        tqqq_prices: list[TradeBar] = self.customAlgo.indicators["TQQQ"]["bars"]
                        tqq_temp_price: TradeBar = self.customAlgo.indicators["TQQQ"]["tempBar"] # offset -6 and -2 to -5 and -1 to compensat for temp
                        price_change_7_days = ((tqq_temp_price.close / tqqq_prices[4].close) - 1)*100
                        price_change_1_day = ((tqq_temp_price.close / tqqq_prices[0].close) - 1)*100
                        
                        if (price_change_7_days < -12.0) and (price_change_1_day > 5.5):
                            return self.allocate([("UVIX",1)])
            
            return self.allocate([("SVIX",1)])
