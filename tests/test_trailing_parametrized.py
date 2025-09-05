import pytest

from fantastic_palm_tree import EnhancedStrategy, StrategyConfig


@pytest.mark.parametrize("use_dynamic,min_samples", [(False, 1), (True, 1), (True, 3)])
@pytest.mark.parametrize("is_long", [True, False])
def test_trailing_distance_behavior(use_dynamic, min_samples, is_long):
    cfg = StrategyConfig()
    cfg.exits["trailing"]["use_dynamic_atr"] = use_dynamic
    cfg.exits["trailing"]["dynamic_atr_min_samples"] = min_samples
    strategy = EnhancedStrategy(cfg)

    # Seed ATR with bars (ATR becomes 2 after two identical 2-range bars)
    strategy.update_atr(101, 99, 100)  # TR=2
    strategy.update_atr(102, 100, 101)  # TR=2
    strategy.enter_position(price=100, size=1000, is_long=is_long)

    base_distance = strategy.trailing.compute_distance(strategy.position)
    assert base_distance > 0

    # Add bars with smaller ranges to reduce ATR
    strategy.update_atr(102.6, 101.4, 102)  # TR ~1.2
    strategy.update_atr(103.0, 102.0, 102.6)  # TR 1.0

    new_distance = strategy.trailing.compute_distance(strategy.position)

    if use_dynamic and strategy.atr_calc.has_enough_samples(min_samples):
        # ATR should decrease relative to entry ATR=2
        assert new_distance <= strategy.position.entry_atr + 1e-9
    else:
        # Should remain at entry ATR
        assert new_distance == strategy.position.entry_atr
