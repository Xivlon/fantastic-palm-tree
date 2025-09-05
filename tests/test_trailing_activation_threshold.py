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


def test_trailing_not_active_before_activation_r():
    cfg = {
        "strategy": {
            "allow_shorts": False,
            "atr": {"period": 2, "stop_mult": 1.0, "account_risk_fraction": 0.05},
            "exits": {
                "trailing": {
                    "enabled": True,
                    "type": "percent",
                    "percent": 0.05,
                    "activation_r_multiple": 1.5,
                },
                "partials": {"enabled": False},
            },
        },
        "slippage": {"tiers": [{"adv_threshold": 0, "bps": 0}]},
        "commission": {"per_share": 0.0},
    }
    broker = TrackingBroker()
    ctx = EnhancementsContext(cfg, broker, indicator)
    base = datetime.datetime(2024, 1, 1, 9, 30)

    bar0 = Bar("ACT", base, 100, 101, 99, 100, 10000)
    ctx.on_bar_start(bar0, broker)
    fills = ctx.process_symbol("ACT", bar0, broker, adv_lookup)
    broker.apply_fills(fills)

    bar1 = Bar(
        "ACT", base + datetime.timedelta(minutes=1), 102, 102.5, 101.8, 102, 12000
    )
    ctx.on_bar_start(bar1, broker)
    fills = ctx.process_symbol("ACT", bar1, broker, adv_lookup)
    broker.apply_fills(fills)

    bar2 = Bar(
        "ACT", base + datetime.timedelta(minutes=2), 100, 100.5, 99.5, 99.8, 15000
    )
    ctx.on_bar_start(bar2, broker)
    fills = ctx.process_symbol("ACT", bar2, broker, adv_lookup)
    broker.apply_fills(fills)

    open_trade = ctx.metrics_tracker.get_open_trade("ACT")
    assert open_trade is not None
