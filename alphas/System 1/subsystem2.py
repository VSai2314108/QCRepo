from AlgorithmImports import *
from QuantConnect.Algorithm import QCAlgorithm
from AlphaQM import AlphaQM
from utils.indicators.RelativeStrengthIndexQM import RelativeStrengthIndexQM
from utils.indicators.MaxDrawdownQM import MaxDrawdownQM
from utils.indicators.CumulativeReturnQM import CumulativeReturnQM
from utils.indicators.MovingAverageQM import MovingAverageQM
from utils.indicators.VolatilityQM import VolatilityQM
from datetime import datetime

class UncorrelatedBonds2(AlphaQM):
    def __init__(self, customAlgo: QCAlgorithm) -> None:
        symbols = [
            "SPY", "IEF", "BIL", "SVXY", "TQQQ", "TECL", "UPRO", "SQQQ", "SOXS", "TECS", "UVXY", "TLT", "BND", "PSQ", "QQQ", "VIXY", "SHY", "GLD", "XLP", "BTAL", "SHV", "TMF", "VIXM", "SOXL"
        ]
        indicators = [
            (MovingAverageQM, 15), (MovingAverageQM, 25), (MovingAverageQM, 50), (MovingAverageQM, 200), (MovingAverageQM, 450),
            (MaxDrawdownQM, 2), (MaxDrawdownQM, 3), (MaxDrawdownQM, 10), (MaxDrawdownQM, 60),
            (RelativeStrengthIndexQM, 5), (RelativeStrengthIndexQM, 10), (RelativeStrengthIndexQM, 20), (RelativeStrengthIndexQM, 45), (RelativeStrengthIndexQM, 60), (RelativeStrengthIndexQM, 200),
            (VolatilityQM, 2), (VolatilityQM, 3), (VolatilityQM, 5), (VolatilityQM, 10), (VolatilityQM, 21), (VolatilityQM, 40),
            (CumulativeReturnQM, 1), (CumulativeReturnQM, 6), (CumulativeReturnQM, 60), (CumulativeReturnQM, 100)
        ]
        AlphaQM.__init__(self, customAlgo, (14, 4, 10, -10), symbols, indicators, True)

    def calculate(self):
        current_month = datetime.now().month

        # Check if it's November or December
        if current_month in [11, 12]:
            return self.allocate([("SPY", 0.6), ("IEF", 0.4)])

        # Bonds Exciting condition
        if self.check_bonds_exciting():
            return self.allocate([("TMF", 1)])

        # Only Bulls (popped) condition
        if self.check_only_bulls_popped():
            return self.allocate([("BIL", 1)])

        # Volmageddon II conditions
        if self.check_volmageddon():
            return self.allocate([("BIL", 1)])

        # Overbought conditions
        overbought_result = self.check_overbought()
        if overbought_result:
            return overbought_result

        # BSC conditions
        bsc_result = self.check_bsc()
        if bsc_result:
            return bsc_result

        # No BSC conditions
        no_bsc_result = self.check_no_bsc()
        if no_bsc_result:
            return no_bsc_result

        # Default allocation if no conditions are met
        return self.allocate([("SHV", 1)])

    def check_bonds_exciting(self):
        tlt_ma15 = self.customAlgo.indicators["TLT"]["MovingAverageQM_15"].temp_value
        tlt_ma50 = self.customAlgo.indicators["TLT"]["MovingAverageQM_50"].temp_value
        tmf_md60 = self.customAlgo.indicators["TMF"]["MaxDrawdownQM_60"].temp_value
        return tlt_ma15 > tlt_ma50 and tmf_md60 <= 15.0

    def check_only_bulls_popped(self):
        svxy_md2 = self.customAlgo.indicators["SVXY"]["MaxDrawdownQM_2"].temp_value
        svxy_md3 = self.customAlgo.indicators["SVXY"]["MaxDrawdownQM_3"].temp_value
        return svxy_md2 > 10.0 or svxy_md3 > 20.0

    def check_volmageddon(self):
        tqqq_rsi = self.customAlgo.indicators["TQQQ"]["RelativeStrengthIndexQM_10"].temp_value
        tecl_rsi = self.customAlgo.indicators["TECL"]["RelativeStrengthIndexQM_10"].temp_value
        upro_rsi = self.customAlgo.indicators["UPRO"]["RelativeStrengthIndexQM_10"].temp_value

        if tqqq_rsi > 82.0 and tecl_rsi > 80.0 and upro_rsi > 78.0:
            return self.handle_overbought_condition(1)
        elif tqqq_rsi > 82.0 and tecl_rsi > 80.0:
            return self.handle_overbought_condition(2)
        elif tqqq_rsi > 82.0 and upro_rsi > 78.0:
            return self.handle_overbought_condition(3)
        return None

    def handle_overbought_condition(self, condition):
        if condition == 1:
            return self.allocate([("BIL", 1)])
        elif condition == 2:
            return self.allocate([("BIL", 0.66), ("TECS", 0.113), ("SQQQ", 0.113), ("SOXS", 0.057), ("UVXY", 0.057)])
        elif condition == 3:
            return self.allocate([("BIL", 0.33), ("TECS", 0.223), ("SQQQ", 0.223), ("SOXS", 0.111), ("UVXY", 0.111)])

    def check_bsc(self):
        vixm_rsi = self.customAlgo.indicators["VIXM"]["RelativeStrengthIndexQM_10"].temp_value
        qqq_vol = self.customAlgo.indicators["QQQ"]["VolatilityQM_10"].temp_value
        spy_vol = self.customAlgo.indicators["SPY"]["VolatilityQM_5"].temp_value

        if vixm_rsi > 70.0 and qqq_vol > 3.0 and spy_vol > 2.5:
            return self.allocate([("TLT", 0.5), ("VIXM", 0.5)])
        elif vixm_rsi > 70.0 and qqq_vol > 3.0:
            return self.allocate([("TLT", 0.33), ("VIXM", 0.33), ("BIL", 0.34)])
        elif vixm_rsi > 70.0 and spy_vol > 2.5:
            return self.allocate([("TLT", 0.165), ("VIXM", 0.165), ("BIL", 0.67)])

        return self.check_bsc_sub()

    def check_bsc_sub(self):
        qqq_md = self.customAlgo.indicators["QQQ"]["MaxDrawdownQM_10"].temp_value
        tlt_md = self.customAlgo.indicators["TLT"]["MaxDrawdownQM_10"].temp_value

        if qqq_md <= 6.0 and tlt_md <= 3.0:
            return self.allocate([("TMF", 1/3), ("TQQQ", 1/3), ("UPRO", 1/3)])

        bsmr_result = self.check_bsmr()
        if bsmr_result:
            return bsmr_result

        bab_result = self.check_bab()
        if bab_result:
            return bab_result

        wmdyn_result = self.check_wmdyn()
        if wmdyn_result:
            return wmdyn_result

        tqqq_result = self.check_rsi_strategy("TQQQ")
        if tqqq_result:
            return tqqq_result

        tecl_result = self.check_rsi_strategy("TECL")
        if tecl_result:
            return tecl_result

        soxl_result = self.check_rsi_strategy("SOXL")
        if soxl_result:
            return soxl_result

        upro_result = self.check_rsi_strategy("UPRO")
        if upro_result:
            return upro_result

        svxy_result = self.check_svxy_strategy()
        if svxy_result:
            return svxy_result

        return None

    def check_bsmr(self):
        tqqq_rsi = self.customAlgo.indicators["TQQQ"]["RelativeStrengthIndexQM_10"].temp_value
        tqqq_cr6 = self.customAlgo.indicators["TQQQ"]["CumulativeReturnQM_6"].temp_value

        if tqqq_rsi > 79.0:
            return self.allocate([("UVXY", 1)])
        elif tqqq_cr6 < -12.0:
            return self.handle_bsmr_condition()
        return None

    def handle_bsmr_condition(self):
        tqqq_cr1 = self.customAlgo.indicators["TQQQ"]["CumulativeReturnQM_1"].temp_value
        if tqqq_cr1 > 5.5:
            return self.allocate([("UVXY", 1)])
        else:
            tqqq_rsi = self.customAlgo.indicators["TQQQ"]["RelativeStrengthIndexQM_10"].temp_value
            tmf_md = self.customAlgo.indicators["TMF"]["MaxDrawdownQM_10"].temp_value
            if tqqq_rsi < 32.0 or tmf_md < 7.0:
                return self.allocate([("TQQQ", 1)])
            else:
                qqq_price = self.customAlgo.indicators["QQQ"]["tempBar"].close
                qqq_ma25 = self.customAlgo.indicators["QQQ"]["MovingAverageQM_25"].temp_value
                if qqq_price > qqq_ma25:
                    return self.allocate([("TQQQ", 1)])
                else:
                    spy_rsi60 = self.customAlgo.indicators["SPY"]["RelativeStrengthIndexQM_60"].temp_value
                    bnd_rsi45 = self.customAlgo.indicators["BND"]["RelativeStrengthIndexQM_45"].temp_value
                    spy_rsi45 = self.customAlgo.indicators["SPY"]["RelativeStrengthIndexQM_45"].temp_value
                    ief_rsi200 = self.customAlgo.indicators["IEF"]["RelativeStrengthIndexQM_200"].temp_value
                    tlt_rsi200 = self.customAlgo.indicators["TLT"]["RelativeStrengthIndexQM_200"].temp_value

                    if spy_rsi60 > 50.0:
                        if bnd_rsi45 > spy_rsi45:
                            return self.allocate([("TQQQ", 1)])
                        else:
                            return self.allocate([("SHV", 1)])
                    elif ief_rsi200 < tlt_rsi200:
                        if bnd_rsi45 > spy_rsi45:
                            return self.allocate([("TQQQ", 1)])
                        else:
                            return self.allocate([("SHV", 1)])
                    else:
                        return self.allocate([("SHV", 1)])

    def check_bab(self):
        qqq_rsi10 = self.customAlgo.indicators["QQQ"]["RelativeStrengthIndexQM_10"].temp_value
        vixy_vol40 = self.customAlgo.indicators["VIXY"]["VolatilityQM_40"].temp_value
        bnd_cr60 = self.customAlgo.indicators["BND"]["CumulativeReturnQM_60"].temp_value
        bil_cr60 = self.customAlgo.indicators["BIL"]["CumulativeReturnQM_60"].temp_value
        svxy_vol2 = self.customAlgo.indicators["SVXY"]["VolatilityQM_2"].temp_value
        svxy_vol3 = self.customAlgo.indicators["SVXY"]["VolatilityQM_3"].temp_value
        spy_vol21 = self.customAlgo.indicators["SPY"]["VolatilityQM_21"].temp_value

        if qqq_rsi10 > 80.0:
            return self.allocate([("UVXY", 0.5), ("BTAL", 0.5)])
        elif vixy_vol40 < 5.0:
            if bnd_cr60 > bil_cr60:
                return self.allocate([("TQQQ", 1)])
            else:
                return self.allocate([("SVXY", 0.55), ("BTAL", 0.45)])
        elif svxy_vol2 > 10.0 or svxy_vol3 > 20.0:
            return self.allocate([("SHY", 1)])
        elif qqq_rsi10 > 80.0:
            return self.allocate([("UVXY", 0.5), ("BTAL", 0.5)])
        elif spy_vol21 < 1.25:
            if bnd_cr60 > bil_cr60:
                return self.allocate([("TQQQ", 1)])
            else:
                return self.allocate([("SVXY", 0.55), ("BTAL", 0.45)])
        else:
            return self.allocate([("SHY", 0.2), ("SPY", 0.2), ("BTAL", 0.2), ("GLD", 0.2), ("XLP", 0.2)])

    def check_wmdyn(self):
        spy_rsi5 = self.customAlgo.indicators["SPY"]["RelativeStrengthIndexQM_5"].temp_value
        spy_vol10 = self.customAlgo.indicators["SPY"]["VolatilityQM_10"].temp_value
        bil_cr100 = self.customAlgo.indicators["BIL"]["CumulativeReturnQM_100"].temp_value
        tlt_cr100 = self.customAlgo.indicators["TLT"]["CumulativeReturnQM_100"].temp_value
        ief_rsi10 = self.customAlgo.indicators["IEF"]["RelativeStrengthIndexQM_10"].temp_value
        psq_rsi20 = self.customAlgo.indicators["PSQ"]["RelativeStrengthIndexQM_20"].temp_value
        spy_price = self.customAlgo.indicators["SPY"]["tempBar"].close
        spy_ma200 = self.customAlgo.indicators["SPY"]["MovingAverageQM_200"].temp_value
        spy_rsi60 = self.customAlgo.indicators["SPY"]["RelativeStrengthIndexQM_60"].temp_value
        ief_rsi200 = self.customAlgo.indicators["IEF"]["RelativeStrengthIndexQM_200"].temp_value
        tlt_rsi200 = self.customAlgo.indicators["TLT"]["RelativeStrengthIndexQM_200"].temp_value

        if spy_rsi5 < 25.0:
            return self.allocate([("SOXL", 0.5), ("TLT", 0.125), ("SVXY", 0.125), ("SOXL", 0.125), ("TECL", 0.125)])
        elif spy_vol10 > 2.5:
            return self.allocate([("SHV", 1)])
        elif bil_cr100 < tlt_cr100:
            return self.allocate([("SOXL", 0.5), ("TLT", 0.125), ("SVXY", 0.125), ("SOXL", 0.125), ("TECL", 0.125)])
        elif ief_rsi10 > psq_rsi20:
            return self.allocate([("SOXL", 0.5), ("TLT", 0.125), ("SVXY", 0.125), ("SOXL", 0.125), ("TECL", 0.125)])
        elif spy_price > spy_ma200:
            return self.allocate([("SHV", 1)])
        elif spy_rsi60 > 50.0:
            return self.allocate([("SHV", 1)])
        elif ief_rsi200 < tlt_rsi200:
            return self.allocate([("SHV", 1)])
        else:
            return self.allocate([("SOXL", 0.5), ("TLT", 0.125), ("SVXY", 0.125), ("SOXL", 0.125), ("TECL", 0.125)])
            
    def check_rsi_strategy(self, ticker):
        price = self.customAlgo.indicators[ticker]["tempBar"].close
        ma200 = self.customAlgo.indicators[ticker]["MovingAverageQM_200"].temp_value
        rsi10 = self.customAlgo.indicators[ticker]["RelativeStrengthIndexQM_10"].temp_value
        cr1 = self.customAlgo.indicators[ticker]["CumulativeReturnQM_1"].temp_value

        if price > ma200:
            if rsi10 < 49.0:
                if cr1 < -2.0:
                    return self.allocate([("SHV", 1)])
                elif cr1 > 8.5:
                    if rsi10 < 31.0:
                        return self.allocate([(ticker, 1)])
                    else:
                        return self.allocate([("SHV", 1)])
                else:
                    return self.allocate([(ticker, 1)])
            else:
                if ticker == "TQQQ" and rsi10 > 80.0:
                    return self.allocate([("UVXY", 1)])
                elif rsi10 > 82.0:
                    return self.allocate([("SHV", 1)])
                else:
                    return self.allocate([("SHV", 1)])
        else:
            if rsi10 < 31.0:
                if cr1 < -6.0:
                    return self.allocate([(ticker, 1)])
                else:
                    return self.allocate([(ticker, 1)])
            else:
                return self.allocate([("SHV", 1)])

    def check_svxy_strategy(self):
        tqqq_cr6 = self.customAlgo.indicators["TQQQ"]["CumulativeReturnQM_6"].temp_value
        tqqq_cr1 = self.customAlgo.indicators["TQQQ"]["CumulativeReturnQM_1"].temp_value
        svxy_price = self.customAlgo.indicators["SVXY"]["tempBar"].close
        svxy_ma200 = self.customAlgo.indicators["SVXY"]["MovingAverageQM_200"].temp_value
        svxy_rsi10 = self.customAlgo.indicators["SVXY"]["RelativeStrengthIndexQM_10"].temp_value
        svxy_cr1 = self.customAlgo.indicators["SVXY"]["CumulativeReturnQM_1"].temp_value

        if tqqq_cr6 < 0.0:
            if tqqq_cr1 > 5.0:
                return self.allocate([("SHV", 1)])
            elif svxy_price > svxy_ma200:
                if svxy_rsi10 < 49.0:
                    if svxy_cr1 < -2.0:
                        return self.allocate([("SHV", 1)])
                    elif svxy_cr1 > 8.5:
                        if svxy_rsi10 < 31.0:
                            return self.allocate([("SVXY", 1)])
                        else:
                            return self.allocate([("SHV", 1)])
                    else:
                        return self.allocate([("SVXY", 1)])
                else:
                    if svxy_rsi10 > 82.0:
                        return self.allocate([("VIXM", 1)])
                    else:
                        return self.allocate([("SHV", 1)])
            else:
                if svxy_rsi10 < 31.0:
                    if svxy_cr1 < -6.0:
                        return self.allocate([("SVXY", 1)])
                    else:
                        return self.allocate([("SVXY", 1)])
                else:
                    return self.allocate([("SHV", 1)])
        return self.allocate([("SHV", 1)])
    def check_overbought(self):
        tqqq_rsi = self.customAlgo.indicators["TQQQ"]["RelativeStrengthIndexQM_10"].temp_value
        tecl_rsi = self.customAlgo.indicators["TECL"]["RelativeStrengthIndexQM_10"].temp_value
        upro_rsi = self.customAlgo.indicators["UPRO"]["RelativeStrengthIndexQM_10"].temp_value

        if tqqq_rsi > 82.0 and tecl_rsi > 80.0 and upro_rsi > 78.0:
            return self.handle_overbought_condition(1)
        elif tqqq_rsi > 82.0 and tecl_rsi > 80.0:
            return self.handle_overbought_condition(2)
        elif tqqq_rsi > 82.0 and upro_rsi > 78.0:
            return self.handle_overbought_condition(3)
        return None
    def check_no_bsc(self):
        tqqq_result = self.check_rsi_strategy("TQQQ")
        if tqqq_result:
            return tqqq_result

        tecl_result = self.check_rsi_strategy("TECL")
        if tecl_result:
            return tecl_result

        soxl_result = self.check_rsi_strategy("SOXL")
        if soxl_result:
            return soxl_result

        upro_result = self.check_rsi_strategy("UPRO")
        if upro_result:
            return upro_result

        svxy_result = self.check_svxy_strategy()
        if svxy_result:
            return svxy_result

        return None