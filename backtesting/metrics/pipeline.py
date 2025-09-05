import pandas as pd
from typing import List, Dict, Any, Callable

class Metric:
    """
    Base class for all metrics. Subclass this to implement new metrics.
    """
    def process_bar(self, bar: Dict[str, Any]):
        pass

    def process_trade(self, trade: Dict[str, Any]):
        pass

    def finalize(self):
        pass

    def result(self):
        raise NotImplementedError

class EquityCurveMetric(Metric):
    def __init__(self):
        self.equity_curve = []

    def process_bar(self, bar: Dict[str, Any]):
        self.equity_curve.append(bar['equity'])

    def result(self):
        return pd.Series(self.equity_curve, name='equity')

class DrawdownMetric(Metric):
    def __init__(self):
        self.equity_curve = []
        self.drawdown = None

    def process_bar(self, bar: Dict[str, Any]):
        self.equity_curve.append(bar['equity'])

    def finalize(self):
        equity = pd.Series(self.equity_curve)
        peak = equity.expanding().max()
        self.drawdown = (equity - peak) / peak

    def result(self):
        return self.drawdown

class TradeListMetric(Metric):
    def __init__(self):
        self.trades = []

    def process_trade(self, trade: Dict[str, Any]):
        self.trades.append(trade)

    def result(self):
        return pd.DataFrame(self.trades)

class MetricsPipeline:
    """
    Pipeline to process and aggregate metrics. Extensible for new metrics.
    """
    def __init__(self, metrics: List[Metric]):
        self.metrics = metrics

    def process_bar(self, bar: Dict[str, Any]):
        for metric in self.metrics:
            metric.process_bar(bar)

    def process_trade(self, trade: Dict[str, Any]):
        for metric in self.metrics:
            metric.process_trade(trade)

    def finalize(self):
        for metric in self.metrics:
            metric.finalize()

    def results(self) -> Dict[str, Any]:
        return {metric.__class__.__name__: metric.result() for metric in self.metrics}
