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
        spy_price_0 = self.customAlgo.indicators["SPY"]["tempBar"].Close
        spy_ma_200 = self.customAlgo.indicators["SPY"]["MovingAverageQM_200"].temp_value

        if spy_price_0 > spy_ma_200:
            spxu_rsi_10 = self.customAlgo.indicators["SPXU"]["RelativeStrengthIndexQM_10"].temp_value
            if spxu_rsi_10 > 79.0:
                return self.allocate([("UVXY", 1)])
            else:
                return self.risk_off_strategy()
        else:
            spxu_rsi_10 = self.customAlgo.indicators["SPXU"]["RelativeStrengthIndexQM_10"].temp_value
            if spxu_rsi_10 < 31.0:
                return self.risk_off_strategy()
            else:
                uvxy_rsi_10 = self.customAlgo.indicators["UVXY"]["RelativeStrengthIndexQM_10"].temp_value
                if uvxy_rsi_10 > 74.0:
                    if uvxy_rsi_10 > 84.0:
                        return self.risk_off_strategy()
                    else:
                        return self.allocate([("UVXY", 1)])
                else:
                    return self.risk_off_strategy()

    def risk_off_strategy(self):
        spy_drawdown_10 = self.customAlgo.indicators["SPY"]["MaxDrawdownQM_10"].temp_value
        tmf_drawdown_10 = self.customAlgo.indicators["TMF"]["MaxDrawdownQM_10"].temp_value
        
        if spy_drawdown_10 > 6.0 or tmf_drawdown_10 > 7.0:
            return self.allocate(self.inverse_volatility_allocation(["GLD", "UUP"]))
        else:
            return self.risk_on_strategy()

    def risk_on_strategy(self):
        spy_price_0 = self.customAlgo.indicators["SPY"]["tempBar"].Close
        spy_ema_200 = self.customAlgo.indicators["SPY"]["ExponentialMovingAverageQM_200"].temp_value
        if spy_price_0 > spy_ema_200:
            spxl_rsi_10 = self.customAlgo.indicators["SPXL"]["RelativeStrengthIndexQM_10"].temp_value
            if spxl_rsi_10 > 79.0:
                return self.allocate([("UVXY", 1)])
            else:
                spy_return_5 = self.customAlgo.indicators["SPY"]["CumulativeReturnQM_5"].temp_value
                if spy_return_5 < -6.0:
                    spxl_return_1 = self.customAlgo.indicators["SPXL"]["CumulativeReturnQM_1"].temp_value
                    if spxl_return_1 > 5.0 or spxl_rsi_10 > 31.0:
                        return self.allocate(self.inverse_volatility_allocation(["GLD", "UUP"]))
                    else:
                        return self.allocate([("SPXL", 1)])
                else:
                    spy_rsi_10 = self.customAlgo.indicators["SPY"]["RelativeStrengthIndexQM_10"].temp_value
                    if spy_rsi_10 < 31.0:
                        return self.allocate([("SPXL", 1)])
                    else:
                        return self.allocate([("SPY", 1)])
        else:
            spxl_rsi_10 = self.customAlgo.indicators["SPXL"]["RelativeStrengthIndexQM_10"].temp_value
            if spxl_rsi_10 < 31.0:
                return self.allocate([("SPXL", 1)])
            else:
                uvxy_rsi_10 = self.customAlgo.indicators["UVXY"]["RelativeStrengthIndexQM_10"].temp_value
                if uvxy_rsi_10 > 74.0:
                    if uvxy_rsi_10 > 84.0:
                        return self.allocate(self.inverse_volatility_allocation(["GLD", "UUP"]))
                    else:
                        return self.allocate([("UVXY", 1)])
                else:
                    spxl_price_0 = self.customAlgo.indicators["SPXL"]["tempBar"].Close
                    spxl_ma_20 = self.customAlgo.indicators["SPXL"]["MovingAverageQM_20"].temp_value
                    if spxl_price_0 > spxl_ma_20:
                        sqqq_rsi_10 = self.customAlgo.indicators["SQQQ"]["RelativeStrengthIndexQM_10"].temp_value
                        if sqqq_rsi_10 < 31.0:
                            return self.allocate(self.inverse_volatility_allocation(["GLD", "UUP"]))
                        else:
                            return self.allocate([("SPXL", 1)])
                    else:
                        return self.allocate(self.inverse_volatility_allocation(["GLD", "UUP"]))

    def inverse_volatility_allocation(self, tickers):
        volatilities = [self.customAlgo.indicators[ticker]["VolatilityQM_30"].temp_value for ticker in tickers]
        inverse_volatilities = [1 / vol if vol != 0 else 0 for vol in volatilities]
        total_inverse_volatility = sum(inverse_volatilities)
        if total_inverse_volatility == 0:
            return [(ticker, 1 / len(tickers)) for ticker in tickers]
        weights = [inv_vol / total_inverse_volatility for inv_vol in inverse_volatilities]
        return list(zip(tickers, weights))