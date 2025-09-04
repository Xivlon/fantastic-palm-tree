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

def test_partial_priority_over_trailing():
    cfg = {
        "strategy": {
            "allow_shorts": False,
            "atr": {"period": 2, "stop_mult": 1.0, "account_risk_fraction": 0.05},
            "exits": {
                "partials": {
                    "enabled": True,
                    "levels": [{"r_multiple": 0.5, "exit_pct": 0.5}]
                },
                "trailing": {
                    "enabled": True,
                    "type": "percent",
                    "percent": 0.02,
                    "activation_r_multiple": 0.0
                }
            }
        },
        "slippage":{"tiers":[{"adv_threshold":0,"bps":0}]},
        "commission":{"per_share":0.0}
    }
    broker = TrackingBroker()
    ctx = EnhancementsContext(cfg, broker, indicator)
    base = datetime.datetime(2024,1,1,9,30)

    bar0 = Bar("PRIO", base, 100,101,99,100,10000)
    ctx.on_bar_start(bar0, broker)
    fills = ctx.process_symbol("PRIO", bar0, broker, adv_lookup)
    broker.apply_fills(fills)

    bar1 = Bar("PRIO", base + datetime.timedelta(minutes=1), 104,104.5,103.5,104,12000)
    ctx.on_bar_start(bar1, broker)
    fills = ctx.process_symbol("PRIO", bar1, broker, adv_lookup)
    broker.apply_fills(fills)

    sells = [f for f in fills if f.side == "SELL"]
    assert len(sells) >= 1
