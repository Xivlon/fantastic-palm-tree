"""
Test realistic execution models including slippage, commissions, and spreads.
"""

import datetime
from enhancements_strategy import (
    Bar, EnhancementsContext, Order, Fill,
    FixedSlippageModel, PercentageSlippageModel, VolumeBasedSlippageModel,
    PerShareCommissionModel, PercentageCommissionModel, TieredCommissionModel,
    ExecutionEngine, create_slippage_model, create_commission_model
)
from tests.test_utils import TrackingBroker


def test_fixed_slippage_model():
    """Test fixed slippage model"""
    model = FixedSlippageModel(0.05)  # 5 cent slippage
    
    buy_order = Order(symbol="TEST", side="BUY", qty=100)
    sell_order = Order(symbol="TEST", side="SELL", qty=100)
    
    # Buy orders pay more (positive slippage)
    buy_slippage = model.calculate_slippage(buy_order, 100.0)
    assert buy_slippage == 0.05
    
    # Sell orders receive less (negative slippage)
    sell_slippage = model.calculate_slippage(sell_order, 100.0)
    assert sell_slippage == -0.05


def test_percentage_slippage_model():
    """Test percentage-based slippage model"""
    model = PercentageSlippageModel(10)  # 10 bps = 0.1%
    
    buy_order = Order(symbol="TEST", side="BUY", qty=100)
    market_price = 100.0
    
    slippage = model.calculate_slippage(buy_order, market_price)
    expected = market_price * 0.001  # 10 bps = 0.1%
    assert abs(slippage - expected) < 0.0001


def test_volume_based_slippage_model():
    """Test volume-dependent slippage model"""
    tiers = [
        {"adv_threshold": 0, "bps": 5},      # 5 bps for low volume
        {"adv_threshold": 1000000, "bps": 10}  # 10 bps for high volume
    ]
    model = VolumeBasedSlippageModel(tiers)
    
    buy_order = Order(symbol="TEST", side="BUY", qty=100)
    market_price = 100.0
    
    # Low volume trade
    low_vol_slippage = model.calculate_slippage(buy_order, market_price, volume=500000)
    expected_low = market_price * 0.0005  # 5 bps
    assert abs(low_vol_slippage - expected_low) < 0.0001
    
    # High volume trade
    high_vol_slippage = model.calculate_slippage(buy_order, market_price, volume=2000000)
    expected_high = market_price * 0.001  # 10 bps
    assert abs(high_vol_slippage - expected_high) < 0.0001


def test_per_share_commission_model():
    """Test per-share commission model"""
    model = PerShareCommissionModel(per_share=0.005, min_commission=1.0)
    
    order = Order(symbol="TEST", side="BUY", qty=100)
    commission = model.calculate_commission(order, 100.0)
    expected = max(100 * 0.005, 1.0)  # $0.50, but min is $1.00
    assert commission == 1.0
    
    # Large order
    large_order = Order(symbol="TEST", side="BUY", qty=1000)
    large_commission = model.calculate_commission(large_order, 100.0)
    assert large_commission == 5.0  # 1000 * $0.005


def test_percentage_commission_model():
    """Test percentage-based commission model"""
    model = PercentageCommissionModel(rate=0.001, min_commission=1.0)  # 0.1%
    
    # Small order - commission should be minimum
    small_order = Order(symbol="TEST", side="BUY", qty=10)
    small_commission = model.calculate_commission(small_order, 50.0)
    expected_small = max(10 * 50.0 * 0.001, 1.0)  # $0.50, but min is $1.00
    assert small_commission == 1.0
    
    # Large order - commission should be calculated amount
    order = Order(symbol="TEST", side="BUY", qty=100)
    commission = model.calculate_commission(order, 100.0)
    expected = 100 * 100.0 * 0.001  # $10.00
    assert commission == 10.0
    
    # Very large order
    large_order = Order(symbol="TEST", side="BUY", qty=1000)
    large_commission = model.calculate_commission(large_order, 100.0)
    assert large_commission == 100.0  # 1000 * $100 * 0.1%


def test_execution_engine_with_slippage_and_commission():
    """Test complete execution engine with slippage and commissions"""
    slippage_model = FixedSlippageModel(0.02)
    commission_model = PerShareCommissionModel(0.005, 1.0)
    
    engine = ExecutionEngine(
        slippage_model=slippage_model,
        commission_model=commission_model,
        spread_bps=20  # 20 bps spread
    )
    
    order = Order(symbol="TEST", side="BUY", qty=100)
    market_price = 100.0
    
    fill = engine.execute_order(order, market_price)
    
    # Check fill details
    assert fill.symbol == "TEST"
    assert fill.side == "BUY"
    assert fill.qty == 100
    assert fill.commission == 1.0  # min commission
    
    # Check price includes spread and slippage
    # Buy price = market + spread/2 + slippage
    spread = market_price * 0.002  # 20 bps spread
    expected_price = market_price + (spread / 2) + 0.02  # spread + slippage
    assert abs(fill.price - expected_price) < 0.0001


