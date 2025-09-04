import datetime
from enhancements_strategy import EnhancementsContext, Bar
from tests.test_utils import TrackingBroker

def indicator(symbol, bar):
    return {
        "long_entry": bar.datetime.minute == 0,
        "long_exit": False,
        "short_entry": False,
        "short_exit": False
    }

def adv_lookup(symbol): return 5_000_000

def test_only_one_partial_per_bar():
    cfg = {
        "strategy": {
            "allow_shorts": False,
            "atr": {"period": 2, "stop_mult": 2.0, "account_risk_fraction": 0.05},
            "exits": {
                "partials": {
                    "enabled": True,
                    "levels": [
                        {"r_multiple": 0.5, "exit_pct": 0.4},
                        {"r_multiple": 0.6, "exit_pct": 0.4},
                    ]
                },
                "trailing": {"enabled": False}
            }
        },
        "slippage": {"tiers": [{"adv_threshold": 0, "bps": 0}]},
        "commission": {"per_share": 0.0, "min_trade_commission": 0.0}
    }
    broker = TrackingBroker()
    ctx = EnhancementsContext(cfg, broker, indicator)
    base = datetime.datetime(2024,1,1,9,30)

    # Entry bar
    bar0 = Bar("AAA", base, 100,101,99,100,10000)
    ctx.on_bar_start(bar0, broker)
    fills = ctx.process_symbol("AAA", bar0, broker, adv_lookup)
    broker.apply_fills(fills)

    # Price jump to pass both partial thresholds simultaneously
    bar1 = Bar("AAA", base + datetime.timedelta(minutes=1), 101.2, 101.5, 100.8, 101.3, 12000)
    ctx.on_bar_start(bar1, broker)
    fills = ctx.process_symbol("AAA", bar1, broker, adv_lookup)
    broker.apply_fills(fills)

    open_trade = ctx.metrics_tracker.get_open_trade("AAA")
    assert open_trade is not None
    assert len(open_trade.executed_partial_levels) == 1
    assert 0.5 in open_trade.executed_partial_levels
    assert 0.6 not in open_trade.executed_partial_levels
