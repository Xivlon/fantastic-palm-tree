import datetime
import pytest
from tests.test_utils import TrackingBroker
from enhancements_strategy import EnhancementsContext, Bar

@pytest.fixture
def base_time():
    return datetime.datetime(2024, 1, 1, 9, 30)

@pytest.fixture
def broker():
    return TrackingBroker(starting_equity=200_000)

@pytest.fixture
def indicator_factory():
    def _make(entry_side="long", exit_signal=False):
        def fn(symbol, bar):
            return {
                "long_entry": entry_side == "long" and bar.datetime.minute == 0,
                "short_entry": entry_side == "short" and bar.datetime.minute == 0,
                "long_exit": exit_signal and entry_side == "long",
                "short_exit": exit_signal and entry_side == "short"
            }
        return fn
    return _make

@pytest.fixture
def cfg_base():
    return {
        "strategy": {
            "allow_shorts": True,
            "atr": {"period": 2, "stop_mult": 2.0, "account_risk_fraction": 0.05},
        },
        "slippage": {"tiers": [{"adv_threshold": 0, "bps": 0}]},
        "commission": {"per_share": 0.0}
    }

@pytest.fixture
def context_builder(cfg_base, broker):
    def _build(indicator_fn, mutate=None):
        # shallow copy root level
        cfg = {**cfg_base}
        # ensure nested references duplicated where mutated
        import copy
        cfg["strategy"] = copy.deepcopy(cfg_base["strategy"])
        if mutate:
            mutate(cfg)
        return EnhancementsContext(cfg, broker, indicator_fn)
    return _build

@pytest.fixture
def make_bar():
    def _bar(symbol, t, o, h, l, c, v=10000):
        return Bar(symbol, t, o, h, l, c, v)
    return _bar
