from AlgorithmImports import *
from QuantConnect.Algorithm import QCAlgorithm
from AlphaQM import AlphaQM
from utils.indicators.RelativeStrengthIndexQM import RelativeStrengthIndexQM
from utils.indicators.MaxDrawdownQM import MaxDrawdownQM
from utils.indicators.CumulativeReturnQM import CumulativeReturnQM
from utils.indicators.MovingAverageQM import MovingAverageQM
from utils.indicators.ExponentialMovingAverageQM import ExponentialMovingAverageQM

class BullOrHedge(AlphaQM):
    def __init__(self, customAlgo: QCAlgorithm) -> None:
        symbols = ['TECS', 'SQQQ', 'SOXS', 'FNGD', 'UVXY', 'TECL', 'TQQQ', 'FNGU', 'SOXL', 'SVXY', 'SGOV', 'VIXM', 'UUP', 'IEF', 'PSQ', 'SPY', 'XLP', 'ERX', 'UPRO', 'BND', 'SPXU', 'SPXL', 'UDOW']

        indicators = [
            (RelativeStrengthIndexQM, 5), (RelativeStrengthIndexQM, 10), (RelativeStrengthIndexQM, 15), 
            (RelativeStrengthIndexQM, 20), (MaxDrawdownQM, 2), (MaxDrawdownQM, 3),
            (CumulativeReturnQM, 5), (CumulativeReturnQM, 10), (CumulativeReturnQM, 15),
            (MovingAverageQM, 10), (MovingAverageQM, 20), (MovingAverageQM, 200),
            (ExponentialMovingAverageQM, 10), (ExponentialMovingAverageQM, 200),
        ]        
        AlphaQM.__init__(self, customAlgo, (14, 4, 10, -10), symbols, indicators, True)
        
    def calculate(self):
        # Declaring variables
        tickers_weights = []

        if self.customAlgo.indicators["SVXY"]["MaxDrawdownQM_2"].temp_value > 10.0:
            tickers_weights.append(("SGOV", 1.0))
        else:
            if self.customAlgo.indicators["SVXY"]["MaxDrawdownQM_3"].temp_value > 20.0:
                tickers_weights.append(("SGOV", 1.0))
            else:
                if self.customAlgo.indicators["TQQQ"]["RelativeStrengthIndexQM_10"].temp_value > 82.0 and \
                self.customAlgo.indicators["TECL"]["RelativeStrengthIndexQM_10"].temp_value > 80.0 and \
                self.customAlgo.indicators["UPRO"]["RelativeStrengthIndexQM_10"].temp_value > 78.0:
                    short_group_tickers = ['TECS', 'SQQQ', 'SOXS', 'FNGD', 'UVXY']
                    short_group_weights = self.selection_helper(short_group_tickers, ["VolatilityQM", "CumulativeReturnQM", "RelativeStrengthIndexQM"], [5, 10, 15], mx=False, k_top=1)
                    tickers_weights.extend([
                        (short_group_weights[0][0], 1.0),
                        ("SGOV", 0.0)
                    ])
                else:
                    if self.customAlgo.indicators["TQQQ"]["RelativeStrengthIndexQM_10"].temp_value < 28.0 and \
                    self.customAlgo.indicators["TECL"]["RelativeStrengthIndexQM_10"].temp_value < 29.0 and \
                    self.customAlgo.indicators["UDOW"]["RelativeStrengthIndexQM_10"].temp_value < 24.0 and \
                    self.customAlgo.indicators["UPRO"]["RelativeStrengthIndexQM_10"].temp_value < 26.0:
                        long_group_tickers = ['TECL', 'TQQQ', 'FNGU', 'SOXL', 'SVXY']
                        long_group_weights = self.selection_helper(long_group_tickers, ["VolatilityQM", "CumulativeReturnQM", "RelativeStrengthIndexQM"], [5, 10, 15], mx=True, k_top=1)
                        tickers_weights.extend([
                            (long_group_weights[0][0], 1.0),
                            ("SGOV", 0.0)
                        ])
                    else:
                        mb_total_market_weights = self.mb_total_market()
                        tickers_weights.extend(mb_total_market_weights)

        return self.allocate(tickers_weights)

    def mb_total_market(self):
        tickers_weights = []
        if self.customAlgo.indicators["VIXM"]["RelativeStrengthIndexQM_10"].temp_value > 70.0:
            tickers_weights.extend([
                ("VIXM", 0.5),
                ("UUP", 0.5)
            ])
        else:
            if self.customAlgo.indicators["IEF"]["RelativeStrengthIndexQM_10"].temp_value > self.customAlgo.indicators["PSQ"]["RelativeStrengthIndexQM_20"].temp_value:
                tickers_weights.append(("TQQQ", 1.0))
            else:
                spy_current_price = self.customAlgo.Securities["SPY"].Price
                spy_ma_200 = self.customAlgo.indicators["SPY"]["MovingAverageQM_200"].temp_value
                if spy_current_price > spy_ma_200:
                    tickers_weights.extend([
                        ("XLP", 0.5),
                        (self.selection_helper(['UUP', 'ERX', 'UPRO'], ["RelativeStrengthIndexQM"], [20], mx=True, k_top=1)[0][0], 0.5)
                    ])
                else:
                    if self.customAlgo.indicators["SPY"]["ExponentialMovingAverageQM_10"].temp_value < self.customAlgo.indicators["SPY"]["MovingAverageQM_10"].temp_value:
                        tickers_weights.append(("SPXU", 1.0))
                    else:
                        tqqq_current_price = self.customAlgo.Securities["TQQQ"].Price
                        tqqq_ma_20 = self.customAlgo.indicators["TQQQ"]["MovingAverageQM_20"].temp_value
                        if tqqq_current_price < tqqq_ma_20:
                            tickers_weights.append(("SQQQ", 1.0))
                        else:
                            tickers_weights.append(("BND", 1.0))
        return tickers_weights