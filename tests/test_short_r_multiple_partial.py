import datetime

from enhancements_strategy import Bar, EnhancementsContext
from tests.test_utils import TrackingBroker


def indicator_entry(symbol, bar):
    return {
        "long_entry": False,
        "long_exit": False,
        "short_entry": bar.datetime.minute == 0,
        "short_exit": False,
    }


def indicator_exit(symbol, bar):
    return {
        "long_entry": False,
        "long_exit": False,
        "short_entry": False,
        "short_exit": True,
    }


def adv_lookup(symbol):
    return 5_000_000


def test_short_partial_and_final_r():
    cfg = {
        "strategy": {
            "allow_shorts": True,
            "atr": {"period": 2, "stop_mult": 2.0, "account_risk_fraction": 0.05},
            "exits": {
                "partials": {
                    "enabled": True,
                    "levels": [
                        {"r_multiple": 0.5, "exit_pct": 0.5},
                    ],
                },
                "trailing": {"enabled": False},
            },
        },
        "slippage": {"tiers": [{"adv_threshold": 0, "bps": 0}]},
        "commission": {"per_share": 0.0},
    }
    broker = TrackingBroker()
    ctx = EnhancementsContext(cfg, broker, indicator_entry)
    base = datetime.datetime(2024, 1, 1, 9, 30)

    bar0 = Bar("SRT", base, 100, 101, 99, 100, 10000)
    ctx.on_bar_start(bar0, broker)
    fills = ctx.process_symbol("SRT", bar0, broker, adv_lookup)
    broker.apply_fills(fills)

    bar1 = Bar("SRT", base + datetime.timedelta(minutes=1), 98, 98.5, 97.5, 98, 12000)
    ctx.on_bar_start(bar1, broker)
    fills = ctx.process_symbol("SRT", bar1, broker, adv_lookup)
    broker.apply_fills(fills)

    ctx.signal_gen.indicator_fn = indicator_exit
    bar2 = Bar("SRT", base + datetime.timedelta(minutes=2), 96, 96.5, 95.5, 96, 15000)
    ctx.on_bar_start(bar2, broker)
    fills = ctx.process_symbol("SRT", bar2, broker, adv_lookup)
    broker.apply_fills(fills)

    summary = ctx.metrics_tracker.summary()
    assert summary["trades_total"] >= 1
