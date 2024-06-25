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
# from main import ManagementAlgorithm

# endregion
class NeoBetaBaller(AlphaQM):
    def __init__(self, customAlgo:QCAlgorithm, slope_params=(14,4,10,-10)) -> None:
        symbols = [ # first row is traded, second is data
            "SPY", "BTAL", "FNGD", "FNGU", "PDBC", "SGOV", "SOXL", "SOXS", "SPLV", "SPXU", "SQQQ", "SVXY", "TECL", "TECS", "TLT", "TMV", "TQQQ", "UQL", "UUP", "UVXY", "VIXM", "UPRO", "UDOW", "BIL", "TMF", "PSQ", "IEF", "UGL"
        ]
        indicators = [(MaxDrawdownQM,2), (MaxDrawdownQM,3),
                      (VolatilityQM, 5), (CumulativeReturnQM, 5), (RelativeStrengthIndexQM, 5),
                      (VolatilityQM, 10), (CumulativeReturnQM, 10), (RelativeStrengthIndexQM, 10),
                      (VolatilityQM, 15), (CumulativeReturnQM, 15), (RelativeStrengthIndexQM, 15),
                      (CumulativeReturnQM, 100), (CumulativeReturnQM, 6), (CumulativeReturnQM, 1), (RelativeStrengthIndexQM, 20), (MovingAverageQM, 200), (RelativeStrengthIndexQM, 60), (RelativeStrengthIndexQM, 200)]
        AlphaQM.__init__(self, customAlgo, slope_params, symbols, indicators)

    def calculate(self):
        def selection_helper(tickers, used_indicators, periods, mx=True, k_top=1):
            selected_tickers = []

            for indicator in used_indicators:
                for period in periods:
                    key = f"{indicator}_{period}"
                    # Sort the tickers based on the temp_value for the given key
                    sorted_tickers = sorted(
                        tickers,
                        key=lambda ticker: self.customAlgo.indicators[ticker][key].temp_value,
                        reverse=mx
                    )
                    # Select the top k tickers
                    selected_tickers.extend(sorted_tickers[:k_top])

            # Count the occurrences of each ticker
            ticker_counts = {}
            for ticker in selected_tickers:
                if ticker in ticker_counts:
                    ticker_counts[ticker] += 1
                else:
                    ticker_counts[ticker] = 1

            # Convert the counts to a list of tuples
            ticker_count_list = [(ticker, count / (len(selected_tickers) * 1.0)) for ticker, count in ticker_counts.items()]

            return ticker_count_list
            
        if self.customAlgo.indicators["SVXY"]["MaxDrawdownQM_2"].temp_value > 10:
            return self.allocate([("SGOV", 1)])  
        if self.customAlgo.indicators["SVXY"]["MaxDrawdownQM_3"].temp_value > 20:
            return self.allocate([("SGOV", 1)])  
        
        cond1 = self.customAlgo.indicators["TQQQ"]["RelativeStrengthIndexQM_10"].temp_value > 82
        cond2 = self.customAlgo.indicators["TECL"]["RelativeStrengthIndexQM_10"].temp_value > 80
        cond3 = self.customAlgo.indicators["UPRO"]["RelativeStrengthIndexQM_10"].temp_value > 78
        weight = (sum([cond1, cond2, cond3]))/3

        if weight > 0: # short scenario
            tickers_short = ["TECS", "SQQQ", "SOXS", "FNGD", "UVXY"]
            used_indicators = ["VolatilityQM", "CumulativeReturnQM", "RelativeStrengthIndexQM"]
            periods = [5, 10, 15]
            tickers_weights = [(ticker, weight * value) for ticker, value in self.selection_helper(tickers_short, used_indicators, periods, True)]
            tickers_weights.append(("SGOV", 1-weight))
            return self.allocate(tickers_weights)
        
        cond1 = self.customAlgo.indicators["TQQQ"]["RelativeStrengthIndexQM_10"].temp_value < 28
        cond2 = self.customAlgo.indicators["TECL"]["RelativeStrengthIndexQM_10"].temp_value < 29
        cond3 = self.customAlgo.indicators["UDOW"]["RelativeStrengthIndexQM_10"].temp_value < 24
        cond4 = self.customAlgo.indicators["UPRO"]["RelativeStrengthIndexQM_10"].temp_value < 26
        weight = (sum([cond1, cond2, cond3, cond4]))/4
        
        if weight > 0: # long scenario
            tickers_short = ["TECL", "TQQQ", "FNGU", "SOXL", "SVXY"]
            used_indicators = ["VolatilityQM", "CumulativeReturnQM", "RelativeStrengthIndexQM"]
            periods = [5, 10, 15]
            tickers_weights = [(ticker, weight * value) for ticker, value in self.selection_helper(tickers_short, used_indicators, periods, False)]
            tickers_weights.append(("SGOV", 1-weight))
            return self.allocate(tickers_weights)
        
        # SPY and VIX
        if self.customAlgo.indicators["VIXM"]["RelativeStrengthIndexQM_10"].temp_value > 70:
            last_4_values = self.customAlgo.indicators["VIXM"]["RelativeStrengthIndexQM_10"].values[-4:]
            if len(last_4_values) == 4 and all(value > 70 for value in last_4_values):
                return self.allocate([("VIXM", 0.5), ("UUP", 0.5)])
        
        if self.customAlgo.indicators["SPY"]["RelativeStrengthIndexQM_5"].temp_value < 25:
            temp_tickers = ["TLT", "SVXY", "SOXL", "TECL"]
            used_indicators = ["RelativeStrengthIndexQM"]
            periods = [5]
            tickers_weights = [(ticker, 0.5 * value) for ticker, value in self.selection_helper(temp_tickers, used_indicators, periods, True)]
            tickers_weights.append(("SOXL", 0.5))
            return self.allocate(tickers_weights)
        
        if self.customAlgo.indicators["SPY"]["VolatilityQM_10"].temp_value > 2.5:
            temp_tickers = ["UVXY", "TMF", "SPXU"]
            used_indicators = ["RelativeStrengthIndexQM"]
            periods = [5]
            tickers_weights = [(ticker, value) for ticker, value in self.selection_helper(temp_tickers, used_indicators, periods, True)]
            return self.allocate(tickers_weights)
        
        if self.customAlgo.indicators["BIL"]["CumulativeReturnQM_100"].temp_value < self.customAlgo.indicators["TLT"]["CumulativeReturnQM_100"].temp_value:
            if self.customAlgo.indicators["TQQQ"]["CumulativeReturnQM_6"].temp_value < -8:
                if self.customAlgo.indicators["TQQQ"]["CumulativeReturnQM_1"].temp_value > 4:
                    self.allocate([("UVXY", 1)])
                else:
                    self.allocate([("FNGU", 1)])
            else:
                temp_tickers = ["TLT", "SVXY", "FNGU", "TECL"]
                used_indicators = ["RelativeStrengthIndexQM"]
                periods = [5]
                tickers_weights = [(ticker, 0.5 * value) for ticker, value in self.selection_helper(temp_tickers, used_indicators, periods, True)]
                tickers_weights.append(("FNGU", 0.5))
                return self.allocate(tickers_weights)
        else:
            if self.customAlgo.indicators["IEF"]["RelativeStrengthIndexQM_10"].temp_value > self.customAlgo.indicators["PSQ"]["RelativeStrengthIndexQM_20"].temp_value:
                temp_tickers = ["TLT", "SVXY", "FNGU", "TECL"]
                used_indicators = ["RelativeStrengthIndexQM"]
                periods = [5]
                tickers_weights = [(ticker, 0.5 * value) for ticker, value in self.selection_helper(temp_tickers, used_indicators, periods, True)]
                tickers_weights.append(("FNGU", 0.5))
                return self.allocate(tickers_weights)
            else:
                if self.customAlgo.indicators["SPY"]["tempBar"].close > self.customAlgo.indicators["SPY"]["MovingAverageQM_200"].temp_value:
                    temp_tickers = ["BTAL", "SPLV", "PDBC", "UGL"]
                    used_indicators = ["RelativeStrengthIndexQM"]
                    periods = [5]
                    tickers_weights = [(ticker, 0.5 * value) for ticker, value in self.selection_helper(temp_tickers, used_indicators, periods, True, 2)]
                    return self.allocate(tickers_weights)
                else:
                    if self.customAlgo.indicators["SPY"]["RelativeStrengthIndexQM_60"].temp_value > 50:
                        temp_tickers = ["TLT", "FNGD", "TECS"]
                        used_indicators = ["RelativeStrengthIndexQM"]
                        periods = [5]
                        tickers_weights = [(ticker, 0.5 * value) for ticker, value in self.selection_helper(temp_tickers, used_indicators, periods, True, 1)]
                        tickers_weights.append(("FNGD", 0.5))
                        return self.allocate(tickers_weights)
                    else:
                        if self.customAlgo.indicators["IEF"]["RelativeStrengthIndexQM_200"].temp_value < self.customAlgo.indicators["TLT"]["RelativeStrengthIndexQM_200"].temp_value:
                            temp_tickers = ["TMV", "SQQQ", "SOXS"]
                            used_indicators = ["RelativeStrengthIndexQM"]
                            periods = [5]
                            tickers_weights = [(ticker, 0.5 * value) for ticker, value in self.selection_helper(temp_tickers, used_indicators, periods, True, 1)]
                            tickers_weights.append(("SQQQ", 0.5))
                            return self.allocate(tickers_weights)
                        else:
                            temp_tickers = ["TLT", "SVXY", "FNGU", "TECL"]
                            used_indicators = ["RelativeStrengthIndexQM"]
                            periods = [5]
                            tickers_weights = [(ticker, 0.5 * value) for ticker, value in self.selection_helper(temp_tickers, used_indicators, periods, True, 1)]
                            tickers_weights.append(("FNGU", 0.5))
                            return self.allocate(tickers_weights)
        return []
                    
                
                
            
        
    
