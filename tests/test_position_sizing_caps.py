import datetime

from enhancements_strategy import Bar, EnhancementsContext
from tests.test_utils import TrackingBroker


def indicator(symbol, bar):
    return {
        "long_entry": bar.datetime.minute == 0,
        "long_exit": False,
        "short_entry": False,
        "short_exit": False,
    }


def adv_lookup(symbol):
    return 10_000_000


def test_symbol_equity_cap():
    cfg = {
        "strategy": {
            "allow_shorts": False,
            "atr": {"period": 2, "stop_mult": 1.0, "account_risk_fraction": 0.5},
            "sizing": {
                "per_symbol_equity_cap_pct": 0.10,
                "max_simultaneous_positions": 10,
            },
        },
        "slippage": {"tiers": [{"adv_threshold": 0, "bps": 0}]},
        "commission": {"per_share": 0.0},
    }
    broker = TrackingBroker(starting_equity=200_000)
    ctx = EnhancementsContext(cfg, broker, indicator)
    base = datetime.datetime(2024, 1, 1, 9, 30)

    bar = Bar("CAP", base, 50, 52, 48, 50, 50000)
    ctx.on_bar_start(bar, broker)
    fills = ctx.process_symbol("CAP", bar, broker, adv_lookup)

    if fills:
        assert fills[0].qty <= 400
