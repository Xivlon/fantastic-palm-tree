import datetime
from enhancements_strategy import EnhancementsContext, Bar
from tests.test_utils import TrackingBroker

def indicator(symbol, bar):
    return {
        "long_entry": False,
        "long_exit": False,
        "short_entry": True,
        "short_exit": False
    }

def adv_lookup(symbol): return 1_000_000

def test_shorts_blocked():
    cfg = {
        "strategy": {
            "allow_shorts": False,
            "atr": {"period": 3, "stop_mult": 2.0, "account_risk_fraction": 0.05},
        },
        "slippage": {"tiers":[{"adv_threshold":0,"bps":0}]},
        "commission":{"per_share":0.0}
    }
    broker = TrackingBroker()
    ctx = EnhancementsContext(cfg, broker, indicator)
    base = datetime.datetime(2024,1,1,9,30)

    bar = Bar("NOSHORT", base, 100,101,99,100,10000)
    ctx.on_bar_start(bar, broker)
    fills = ctx.process_symbol("NOSHORT", bar, broker, adv_lookup)
    assert fills == []
