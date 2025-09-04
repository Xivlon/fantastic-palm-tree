class StrategyError(Exception):
    pass


class InvalidConfigError(StrategyError):
    pass


class PositionExistsError(StrategyError):
    pass


class NoPositionError(StrategyError):
    pass
