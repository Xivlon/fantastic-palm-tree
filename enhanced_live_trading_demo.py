#!/usr/bin/env python3
"""
Enhanced Live Trading Demo with Comprehensive Paper Trading and Metrics

This script demonstrates:
1. Paper broker with mock fills and real-time P&L tracking
2. Live data from Alpha Vantage API with fallback to mock
3. Comprehensive metrics calculation (Sharpe, drawdown, etc.)
4. CSV export of all trading data and metrics
5. Bridge from backtest configuration to live trading
6. Real-time performance monitoring
"""

import asyncio
import logging
import sys
from datetime import datetime
from pathlib import Path

# Add the parent directory to the path so we can import from backtesting
sys.path.insert(0, '/home/runner/work/fantastic-palm-tree/fantastic-palm-tree')

from backtesting.brokers.paper import PaperBroker
from backtesting.data_providers.alpha_vantage import AlphaVantageDataProvider
from backtesting.data_providers.mock_alpha_vantage import MockAlphaVantageDataProvider
from backtesting.execution.live_engine import LiveTradingEngine, SimpleTradingStrategy
from backtesting.execution.bridge import BacktestToLiveBridge


async def demo_enhanced_paper_trading():
    """Demonstrate enhanced paper trading with P&L tracking and CSV export."""
    print("=" * 70)
    print("ENHANCED PAPER TRADING DEMO")
    print("=" * 70)
    
    # Create paper broker with enhanced tracking
    broker = PaperBroker("ENHANCED_DEMO", initial_cash=100000.0)
    
    # Connect broker
    await broker.connect()
    
    # Show initial state
    account_info = await broker.get_account_info()
    print(f"Initial Account State:")
    print(f"  Cash Balance: ${account_info.cash_balance:,.2f}")
    print(f"  Total Value: ${account_info.total_value:,.2f}")
    print()
    
    # Simulate some trades with different prices
    from backtesting.brokers.base import BrokerOrder, OrderSide, OrderType
    
    # Place some buy orders
    buy_order1 = BrokerOrder(
        symbol="AAPL",
        side=OrderSide.BUY,
        quantity=100,
        order_type=OrderType.MARKET,
        price=150.0
    )
    buy_order1.average_fill_price = 150.50  # Simulate slight slippage
    
    buy_order2 = BrokerOrder(
        symbol="MSFT",
        side=OrderSide.BUY,
        quantity=50,
        order_type=OrderType.MARKET,
        price=300.0
    )
    buy_order2.average_fill_price = 299.75  # Simulate favorable fill
    
    order_id1 = await broker.place_order(buy_order1)
    order_id2 = await broker.place_order(buy_order2)
    
    print(f"Placed orders: {order_id1}, {order_id2}")
    
    # Simulate price updates
    print("\nSimulating price movements...")
    broker.update_market_prices({"AAPL": 152.0, "MSFT": 305.0})  # Prices up
    
    # Show updated positions
    positions = await broker.get_positions()
    print(f"\nCurrent Positions:")
    for pos in positions:
        print(f"  {pos.symbol}: {pos.quantity} shares @ ${pos.average_price:.2f}")
        print(f"    Market Value: ${pos.market_value:.2f}")
        print(f"    Unrealized P&L: ${pos.unrealized_pnl:.2f}")
        print(f"    Day Change: ${pos.day_change:.2f} ({pos.day_change_percent:.2f}%)")
    
    # Get portfolio metrics
    metrics = broker.get_portfolio_metrics()
    print(f"\nPortfolio Metrics:")
    for key, value in metrics.items():
        if isinstance(value, float):
            if 'percent' in key.lower():
                print(f"  {key}: {value:.2f}%")
            elif 'ratio' in key.lower():
                print(f"  {key}: {value:.3f}")
            else:
                print(f"  {key}: ${value:,.2f}")
        else:
            print(f"  {key}: {value}")
    
    # Export to CSV
    print(f"\nExporting data to CSV...")
    exported_files = broker.export_to_csv("demo_results")
    print(f"Exported files:")
    for file_type, file_path in exported_files.items():
        print(f"  {file_type}: {file_path}")
    
    await broker.disconnect()
    print("\nEnhanced paper trading demo completed!")
    return broker


