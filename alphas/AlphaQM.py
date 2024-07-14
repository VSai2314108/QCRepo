from AlgorithmImports import *
from utils.utils.LinRegIndicators import *
from utils.utils.SimulatedPortfolio import *
from utils.indicators.QMParent import QM
from utils.utils.Charter import Charter

class AlphaQM(AlphaModel):
    def __init__(self, customAlgo: QCAlgorithm, slope_params, symbols, indicators, ignore_lin_slope=True) -> None:
        super().__init__()
        self.name = self.__class__.__name__
        self.customAlgo: QCAlgorithm = customAlgo
        self.symbols = symbols

        self.lin_reg_slope = SlopeIndicator(*slope_params)
        self.sim_portfolio: SimulatedPortfolio = SimulatedPortfolio(self, customAlgo.starting_value)
        self.real_portfolio: SimulatedPortfolio = SimulatedPortfolio(self, customAlgo.starting_value, lin_slope=True)
        self.ignore_lin_slope = ignore_lin_slope
        self.charter = Charter(self)
        
        self.allocations:dict = {symbol: 0 for symbol in self.symbols}
        self.indicators: list[(QM, int)] = indicators
    
    def allocate(self, list_tuples):
        for key in self.allocations.keys():
            self.allocations[key] = 0
        for pair in list_tuples:
            self.allocations[pair[0]] = self.allocations[pair[0]] + pair[1]
               
        ######### update sim port ##########
        self.sim_portfolio._update()
        self.lin_reg_slope.update(self.sim_portfolio.equity)
        self.real_portfolio._update()
        self.charter.update()
        
        ####### generate insights
        insights = []
        if self.ignore_lin_slope or (self.lin_reg_slope.Signal == None) or (self.lin_reg_slope.Signal == 1):
            insights = [Insight(
                symbol=symbol, 
                period=timedelta(hours=23, minutes=59),
                type = InsightType.PRICE,
                direction = 1 if allocation > 0 else (0 if allocation == 0 else -1),
                magnitude = None,
                confidence = None,
                weight = abs(allocation),
                tag= self.name) for symbol,allocation in self.allocations.items()]
        else:
            insights = [Insight(
                symbol=symbol, 
                period=timedelta(hours=23, minutes=59),
                type = InsightType.PRICE,
                direction = 0,
                magnitude = None,
                confidence = None,
                weight = 0,
                tag= self.name) for symbol,_ in self.allocations.items()]
        return insights
        
    def selection_helper(self, tickers, used_indicators, periods, mx=True, k_top=1):
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
        
    def update(self, algorithm: QCAlgorithm, data: Slice) -> List[Insight]:
        # Updates this Alpha model with the latest data from the algorithm.
        # This is called each time the algorithm receives data for subscribed securities
        # Generate insights on the securities in the universe.
        insights = []
        return insights    
    
    def calculate():
        pass        
    