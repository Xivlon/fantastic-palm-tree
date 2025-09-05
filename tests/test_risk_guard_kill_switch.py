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
    return 1_000_000


def test_drawdown_kill_switch():
    cfg = {
        "strategy": {
            "allow_shorts": False,
            "atr": {"period": 2, "stop_mult": 2.0, "account_risk_fraction": 0.05},
        },
        "risk": {"max_drawdown_pct": 0.05, "max_daily_loss_pct": 0.10},
        "slippage": {"tiers": [{"adv_threshold": 0, "bps": 0}]},
        "commission": {"per_share": 0.0},
    }
    broker = TrackingBroker(starting_equity=100_000)
    ctx = EnhancementsContext(cfg, broker, indicator)
    base = datetime.datetime(2024, 1, 1, 9, 30)

    bar0 = Bar("DD", base, 100, 101, 99, 100, 10000)
    ctx.on_bar_start(bar0, broker)
    ctx.process_symbol("DD", bar0, broker, adv_lookup)

    broker.adjust_equity(94_000)
    bar1 = Bar("DD", base + datetime.timedelta(minutes=1), 99, 100, 98, 99, 12000)
    ctx.on_bar_start(bar1, broker)
    ctx.risk_guard.evaluate_global(bar1, broker.equity)

    assert ctx.risk_guard.kill_switch_triggered is True
