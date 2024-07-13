from AlgorithmImports import *
from QuantConnect.Algorithm import QCAlgorithm
from AlphaQM import AlphaQM
from utils.indicators.RelativeStrengthIndexQM import RelativeStrengthIndexQM
from utils.indicators.CumulativeReturnQM import CumulativeReturnQM

class HedgedTrinityPop2(AlphaQM):
    def __init__(self, customAlgo: QCAlgorithm) -> None:
        symbols = [
            "SPY", "SPXL", "TQQQ", "SOXL", "UVXY", "VIXM", "UUP", "DBC", "TLT", "TMF", "UGL", "PDBC", "TMV", "USDU"
        ]
        indicators = [
            (RelativeStrengthIndexQM, 10),
            (CumulativeReturnQM, 126)
        ]
        AlphaQM.__init__(self, customAlgo, (14, 1, 5, -5), symbols, indicators, True)

    def calculate(self):
        # SPY Pop Bot
        spy_allocation = self.spy_pop_bot()
        if spy_allocation:
            return spy_allocation

        # QQQ Pop Bot
        qqq_allocation = self.qqq_pop_bot()
        if qqq_allocation:
            return qqq_allocation

        # SMH Pop Bot
        smh_allocation = self.smh_pop_bot()
        if smh_allocation:
            return smh_allocation

        # If none of the above conditions are met, proceed with Trinity strategy
        return self.trinity_strategy()

    def spy_pop_bot(self):
        vixm_rsi = self.customAlgo.indicators["VIXM"]["RelativeStrengthIndexQM_10"].temp_value
        if vixm_rsi > 70:
            return self.allocate([("VIXM", 0.5), ("UUP", 0.5)])
        else:
            spxl_rsi = self.customAlgo.indicators["SPXL"]["RelativeStrengthIndexQM_10"].temp_value
            if spxl_rsi > 80:
                return self.allocate([("UVXY", 1)])
            elif spxl_rsi < 30:
                return self.allocate([("SPXL", 1)])
        return None

    def qqq_pop_bot(self):
        tqqq_rsi = self.customAlgo.indicators["TQQQ"]["RelativeStrengthIndexQM_10"].temp_value
        if tqqq_rsi > 80:
            return self.allocate([("UVXY", 1)])
        elif tqqq_rsi < 30:
            return self.allocate([("TQQQ", 1)])
        return None

    def smh_pop_bot(self):
        soxl_rsi = self.customAlgo.indicators["SOXL"]["RelativeStrengthIndexQM_10"].temp_value
        if soxl_rsi < 30:
            return self.allocate([("SOXL", 1)])
        return None

    def trinity_strategy(self):
        spy_return = self.customAlgo.indicators["SPY"]["CumulativeReturnQM_126"].temp_value
        uup_return = self.customAlgo.indicators["UUP"]["CumulativeReturnQM_126"].temp_value
        dbc_return = self.customAlgo.indicators["DBC"]["CumulativeReturnQM_126"].temp_value
        tlt_return = self.customAlgo.indicators["TLT"]["CumulativeReturnQM_126"].temp_value

        if spy_return <= uup_return:
            if uup_return <= tlt_return:
                if dbc_return <= tlt_return:
                    return self.allocate([("TMV", 0.8), ("USDU", 0.2)])
                else:
                    return self.allocate([("TMF", 0.8), ("USDU", 0.2)])
            elif dbc_return <= uup_return:
                return self.allocate([("TMF", 0.5), ("PDBC", 0.5)])
            else:
                return self.allocate([("UGL", 0.5), ("TMF", 0.5)])
        elif dbc_return <= spy_return:
            if spy_return <= tlt_return:
                return self.allocate([("TMF", 0.5), ("PDBC", 0.5)])
            else:
                return self.allocate([("TQQQ", 0.5), ("PDBC", 0.5)])
        elif tlt_return <= uup_return:
            if uup_return <= dbc_return:
                return self.allocate([("PDBC", 0.5), ("UGL", 0.5)])
            else:
                return self.allocate([("TQQQ", 0.8), ("USDU", 0.2)])
        elif tlt_return <= dbc_return:
            return self.allocate([("TQQQ", 0.5), ("PDBC", 0.5)])
        else:
            return self.allocate([("TQQQ", 0.5), ("TMF", 0.5)])