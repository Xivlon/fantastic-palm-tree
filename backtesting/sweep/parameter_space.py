import itertools
from typing import Any


class ParameterSpace:
    """Defines parameter space for optimization."""

    def __init__(self):
        self.parameters: dict[str, list[Any]] = {}

    def add_parameter(self, name: str, values: list[Any]) -> None:
        """Add parameter with possible values."""
        self.parameters[name] = values

    def get_combinations(self) -> list[dict[str, Any]]:
        """Get all parameter combinations."""
        if not self.parameters:
            return [{}]

        keys = list(self.parameters.keys())
        values = list(self.parameters.values())

        combinations = []
        for combo in itertools.product(*values):
            combinations.append(dict(zip(keys, combo, strict=False)))

        return combinations

    def size(self) -> int:
        """Get total number of combinations."""
        if not self.parameters:
            return 1
        size = 1
        for values in self.parameters.values():
            size *= len(values)
        return size
