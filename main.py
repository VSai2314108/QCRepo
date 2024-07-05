# region imports
from datetime import timedelta
from AlgorithmImports import *
from utils.utils.CustomConsolidators import ShorterDayConsolidator

from utils.indicators.QMParent import QM

from alphas.SVIX10 import SVIX10
from alphas.NeoBetaBaller import NeoBetaBaller
from alphas.BullOrHedge import BullOrHedge
from alphas.AlphaQM import AlphaQM

class ManagementAlgorithm(QCAlgorithm):
    def initialize(self):
        ############ SET BACKTEST PARAMETERS ##############
        self.starting_value = 100000
        self.set_start_date(2021, 4, 20)  # Set Start Date
        self.set_end_date(2024, 6, 20)    # Set End Date
        self.set_cash(self.starting_value)  
        # self.set_brokerage_model(BrokerageName.DEFAULT, AccountType.CASH)
        
        ############# ADD ALPHA MODELS AND NECESSARY PARAMETERS ###############

        self.alpha_models: list[AlphaQM] = []
        # self.alpha_models.append(SVIX10(self))
        self.alpha_models.append(NeoBetaBaller(self, (14,14,5,-5)))
        self.alpha_models.append(BullOrHedge(self))
        self.insight_list: list[Insight] = []
        self.weights: dict[str, float] = {
            "SVIX10": 0, 
            "NeoBetaBaller": 1, 
            "BullOrHedge": 0,
            # Add any other strategies here with default weights
        }
        
        ############ SET UNIVERSE OF SYMBOLS AND INDICATORS##############
        self.symbols = list(set([symbol for model in self.alpha_models for symbol in model.symbols]))
        self.symbols.append("SPY")
        indicators_needed: list[(QM, int)] = list({indicator for model in self.alpha_models for indicator in model.indicators})

        symbols = [
            "SPY", "BTAL", "FNGD", "FNGU", "PDBC", "SGOV", "SOXL", "SOXS", "SPLV", "SPXU", "SQQQ", "SVXY", "TECL", "TECS", "TLT", "TMV", "TQQQ", "UQL", "UUP", "UVXY", "VIXM", "UPRO", "UDOW", "BIL", "TMF", "PSQ", "IEF", "UGL"
        ]
        for symbol in symbols:
            self.symbols.append(symbol)
            

        
        ############# CREATE NECESSARY INDICATORS AND STORAGE UNITS ###############
        self.indicators = {symbol:{} for symbol in self.symbols}

        # indicators_needed: list[(QM, int)] = []
        # indicators_needed.append((RelativeStrengthIndexQM, 10))
        for symbol in self.symbols:
            self.indicators[symbol]["CurrentPrice"] = Identity(symbol)
            self.add_equity(symbol, Resolution.DAILY)
            self.AddEquity(symbol, Resolution.Daily)
            self.RegisterIndicator(symbol, self.indicators[symbol]["CurrentPrice"], Resolution.Daily)

            
            # each sub dict will have - consolidator, RSI, tempClose
            self.indicators[symbol]["consolidator"] = ShorterDayConsolidator()
            self.indicators[symbol]["consolidator"].data_consolidated += self._consolidation_handler
            self.subscription_manager.add_consolidator(symbol, self.indicators[symbol]["consolidator"])
            
            for indicator, period in indicators_needed:
                indicator_instance: QM = indicator(period)
                self.register_indicator(symbol, indicator_instance, Resolution.DAILY)
                self.warm_up_indicator(symbol, indicator_instance)
                self.indicators[symbol][indicator_instance.indicator_name] = indicator_instance

            self.indicators[symbol]["bars"] = RollingWindow[TradeBar](20)
          
        ############# CONFIGURE BACKTEST PARAMETERS FOR SECURITIES ###############
  
        for security in self.securities.values():
            security: Security
            security.set_fee_model(ConstantFeeModel(0))
            security.set_slippage_model(NullSlippageModel())
            security.set_fill_model(ImmediateFillModel())
            
        ############# SCHEDULE EVENTS ###############
        self.schedule.on(self.date_rules.every_day(), self.time_rules.before_market_close("SPY", 4), self.EvaluateConditions)
                            
            
    def _consolidation_handler(self, sender, bar: TradeBar):
        ############# UPDATE TEMP VALUES ###############
        symbol = bar.symbol.__str__()
        for indicator in self.indicators[symbol].values():
            if isinstance(indicator, QM):
                indicator.temp_update(bar)
        self.indicators[symbol]["tempBar"] = bar
    
    def EvaluateConditions(self):
        ############# UPDATE ALPHA MODELS ######################################
        # if not self.indicators["TQQQ"]["RSI"].temp_value:
        #     return
        
        # remove expired insights
        self.insight_list = []
        
        # call update method on 
        for model in self.alpha_models:
            self.insight_list.extend(model.calculate())
        
        # iterate though insights and create an allocations map
        allocations = {}
        
        for insight in self.insight_list:
            symbol, weight, dir, strat = insight.symbol.__str__(), insight.weight, 1 if insight.direction == InsightDirection.UP else (0 if insight.direction == InsightDirection.FLAT else -1), insight.tag
            if symbol in allocations:
                allocations[symbol] = allocations[symbol] + (weight * self.weights.get(strat, 0) * dir)
            else:
                allocations[symbol] = (weight * self.weights.get(strat, 0) * dir)
        
        port: list[PortfolioTarget] = []
        for symbol, allocation in allocations.items():
            if allocation != 0:
                self.log(allocation)
            port.append(PortfolioTarget(symbol,allocation))
        self.set_holdings(port, liquidate_existing_holdings=True)
        
    
    def on_data(self, data: slice):
        ############# UPDATE REAL VALUES ######################################
        for symbol,bar in data.bars.items():
            self.indicators[bar.Symbol.__str__()]["bars"].add(bar)    
            self.indicators[bar.Symbol.__str__()]["tempBar"] = bar

        
        ############# ENSURE THAT MANUAL INDICATORS ARE UPDATED HERE ###########
