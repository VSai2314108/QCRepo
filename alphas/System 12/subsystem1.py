from AlgorithmImports import *
from QuantConnect.Algorithm import QCAlgorithm
from AlphaQM import AlphaQM
from utils.indicators.RelativeStrengthIndexQM import RelativeStrengthIndexQM
from utils.indicators.MaxDrawdownQM import MaxDrawdownQM
from utils.indicators.CumulativeReturnQM import CumulativeReturnQM
from utils.indicators.MovingAverageQM import MovingAverageQM
from utils.indicators.ExponentialMovingAverageQM import ExponentialMovingAverageQM
from utils.indicators.VolatilityQM import VolatilityQM

class BullOrHedge(AlphaQM):
    def __init__(self, customAlgo: QCAlgorithm) -> None:
        symbols = ['TMF', 'SQQQ', 'UVXY', 'GLD', 'SPY', 'UUP', 'SPXL', 'SPXU']

        indicators = [
            (RelativeStrengthIndexQM, 10), (MaxDrawdownQM, 10),
            (CumulativeReturnQM, 5), (CumulativeReturnQM, 1),
            (ExponentialMovingAverageQM, 200), (MovingAverageQM, 20),
            (MovingAverageQM, 200), (VolatilityQM, 30)
        ]        
        AlphaQM.__init__(self, customAlgo, (14, 4, 10, -10), symbols, indicators, True)
        
    def calculate(self):
        ### PRICE ###
        spy_price_0 = self.customAlgo.indicators["SPY"]["tempBar"].Close
        spxl_price_0 = self.customAlgo.indicators["SPXL"]["tempBar"].Close
        
        ### INDICATORS ###
        spy_price_200 = self.customAlgo.indicators["SPY"]["MovingAverageQM_200"].temp_value
        spxu_rsi_10 = self.customAlgo.indicators["SPXU"]["RelativeStrengthIndexQM_10"].temp_value
        spy_maxdrawdown_10 = self.customAlgo.indicators["SPY"]["MaxDrawdownQM_10"].temp_value
        tmf_maxdrawdown_10 = self.customAlgo.indicators["TMF"]["MaxDrawdownQM_10"].temp_value
        spy_ema_200 = self.customAlgo.indicators["SPY"]["ExponentialMovingAverageQM_200"].temp_value
        spxl_rsi_10 = self.customAlgo.indicators["SPXL"]["RelativeStrengthIndexQM_10"].temp_value
        spy_cumret_5 = self.customAlgo.indicators["SPY"]["CumulativeReturnQM_5"].temp_value
        spxl_cumret_1 = self.customAlgo.indicators["SPXL"]["CumulativeReturnQM_1"].temp_value
        spy_rsi_10 = self.customAlgo.indicators["SPY"]["RelativeStrengthIndexQM_10"].temp_value
        uvxy_rsi_10 = self.customAlgo.indicators["UVXY"]["RelativeStrengthIndexQM_10"].temp_value
        spxl_ma_20 = self.customAlgo.indicators["SPXL"]["MovingAverageQM_20"].temp_value
        sqqq_rsi_10 = self.customAlgo.indicators["SQQQ"]["RelativeStrengthIndexQM_10"].temp_value

        tickers_weights = []
        if spy_price_0 > spy_price_200:
            if spxu_rsi_10 > 79.0:
                tickers_weights.append(("UVXY", 1))
            else:
                if spy_maxdrawdown_10 > 6.0 or tmf_maxdrawdown_10 > 7.0:
                    tickers_weights = self.inverse_volatility_allocation(["GLD", "UUP"])
                else:
                    if spy_price_0 > spy_ema_200:
                        if spxl_rsi_10 > 79.0:
                            tickers_weights.append(("UVXY", 1))
                        else:
                            if spy_cumret_5 < -6.0:
                                if spxl_cumret_1 > 5.0 or spxl_rsi_10 > 31.0:
                                    tickers_weights = self.inverse_volatility_allocation(["GLD", "UUP"])
                                else:
                                    tickers_weights.append(("SPXL", 1))
                            else:
                                if spy_rsi_10 < 31.0:
                                    tickers_weights.append(("SPXL", 1))
                                else:
                                    tickers_weights.append(("SPY", 1))
                    else:
                        if spxl_rsi_10 < 31.0:
                            tickers_weights.append(("SPXL", 1))
                        else:
                            if uvxy_rsi_10 > 74.0:
                                if uvxy_rsi_10 > 84.0:
                                    tickers_weights = self.inverse_volatility_allocation(["GLD", "UUP"])
                                else:
                                    tickers_weights.append(("UVXY", 1))
                            else:
                                if spxl_price_0 > spxl_ma_20:
                                    if sqqq_rsi_10 < 31.0:
                                        tickers_weights = self.inverse_volatility_allocation(["GLD", "UUP"])
                                    else:
                                        tickers_weights.append(("SPXL", 1))
                                else:
                                    tickers_weights = self.inverse_volatility_allocation(["GLD", "UUP"])
        else:
            if spxu_rsi_10 < 31.0:
                if spy_maxdrawdown_10 > 6.0 or tmf_maxdrawdown_10 > 7.0:
                    tickers_weights = self.inverse_volatility_allocation(["GLD", "UUP"])
                else:
                    if spy_price_0 > spy_ema_200:
                        if spxl_rsi_10 > 79.0:
                            tickers_weights.append(("UVXY", 1))
                        else:
                            if spy_cumret_5 < -6.0:
                                if spxl_cumret_1 > 5.0 or spxl_rsi_10 > 31.0:
                                    tickers_weights = self.inverse_volatility_allocation(["GLD", "UUP"])
                                else:
                                    tickers_weights.append(("SPXL", 1))
                            else:
                                if spy_rsi_10 < 31.0:
                                    tickers_weights.append(("SPXL", 1))
                                else:
                                    tickers_weights.append(("SPY", 1))
                    else:
                        if spxl_rsi_10 < 31.0:
                            tickers_weights.append(("SPXL", 1))
                        else:
                            if uvxy_rsi_10 > 74.0:
                                if uvxy_rsi_10 > 84.0:
                                    tickers_weights = self.inverse_volatility_allocation(["GLD", "UUP"])
                                else:
                                    tickers_weights.append(("UVXY", 1))
                            else:
                                if spxl_price_0 > spxl_ma_20:
                                    if sqqq_rsi_10 < 31.0:
                                        tickers_weights = self.inverse_volatility_allocation(["GLD", "UUP"])
                                    else:
                                        tickers_weights.append(("SPXL", 1))
                                else:
                                    tickers_weights = self.inverse_volatility_allocation(["GLD", "UUP"])
            else:
                if uvxy_rsi_10 > 74.0:
                    if uvxy_rsi_10 > 84.0:
                        if spy_maxdrawdown_10 > 6.0 or tmf_maxdrawdown_10 > 7.0:
                            tickers_weights = self.inverse_volatility_allocation(["GLD", "UUP"])
                        else:
                            if spy_price_0 > spy_ema_200:
                                if spxl_rsi_10 > 79.0:
                                    tickers_weights.append(("UVXY", 1))
                                else:
                                    if spy_cumret_5 < -6.0:
                                        if spxl_cumret_1 > 5.0 or spxl_rsi_10 > 31.0:
                                            tickers_weights = self.inverse_volatility_allocation(["GLD", "UUP"])
                                        else:
                                            tickers_weights.append(("SPXL", 1))
                                    else:
                                        if spy_rsi_10 < 31.0:
                                            tickers_weights.append(("SPXL", 1))
                                        else:
                                            tickers_weights.append(("SPY", 1))
                            else:
                                if spxl_rsi_10 < 31.0:
                                    tickers_weights.append(("SPXL", 1))
                                else:
                                    if uvxy_rsi_10 > 74.0:
                                        if uvxy_rsi_10 > 84.0:
                                            tickers_weights = self.inverse_volatility_allocation(["GLD", "UUP"])
                                        else:
                                            tickers_weights.append(("UVXY", 1))
                                    else:
                                        if spxl_price_0 > spxl_ma_20:
                                            if sqqq_rsi_10 < 31.0:
                                                tickers_weights = self.inverse_volatility_allocation(["GLD", "UUP"])
                                            else:
                                                tickers_weights.append(("SPXL", 1))
                                        else:
                                            tickers_weights = self.inverse_volatility_allocation(["GLD", "UUP"])
                    else:
                        tickers_weights.append(("UVXY", 1))
                else:
                    if spy_maxdrawdown_10 > 6.0 or tmf_maxdrawdown_10 > 7.0:
                        tickers_weights = self.inverse_volatility_allocation(["GLD", "UUP"])
                    else:
                        if spy_price_0 > spy_ema_200:
                            if spxl_rsi_10 > 79.0:
                                tickers_weights.append(("UVXY", 1))
                            else:
                                if spy_cumret_5 < -6.0:
                                    if spxl_cumret_1 > 5.0 or spxl_rsi_10 > 31.0:
                                        tickers_weights = self.inverse_volatility_allocation(["GLD", "UUP"])
                                    else:
                                        tickers_weights.append(("SPXL", 1))
                                else:
                                    if spy_rsi_10 < 31.0:
                                        tickers_weights.append(("SPXL", 1))
                                    else:
                                        tickers_weights.append(("SPY", 1))
                        else:
                            if spxl_rsi_10 < 31.0:
                                tickers_weights.append(("SPXL", 1))
                            else:
                                if uvxy_rsi_10 > 74.0:
                                    if uvxy_rsi_10 > 84.0:
                                        tickers_weights = self.inverse_volatility_allocation(["GLD", "UUP"])
                                    else:
                                        tickers_weights.append(("UVXY", 1))
                                else:
                                    if spxl_price_0 > spxl_ma_20:
                                        if sqqq_rsi_10 < 31.0:
                                            tickers_weights = self.inverse_volatility_allocation(["GLD", "UUP"])
                                        else:
                                            tickers_weights.append(("SPXL", 1))
                                    else:
                                        tickers_weights = self.inverse_volatility_allocation(["GLD", "UUP"])

        return self.allocate(tickers_weights)

    def inverse_volatility_allocation(self, tickers):
        volatilities = [self.customAlgo.indicators[ticker]["VolatilityQM_30"].temp_value for ticker in tickers]
        inverse_volatilities = [1 / vol if vol != 0 else 0 for vol in volatilities]
        total_inverse_volatility = sum(inverse_volatilities)
        
        if total_inverse_volatility == 0:
            return [(ticker, 1 / len(tickers)) for ticker in tickers]
        
        weights = [inv_vol / total_inverse_volatility for inv_vol in inverse_volatilities]
        return list(zip(tickers, weights))