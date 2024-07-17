from AlgorithmImports import *
from QuantConnect.Algorithm import QCAlgorithm
from AlphaQM import AlphaQM
from utils.indicators.RelativeStrengthIndexQM import RelativeStrengthIndexQM
from utils.indicators.MaxDrawdownQM import MaxDrawdownQM
from utils.indicators.CumulativeReturnQM import CumulativeReturnQM
from utils.indicators.MovingAverageQM import MovingAverageQM
from utils.indicators.VolatilityQM import VolatilityQM
from datetime import datetime
from collections import defaultdict

class BullOrHedge(AlphaQM):
    def __init__(self, customAlgo: QCAlgorithm) -> None:
        
        # Symbols
        symbols = [
            'BIL',
            'BND',
            'BTAL',
            'GLD',
            'IEF',
            'PSQ',
            'QQQ',
            'SHV',
            'SHY',
            'SOXL',
            'SOXS',
            'SPY',
            'SQQQ',
            'SVXY',
            'TECL',
            'TECS',
            'TLT',
            'TMF',
            'TMV',
            'TQQQ',
            'UPRO',
            'UVXY',
            'VIXM',
            'VIXY',
            'XLP',
        ]

        # Indicators
        indicators = [
            (CumulativeReturnQM, 1),
            (CumulativeReturnQM, 6),
            (CumulativeReturnQM, 60),
            (CumulativeReturnQM, 100),
            (MaxDrawdownQM, 2),
            (MaxDrawdownQM, 3),
            (MaxDrawdownQM, 10),
            (MaxDrawdownQM, 60),
            (MovingAverageQM, 10),
            (MovingAverageQM, 25),
            (MovingAverageQM, 40),
            (MovingAverageQM, 100),
            (MovingAverageQM, 200),
            (RelativeStrengthIndexQM, 5),
            (RelativeStrengthIndexQM, 10),
            (RelativeStrengthIndexQM, 20),
            (RelativeStrengthIndexQM, 45),
            (RelativeStrengthIndexQM, 60),
            (RelativeStrengthIndexQM, 200),
            (VolatilityQM, 2),
            (VolatilityQM, 3),
            (VolatilityQM, 5),
            (VolatilityQM, 10),
            (VolatilityQM, 21),
            (VolatilityQM, 40),
            (VolatilityQM, 45),
        ]

        self.vixm_rsi10_window = RollingWindow[float](5)
        self.tmf_md60_window = RollingWindow[float](10)
        self.tmv_ma10_window = RollingWindow[float](10)
        self.tmv_ma40_window = RollingWindow[float](10)
        self.tmv_ma100_window = RollingWindow[float](10)
        self.tmv_price_window = RollingWindow[float](10)
        AlphaQM.__init__(self, customAlgo, (14, 4, 10, -10), symbols, indicators, True)

    def calculate(self):
        import re
        for symbol in self.symbols:
            # Assign price for each symbol
            exec(f"self.{symbol.lower()}_price = self.customAlgo.indicators['{symbol}']['tempBar'].close")
            for indicator_name, indicator_obj in self.customAlgo.indicators[symbol].items():
                if indicator_name != 'tempBar':
                    abbr = ''.join(word[0].lower() for word in re.findall(r'[A-Z][^A-Z]*', indicator_name.split('_')[0]))
                    window = indicator_name.split('_')[-1]
                    var_name = f"{symbol.lower()}_{abbr[:-2]}{window}"
                    try:
                        exec(f"self.{var_name} = self.customAlgo.indicators['{symbol}']['{indicator_name}'].temp_value")
                    except:
                        pass
        
        self.tmf_md60_window.add(self.tmf_md60)
        self.vixm_rsi10_window.add(self.vixm_rsi10)
        self.tmv_price_window.add(self.tmv_price)
        self.tmv_ma10_window.add(self.tmv_ma10)
        self.tmv_ma40_window.add(self.tmv_ma40)
        self.tmv_ma100_window.add(self.tmv_ma100)

        # Uncorrelated Bonds
        current_month = datetime.now().month


        # Check if it's November or December
        if current_month in [11, 12]:
            return self.allocate([("SPY", 0.6), ("IEF", 0.4)])
        else:
            # Bonds Exciting condition
            if self.tmv_ma10_window.is_ready and self.tmv_ma40_window.is_ready:
                tmv_ma10_ma40_condition = True
                for i in range(10):
                    tmv_ma10 = self.tmv_ma10_window[i]
                    tmv_ma40 = self.tmv_ma40_window[i]
                    if not tmv_ma10 > tmv_ma40:
                        tmv_ma10_ma40_condition = False
                        break
            else:
                tmv_ma10_ma40_condition = False

            if self.tmv_price_window.is_ready and self.tmv_ma100_window.is_ready:
                tmv_price_ma100_condition = True
                for i in range(10):
                    tmv_price = self.tmv_price_window[i]
                    tmv_ma100 = self.tmv_ma100_window[i]
                    if not tmv_price > tmv_ma100:
                        tmv_price_ma100_condition = False
                        break
            else:
                tmv_price_ma100_condition = False

            if tmv_ma10_ma40_condition and tmv_price_ma100_condition:
                return self.allocate([("TMV", 1)])
            else:
                return self.only_bulls()

    def only_bulls(self):
        if self.svxy_md2 > 10.0:
            return self.allocate([("BIL", 1)])
        else:
            return self.volmageddon_ii()

    def volmageddon_ii(self):
        if self.svxy_md3 > 20.0:
            return self.allocate([("BIL", 1)])
        else:
            return self.handle_overbought_condition()

    def handle_overbought_condition(self):
        conditions = [
            self.tqqq_rsi10 > 82.0, 
            self.tecl_rsi10 > 80.0, 
            self.upro_rsi10 > 78.0
        ]
        true_count = sum(conditions)

        if true_count == 3:
            short_high_beta_allocations = self.get_short_high_beta()
            return self.allocate(short_high_beta_allocations)
        elif true_count == 2:
            short_high_beta_allocations = self.get_short_high_beta()
            bil_allocation = [("BIL", 0.34)]
            # Adjust the weights accordingly
            combined_allocations = [(ticker, weight * 0.66) for ticker, weight in short_high_beta_allocations] 
            return self.allocate(combined_allocations + bil_allocation)
        elif true_count == 1:
            short_high_beta_allocations = self.get_short_high_beta()
            bil_allocation = [("BIL", 0.67)]
            # Adjust the weights accordingly
            combined_allocations = [(ticker, weight * 0.33) for ticker, weight in short_high_beta_allocations]
            return self.allocate(combined_allocations + bil_allocation)
        else:
            bsc_allocation = self.handle_bsc_condition()
            no_bsc_allocation = self.handle_no_bsc_condition()
            
            # Combine BSC and no-BSC allocations with appropriate weights
            combined_allocations = defaultdict(float)
            for ticker, weight in bsc_allocation:
                combined_allocations[ticker] += weight * 0.5  # 50% weight to BSC
            for ticker, weight in no_bsc_allocation:
                combined_allocations[ticker] += weight * 0.5  # 50% weight to no-BSC
            
            return self.allocate(list(combined_allocations.items()))

    def get_bsc_allocation(self):
        return [("VIXM", 0.5), ("UUP", 0.5)]

    def handle_bsc_condition(self):
        vixm_rsi_condition = self.vixm_rsi10_window.is_ready and all(rsi > 70.0 for rsi in self.vixm_rsi10_window)
        conditions = [
            vixm_rsi_condition,
            self.qqq_v10 > 3.0, 
            self.spy_v5 > 2.5
        ]
        true_count = sum(conditions)

        if true_count == 3:
            bsc_allocation = self.get_bsc_allocation()
            return bsc_allocation
        elif true_count == 2:
            bsc_allocation = self.get_bsc_allocation()
            bil_allocation = [("BIL", 0.34)]
            # Adjust the weights accordingly
            combined_allocations = [(ticker, weight * 0.66) for ticker, weight in bsc_allocation] 
            return combined_allocations + bil_allocation
        elif true_count == 1:
            bsc_allocation = self.get_bsc_allocation()
            bil_allocation = [("BIL", 0.67)]
            # Adjust the weights accordingly
            combined_allocations = [(ticker, weight * 0.33) for ticker, weight in bsc_allocation]
            return combined_allocations + bil_allocation
        else:
            no_bsc_allocation = self.handle_no_bsc_condition()
            return no_bsc_allocation

    def get_short_high_beta(self):
        uvxy_group = self.get_short_group(['TECS', 'SQQQ', 'SQQQ', 'SOXS', 'UVXY'])
        no_uvxy_group = self.get_short_group(['TECS', 'SQQQ', 'SQQQ', 'SOXS'])
        
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

    def inverse_vatility_weighted(self, tickers, window):
        volatilities = [1 / self.customAlgo.indicators[ticker][f"VolatilityQM_{window}"].temp_value for ticker in tickers]
        total = sum(volatilities)
        return [(ticker, vol / total) for ticker, vol in zip(tickers, volatilities)]

    def handle_no_bsc_condition(self):
        strategies = [
            self.get_nbdb_allocation(),
            self.get_bsmr_allocation(),
            self.get_babI_allocation(),
            self.get_babII_allocation(),
            self.get_wmdyn_allocation(),
            self.get_tqqq_strategy_allocation(),
            self.get_tecl_rsi_strategy_allocation(),
            self.get_soxl_rsi_strategy_allocation(),
            self.get_svxy_rsi_strategy_allocation(),
            self.get_upro_rsi_strategy_allocation()
        ]

        # Combine all allocations with equal weighting
        final_allocations = defaultdict(float)
        for strategy in strategies:
            for ticker, weight in strategy:
                final_allocations[ticker] += weight / len(strategies)

        return list(final_allocations.items())

    def get_nbdb_allocation(self):
        if self.tlt_md10 > 10.0:
            return [("SHV", 1)]
        else:
            return self.inverse_vatility_weighted(["SHV", "TQQQ"], 45)
        
    def get_bsmr_allocation(self):
        if self.tqqq_rsi10 > 79.0:
            return [("UVXY", 1)]
        else:
            if self.tqqq_cr6 < -12.0:
                if self.tqqq_cr1 > 5.5:
                    return [("UVXY", 1)]
                else:
                    if self.tqqq_rsi10 < 32.0:
                        return [("TQQQ", 1)]
                    else:
                        if self.tmf_md10 < 7.0:
                            return [("TQQQ", 1)]
                        else:
                            return [("SHV", 1)]
            else:
                if self.qqq_md10 > 10.0:
                    return [("SHV", 1)]
                else:
                    if self.tmf_md10 > 10.0:
                        return [("SHV", 1)]
                    else:
                        if self.qqq_price > self.qqq_ma25:
                            return [("TQQQ", 1)]
                        else:
                            if self.spy_rsi60 > 50.0:
                                if self.bnd_rsi45 > self.spy_rsi45:
                                    return [("TQQQ", 1)]
                                else:
                                    return [("SHV", 1)]
                            else:
                                if self.ief_rsi200 > self.tlt_rsi200:
                                    if self.bnd_rsi45 > self.spy_rsi45:
                                        return [("TQQQ", 1)]
                                    else:
                                        return [("SHV", 1)]
                                else:
                                    return [("SHV", 1)]
    
    def get_babI_allocation(self):
        if self.qqq_rsi10 > 80.0:
            return [("UVXY", 0.5), ("BTAL", 0.5)]
        else:
            if self.vixy_v40 < 5.0:
                if self.bnd_cr60 > self.bil_cr60:
                    return [("TQQQ", 1)]
                else:
                    return [("SVXY", 0.55), ("BTAL", 0.45)]
            else:
                return [("SHY", 0.2), ("SPY", 0.2), ("BTAL", 0.2), ("GLD", 0.2), ("XLP", 0.2)]
    
    def get_babII_allocation(self):
        if self.svxy_v2 > 10.0:
            return [("SHV", 1)]
        else:
            if self.svxy_v3 > 20.0:
                return [("SHV", 1)]
            else:
                if self.qqq_rsi10 > 80:
                    return [("UVXY", 0.5), ("BTAL", 0.5)]
                else:
                    if self.spy_v21 < 1.25:
                        if self.bnd_cr60 > self.bil_cr60:
                            return [("TQQQ", 1)]
                        else:
                            return [("SVXY", 0.55), ("BTAL", 0.45)]
                    else:
                        return [("SHY", 0.2), ("SPY", 0.2), ("BTAL", 0.2), ("GLD", 0.2), ("XLP", 0.2)]
    
    def get_wmdyn_allocation(self):
        if self.spy_rsi5 < 25.0:
            selectionResult = self.selection_helper(["TLT", "SVXY", "SOXL", "TECL"], ['RelativeStrengthIndexQM'], [5], mx=True, k_top=1)
            return [("SOXL", 0.5)] + [(selectionResult[0][0], 0.5)]
        else:
            if self.spy_v10 > 2.5:
                return [("SHV", 1)]
            else:
                if self.bil_cr100 < self.tlt_cr100:
                    selectionResult = self.selection_helper(["TLT", "SVXY", "SOXL", "TECL"], ['RelativeStrengthIndexQM'], [5], mx=True, k_top=1)
                    return [("SOXL", 0.5)] + [(selectionResult[0][0], 0.5)]
                else:
                    if self.ief_rsi10 > self.psq_rsi20:
                        selectionResult = self.selection_helper(["TLT", "SVXY", "SOXL", "TECL"], ['RelativeStrengthIndexQM'], [5], mx=True, k_top=1)
                        return [("SOXL", 0.5)] + [(selectionResult[0][0], 0.5)]
                    else:
                        if self.spy_rsi60 > 50.0:
                            return [("SHV", 1)]
                        else:
                            if self.ief_rsi200 < self.tlt_rsi200:
                                return [("SHV", 1)]
                            else:
                                selectionResult = self.selection_helper(["TLT", "SVXY", "SOXL", "TECL"], ['RelativeStrengthIndexQM'], [5], mx=True, k_top=1)
                                return [("SOXL", 0.5)] + [(selectionResult[0][0], 0.5)]
                            
    def get_tqqq_strategy_allocation(self):
        if self.tqqq_price > self.tqqq_ma200:
            if self.tqqq_rsi10 < 49.0:
                if self.tqqq_cr1 < -2.0:
                    return [("SHV", 1)]
                else:
                    if self.tqqq_cr1 > 8.5:
                        if self.tecl_rsi10 < 31.0:
                            return [("TQQQ", 1)]
                        else:
                            return [("SHV", 1)]
                    return [("TQQQ", 1)]
            else:
                if self.qqq_rsi10 > 80.0:
                    return [("UVXY", 1)]
                else:
                    return [("SHV", 1)]
        else:
            if self.tqqq_cr1 < -6.0:
                if self.tqqq_rsi10 < 31.0:
                    return [("TQQQ", 1)]
                else:
                    return [("SHV", 1)]
            else:
                return [("SHV", 1)]
    
    def get_tecl_rsi_strategy_allocation(self):
        if self.tecl_price > self.tecl_ma200:
            if self.tecl_rsi10 < 49.0:
                if self.tecl_cr1 < -2.0: 
                    return [("SHV", 1)]
                else:
                    if self.tecl_cr1 > 8.5:
                        if self.tecl_rsi10 < 31.0:
                            return [("TECL", 1)]
                        else:
                            return [("SHV", 1)]
                    return [("TECL", 1)]
            else:
                if self.tecl_rsi10 > 82.0:
                    return [("SHV", 1)]
                else:
                    return [("SHV", 1)]
        if self.tecl_rsi10 < 31.0:
            if self.tecl_cr1 < -6.0:
                return [("TECL", 1)]
            else:
                return [("TECL", 1)]
        else:
            return [("SHV", 1)]
        
    def get_soxl_rsi_strategy_allocation(self):
        if self.soxl_price > self.soxl_ma200:
            if self.soxl_rsi10 < 49.0:
                if self.soxl_cr1 < -2.0:
                    return [("SHV", 1)]
                else:
                    if self.soxl_cr1 > 8.5:
                        if self.soxl_rsi10 < 31.0:
                            return [("SOXL", 1)]
                        else:
                            return [("SHV", 1)]
                    return [("SOXL", 1)]
            else:
                if self.soxl_rsi10 > 82.0:
                    return [("SHV", 1)]
                else:
                    return [("SHV", 1)]
        if self.soxl_rsi10 < 31.0:
            if self.soxl_cr1 < -6.0:
                return [("SOXL", 1)]
            else:
                return [("SOXL", 1)]
        else:
            return [("SHV", 1)]

    def get_svxy_rsi_strategy_allocation(self):
        if self.tqqq_cr6 < 0.0:
            if self.tqqq_cr1 > 5.0:
                return [("SHV", 1)]
            else:
                if self.svxy_price > self.svxy_ma200:
                    if self.svxy_rsi10 < 49.0:
                        if self.svxy_cr1 < -2.0:
                            return [("SHV", 1)]
                        else:
                            if self.svxy_cr1 > 8.5:
                                if self.svxy_rsi10 < 31.0:
                                    return [("SVXY", 1)]
                                else:
                                    return [("SHV", 1)]
                            return [("SVXY", 1)]
                    else:
                        if self.svxy_rsi10 > 82.0:
                            return [("VIXM", 1)]
                        else:
                            return [("SHV", 1)]
                else:
                    if self.svxy_rsi10 < 31.0:
                        if self.svxy_cr1 < -6.0:
                            return [("SVXY", 1)]
                        else:
                            return [("SVXY", 1)]
                    else:
                        return [("SHV", 1)]
        else:
            return [("SHV", 1)]
   
    def get_upro_rsi_strategy_allocation(self):
        if self.upro_price > self.upro_ma200:
            if self.upro_rsi10 < 49.0:
                if self.upro_cr1 < -2.0:
                    return [("SHV", 1)]
                else:
                    if self.upro_cr1 > 8.5:
                        if self.upro_rsi10 < 31.0:
                            return [("UPRO", 1)]
                        else:
                            return [("SHV", 1)]
                    return [("UPRO", 1)]
            else:
                if self.upro_rsi10 > 82.0:
                    return [("SHV", 1)]
                else:
                    return [("SHV", 1)]
        if self.upro_rsi10 < 31.0:
            if self.upro_cr1 < -6.0:
                return [("UPRO", 1)]
            else:
                return [("UPRO", 1)]
        else:
            return [("SHV", 1)]



