from __future__ import annotations


class ATRCalculator:
    """
    Simple rolling ATR using arithmetic mean of true ranges over a fixed window.
    (Can be swapped for Wilder's smoothing or EMA variant later.)
    """

    def __init__(self, period: int = 14):
        self.period = period
        self._true_ranges: list[float] = []

    def add_bar(self, high: float, low: float, prev_close: float) -> float:
        true_range = max(
            high - low,
            abs(high - prev_close),
            abs(low - prev_close),
        )
        self._true_ranges.append(true_range)
        if len(self._true_ranges) > self.period:
            self._true_ranges.pop(0)
        return self.get_atr()

    def get_atr(self) -> float:
        if not self._true_ranges:
            return 0.0
        return sum(self._true_ranges) / len(self._true_ranges)

    def has_enough_samples(self, min_samples: int) -> bool:
        return len(self._true_ranges) >= min_samples

    def sample_count(self) -> int:
        return len(self._true_ranges)
