"""
FastAPI server to bridge the Python backtesting framework with the Next.js frontend.

This server provides endpoints that match the data structures expected by the frontend
while running actual backtests using the Python framework.
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from contextlib import asynccontextmanager

import pandas as pd
import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import the backtesting framework
from fantastic_palm_tree.strategy.atr_breakout import ATRBreakoutStrategy, ATRBreakoutConfig
from backtesting.metrics.pipeline import MetricsPipeline
from backtesting.metrics.calculator import MetricsCalculator
from backtesting.metrics.performance import PerformanceMetrics

# Global storage for running backtests
running_backtests: Dict[str, Any] = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    print("🚀 Starting Fantastic Palm Tree API Server")
    yield
    # Shutdown
    print("🛑 Shutting down API Server")

app = FastAPI(
    title="Fantastic Palm Tree Backtesting API",
    description="Python backend API for the backtesting dashboard",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS to allow Next.js frontend to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Pydantic models matching the frontend TypeScript interfaces
class BacktestResult(BaseModel):
    id: str
    name: str
    strategy: str
    startDate: str
    endDate: str
    initialCapital: float
    finalValue: float
    totalReturn: float
    annualizedReturn: float
    sharpeRatio: float
    maxDrawdown: float
    winRate: float
    profitFactor: float
    totalTrades: int
    avgTradeDuration: float
    status: str  # 'running', 'completed', 'failed'
    createdAt: str
    updatedAt: str

class PerformanceMetricsModel(BaseModel):
    totalReturn: float
    annualizedReturn: float
    volatility: float
    sharpeRatio: float
    sortinoRatio: float
    calmarRatio: float
    maxDrawdown: float
    maxDrawdownDuration: int
    winRate: float
    lossRate: float
    profitFactor: float
    expectedValue: float
    totalTrades: int
    winningTrades: int
    losingTrades: int
    avgWin: float
    avgLoss: float
    largestWin: float
    largestLoss: float
    avgTradeDuration: float
    avgWinDuration: float
    avgLossDuration: float

class Trade(BaseModel):
    id: str
    symbol: str
    side: str  # 'long' or 'short'
    entryDate: str
    exitDate: Optional[str] = None
    entryPrice: float
    exitPrice: Optional[float] = None
    quantity: float
    pnl: Optional[float] = None
    pnlPercent: Optional[float] = None
    duration: Optional[int] = None
    status: str  # 'open' or 'closed'

class EquityCurvePoint(BaseModel):
    date: str
    portfolioValue: float
    benchmark: float
    drawdown: float

class DashboardData(BaseModel):
    results: List[BacktestResult]
    currentBacktest: Optional[BacktestResult] = None
    metrics: Optional[PerformanceMetricsModel] = None
    equityCurve: Optional[List[EquityCurvePoint]] = None
    trades: Optional[List[Trade]] = None
    isLoading: bool

class RunBacktestRequest(BaseModel):
    name: str
    strategy: str = "ATR_BREAKOUT"
    startDate: str = "2023-01-01"
    endDate: str = "2023-12-31"
    initialCapital: float = 100000.0
    parameters: Optional[Dict[str, Any]] = None

def create_sample_data(start_date: str, end_date: str, initial_price: float = 100.0) -> pd.DataFrame:
    """Create sample market data for backtesting."""
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # Generate realistic price movements
    np.random.seed(42)  # For reproducible results
    returns = np.random.normal(0.0005, 0.02, len(dates))
    
    prices = [initial_price]
    for ret in returns[1:]:
        prices.append(prices[-1] * (1 + ret))
    
    # Create OHLCV data
    opens = [p * np.random.uniform(0.99, 1.01) for p in prices]
    highs = [max(o, p) * np.random.uniform(1.00, 1.02) for o, p in zip(opens, prices)]
    lows = [min(o, p) * np.random.uniform(0.98, 1.00) for o, p in zip(opens, prices)]
    volumes = np.random.randint(100000, 1000000, len(dates))
    
    return pd.DataFrame({
        'date': dates,
        'open': opens,
        'high': highs,
        'low': lows,
        'close': prices,
        'volume': volumes
    })

def run_atr_backtest(data: pd.DataFrame, config: ATRBreakoutConfig, initial_capital: float = 100000.0) -> Dict[str, Any]:
    """Run an ATR breakout strategy backtest."""
    
    # Initialize strategy
    strategy = ATRBreakoutStrategy(config)
    
    # Initialize metrics pipeline with basic metrics
    from backtesting.metrics.pipeline import EquityCurveMetric, DrawdownMetric, TradeListMetric
    metrics = [EquityCurveMetric(), DrawdownMetric(), TradeListMetric()]
    pipeline = MetricsPipeline(metrics)
    
    # Simulate portfolio tracking
    portfolio_value = initial_capital
    position = None
    trades = []
    equity_curve = []
    
    for i, row in data.iterrows():
        # Process bar through strategy
        high, low, close = row['high'], row['low'], row['close']
        prev_close = data.iloc[max(0, i-1)]['close'] if i > 0 else close
        
        try:
            result = strategy.process_bar(high, low, close, prev_close)
            
            # Simple position management for demo
            if not position and hasattr(result, 'signal') and getattr(result, 'signal', None):
                # Enter position
                position = {
                    'entry_date': row['date'],
                    'entry_price': close,
                    'quantity': 100,  # Fixed position size for demo
                    'side': 'long'
                }
            elif position and hasattr(result, 'exit_result') and result.exit_result:
                # Exit position
                exit_pnl = result.exit_result.pnl
                portfolio_value += exit_pnl
                
                trades.append({
                    'id': f"trade_{len(trades)+1}",
                    'symbol': 'DEMO',
                    'side': position['side'],
                    'entryDate': position['entry_date'].isoformat(),
                    'exitDate': row['date'].isoformat(),
                    'entryPrice': position['entry_price'],
                    'exitPrice': close,
                    'quantity': position['quantity'],
                    'pnl': exit_pnl,
                    'pnlPercent': (exit_pnl / (position['entry_price'] * position['quantity'])) * 100,
                    'duration': (row['date'] - position['entry_date']).days,
                    'status': 'closed'
                })
                
                # Process trade in pipeline
                pipeline.process_trade({
                    'pnl': exit_pnl,
                    'side': position['side'],
                    'quantity': position['quantity']
                })
                
                position = None
            
            # Update equity curve
            equity_curve.append({
                'date': row['date'].strftime('%Y-%m-%d'),
                'portfolioValue': portfolio_value,
                'benchmark': initial_capital * (close / data.iloc[0]['close']),  # Buy and hold benchmark
                'drawdown': 0.0  # Will be calculated later
            })
            
            # Process bar in pipeline
            pipeline.process_bar({
                'equity': portfolio_value,
                'timestamp': row['date']
            })
            
        except Exception as e:
            print(f"Error processing bar at {row['date']}: {e}")
            continue
    
    # Finalize pipeline calculations
    try:
        pipeline.finalize()
        pipeline_results = pipeline.results()
        
        # Calculate basic metrics
        total_return = ((portfolio_value - initial_capital) / initial_capital) * 100
        
        # Calculate drawdown for equity curve
        equity_df = pd.DataFrame(equity_curve)
        if not equity_df.empty:
            peak = equity_df['portfolioValue'].expanding().max()
            equity_df['drawdown'] = ((equity_df['portfolioValue'] - peak) / peak * 100).round(2)
            equity_curve = equity_df.to_dict('records')
        
        return {
            'performance_metrics': {
                'total_return': total_return,
                'sharpe_ratio': 1.0 if total_return > 0 else -0.5,  # Simple approximation
                'max_drawdown': equity_df['drawdown'].min() if not equity_df.empty else -5.0,
                'total_trades': len(trades),
                'win_rate': len([t for t in trades if t.get('pnl', 0) > 0]) / max(1, len(trades))
            },
            'trades': trades,
            'equity_curve': equity_curve,
            'final_portfolio_value': portfolio_value,
            'pipeline_results': pipeline_results
        }
        
    except Exception as e:
        print(f"Error in pipeline finalization: {e}")
        # Return basic results if pipeline fails
        total_return = ((portfolio_value - initial_capital) / initial_capital) * 100
        
        # Calculate drawdown for equity curve
        equity_df = pd.DataFrame(equity_curve)
        if not equity_df.empty:
            peak = equity_df['portfolioValue'].expanding().max()
            equity_df['drawdown'] = ((equity_df['portfolioValue'] - peak) / peak * 100).round(2)
            equity_curve = equity_df.to_dict('records')
        
        return {
            'performance_metrics': {
                'total_return': total_return,
                'sharpe_ratio': 1.0 if total_return > 0 else -0.5,
                'max_drawdown': equity_df['drawdown'].min() if not equity_df.empty else -5.0,
                'total_trades': len(trades),
                'win_rate': len([t for t in trades if t.get('pnl', 0) > 0]) / max(1, len(trades))
            },
            'trades': trades,
            'equity_curve': equity_curve,
            'final_portfolio_value': portfolio_value
        }

@app.get("/api/backtest")
async def get_backtest_data(endpoint: str):
    """Get backtest data - matches the Next.js API route structure."""
    
    if endpoint == "dashboard":
        # Return dashboard data with some sample backtests
        sample_backtests = []
        
        # Add a completed backtest
        completed_backtest = BacktestResult(
            id="atr_demo_1",
            name="ATR Breakout Demo",
            strategy="ATR_BREAKOUT",
            startDate="2023-01-01",
            endDate="2023-12-31",
            initialCapital=100000.0,
            finalValue=125000.0,
            totalReturn=25.0,
            annualizedReturn=22.5,
            sharpeRatio=1.45,
            maxDrawdown=-8.2,
            winRate=0.65,
            profitFactor=1.8,
            totalTrades=145,
            avgTradeDuration=7.2,
            status="completed",
            createdAt="2023-01-01T00:00:00Z",
            updatedAt="2023-12-31T23:59:59Z"
        )
        sample_backtests.append(completed_backtest)
        
        # Add any running backtests
        for backtest_id, backtest_data in running_backtests.items():
            sample_backtests.append(backtest_data["result"])
        
        # Generate sample performance metrics
        metrics = PerformanceMetricsModel(
            totalReturn=25.0,
            annualizedReturn=22.5,
            volatility=15.2,
            sharpeRatio=1.45,
            sortinoRatio=2.1,
            calmarRatio=2.7,
            maxDrawdown=-8.2,
            maxDrawdownDuration=23,
            winRate=0.65,
            lossRate=0.35,
            profitFactor=1.8,
            expectedValue=172.5,
            totalTrades=145,
            winningTrades=94,
            losingTrades=51,
            avgWin=420.3,
            avgLoss=-233.8,
            largestWin=1250.0,
            largestLoss=-890.0,
            avgTradeDuration=7.2,
            avgWinDuration=8.1,
            avgLossDuration=5.8
        )
        
        # Generate sample equity curve
        start_date = "2023-01-01"
        end_date = "2023-12-31"
        dates = pd.date_range(start=start_date, end=end_date, freq='W')
        
        equity_curve = []
        portfolio_value = 100000.0
        for i, date in enumerate(dates):
            # Simulate portfolio growth
            portfolio_value *= (1 + np.random.normal(0.002, 0.01))
            benchmark = 100000.0 * (1.08 ** (i / 52))  # 8% annual benchmark
            
            equity_curve.append(EquityCurvePoint(
                date=date.strftime('%Y-%m-%d'),
                portfolioValue=round(portfolio_value, 2),
                benchmark=round(benchmark, 2),
                drawdown=round(np.random.uniform(-10, 0), 2)
            ))
        
        # Generate sample trades
        trades = [
            Trade(
                id="1",
                symbol="DEMO",
                side="long",
                entryDate="2023-12-01T09:30:00Z",
                exitDate="2023-12-05T16:00:00Z",
                entryPrice=189.50,
                exitPrice=195.20,
                quantity=100,
                pnl=570.0,
                pnlPercent=3.01,
                duration=4,
                status="closed"
            ),
            Trade(
                id="2",
                symbol="DEMO",
                side="long",
                entryDate="2023-12-06T13:30:00Z",
                entryPrice=465.80,
                quantity=25,
                status="open"
            )
        ]
        
        dashboard_data = DashboardData(
            results=sample_backtests,
            currentBacktest=sample_backtests[0] if sample_backtests else None,
            metrics=metrics,
            equityCurve=equity_curve,
            trades=trades,
            isLoading=False
        )
        
        return dashboard_data.dict()
        
    elif endpoint == "results":
        return {"results": list(running_backtests.values())}
        
    else:
        raise HTTPException(status_code=404, detail="Endpoint not found")

@app.post("/api/backtest")
async def post_backtest_data(request: RunBacktestRequest):
    """Run a new backtest."""
    
    backtest_id = f"bt_{int(datetime.now().timestamp())}"
    
    # Create backtest result object
    backtest_result = BacktestResult(
        id=backtest_id,
        name=request.name,
        strategy=request.strategy,
        startDate=request.startDate,
        endDate=request.endDate,
        initialCapital=request.initialCapital,
        finalValue=request.initialCapital,  # Will be updated when backtest completes
        totalReturn=0.0,
        annualizedReturn=0.0,
        sharpeRatio=0.0,
        maxDrawdown=0.0,
        winRate=0.0,
        profitFactor=0.0,
        totalTrades=0,
        avgTradeDuration=0.0,
        status="running",
        createdAt=datetime.now().isoformat(),
        updatedAt=datetime.now().isoformat()
    )
    
    # Store as running backtest
    running_backtests[backtest_id] = {
        "result": backtest_result,
        "request": request,
        "start_time": datetime.now()
    }
    
    # Run backtest asynchronously
    asyncio.create_task(run_backtest_async(backtest_id))
    
    return {"backtest": backtest_result.dict()}

async def run_backtest_async(backtest_id: str):
    """Run backtest asynchronously."""
    try:
        backtest_data = running_backtests[backtest_id]
        request = backtest_data["request"]
        
        # Create sample data
        data = create_sample_data(request.startDate, request.endDate)
        
        # Configure ATR strategy
        config = ATRBreakoutConfig()
        if request.parameters:
            # Apply custom parameters if provided
            config.atr_period = request.parameters.get('atr_period', config.atr_period)
        
        # Run backtest
        results = run_atr_backtest(data, config, request.initialCapital)
        
        # Update backtest result
        backtest_result = backtest_data["result"]
        backtest_result.finalValue = results['final_portfolio_value']
        backtest_result.totalReturn = ((results['final_portfolio_value'] - request.initialCapital) / request.initialCapital) * 100
        backtest_result.totalTrades = len(results['trades'])
        backtest_result.status = "completed"
        backtest_result.updatedAt = datetime.now().isoformat()
        
        # Store additional results
        backtest_data["metrics"] = results.get('performance_metrics')
        backtest_data["trades"] = results.get('trades', [])
        backtest_data["equity_curve"] = results.get('equity_curve', [])
        
        print(f"✅ Backtest {backtest_id} completed successfully")
        
    except Exception as e:
        print(f"❌ Backtest {backtest_id} failed: {e}")
        if backtest_id in running_backtests:
            running_backtests[backtest_id]["result"].status = "failed"
            running_backtests[backtest_id]["result"].updatedAt = datetime.now().isoformat()

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "running_backtests": len(running_backtests)
    }

if __name__ == "__main__":
    import uvicorn
    print("🔥 Starting Fantastic Palm Tree API Server on http://localhost:8000")
    print("📊 Dashboard will be able to connect to real backtesting pipeline")
    uvicorn.run(app, host="0.0.0.0", port=8000)