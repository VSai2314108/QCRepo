from AlgorithmImports import *
from AlphaQM import AlphaQM
from utils.indicators.RelativeStrengthIndexQM import RelativeStrengthIndexQM
from utils.indicators.CumulativeReturnQM import CumulativeReturnQM
from utils.indicators.MovingAverageQM import MovingAverageQM
from utils.indicators.VolatilityQM import VolatilityQM

class PoppedHnL(AlphaQM):
    def __init__(self, customAlgo: QCAlgorithm) -> None:
        symbols = [
            "SPY", "SPXL", "TQQQ", "SOXL", "UVXY", "TLT", "TMF", "UPRO", "TMV", "MOAT", 
            "USMV", "CURE", "BIL", "PHDG"
        ]
        indicators = [
            (RelativeStrengthIndexQM, 10),
            (CumulativeReturnQM, 5),
            (CumulativeReturnQM, 30),
            (MovingAverageQM, 23),
            (VolatilityQM, 20),
            (MovingAverageQM, 150),
        ]
        AlphaQM.__init__(self, customAlgo, (14, 4, 10, -10), symbols, indicators, True)

    def calculate(self):
        allocations = []
        
        # SPY Pop Bot
        allocations.extend(self.pop_bot("SPXL"))
        
        # QQQ Pop Bot
        allocations.extend(self.pop_bot("TQQQ"))
        
        # SMH Pop Bot
        allocations.extend(self.pop_bot("SOXL"))
        
        # Combine allocations and normalize weights
        combined_allocations = self.combine_allocations(allocations)
        
        return self.allocate(combined_allocations)

    def pop_bot(self, ticker):
        rsi = self.customAlgo.indicators[ticker]["RelativeStrengthIndexQM_10"].temp_value
        
        if rsi > 80:
            return [("UVXY", 1/3)]
        elif rsi < 30:
            return [(ticker, 1/3)]
        else:
            return self.hnl_stocks_and_bonds()

    def hnl_stocks_and_bonds(self):
        tlt_price = self.customAlgo.indicators["TLT"]["tempBar"].close
        tlt_ma150 = self.customAlgo.indicators["TLT"]["MovingAverageQM_150"].temp_value
        tlt_ma23 = self.customAlgo.indicators["TLT"]["MovingAverageQM_23"].temp_value

        if tlt_price > tlt_ma150:
            return self.inverse_volatility_allocation(["CURE", "TQQQ", "TMF", "PHDG"], [2, 2, 2, 1])
        elif tlt_price < tlt_ma23:
            top_performers = self.selection_helper(["TMV", "CURE", "BIL"], ["CumulativeReturnQM"], [5], mx=True, k_top=2)
            return [(ticker, 1/6) for ticker, _ in top_performers]
        else:
            top_performer = self.selection_helper(["TMF", "UPRO", "TMV", "MOAT", "USMV"], ["CumulativeReturnQM"], [30], mx=True, k_top=1)
            return [(top_performer[0][0], 1/3)]

    def inverse_volatility_allocation(self, tickers, weights):
        volatilities = [self.customAlgo.indicators[ticker]["VolatilityQM_20"].temp_value for ticker in tickers]
        inv_volatilities = [1/vol if vol != 0 else 0 for vol in volatilities]
        total_inv_vol = sum(inv_volatilities)
        
        allocations = []
        for ticker, weight, inv_vol in zip(tickers, weights, inv_volatilities):
            if total_inv_vol != 0:
                allocations.append((ticker, (inv_vol / total_inv_vol) * (weight / sum(weights)) / 3))
        
        return allocations

    def combine_allocations(self, allocations):
        combined = {}
        for alloc in allocations:
            ticker, weight = alloc
            if ticker in combined:
                combined[ticker] += weight
            else:
                combined[ticker] = weight
        
        total_weight = sum(combined.values())
        return [(ticker, weight / total_weight) for ticker, weight in combined.items()]