def test_execution_engine_sell_order():
    """Test execution engine with sell order"""
    slippage_model = FixedSlippageModel(0.02)
    commission_model = PerShareCommissionModel(0.005, 1.0)
    
    engine = ExecutionEngine(
        slippage_model=slippage_model,
        commission_model=commission_model,
        spread_bps=20
    )
    
    order = Order(symbol="TEST", side="SELL", qty=100)
    market_price = 100.0
    
    fill = engine.execute_order(order, market_price)
    
    # For sell orders: price = market - spread/2 - slippage
    spread = market_price * 0.002
    expected_price = market_price - (spread / 2) - 0.02
    assert abs(fill.price - expected_price) < 0.0001


def test_factory_functions():
    """Test slippage and commission model factory functions"""
    
    # Test slippage factory
    fixed_config = {"amount": 0.05}
    slippage_model = create_slippage_model(fixed_config)
    assert isinstance(slippage_model, FixedSlippageModel)
    
    percentage_config = {"bps": 10}
    slippage_model = create_slippage_model(percentage_config)
    assert isinstance(slippage_model, PercentageSlippageModel)
    
    volume_config = {"tiers": [{"adv_threshold": 0, "bps": 5}]}
    slippage_model = create_slippage_model(volume_config)
    assert isinstance(slippage_model, VolumeBasedSlippageModel)
    
    # Test commission factory
    per_share_config = {"per_share": 0.005}
    commission_model = create_commission_model(per_share_config)
    assert isinstance(commission_model, PerShareCommissionModel)
    
    rate_config = {"rate": 0.001}
    commission_model = create_commission_model(rate_config)
    assert isinstance(commission_model, PercentageCommissionModel)
    
    tiered_config = {"tiers": [{"threshold": 0, "rate": 0.001}]}
    commission_model = create_commission_model(tiered_config)
    assert isinstance(commission_model, TieredCommissionModel)


def test_tracking_broker_with_realistic_execution():
    """Test TrackingBroker with realistic execution enabled"""
    
    slippage_config = {"bps": 10}  # 10 bps slippage
    commission_config = {"per_share": 0.01, "min_commission": 1.0}
    
    broker = TrackingBroker(
        starting_equity=100000,
        slippage_config=slippage_config,
        commission_config=commission_config,
        enable_realistic_execution=True
    )
    
    # Initial state
    assert broker.equity == 100000
    assert broker.total_commission == 0.0
    
    # Create a fill with commission
    fill = Fill(symbol="TEST", side="BUY", qty=100, price=100.05, commission=1.0)
    
    # Apply the fill
    broker.apply_fills([fill])
    
    # Check position was created
    position = broker.get_position("TEST")
    assert position is not None
    assert position.qty == 100
    assert position.avg_price == 100.05
    
    # Check commission was tracked
    assert broker.total_commission == 1.0
    assert broker.equity == 99999.0  # Starting equity minus commission


def test_tracking_broker_commission_tracking():
    """Test that TrackingBroker properly tracks commissions"""
    broker = TrackingBroker(starting_equity=100000)
    
    # Multiple fills with commissions
    fills = [
        Fill(symbol="AAPL", side="BUY", qty=100, price=150.0, commission=1.5),
        Fill(symbol="MSFT", side="BUY", qty=50, price=300.0, commission=0.75),
        Fill(symbol="AAPL", side="SELL", qty=50, price=155.0, commission=0.75)
    ]
    
    broker.apply_fills(fills)
    
    # Check total commission
    expected_commission = 1.5 + 0.75 + 0.75
    assert broker.total_commission == expected_commission
    assert broker.equity == 100000 - expected_commission
    
    # Check positions
    aapl_pos = broker.get_position("AAPL")
    msft_pos = broker.get_position("MSFT")
    
    assert aapl_pos.qty == 50  # 100 bought - 50 sold
    assert msft_pos.qty == 50


if __name__ == "__main__":
    # Run tests
    test_fixed_slippage_model()
    test_percentage_slippage_model() 
    test_volume_based_slippage_model()
    test_per_share_commission_model()
    test_percentage_commission_model()
    test_execution_engine_with_slippage_and_commission()
    test_execution_engine_sell_order()
    test_factory_functions()
    test_tracking_broker_with_realistic_execution()
    test_tracking_broker_commission_tracking()
    
    print("All realistic execution tests passed!")