async def demo_live_trading_with_metrics():
    """Demonstrate live trading with real-time metrics tracking."""
    print("\n" + "=" * 70)
    print("LIVE TRADING WITH METRICS DEMO")
    print("=" * 70)
    
    # API key from the problem statement
    api_key = "0N0CM2NH0LUPJFXJ"
    
    # Create bridge utility
    bridge = BacktestToLiveBridge(api_key)
    
    # Create paper trading setup
    setup = bridge.create_paper_trading_setup(
        initial_cash=100000.0,
        symbols=["IBM", "AAPL"],
        update_interval=10  # Faster updates for demo
    )
    
    broker = setup['broker']
    engine = setup['engine']
    
    # Create simple trading strategy
    strategy = SimpleTradingStrategy(buy_threshold=0.005, sell_threshold=0.01)
    
    print(f"Created live trading setup:")
    print(f"  Account ID: {setup['account_id']}")
    print(f"  Symbols: {', '.join(setup['symbols'])}")
    print(f"  Initial Cash: ${setup['initial_cash']:,.2f}")
    print(f"  Data Provider: {type(setup['data_provider']).__name__}")
    
    # Start live trading for a short demo
    print(f"\nStarting live trading demo (will run for 3 cycles)...")
    print(f"Monitoring metrics and strategy performance...")
    
    try:
        # Start trading in background
        task = asyncio.create_task(engine.start(strategy))
        
        # Let it run for a few cycles
        for cycle in range(3):
            await asyncio.sleep(12)  # Wait a bit longer than update interval
            
            # Show current metrics
            metrics = engine.get_current_metrics()
            if metrics:
                print(f"\nCycle {cycle + 1} Metrics:")
                print(f"  Total Value: ${metrics.get('total_value', 0):,.2f}")
                print(f"  Unrealized P&L: ${metrics.get('unrealized_pnl', 0):,.2f}")
                print(f"  Total Return: {metrics.get('total_return_percent', 0):.2f}%")
                if 'sharpe_ratio' in metrics:
                    print(f"  Sharpe Ratio: {metrics['sharpe_ratio']:.3f}")
                if 'max_drawdown_percent' in metrics:
                    print(f"  Max Drawdown: {metrics['max_drawdown_percent']:.2f}%")
        
        # Stop trading
        await engine.stop()
        task.cancel()
        
        # Export results
        print(f"\nExporting live trading results...")
        exported_files = engine.export_results("live_demo_results")
        print(f"Exported files:")
        for file_type, file_path in exported_files.items():
            print(f"  {file_type}: {file_path}")
        
        # Show final metrics
        final_metrics = engine.get_current_metrics()
        if final_metrics:
            print(f"\nFinal Session Metrics:")
            account_info = await broker.get_account_info()
            print(f"  Final Portfolio Value: ${account_info.total_value:,.2f}")
            print(f"  Session Duration: {final_metrics.get('session_duration_hours', 0):.2f} hours")
            print(f"  Total Orders: {final_metrics.get('total_orders', 0)}")
            
    except Exception as e:
        print(f"Error in live trading demo: {e}")
        await engine.stop()
    
    print("\nLive trading with metrics demo completed!")
    return engine


async def demo_backtest_to_live_bridge():
    """Demonstrate the bridge from backtest to live trading."""
    print("\n" + "=" * 70)
    print("BACKTEST TO LIVE BRIDGE DEMO")
    print("=" * 70)
    
    # API key
    api_key = "0N0CM2NH0LUPJFXJ"
    
    # Create bridge
    bridge = BacktestToLiveBridge(api_key)
    
    # Create a mock backtest scenario for demonstration
    print("Creating paper trading setup based on hypothetical backtest...")
    
    setup = bridge.create_paper_trading_setup(
        backtest_results=None,  # No actual backtest for demo
        initial_cash=50000.0,
        symbols=["IBM", "AAPL", "MSFT"],
        update_interval=15
    )
    
    # Generate bridge report
    report_content = bridge.export_bridge_report(
        backtest_results=None,
        live_setup=setup,
        output_file="demo_bridge_report.txt"
    )
    
    print("Bridge report generated:")
    print("-" * 50)
    print(report_content)
    
    print("Backtest to live bridge demo completed!")


async def main():
    """Main demo function."""
    print("FANTASTIC PALM TREE - ENHANCED LIVE TRADING DEMONSTRATION")
    print(f"Started at: {datetime.now()}")
    print()
    
    try:
        # Run all demos
        await demo_enhanced_paper_trading()
        await demo_live_trading_with_metrics()
        await demo_backtest_to_live_bridge()
        
        print("\n" + "=" * 70)
        print("ALL DEMOS COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        print("\nKey Features Demonstrated:")
        print("✓ Enhanced paper trading with real-time P&L tracking")
        print("✓ Comprehensive metrics calculation (Sharpe, drawdown, etc.)")
        print("✓ CSV export of all trading data and performance metrics")
        print("✓ Live trading engine with real-time monitoring")
        print("✓ Bridge utility for backtest-to-live transitions")
        print("✓ Mock data provider integration with real API fallback")
        print("\nGenerated Files:")
        
        # List generated files
        demo_dir = Path("demo_results")
        live_dir = Path("live_demo_results")
        for directory in [demo_dir, live_dir, Path(".")]:
            if directory.exists():
                csv_files = list(directory.glob("*.csv"))
                txt_files = list(directory.glob("*bridge_report.txt"))
                for file in csv_files + txt_files:
                    print(f"  {file}")
        
    except KeyboardInterrupt:
        print("\nDemo interrupted by user")
    except Exception as e:
        print(f"\nDemo error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run demo
    asyncio.run(main())