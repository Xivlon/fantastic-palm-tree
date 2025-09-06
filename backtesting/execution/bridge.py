"""Bridge utility to transfer backtest configurations to live trading."""

import logging
from typing import Any, Dict, Optional
from datetime import datetime

from ..brokers.base import BaseBroker
from ..brokers.paper import PaperBroker
from ..data_providers.alpha_vantage import AlphaVantageDataProvider
from ..data_providers.mock_alpha_vantage import MockAlphaVantageDataProvider
from ..execution.live_engine import LiveTradingEngine
from ..core.engine import BacktestResults
from ..metrics.calculator import MetricsCalculator


class BacktestToLiveBridge:
    """Bridge to help transition from backtest to live trading."""
    
    def __init__(self, alpha_vantage_api_key: str):
        self.alpha_vantage_api_key = alpha_vantage_api_key
        self.logger = logging.getLogger("BacktestToLiveBridge")
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    
    def create_paper_trading_setup(
        self,
        backtest_results: Optional[BacktestResults] = None,
        initial_cash: float = 100000.0,
        symbols: list[str] = None,
        update_interval: int = 60
    ) -> Dict[str, Any]:
        """Create a paper trading setup based on backtest results."""
        
        # Extract symbols from backtest if available
        if symbols is None and backtest_results:
            symbols = getattr(backtest_results, 'symbols', ['IBM'])  # Default fallback
        elif symbols is None:
            symbols = ['IBM']  # Default symbol
        
        # Adjust initial cash based on backtest if available
        if backtest_results and hasattr(backtest_results, 'portfolio'):
            initial_cash = getattr(backtest_results.portfolio, 'initial_cash', initial_cash)
        
        # Create data provider (try real, fallback to mock)
        data_provider = AlphaVantageDataProvider(self.alpha_vantage_api_key)
        if not data_provider.test_connection():
            self.logger.warning("Real Alpha Vantage API not accessible, using mock provider")
            data_provider = MockAlphaVantageDataProvider(self.alpha_vantage_api_key)
        
        # Create paper broker
        account_id = f"PAPER_LIVE_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        broker = PaperBroker(account_id, initial_cash)
        
        # Create live trading engine
        engine = LiveTradingEngine(
            broker=broker,
            data_provider=data_provider,
            symbols=symbols,
            update_interval=update_interval,
            enable_metrics=True
        )
        
        setup_info = {
            'broker': broker,
            'data_provider': data_provider,
            'engine': engine,
            'symbols': symbols,
            'initial_cash': initial_cash,
            'account_id': account_id,
            'update_interval': update_interval
        }
        
        self.logger.info(f"Created paper trading setup with {len(symbols)} symbols and ${initial_cash:,.2f} initial cash")
        
        return setup_info
    
    def analyze_backtest_performance(self, backtest_results: BacktestResults) -> Dict[str, Any]:
        """Analyze backtest performance to help configure live trading."""
        if not backtest_results:
            return {}
        
        try:
            # Calculate comprehensive metrics
            metrics = MetricsCalculator.calculate(backtest_results)
            
            # Extract key insights for live trading
            analysis = {
                'total_return': metrics.total_return,
                'sharpe_ratio': metrics.sharpe_ratio,
                'max_drawdown': metrics.max_drawdown,
                'total_trades': metrics.total_trades,
                'win_rate': metrics.win_rate,
                'avg_win': metrics.avg_win,
                'avg_loss': metrics.avg_loss,
                'profit_factor': metrics.profit_factor,
                'volatility': metrics.volatility,
                'calmar_ratio': metrics.calmar_ratio
            }
            
            # Generate recommendations
            recommendations = self._generate_live_trading_recommendations(analysis)
            analysis['recommendations'] = recommendations
            
            self.logger.info(f"Analyzed backtest: {metrics.total_trades} trades, "
                           f"{metrics.sharpe_ratio:.2f} Sharpe ratio, "
                           f"{metrics.max_drawdown:.2%} max drawdown")
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing backtest results: {e}")
            return {}
    
    def _generate_live_trading_recommendations(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate recommendations for live trading based on backtest analysis."""
        recommendations = {}
        
        # Risk management recommendations
        if analysis.get('max_drawdown', 0) < -0.20:  # More than 20% drawdown
            recommendations['risk_warning'] = "High drawdown detected. Consider position sizing limits."
        
        if analysis.get('sharpe_ratio', 0) < 1.0:
            recommendations['performance_warning'] = "Low Sharpe ratio. Monitor closely in live trading."
        
        if analysis.get('win_rate', 0) < 0.5:
            recommendations['win_rate_note'] = "Win rate below 50%. Ensure profit factor is adequate."
        
        # Position sizing recommendations
        max_drawdown = abs(analysis.get('max_drawdown', 0.10))
        recommended_position_size = min(0.10, 0.05 / max_drawdown)  # Risk-based position sizing
        recommendations['max_position_size'] = recommended_position_size
        
        # Update interval recommendations
        total_trades = analysis.get('total_trades', 0)
        if total_trades > 1000:
            recommendations['update_interval'] = "Consider shorter update intervals for high-frequency strategies"
        elif total_trades < 50:
            recommendations['update_interval'] = "Longer update intervals may be sufficient for low-frequency strategies"
        
        return recommendations
    
    def export_bridge_report(
        self, 
        backtest_results: Optional[BacktestResults] = None,
        live_setup: Optional[Dict[str, Any]] = None,
        output_file: str = "backtest_to_live_bridge_report.txt"
    ) -> str:
        """Export a bridge report comparing backtest and live setup."""
        
        report_lines = [
            "BACKTEST TO LIVE TRADING BRIDGE REPORT",
            "=" * 50,
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            ""
        ]
        
        # Backtest analysis
        if backtest_results:
            analysis = self.analyze_backtest_performance(backtest_results)
            report_lines.extend([
                "BACKTEST ANALYSIS:",
                "-" * 20,
                f"Total Return: {analysis.get('total_return', 0):.2%}",
                f"Sharpe Ratio: {analysis.get('sharpe_ratio', 0):.2f}",
                f"Max Drawdown: {analysis.get('max_drawdown', 0):.2%}",
                f"Total Trades: {analysis.get('total_trades', 0)}",
                f"Win Rate: {analysis.get('win_rate', 0):.2%}",
                f"Profit Factor: {analysis.get('profit_factor', 0):.2f}",
                ""
            ])
            
            # Recommendations
            recommendations = analysis.get('recommendations', {})
            if recommendations:
                report_lines.extend([
                    "RECOMMENDATIONS:",
                    "-" * 20
                ])
                for key, value in recommendations.items():
                    report_lines.append(f"{key}: {value}")
                report_lines.append("")
        
        # Live setup info
        if live_setup:
            report_lines.extend([
                "LIVE TRADING SETUP:",
                "-" * 20,
                f"Account ID: {live_setup.get('account_id', 'N/A')}",
                f"Initial Cash: ${live_setup.get('initial_cash', 0):,.2f}",
                f"Symbols: {', '.join(live_setup.get('symbols', []))}",
                f"Update Interval: {live_setup.get('update_interval', 60)} seconds",
                f"Data Provider: {type(live_setup.get('data_provider', 'Unknown')).__name__}",
                f"Broker: {type(live_setup.get('broker', 'Unknown')).__name__}",
                ""
            ])
        
        report_lines.extend([
            "NEXT STEPS:",
            "-" * 20,
            "1. Start with paper trading to validate strategy",
            "2. Monitor performance metrics closely",
            "3. Compare live results with backtest expectations",
            "4. Adjust position sizing and risk parameters as needed",
            "5. Export CSV results regularly for analysis",
            ""
        ])
        
        report_content = "\n".join(report_lines)
        
        # Write to file
        with open(output_file, 'w') as f:
            f.write(report_content)
        
        self.logger.info(f"Bridge report exported to {output_file}")
        return report_content