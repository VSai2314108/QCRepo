from AlgorithmImports import *
from QuantConnect.Algorithm import QCAlgorithm
from QuantConnect.Data import Slice
from AlphaQM import AlphaQM
from utils.indicators.RelativeStrengthIndexQM import RelativeStrengthIndexQM
from utils.indicators.MaxDrawdownQM import MaxDrawdownQM
from utils.indicators.VolatilityQM import VolatilityQM
from utils.indicators.CumulativeReturnQM import CumulativeReturnQM
from utils.indicators.MovingAverageQM import MovingAverageQM
from utils.indicators.ExponentialMovingAverageQM import ExponentialMovingAverageQM

class BullOrHedge(AlphaQM):
    def __init__(self, customAlgo: QCAlgorithm) -> None:
        symbols = [
            "SPY", "SPXU", "UVXY", "TMF", "SPXL", "GLD", "UUP", "SQQQ"
        ]
        indicators = [
            (RelativeStrengthIndexQM, 10), (MaxDrawdownQM, 10),
            (CumulativeReturnQM, 5), (CumulativeReturnQM, 1),
            (ExponentialMovingAverageQM, 200), (MovingAverageQM, 20)
        ]
        AlphaQM.__init__(self, customAlgo, (14, 4, 10, -10), symbols, indicators, True)

    def calculate(self):
        # Get indicator values
        spy_close = self.customAlgo.indicators["SPY"]["tempBar"].Close
        spy_ma200 = self.customAlgo.indicators["SPY"]["ExponentialMovingAverageQM_200"].temp_value
        spy_ema200 = self.customAlgo.indicators["SPY"]["ExponentialMovingAverageQM_200"].temp_value 
        spxu_rsi10 = self.customAlgo.indicators["SPXU"]["RelativeStrengthIndexQM_10"].temp_value
        uvxy_rsi10 = self.customAlgo.indicators["UVXY"]["RelativeStrengthIndexQM_10"].temp_value
        spxl_close = self.customAlgo.indicators["SPXL"]["tempBar"].Close
        spxl_ma20 = self.customAlgo.indicators["SPXL"]["MovingAverageQM_20"].temp_value
        sqqq_rsi10 = self.customAlgo.indicators["SQQQ"]["RelativeStrengthIndexQM_10"].temp_value
        spxl_rsi10 = self.customAlgo.indicators["SPXL"]["RelativeStrengthIndexQM_10"].temp_value
        spy_maxdd10 = self.customAlgo.indicators["SPY"]["MaxDrawdownQM_10"].temp_value
        tmf_maxdd10 = self.customAlgo.indicators["TMF"]["MaxDrawdownQM_10"].temp_value
        spy_cumret5 = self.customAlgo.indicators["SPY"]["CumulativeReturnQM_5"].temp_value
        spxl_cumret1 = self.customAlgo.indicators["SPXL"]["CumulativeReturnQM_1"].temp_value
        spy_rsi10 = self.customAlgo.indicators["SPY"]["RelativeStrengthIndexQM_10"].temp_value

        # Implement the strategy logic
        tickers_weights = []
        if spy_close > spy_ma200:
            if spxu_rsi10 < 31:
                if uvxy_rsi10 > 74:
                    tickers_weights.append(("GLD", 0.5))
                    tickers_weights.append(("UUP", 0.5))
                else:
                    if spy_maxdd10 > 6:
                        tickers_weights.append(("GLD", 0.5))
                        tickers_weights.append(("UUP", 0.5))
                    elif tmf_maxdd10 > 7:
                        tickers_weights.append(("GLD", 0.5))
                        tickers_weights.append(("UUP", 0.5))
                    else:
                        if spy_close > spy_ema200:
                            if spxl_rsi10 < 31:
                                if uvxy_rsi10 > 74:
                                    tickers_weights.append(("GLD", 0.5))
                                    tickers_weights.append(("UUP", 0.5))
                                else:
                                    if spxl_close > spxl_ma20:
                                        if sqqq_rsi10 < 31:
                                            tickers_weights.append(("GLD", 0.5))
                                            tickers_weights.append(("UUP", 0.5))
                                        else:
                                            tickers_weights.append(("SPXL", 1))
                                    else:
                                        tickers_weights.append(("GLD", 0.5))
                                        tickers_weights.append(("UUP", 0.5))
                            else:
                                if uvxy_rsi10 > 84:
                                    tickers_weights.append(("GLD", 0.5))
                                    tickers_weights.append(("UUP", 0.5))
                                else:
                                    tickers_weights.append(("UVXY", 1))
                        else:
                            if spxl_rsi10 > 79:
                                tickers_weights.append(("UVXY", 1))
                            else:
                                if spy_cumret5 < -6:
                                    if spxl_cumret1 > 5:
                                        tickers_weights.append(("GLD", 0.5))
                                        tickers_weights.append(("UUP", 0.5))
                                    else:
                                        if spxl_rsi10 > 31:
                                            tickers_weights.append(("GLD", 0.5))
                                            tickers_weights.append(("UUP", 0.5))
                                        else:
                                            tickers_weights.append(("SPXL", 1))
                                else:
                                    if spy_rsi10 < 31:
                                        tickers_weights.append(("SPXL", 1))
                                    else:
                                        tickers_weights.append(("SPY", 1))
            else:
                tickers_weights.append(("GLD", 0.5))
                tickers_weights.append(("UUP", 0.5))
        else:
            if spxu_rsi10 > 79:
                tickers_weights.append(("UVXY", 1))
            else:
                if spy_maxdd10 > 6:
                    tickers_weights.append(("GLD", 0.5))
                    tickers_weights.append(("UUP", 0.5))
                elif tmf_maxdd10 > 7:
                    tickers_weights.append(("GLD", 0.5))
                    tickers_weights.append(("UUP", 0.5))
                else:
                    if spy_close > spy_ema200:
                        if spxl_rsi10 < 31:
                            if uvxy_rsi10 > 74:
                                tickers_weights.append(("GLD", 0.5))
                                tickers_weights.append(("UUP", 0.5))
                            else:
                                if spxl_close > spxl_ma20:
                                    if sqqq_rsi10 < 31:
                                        tickers_weights.append(("GLD", 0.5))
                                        tickers_weights.append(("UUP", 0.5))
                                    else:
                                        tickers_weights.append(("SPXL", 1))
                                else:
                                    tickers_weights.append(("GLD", 0.5))
                                    tickers_weights.append(("UUP", 0.5))
                        else:
                            if uvxy_rsi10 > 84:
                                tickers_weights.append(("GLD", 0.5))
                                tickers_weights.append(("UUP", 0.5))
                            else:
                                tickers_weights.append(("UVXY", 1))
                    else:
                        if spxl_rsi10 > 79:
                            tickers_weights.append(("UVXY", 1))
                        else:
                            if spy_cumret5 < -6:
                                if spxl_cumret1 > 5:
                                    tickers_weights.append(("GLD", 0.5))
                                    tickers_weights.append(("UUP", 0.5))
                                else:
                                    if spxl_rsi10 > 31:
                                        tickers_weights.append(("GLD", 0.5))
                                        tickers_weights.append(("UUP", 0.5))
                                    else:
                                        tickers_weights.append(("SPXL", 1))
                            else:
                                if spy_rsi10 < 31:
                                    tickers_weights.append(("SPXL", 1))
                                else:
                                    tickers_weights.append(("SPY", 1))

        return self.allocate(tickers_weights)