from .pipeline import Metric
import numpy as np
import pandas as pd

class SortinoMetric(Metric):
    def __init__(self, risk_free_rate: float = 0.0):
        self.returns = []
        self.risk_free_rate = risk_free_rate
        self.sortino = None

    def process_bar(self, bar):
        # Assume bar['return'] is the per-bar return (as a decimal, not %)
        self.returns.append(bar.get('return', 0.0))

    def finalize(self):
        returns = np.array(self.returns)
        downside = returns[returns < self.risk_free_rate]
        downside_std = downside.std() * np.sqrt(252) if len(downside) > 0 else 0
        annualized_return = (1 + returns).prod() ** (252 / len(returns)) - 1 if len(returns) > 0 else 0
        self.sortino = (annualized_return - self.risk_free_rate) / downside_std if downside_std != 0 else 0

    def result(self):
        return self.sortino
