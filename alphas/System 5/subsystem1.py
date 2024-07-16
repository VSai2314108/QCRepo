# region imports
from AlgorithmImports import *
from QuantConnect.Algorithm import QCAlgorithm
from QuantConnect.Algorithm.Framework.Alphas import Insight
from QuantConnect.Data import Slice

from AlphaQM import AlphaQM
from utils.indicators.RelativeStrengthIndexQM import RelativeStrengthIndexQM
from utils.indicators.MaxDrawdownQM import MaxDrawdownQM
from utils.indicators.VolatilityQM import VolatilityQM
from utils.indicators.CumulativeReturnQM import CumulativeReturnQM
from utils.indicators.MovingAverageQM import MovingAverageQM
from utils.indicators.ExponentialMovingAverageQM import ExponentialMovingAverageQM

class BullOnlyVsBearOnly(AlphaQM):
    def __init__(self, customAlgo: QCAlgorithm) -> None:
        symbols = ["SPY", "TMF", "TMV", "TQQQ", "TLT", "SGOV", "SHV"]
        indicators = [
            (RelativeStrengthIndexQM, 10), (RelativeStrengthIndexQM, 60),
            (MaxDrawdownQM, 10),
            (MovingAverageQM, 15), (MovingAverageQM, 21), (MovingAverageQM, 50),
            (MovingAverageQM, 110), (MovingAverageQM, 135), (MovingAverageQM, 200),
            (MovingAverageQM, 350), (MovingAverageQM, 550), (MovingAverageQM, 20),
            (ExponentialMovingAverageQM, 3), (ExponentialMovingAverageQM, 5),
            (ExponentialMovingAverageQM, 8), (ExponentialMovingAverageQM, 20)
        ]
        AlphaQM.__init__(self, customAlgo, (5, 5, 10, -10), symbols, indicators, True)

    def calculate(self):
        # Indicator and price declarations
        self.tmf_rsi10 = self.customAlgo.indicators['TMF']['RelativeStrengthIndexQM_10'].temp_value
        self.tmv_rsi10 = self.customAlgo.indicators['TMV']['RelativeStrengthIndexQM_10'].temp_value
        self.tmv_rsi60 = self.customAlgo.indicators['TMV']['RelativeStrengthIndexQM_60'].temp_value
        self.tlt_rsi60 = self.customAlgo.indicators['TLT']['RelativeStrengthIndexQM_60'].temp_value
        self.tmf_ema5 = self.customAlgo.indicators['TMF']['ExponentialMovingAverageQM_5'].temp_value
        self.tmf_ma200 = self.customAlgo.indicators['TMF']['MovingAverageQM_200'].temp_value
        self.tmv_ema3 = self.customAlgo.indicators['TMV']['ExponentialMovingAverageQM_3'].temp_value
        self.tmv_ma20 = self.customAlgo.indicators['TMV']['MovingAverageQM_20'].temp_value
        self.tlt_ma21 = self.customAlgo.indicators['TLT']['MovingAverageQM_21'].temp_value
        self.tlt_ma110 = self.customAlgo.indicators['TLT']['MovingAverageQM_110'].temp_value
        self.tlt_ema8 = self.customAlgo.indicators['TLT']['ExponentialMovingAverageQM_8'].temp_value
        self.tlt_ema20 = self.customAlgo.indicators['TLT']['ExponentialMovingAverageQM_20'].temp_value
        self.tmv_ma15 = self.customAlgo.indicators['TMV']['MovingAverageQM_15'].temp_value
        self.tmv_ma50 = self.customAlgo.indicators['TMV']['MovingAverageQM_50'].temp_value
        self.tmv_price = self.customAlgo.indicators['TMV']['tempBar'].close
        self.tmv_ma135 = self.customAlgo.indicators['TMV']['MovingAverageQM_135'].temp_value
        self.tlt_ma350 = self.customAlgo.indicators['TLT']['MovingAverageQM_350'].temp_value
        self.tlt_ma550 = self.customAlgo.indicators['TLT']['MovingAverageQM_550'].temp_value
        self.tqqq_mdd10 = self.customAlgo.indicators['TQQQ']['MaxDrawdownQM_10'].temp_value
        self.tmv_mdd10 = self.customAlgo.indicators['TMV']['MaxDrawdownQM_10'].temp_value
        
        if self.tmf_rsi10 < 30:
            return self.allocate([("TMF", 1)])
        
        if self.tmv_mdd10 < 7:
            if self.tqqq_mdd10 < 7:
                return self.bonds_strategy()
            else:
                return self.handle_low_drawdown()
        else:
            return self.bonds_strategy()

    def handle_low_drawdown(self):
        if self.tmf_ema5 > self.tmf_ma200:
            return self.allocate([("TMF", 1)])
        else:
            if self.tmv_ema3 > self.tmv_ma20:
                return self.allocate([("TMV", 1)])
            else:
                return self.bonds_strategy()

    def bonds_strategy(self):
        tmf_momentum = self.get_tmf_momentum()
        tmv_momentum = self.get_tmv_momentum()
        tlt_momentum = self.get_tlt_momentum()

        # Calculating equal weights
        symbols = list(set([tmf_momentum, tmv_momentum, tlt_momentum]))
        weight = 1.0 / len(symbols)
        allocation = [(symbol, weight) for symbol in symbols]
        
        return self.allocate(allocation)

    def get_tmf_momentum(self):
        if self.tmf_rsi10 < 32:
            return "TMF"
        else:
            if self.tlt_ma21 > self.tlt_ma110:
                return "TMF"
            else:
                if self.tlt_ema8 < self.tlt_ema20:
                    return "SGOV"
                else:
                    return "TMF"

    def get_tmv_momentum(self):
        if self.tmf_rsi10 < 32:
            return "TMF"
        else:
            if self.tmv_ma15 > self.tmv_ma50:
                if self.tmv_price > self.tmv_ma135:
                    if self.tmv_rsi10 > 71:
                        return "SGOV"
                    else:
                        if self.tmv_rsi60 > 59:
                            return "TLT"
                        else:
                            return "TMV"
                else:
                    return "SHV"
            else:
                return "SHV"

    def get_tlt_momentum(self):
        if self.tlt_ma350 > self.tlt_ma550:
            if self.tlt_rsi60 > 62:
                return "SGOV"
            else:
                return "TLT"
        else:
            if self.tlt_rsi60 > 53:
                return "TLT"
            else:
                return "SGOV"