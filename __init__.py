import pandas as pd

class Portfolio:
    def __init__(self, name):
        self.name = name
        self.assets = []
        self.liabilities = []
        self.investments = []

    def add_asset(self, asset):
        self.assets.append(asset)

    def add_liability(self, liability):
        self.liabilities.append(liability)

    def add_investment(self, investment):
        self.investments.append(investment)

    def calculate_net_worth(self):
        total_assets = sum([asset.value for asset in self.assets])
        total_liabilities = sum([liability.value for liability in self.liabilities])
        return total_assets - total_liabilities

# Example usage:
portfolio = Portfolio("My Portfolio")
portfolio.add_asset({"name": "Cash", "value": 1000})
portfolio.add_liability({"name": "Credit Card", "value": 500})
print(portfolio.calculate_net_worth())  # Output: 500