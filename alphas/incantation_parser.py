import json
import re
from typing import Dict, Any, Set, Tuple

class IncantationParser:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.incantation = self.load_incantation(file_path)
        self.declarations = set()
        self.symbols, self.indicators = self.extract_symbols_and_indicators(self.incantation)

    def load_incantation(self, file_path: str) -> Dict[str, Any]:
        with open(file_path, 'r') as file:
            return json.load(file)

    def get_indicator_abbreviation(self, indicator_type: str) -> str:
        words = re.findall(r'[A-Z][a-z]*', indicator_type)
        return ''.join(word[0].lower() for word in words)

    def extract_symbols_and_indicators(self, incantation: Dict[str, Any]) -> (Set[str], Set[Tuple[str, int]]):
        symbols = set()
        indicators = set()

        def process_incantation(incantation: Dict[str, Any]):
            # Capture symbols defined directly
            if "symbol" in incantation:
                symbols.add(incantation["symbol"])

            for key in ["lh_indicator", "rh_indicator"]:
                if key in incantation:
                    indicator = incantation[key]
                    indicator_type = indicator["type"]
                    symbol = incantation.get("lh_ticker_symbol")
                    symbol2 = incantation.get("rh_ticker_symbol")
                    window = indicator.get("window", 0)
                    
                    if symbol:
                        symbols.add(symbol)
                    if symbol2:
                        symbols.add(symbol2)
                    
                    if indicator_type != "CurrentPrice":
                        if window != 0:
                            indicator_name = f"{indicator_type}QM"
                            indicators.add((indicator_name, window))

                            # Construct the declaration string
                            abbr_type = self.get_indicator_abbreviation(indicator_type)
                            declaration = f"self.{symbol.lower()}_{abbr_type}{window} = self.customAlgo.indicators['{symbol}']['{indicator_type}QM_{window}'].temp_value"
                            self.declarations.add(declaration)
                    else:
                        # Handle CurrentPrice
                        price_declaration = f"self.{symbol.lower()}_price = self.customAlgo.indicators['{symbol}']['tempBar'].close"
                        self.declarations.add(price_declaration)

            # Recurse into nested dictionaries and lists
            for value in incantation.values():
                if isinstance(value, dict):
                    process_incantation(value)
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            process_incantation(item)

        process_incantation(incantation)
        return symbols, indicators

    def print_to_file(self):
        file_name = f"{self.file_path[:-5]}_init.txt"
        with open(file_name, 'w') as file:
            file.write("        # Indicator and price declarations\n")
            for declaration in sorted(self.declarations):
                file.write(f"        {declaration}\n")

            file.write("\n        # Symbols\n")
            file.write("        symbols = [\n")
            for symbol in sorted(self.symbols):
                file.write(f"            '{symbol}',\n")
            file.write("        ]\n")

            file.write("\n        # Indicators\n")
            file.write("        indicators = [\n")
            for indicator in sorted(self.indicators):
                file.write(f"            ({indicator[0]}, {indicator[1]}),\n")
            file.write("        ]\n")

        print(f"Wrote output to {file_name}")

if __name__ == "__main__":
    file_path = input("Name of the JSON file: ")
    parser = IncantationParser(file_path)
    parser.print_to_file()
