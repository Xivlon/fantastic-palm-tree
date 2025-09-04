import matplotlib.pyplot as plt
import pandas as pd
from typing import Optional, Dict, Any
import io
import base64
from ..core.engine import BacktestResults
from .performance import PerformanceMetrics


class ReportGenerator:
    """Generate comprehensive backtest reports."""
    
    @staticmethod
    def generate_html_report(results: BacktestResults, metrics: PerformanceMetrics, 
                           output_path: Optional[str] = None) -> str:
        """Generate HTML report with charts and metrics."""
        
        equity_curve = results.get_equity_curve()
        trades_df = results.get_trades()
        
        # Generate charts
        charts = ReportGenerator._generate_charts(equity_curve, trades_df, metrics)
        
        # Create HTML content
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Backtest Report - {results.strategy.name}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .header {{ background-color: #f5f5f5; padding: 20px; border-radius: 5px; }}
                .metrics-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
                .metric-card {{ background-color: #fff; border: 1px solid #ddd; padding: 15px; border-radius: 5px; }}
                .chart {{ margin: 20px 0; text-align: center; }}
                table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Backtest Report: {results.strategy.name}</h1>
                <p><strong>Period:</strong> {results.start_time.strftime('%Y-%m-%d')} to {results.end_time.strftime('%Y-%m-%d')}</p>
                <p><strong>Duration:</strong> {results.duration.days} days</p>
                <p><strong>Initial Capital:</strong> ${results.portfolio.initial_cash:,.2f}</p>
            </div>
            
            <h2>Performance Summary</h2>
            <div class="metrics-grid">
                {ReportGenerator._generate_metric_cards(metrics)}
            </div>
            
            <h2>Equity Curve</h2>
            <div class="chart">
                <img src="data:image/png;base64,{charts['equity_curve']}" alt="Equity Curve">
            </div>
            
            <h2>Drawdown Analysis</h2>
            <div class="chart">
                <img src="data:image/png;base64,{charts['drawdown']}" alt="Drawdown Chart">
            </div>
            
            <h2>Returns Distribution</h2>
            <div class="chart">
                <img src="data:image/png;base64,{charts['returns_dist']}" alt="Returns Distribution">
            </div>
            
            <h2>Trade Analysis</h2>
            {ReportGenerator._generate_trades_table(trades_df)}
            
            <h2>Monthly Returns</h2>
            {ReportGenerator._generate_monthly_returns_table(equity_curve)}
            
        </body>
        </html>
        """
        
        if output_path:
            with open(output_path, 'w') as f:
                f.write(html_content)
                
        return html_content
    
    @staticmethod
    def _generate_charts(equity_curve: pd.DataFrame, trades_df: pd.DataFrame, 
                        metrics: PerformanceMetrics) -> Dict[str, str]:
        """Generate base64 encoded charts."""
        charts = {}
        
        # Equity curve chart
        fig, ax = plt.subplots(figsize=(12, 6))
        equity_curve['equity'].plot(ax=ax, title='Portfolio Equity Curve')
        ax.set_ylabel('Portfolio Value ($)')
        ax.grid(True, alpha=0.3)
        charts['equity_curve'] = ReportGenerator._fig_to_base64(fig)
        plt.close(fig)
        
        # Drawdown chart
        fig, ax = plt.subplots(figsize=(12, 4))
        peak = equity_curve['equity'].expanding().max()
        drawdown = (equity_curve['equity'] - peak) / peak * 100
        drawdown.plot(ax=ax, title='Drawdown (%)', color='red', alpha=0.7)
        ax.fill_between(drawdown.index, drawdown, 0, alpha=0.3, color='red')
        ax.set_ylabel('Drawdown (%)')
        ax.grid(True, alpha=0.3)
        charts['drawdown'] = ReportGenerator._fig_to_base64(fig)
        plt.close(fig)
        
        # Returns distribution
        if len(equity_curve) > 1:
            returns = equity_curve['equity'].pct_change().dropna()
            fig, ax = plt.subplots(figsize=(10, 6))
            returns.hist(bins=50, ax=ax, alpha=0.7, edgecolor='black')
            ax.set_title('Daily Returns Distribution')
            ax.set_xlabel('Daily Return')
            ax.set_ylabel('Frequency')
            ax.axvline(returns.mean(), color='red', linestyle='--', label=f'Mean: {returns.mean():.4f}')
            ax.legend()
            ax.grid(True, alpha=0.3)
            charts['returns_dist'] = ReportGenerator._fig_to_base64(fig)
            plt.close(fig)
        else:
            # Empty chart if no data
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.text(0.5, 0.5, 'Insufficient data for returns distribution', 
                   ha='center', va='center', transform=ax.transAxes)
            charts['returns_dist'] = ReportGenerator._fig_to_base64(fig)
            plt.close(fig)
        
        return charts
    
    @staticmethod
    def _fig_to_base64(fig) -> str:
        """Convert matplotlib figure to base64 string."""
        img_buffer = io.BytesIO()
        fig.savefig(img_buffer, format='png', bbox_inches='tight', dpi=100)
        img_buffer.seek(0)
        img_str = base64.b64encode(img_buffer.read()).decode()
        return img_str
    
    @staticmethod
    def _generate_metric_cards(metrics: PerformanceMetrics) -> str:
        """Generate HTML metric cards."""
        metric_dict = metrics.to_dict()
        cards_html = ""
        
        for key, value in metric_dict.items():
            if isinstance(value, (int, float)):
                if 'ratio' in key.lower() or 'factor' in key.lower():
                    formatted_value = f"{value:.2f}"
                elif '%' in key:
                    formatted_value = f"{value:.1f}%"
                else:
                    formatted_value = f"{value:,.0f}"
            else:
                formatted_value = str(value)
                
            cards_html += f"""
                <div class="metric-card">
                    <h4>{key}</h4>
                    <p style="font-size: 1.5em; margin: 0; color: #2E86AB;">{formatted_value}</p>
                </div>
            """
        
        return cards_html
    
    @staticmethod
    def _generate_trades_table(trades_df: pd.DataFrame) -> str:
        """Generate HTML trades table."""
        if trades_df.empty:
            return "<p>No trades executed.</p>"
            
        # Show last 10 trades
        recent_trades = trades_df.tail(10).copy()
        recent_trades['timestamp'] = pd.to_datetime(recent_trades['timestamp']).dt.strftime('%Y-%m-%d %H:%M')
        
        html = "<table><thead><tr>"
        for col in recent_trades.columns:
            html += f"<th>{col.title()}</th>"
        html += "</tr></thead><tbody>"
        
        for _, row in recent_trades.iterrows():
            html += "<tr>"
            for val in row.values:
                if isinstance(val, float):
                    html += f"<td>{val:.2f}</td>"
                else:
                    html += f"<td>{val}</td>"
            html += "</tr>"
        
        html += "</tbody></table>"
        html += f"<p><small>Showing last 10 trades of {len(trades_df)} total</small></p>"
        
        return html
    
    @staticmethod
    def _generate_monthly_returns_table(equity_curve: pd.DataFrame) -> str:
        """Generate monthly returns table."""
        if equity_curve.empty:
            return "<p>No data available for monthly returns.</p>"
            
        # Calculate monthly returns
        monthly_equity = equity_curve['equity'].resample('M').last()
        monthly_returns = monthly_equity.pct_change().dropna()
        
        if monthly_returns.empty:
            return "<p>Insufficient data for monthly returns.</p>"
        
        # Create yearly table
        monthly_returns.index = pd.to_datetime(monthly_returns.index)
        years = monthly_returns.index.year.unique()
        
        html = "<table><thead><tr><th>Year</th>"
        for month in ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']:
            html += f"<th>{month}</th>"
        html += "<th>YTD</th></tr></thead><tbody>"
        
        for year in years:
            year_data = monthly_returns[monthly_returns.index.year == year]
            html += f"<tr><td>{year}</td>"
            
            ytd_return = 1.0
            for month in range(1, 13):
                month_data = year_data[year_data.index.month == month]
                if not month_data.empty:
                    monthly_ret = month_data.iloc[0]
                    ytd_return *= (1 + monthly_ret)
                    html += f"<td>{monthly_ret*100:.1f}%</td>"
                else:
                    html += "<td>-</td>"
            
            html += f"<td>{(ytd_return-1)*100:.1f}%</td></tr>"
        
        html += "</tbody></table>"
        return html