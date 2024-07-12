from AlgorithmImports import *
from QuantConnect.Algorithm import QCAlgorithm
from QuantConnect.Algorithm.Framework.Alphas import Insight
from QuantConnect.Data import Slice

from AlphaQM import AlphaQM
from utils.indicators.RelativeStrengthIndexQM import RelativeStrengthIndexQM
from utils.indicators.MaxDrawdownQM import MaxDrawdownQM
from utils.indicators.VolatilityQM import VolatilityQM
from utils.indicators.CumulativeReturnQM import CumulativeReturnQM

class GoldenRotator(AlphaQM):
    def __init__(self, customAlgo: QCAlgorithm, slope_params=(14, 4, 10, -10)) -> None:
        symbols = [
            "SPY", "BTAL", "FNGD", "FNGU", "PDBC", "SGOV", "SOXL", "SOXS", "SPLV", "SPXU",
            "SQQQ", "SVXY", "TECL", "TECS", "TLT", "TMV", "TQQQ", "UQL", "UUP", "UVXY",
            "VIXM", "UPRO", "UDOW", "GLD"
        ]
        indicators = [
            (MaxDrawdownQM, 2), (MaxDrawdownQM, 3),
            (VolatilityQM, 5), (CumulativeReturnQM, 5), (RelativeStrengthIndexQM, 5),
            (VolatilityQM, 10), (CumulativeReturnQM, 10), (RelativeStrengthIndexQM, 10),
            (VolatilityQM, 15), (CumulativeReturnQM, 15), (RelativeStrengthIndexQM, 15)
        ]
        AlphaQM.__init__(self, customAlgo, slope_params, symbols, indicators)

    def calculate(self):
        # Volmageddon I check
        if self.customAlgo.indicators["SVXY"]["MaxDrawdownQM_2"].temp_value > 10:
            return self.allocate([("SGOV", 1)])

        # Volmageddon II check 
        if self.customAlgo.indicators["SVXY"]["MaxDrawdownQM_3"].temp_value > 20:
            return self.allocate([("SGOV", 1)])

        # Short conditions
        short_rsi_tqqq = self.customAlgo.indicators["TQQQ"]["RelativeStrengthIndexQM_10"].temp_value > 82
        short_rsi_tecl = self.customAlgo.indicators["TECL"]["RelativeStrengthIndexQM_10"].temp_value > 80
        short_rsi_upro = self.customAlgo.indicators["UPRO"]["RelativeStrengthIndexQM_10"].temp_value > 78

        if any([short_rsi_tqqq, short_rsi_tecl, short_rsi_upro]):
            weight = sum([short_rsi_tqqq, short_rsi_tecl, short_rsi_upro]) / 3
            return self.short_allocation(weight)

        # Long conditions 
        long_rsi_tqqq = self.customAlgo.indicators["TQQQ"]["RelativeStrengthIndexQM_10"].temp_value < 28
        long_rsi_tecl = self.customAlgo.indicators["TECL"]["RelativeStrengthIndexQM_10"].temp_value < 29
        long_rsi_udow = self.customAlgo.indicators["UDOW"]["RelativeStrengthIndexQM_10"].temp_value < 24
        long_rsi_upro = self.customAlgo.indicators["UPRO"]["RelativeStrengthIndexQM_10"].temp_value < 26

        if any([long_rsi_tqqq, long_rsi_tecl, long_rsi_udow, long_rsi_upro]):
            weight = sum([long_rsi_tqqq, long_rsi_tecl, long_rsi_udow, long_rsi_upro]) / 4
            return self.long_allocation(weight)

        # Dip Buy scenario
        vixm_rsi = self.customAlgo.indicators["VIXM"]["RelativeStrengthIndexQM_10"].temp_value
        if vixm_rsi > 70:
            last_5_values = self.customAlgo.indicators["VIXM"]["RelativeStrengthIndexQM_10"].values[-5:]
            if len(last_5_values) == 5 and all(value > 70 for value in last_5_values):
                return self.allocate([("VIXM", 0.5), ("UUP", 0.5)])

        # Golden Rotator (default scenario)
        return self.golden_rotator_allocation()

    def short_allocation(self, weight):
        tickers = ["TECS", "SQQQ", "SOXS", "FNGD", "UVXY"]
        allocation = self.calculate_allocation(tickers, weight)
        allocation.append(("SGOV", 1 - weight))
        return self.allocate(allocation)

    def long_allocation(self, weight):
        tickers = ["TECL", "TQQQ", "FNGU", "SOXL", "SVXY"] 
        allocation = self.calculate_allocation(tickers, weight)
        allocation.append(("SGOV", 1 - weight))
        return self.allocate(allocation)

    def golden_rotator_allocation(self):
        tickers = ["SVXY", "VIXM", "GLD", "GLD"] 
        return self.allocate(self.calculate_allocation(tickers, 1, k_top=3))

    def calculate_allocation(self, tickers, weight, k_top=1):
        indicators = ["VolatilityQM", "CumulativeReturnQM", "RelativeStrengthIndexQM"]
        periods = [5, 10, 15]
        selected_tickers = []

        for indicator in indicators:
            for period in periods:
                key = f"{indicator}_{period}"
                sorted_tickers = sorted(
                    tickers,
                    key=lambda ticker: self.customAlgo.indicators[ticker][key].temp_value, 
                    reverse=True
                )
                selected_tickers.extend(sorted_tickers[:k_top])

        ticker_counts = {}
        for ticker in selected_tickers:
            ticker_counts[ticker] = ticker_counts.get(ticker, 0) + 1

        total_count = sum(ticker_counts.values())
        return [(ticker, (count / total_count) * weight) for ticker, count in ticker_counts.items()]