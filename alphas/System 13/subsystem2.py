from AlgorithmImports import *
from QuantConnect.Algorithm import QCAlgorithm
from collections import defaultdict
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
        self.vixm_rsi10_window = RollingWindow[float](5)
        AlphaQM.__init__(self, customAlgo, (14, 4, 10, -10), symbols, indicators, True)
        
    def calculate(self):
        # Indicator and price declarations
        self.svix_price = self.customAlgo.indicators['SVIX']['tempBar'].close
        self.svix_rsi3 = self.customAlgo.indicators['SVIX']['RelativeStrengthIndexQM_3'].temp_value
        self.svxy_md2 = self.customAlgo.indicators['SVXY']['MaxDrawdownQM_2'].temp_value
        self.svxy_md3 = self.customAlgo.indicators['SVXY']['MaxDrawdownQM_3'].temp_value
        self.svxy_price = self.customAlgo.indicators['SVXY']['tempBar'].close
        self.tecl_price = self.customAlgo.indicators['TECL']['tempBar'].close
        self.tecl_rsi10 = self.customAlgo.indicators['TECL']['RelativeStrengthIndexQM_10'].temp_value
        self.tqqq_price = self.customAlgo.indicators['TQQQ']['tempBar'].close
        self.tqqq_rsi10 = self.customAlgo.indicators['TQQQ']['RelativeStrengthIndexQM_10'].temp_value
        self.udow_price = self.customAlgo.indicators['UDOW']['tempBar'].close
        self.udow_rsi10 = self.customAlgo.indicators['UDOW']['RelativeStrengthIndexQM_10'].temp_value
        self.upro_price = self.customAlgo.indicators['UPRO']['tempBar'].close
        self.upro_rsi10 = self.customAlgo.indicators['UPRO']['RelativeStrengthIndexQM_10'].temp_value
        self.vixm_price = self.customAlgo.indicators['VIXM']['tempBar'].close
        self.vixm_rsi10 = self.customAlgo.indicators['VIXM']['RelativeStrengthIndexQM_10'].temp_value
        self.vixm_rsi10_window.add(self.vixm_rsi10)

        # Volmageddon I
        if self.svxy_md2 > 10.0:
            return self.allocate([("SGOV", 1.0)])
        else:
            if self.svxy_md3 > 20.0:
                return self.allocate([("SGOV", 1.0)])
            else:
                mb_total_market = self.mb_total_market_conditions()
                return self.allocate(mb_total_market)
        
    def mb_total_market_conditions(self):
        conditions = [
            self.tqqq_rsi10 > 82.0, 
            self.tecl_rsi10 > 80.0, 
            self.upro_rsi10 > 78.0
        ]
        true_count = sum(conditions)

        if true_count == 3:
            short_high_beta_allocations = self.get_short_high_beta()
            return short_high_beta_allocations
        elif true_count == 2:
            short_high_beta_allocations = self.get_short_high_beta()
            bil_allocation = [("SGOV", 0.34)]
            # Adjust the weights accordingly
            combined_allocations = [(ticker, weight * 0.66) for ticker, weight in short_high_beta_allocations] 
            return combined_allocations + bil_allocation
        elif true_count == 1:
            short_high_beta_allocations = self.get_short_high_beta()
            bil_allocation = [("SGOV", 0.67)]
            # Adjust the weights accordingly
            combined_allocations = [(ticker, weight * 0.33) for ticker, weight in short_high_beta_allocations]
            return combined_allocations + bil_allocation
        else:
            conditions = [
                self.tqqq_rsi10 < 28.0, 
                self.tecl_rsi10 < 29.0, 
                self.udow_rsi10 < 24.0, 
                self.upro_rsi10 < 26.0
            ]
            true_count = sum(conditions)

            if true_count == 4:
                short_low_beta_allocations = self.get_long_high_beta()
                return short_low_beta_allocations
            elif true_count == 3:
                short_low_beta_allocations = self.get_long_high_beta()
                bil_allocation = [("SGOV", 0.25)]
                # Adjust the weights accordingly
                combined_allocations = [(ticker, weight * 0.75) for ticker, weight in short_low_beta_allocations] 
                return combined_allocations + bil_allocation
            elif true_count == 2:
                short_low_beta_allocations = self.get_long_high_beta()
                bil_allocation = [("SGOV", 0.5)]
                # Adjust the weights accordingly
                combined_allocations = [(ticker, weight * 0.5) for ticker, weight in short_low_beta_allocations] 
                return combined_allocations + bil_allocation
            elif true_count == 1:
                short_low_beta_allocations = self.get_long_high_beta()
                bil_allocation = [("SGOV", 0.75)]
                # Adjust the weights accordingly
                combined_allocations = [(ticker, weight * 0.25) for ticker, weight in short_low_beta_allocations] 
                return combined_allocations + bil_allocation
            else:
                vixm_rsi_condition = self.vixm_rsi10_window.is_ready and all(rsi > 70.0 for rsi in self.vixm_rsi10_window)
                if vixm_rsi_condition:
                    bsc_allocation = self.get_bsc_allocation()
                    return bsc_allocation
                else:
                    mb_total_market = self.mb_total_market()
                    return mb_total_market

    def mb_total_market(self):
        volatility_scale_in = self.volatility_scale_in()
        return volatility_scale_in
    
    def volatility_scale_in(self):
        # Base allocations
        base_allocations = {
            "SVIX": 0.55,
            "SPXS": 0.35
        }
        
        # Scale In portion (10%)
        scale_in_allocations = defaultdict(float)
        scale_in_weight = 0.10

        for i in range(1, 101):  # Check from 1% to 100%
            if self.svix_rsi3 < i:
                scale_in_allocations["SVIX"] += 0.01 * scale_in_weight  # Add 0.1% to SVIX
            else:
                scale_in_allocations["SPXS"] += 0.01 * scale_in_weight  # Add 0.1% to SPXS

        # Combine base allocations with scale-in allocations
        final_allocations = defaultdict(float)
        for ticker, base_weight in base_allocations.items():
            final_allocations[ticker] = base_weight + scale_in_allocations.get(ticker, 0)

        # Convert to list of tuples and return
        return [(ticker, weight) for ticker, weight in final_allocations.items()]


    def get_short_high_beta(self):
        uvxy_group = self.get_short_group(['TECS', 'SQQQ', 'SOXS', 'FNGD', 'UVXY'])
        no_uvxy_group = self.get_short_group(['TECS', 'SQQQ', 'SOXS', 'FNGD'])
        
        # Combine the two groups with equal weighting
        final_allocations = defaultdict(float)
        for group in [uvxy_group, no_uvxy_group]:
            for ticker, weight in group:
                final_allocations[ticker] += weight / 2  # Equal weight to each main group since we have 2 groups

        return list(final_allocations.items())
    
    def get_short_group(self, tickers):
        indicators = ['VolatilityQM', 'CumulativeReturnQM', 'RelativeStrengthIndexQM']
        periods = [5, 10, 15]
        
        period_allocations = []
        
        for period in periods:
            period_results = []
            for indicator in indicators:
                period_results.extend(self.selection_helper(tickers, [indicator], [period], mx=True, k_top=1))
            
            # Normalize weights within this period
            period_weights = defaultdict(float)
            for ticker, weight in period_results:
                period_weights[ticker] += weight
            
            total_weight = sum(period_weights.values())
            normalized_period_weights = [(ticker, weight / total_weight) for ticker, weight in period_weights.items()]
            
            period_allocations.append(normalized_period_weights)
        
        # Combine allocations from all periods with equal weight
        final_allocations = defaultdict(float)
        for period_alloc in period_allocations:
            for ticker, weight in period_alloc:
                final_allocations[ticker] += weight / len(periods)
        
        return list(final_allocations.items())

    def get_long_high_beta(self):
        svxy_group = self.get_long_group(['TECL', 'TQQQ', 'FNGU', 'SOXL', 'SVXY'])
        no_svxy_group = self.get_long_group(['TECL', 'TQQQ', 'FNGU', 'SOXL'])
        
        # Combine the two groups with equal weighting
        final_allocations = defaultdict(float)
        for group in [svxy_group, no_svxy_group]:
            for ticker, weight in group:
                final_allocations[ticker] += weight / 2  # Equal weight to each main group since we have 2 groups

        return list(final_allocations.items())

    def get_long_group(self, tickers):
        indicators = ['VolatilityQM', 'CumulativeReturnQM', 'RelativeStrengthIndexQM']
        periods = [5, 10, 15]
        
        period_allocations = []
        
        for period in periods:
            period_results = []
            for indicator in indicators:
                period_results.extend(self.selection_helper(tickers, [indicator], [period], mx=False, k_top=1))
            
            # Normalize weights within this period
            period_weights = defaultdict(float)
            for ticker, weight in period_results:
                period_weights[ticker] += weight
            
            total_weight = sum(period_weights.values())
            normalized_period_weights = [(ticker, weight / total_weight) for ticker, weight in period_weights.items()]
            
            period_allocations.append(normalized_period_weights)
        
        # Combine allocations from all periods with equal weight
        final_allocations = defaultdict(float)
        for period_alloc in period_allocations:
            for ticker, weight in period_alloc:
                final_allocations[ticker] += weight / len(periods)
        
        return list(final_allocations.items())

    def get_bsc_allocation(self):
        return [("VIXM", 0.5), ("UUP", 0.5)]