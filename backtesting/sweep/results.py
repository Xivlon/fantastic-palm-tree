from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
from .parameter_space import ParameterSpace


class OptimizationResults:
    """Container for optimization results."""
    
    def __init__(self, results: List[Dict[str, Any]], parameter_space: ParameterSpace,
                 optimizer_type: str):
        self.results = results
        self.parameter_space = parameter_space
        self.optimizer_type = optimizer_type
        self._successful_results = [r for r in results if r['success']]
        self._failed_results = [r for r in results if not r['success']]
        
    def get_best_result(self) -> Optional[Dict[str, Any]]:
        """Get the best result based on objective value."""
        if not self._successful_results:
            return None
            
        return max(self._successful_results, key=lambda x: x['objective_value'])
    
    def get_worst_result(self) -> Optional[Dict[str, Any]]:
        """Get the worst result based on objective value."""
        if not self._successful_results:
            return None
            
        return min(self._successful_results, key=lambda x: x['objective_value'])
    
    def get_top_n_results(self, n: int = 10) -> List[Dict[str, Any]]:
        """Get top N results."""
        if not self._successful_results:
            return []
            
        sorted_results = sorted(self._successful_results, 
                              key=lambda x: x['objective_value'], reverse=True)
        return sorted_results[:n]
    
    def get_results_dataframe(self) -> pd.DataFrame:
        """Get results as DataFrame for analysis."""
        if not self._successful_results:
            return pd.DataFrame()
        
        data = []
        for result in self._successful_results:
            row = result['parameters'].copy()
            row['objective_value'] = result['objective_value']
            
            # Add key metrics
            if result['metrics']:
                metrics = result['metrics']
                row['total_return'] = metrics.total_return
                row['sharpe_ratio'] = metrics.sharpe_ratio
                row['max_drawdown'] = metrics.max_drawdown
                row['total_trades'] = metrics.total_trades
                row['win_rate'] = metrics.win_rate
                
            data.append(row)
        
        return pd.DataFrame(data)
    
    def get_parameter_sensitivity(self) -> Dict[str, Dict[str, float]]:
        """Analyze parameter sensitivity."""
        df = self.get_results_dataframe()
        if df.empty:
            return {}
        
        sensitivity = {}
        param_columns = list(self.parameter_space.parameters.keys())
        
        for param in param_columns:
            if param in df.columns:
                grouped = df.groupby(param)['objective_value'].agg(['mean', 'std', 'count'])
                sensitivity[param] = {
                    'mean_by_value': grouped['mean'].to_dict(),
                    'std_by_value': grouped['std'].fillna(0).to_dict(),
                    'count_by_value': grouped['count'].to_dict(),
                    'range': grouped['mean'].max() - grouped['mean'].min()
                }
        
        return sensitivity
    
    def get_correlation_matrix(self) -> pd.DataFrame:
        """Get correlation matrix between parameters and objective."""
        df = self.get_results_dataframe()
        if df.empty:
            return pd.DataFrame()
        
        # Only include numeric columns
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        return df[numeric_columns].corr()
    
    def plot_parameter_sweep(self, param1: str, param2: str = None, 
                           metric: str = 'objective_value'):
        """Plot parameter sweep results."""
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            print("Matplotlib not available for plotting")
            return None
        
        df = self.get_results_dataframe()
        if df.empty:
            print("No successful results to plot")
            return None
        
        if param2 is None:
            # 1D plot
            fig, ax = plt.subplots(figsize=(10, 6))
            grouped = df.groupby(param1)[metric].mean()
            grouped.plot(kind='line', marker='o', ax=ax)
            ax.set_title(f'{metric} vs {param1}')
            ax.set_xlabel(param1)
            ax.set_ylabel(metric)
            ax.grid(True, alpha=0.3)
            return fig
        else:
            # 2D heatmap
            pivot_table = df.pivot_table(values=metric, index=param1, columns=param2, aggfunc='mean')
            
            fig, ax = plt.subplots(figsize=(12, 8))
            im = ax.imshow(pivot_table.values, cmap='viridis', aspect='auto')
            
            # Set ticks and labels
            ax.set_xticks(range(len(pivot_table.columns)))
            ax.set_yticks(range(len(pivot_table.index)))
            ax.set_xticklabels(pivot_table.columns)
            ax.set_yticklabels(pivot_table.index)
            
            # Add colorbar
            plt.colorbar(im, ax=ax, label=metric)
            
            ax.set_title(f'{metric} Heatmap: {param1} vs {param2}')
            ax.set_xlabel(param2)
            ax.set_ylabel(param1)
            
            # Rotate the tick labels and set their alignment
            plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
            
            return fig
    
    def summary(self) -> str:
        """Get summary statistics."""
        total_runs = len(self.results)
        successful_runs = len(self._successful_results)
        failed_runs = len(self._failed_results)
        
        summary = f"""
Optimization Summary:
=====================
Optimizer: {self.optimizer_type}
Total Runs: {total_runs}
Successful: {successful_runs}
Failed: {failed_runs}
Success Rate: {successful_runs/total_runs*100:.1f}%

"""
        
        if self._successful_results:
            objective_values = [r['objective_value'] for r in self._successful_results]
            best_result = self.get_best_result()
            
            summary += f"""
Objective Value Statistics:
  Best: {max(objective_values):.4f}
  Worst: {min(objective_values):.4f}
  Mean: {np.mean(objective_values):.4f}
  Std: {np.std(objective_values):.4f}

Best Parameters:
{best_result['parameters']}
"""
        
        return summary
    
    def get_correlation_matrix(self) -> pd.DataFrame:
        """Get correlation matrix between parameters and objective."""
        df = self.get_results_dataframe()
        if df.empty:
            return pd.DataFrame()
        
        # Only include numeric columns
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        return df[numeric_columns].corr()