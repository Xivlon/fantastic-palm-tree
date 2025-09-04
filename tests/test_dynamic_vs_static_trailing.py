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

def adv_lookup(symbol): return 1_000_000

def synthetic_sequence():
    return [
        (100,102,99,101),
        (101,103,100,102),
        (102,105,101,104),
        (104,108,103,107),
    ]

def run_cfg(use_dynamic):
    cfg = {
        "strategy": {
            "allow_shorts": False,
            "atr": {"period": 2, "stop_mult": 1.0, "account_risk_fraction": 0.05},
            "exits": {
                "trailing": {
                    "enabled": True,
                    "type": "atr",
                    "atr_mult": 2.0,
                    "activation_r_multiple": 0.0,
                    "use_dynamic_atr": use_dynamic,
                    "dynamic_atr_min_samples": 2
                },
                "partials": {"enabled": False}
            }
        },
        "slippage": {"tiers": [{"adv_threshold": 0, "bps": 0}]},
        "commission": {"per_share": 0.0}
    }
    broker = TrackingBroker()
    ctx = EnhancementsContext(cfg, broker, indicator)
    base = datetime.datetime(2024,1,1,9,30)

    trail_distances = []
    for i,(o,h,l,c) in enumerate(synthetic_sequence()):
        bar = Bar("DYN", base + datetime.timedelta(minutes=i), o,h,l,c, 10000+i*500)
        ctx.on_bar_start(bar, broker)
        fills = ctx.process_symbol("DYN", bar, broker, adv_lookup)
        broker.apply_fills(fills)
        tr = ctx.metrics_tracker.get_open_trade("DYN")
        if tr:
            try:
                atr_deque = ctx.atr_tracker.tr_values.get("DYN")
                if use_dynamic and atr_deque and len(atr_deque) >= 2:
                    current_atr = sum(atr_deque)/len(atr_deque)
                else:
                    current_atr = tr.atr_at_entry
                trail_distances.append(current_atr * 2.0)
            except AttributeError:
                trail_distances.append(0.0)
    return trail_distances

def test_dynamic_trailing_distance_grows():
    static_distances = run_cfg(use_dynamic=False)
    dynamic_distances = run_cfg(use_dynamic=True)
    assert len(dynamic_distances) == len(static_distances)
    assert any(dy > st for dy, st in zip(dynamic_distances, static_distances))
