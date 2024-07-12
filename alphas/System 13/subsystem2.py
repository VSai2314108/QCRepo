from AlgorithmImports import *
from QuantConnect.Algorithm import QCAlgorithm
from QuantConnect.Algorithm.Framework.Alphas import Insight
from QuantConnect.Data import Slice

from AlphaQM import AlphaQM
from utils.indicators.RelativeStrengthIndexQM import RelativeStrengthIndexQM
from utils.indicators.MaxDrawdownQM import MaxDrawdownQM  
from utils.indicators.VolatilityQM import VolatilityQM
from utils.indicators.CumulativeReturnQM import CumulativeReturnQM

class VolatilityScaleIn(AlphaQM):
    def __init__(self, customAlgo: QCAlgorithm) -> None:
        symbols = ['TECS', 'SQQQ', 'SOXS', 'FNGD', 'UVXY', 'TECL', 'TQQQ', 'FNGU', 'SOXL', 'SVXY', 'SGOV', 'VIXM', 'UUP', 'SPXS', 'SPXL', 'UDOW', 'SVIX', 'UPRO', 'SPY']
        
        indicators = [
            (MaxDrawdownQM, 2), (MaxDrawdownQM, 3),  
            (RelativeStrengthIndexQM, 3), (RelativeStrengthIndexQM, 5), (RelativeStrengthIndexQM, 10), (RelativeStrengthIndexQM, 15),
            (VolatilityQM, 5), (VolatilityQM, 10), (VolatilityQM, 15),
            (CumulativeReturnQM, 5), (CumulativeReturnQM, 10), (CumulativeReturnQM, 15)  
        ]
        
        AlphaQM.__init__(self, customAlgo, (14, 4, 10, -10), symbols, indicators, True)
        
    def calculate(self):
        # Volmageddon I
        if self.customAlgo.indicators["SVXY"]["MaxDrawdownQM_2"].temp_value > 10.0:
            return self.allocate([("SGOV", 1.0)])
        
        # Volmageddon II  
        if self.customAlgo.indicators["SVXY"]["MaxDrawdownQM_3"].temp_value > 20.0:
            return self.allocate([("SGOV", 1.0)])
        
        # Dip Buy
        if (self.customAlgo.indicators["TQQQ"]["RelativeStrengthIndexQM_10"].temp_value < 28.0 and
            self.customAlgo.indicators["TECL"]["RelativeStrengthIndexQM_10"].temp_value < 29.0 and 
            self.customAlgo.indicators["UDOW"]["RelativeStrengthIndexQM_10"].temp_value < 24.0 and
            self.customAlgo.indicators["UPRO"]["RelativeStrengthIndexQM_10"].temp_value < 26.0):
            
            return self.allocate_long_portfolio("100/0")
        
        # MB Total Market
        return self.mb_total_market()
    
    def allocate_long_portfolio(self, ratio):
        weights = self.get_weights(ratio)

        svxy_rsi = self.customAlgo.indicators["SVIX"]["RelativeStrengthIndexQM_3"].temp_value

        if svxy_rsi <= 1.0:
            long_tickers = self.selection_helper(['TECL', 'TQQQ', 'FNGU', 'SOXL', 'SVXY'], ["VolatilityQM", "CumulativeReturnQM", "RelativeStrengthIndexQM"], [5, 10, 15], mx=True, k_top=1)[0][0]
        else:
            long_tickers = self.selection_helper(['TECL', 'TQQQ', 'SOXL', 'FNGU'], ["VolatilityQM", "CumulativeReturnQM", "RelativeStrengthIndexQM"], [5, 10, 15], mx=True, k_top=1)[0][0]

        return self.allocate([(long_tickers, weights[0]), ("SGOV", weights[1])])

    def get_weights(self, ratio):
        weights = ratio.split('/')
        return [float(weights[0])/100, float(weights[1])/100]
    
    def mb_total_market(self):
        vixm_rsi = self.customAlgo.indicators["VIXM"]["RelativeStrengthIndexQM_10"].temp_value
        
        if vixm_rsi > 70.0:
            last_5_values = self.customAlgo.indicators["VIXM"]["RelativeStrengthIndexQM_10"].values[-5:]
            if len(last_5_values) == 5 and all(value > 70 for value in last_5_values):  
                return self.allocate([("VIXM", 0.5), ("UUP", 0.5)])
        
        return self.volatility_scale_in()
    
    def volatility_scale_in(self):
        svix_rsi = self.customAlgo.indicators["SVIX"]["RelativeStrengthIndexQM_3"].temp_value
        
        if svix_rsi <= 100:
            weights = [0.55, 0.35, 0.10]
            allocations = []
            
            for i in range(1, 101):
                if svix_rsi <= i:
                    allocations.append(("SVIX", weights[0]))
                    break
            
            if not allocations:
                allocations.append(("SPXS", weights[0]))
            
            allocations.extend([("SPXS", weights[1]), ("SGOV", weights[2])])
            
            return self.allocate(allocations)
        else:
            return self.allocate([("SPXS", 1.0)])