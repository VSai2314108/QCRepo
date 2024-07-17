from AlgorithmImports import *
from QuantConnect.Algorithm import QCAlgorithm
from AlphaQM import AlphaQM
from utils.indicators.RelativeStrengthIndexQM import RelativeStrengthIndexQM
from utils.indicators.MaxDrawdownQM import MaxDrawdownQM
from utils.indicators.CumulativeReturnQM import CumulativeReturnQM
from utils.indicators.MovingAverageQM import MovingAverageQM
from utils.indicators.VolatilityQM import VolatilityQM
from collections import defaultdict

class HedgedTrinityPop(AlphaQM):
    def __init__(self, customAlgo: QCAlgorithm) -> None:
        symbols = [
            "SPY", "SPXL", "TQQQ", "CURE", "SOXL", "UVXY", "VIXM", "SVXY", "SQQQ", "UUP", "DBC", "BIL", "TLT", "TMF", "UGL", "PDBC", "TMV", "USDU", "UTSL"
        ]
        # Indicators
        indicators = [
            (CumulativeReturnQM, 1),
            (CumulativeReturnQM, 6),
            (CumulativeReturnQM, 60),
            (CumulativeReturnQM, 100),
            (CumulativeReturnQM, 200),
            (CumulativeReturnQM, 300),
            (CumulativeReturnQM, 400),
            (CumulativeReturnQM, 500),
            (CumulativeReturnQM, 600),
            (MaxDrawdownQM, 2),
            (MaxDrawdownQM, 3),
            (MaxDrawdownQM, 10),
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
            (VolatilityQM, 20),
            (VolatilityQM, 21),
            (VolatilityQM, 40),
            (VolatilityQM, 45),
        ]
        AlphaQM.__init__(self, customAlgo, (14, 1, 5, -5), symbols, indicators, True)

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
                    
        if self.vixm_rsi10 > 70:
            # v2.1.0 Pop Bots l Oct 28th 2011
            spy_pop_bot = self.spy_pop_bot()
            qqq_pop_bot = self.qqq_pop_bot()
            smh_pop_bot = self.smh_pop_bot()
            
            # Combine the pop bots with equal weights
            combined_pop_bots = []
            for allocation in [spy_pop_bot, qqq_pop_bot, smh_pop_bot]:
                combined_pop_bots.extend([(ticker, weight * (1/3)) for ticker, weight in allocation])
            
            # Combine allocations for the same ticker
            final_allocations = defaultdict(float)
            for ticker, weight in combined_pop_bots:
                final_allocations[ticker] += weight
            
            return self.allocate(list(final_allocations.items()))
        else:
            # Trinity Pop l BrianE l Jun 2nd 2017 (17% DD)
            spy_pop_bot_BrianE = self.spy_pop_bot_BrianE()
            qqq_pop_bot_BrianE = self.qqq_pop_bot_BrianE()
            smh_pop_bot_BrianE = self.smh_pop_bot_BrianE()
            
            # Combine the pop bots with equal weights
            combined_pop_bots_BrianE = []
            for allocation in [spy_pop_bot_BrianE, qqq_pop_bot_BrianE, smh_pop_bot_BrianE]:
                combined_pop_bots_BrianE.extend([(ticker, weight * (1/3)) for ticker, weight in allocation])
            
            # Combine allocations for the same ticker
            final_allocations_BrianE = defaultdict(float)
            for ticker, weight in combined_pop_bots_BrianE:
                final_allocations_BrianE[ticker] += weight
            
            return self.allocate(list(final_allocations_BrianE.items()))



    def spy_pop_bot_BrianE(self):
        if self.spxl_rsi10 > 80:
            return [("UVXY", 1)]
        else:
            if self.spxl_rsi10 < 30:
                return [("SPXL", 1)]
            else:
                trinity_13_6_DD = self.trinity_13_6_DD()
                return trinity_13_6_DD

    def trinity_13_6_DD(self):
        if self.vixm_rsi10 > 70:
            return [("BIL", 1)]
        else:
            waves = self.waves()
            return waves
    
    def bull_market(self):
        if self.svxy_cr5 > 0:
            bull_tqqq_cure_svxy = self.inverse_vatility_weighted(["TQQQ", "CURE", "SVXY"], 20)
            return bull_tqqq_cure_svxy
        else:
            bull_tqqq_cure_utsl = self.inverse_vatility_weighted(["TQQQ", "CURE", "UTSL"], 20)
            return bull_tqqq_cure_utsl

    def waves(self):
        periods = [600, 500, 400, 300, 200, 100]
        waves = []
        for period in periods:
            if eval(f"self.spy_cr{period} > self.dbc_cr{period}"):
                bull_market = self.bull_market()
                waves.append((bull_market, 1/len(periods)))
            else:
                bull_tqqq_cure_utsl = self.inverse_vatility_weighted(["SQQQ", "CURE", "SVXY", "UTSL"], 20)
                waves.append((bull_tqqq_cure_utsl, 1/len(periods)))
        
        # Combine allocations with weights
        final_allocations = defaultdict(float)
        for allocation, weight in waves:
            for ticker, alloc in allocation:
                final_allocations[ticker] += alloc * weight
        
        return list(final_allocations.items())


    def qqq_pop_bot_BrianE(self):
        if self.tqqq_rsi10 > 80:
            return [("UVXY", 1)]
        else:
            if self.tqqq_rsi10 < 30:
                return [("TQQQ", 1)]
            else:
                trinity_13_6_DD = self.trinity_13_6_DD()
                return trinity_13_6_DD
    
    def smh_pop_bot_BrianE(self):
        if self.soxl_rsi10 < 30:
            return [("SOXL", 1)]
        else:
            trinity_13_6_DD = self.trinity_13_6_DD()
            return trinity_13_6_DD

    def spy_pop_bot(self):
        if self.spxl_rsi10 > 80:
            return [("UVXY", 1)]
        else:
            if self.spxl_rsi10 < 30:
                return [("SPXL", 1)]
            else:
                return [("BIL", 1)]
    
    def qqq_pop_bot(self):
        if self.tqqq_rsi10 > 80:
            return [("UVXY", 1)]
        else:
            if self.tqqq_rsi10 < 30:
                return [("TQQQ", 1)]
            else:
                return [("BIL", 1)]
    
    def smh_pop_bot(self):
        if self.soxl_rsi10 < 30:
            return [("SOXL", 1)]
        else:
            return [("BIL", 1)]

    def inverse_vatility_weighted(self, tickers, window):
        volatilities = [1 / self.customAlgo.indicators[ticker][f"VolatilityQM_{window}"].temp_value for ticker in tickers]
        total = sum(volatilities)
        return [(ticker, vol / total) for ticker, vol in zip(tickers, volatilities)]
