from typing import Any

import pandas as pd


class DataHandler:
    """Handles market data for backtesting."""

    def __init__(self, data: pd.DataFrame):
        """Initialize with market data.

        Args:
            data: DataFrame with timestamp index and market data columns
        """
        self.data = data.copy()
        self.current_index = 0
        self.symbols = self._extract_symbols()

    def _extract_symbols(self) -> list[str]:
        """Extract available symbols from data columns."""
        # Assume columns like 'AAPL_close', 'AAPL_volume', etc.
        symbols = set()
        for col in self.data.columns:
            if "_" in col:
                symbol = col.split("_")[0]
                symbols.add(symbol)
        return list(symbols)

    def get_current_data(self) -> dict[str, Any]:
        """Get current market data."""
        if self.current_index >= len(self.data):
            return {}

        current_row = self.data.iloc[self.current_index]
        timestamp = self.data.index[self.current_index]

        # Organize data by symbol
        data = {"timestamp": timestamp}
        for symbol in self.symbols:
            symbol_data = {}
            for col in self.data.columns:
                if col.startswith(f"{symbol}_"):
                    field = col.split("_", 1)[1]
                    symbol_data[field] = current_row[col]
            if symbol_data:
                data[symbol] = symbol_data

        return data

    def next(self) -> bool:
        """Move to next data point. Returns True if successful."""
        self.current_index += 1
        return self.current_index < len(self.data)

    def has_data(self) -> bool:
        """Check if more data is available."""
        return self.current_index < len(self.data)

    def reset(self) -> None:
        """Reset to beginning of data."""
        self.current_index = 0

    def get_price(self, symbol: str, price_type: str = "close") -> float | None:
        """Get current price for a symbol."""
        current_data = self.get_current_data()
        if symbol in current_data and price_type in current_data[symbol]:
            return float(current_data[symbol][price_type])
        return None

    def get_historical_data(self, symbol: str, lookback: int = 100) -> pd.DataFrame:
        """Get historical data for a symbol."""
        end_idx = self.current_index + 1
        start_idx = max(0, end_idx - lookback)

        symbol_cols = [col for col in self.data.columns if col.startswith(f"{symbol}_")]
        historical = self.data.iloc[start_idx:end_idx][symbol_cols].copy()

        # Clean column names
        historical.columns = [col.split("_", 1)[1] for col in historical.columns]
        return historical
