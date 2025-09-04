from abc import ABC, abstractmethod
from typing import Dict, Any, List, Callable, Optional
from concurrent.futures import ProcessPoolExecutor, as_completed
import pandas as pd
from ..core.engine import BacktestEngine
from ..core.strategy import Strategy
from ..metrics.calculator import MetricsCalculator


class ParameterOptimizer(ABC):
    """Base class for parameter optimization."""
    
    def __init__(self, engine: BacktestEngine, strategy_class: type,
                 objective_function: Optional[Callable] = None,
                 max_workers: Optional[int] = None):
        self.engine = engine
        self.strategy_class = strategy_class
        self.objective_function = objective_function or self._default_objective
        self.max_workers = max_workers
        
    @staticmethod
    def _default_objective(metrics) -> float:
        """Default objective function (Sharpe ratio)."""
        return metrics.sharpe_ratio
    
    @abstractmethod
    def optimize(self, data: pd.DataFrame, parameter_space) -> 'OptimizationResults':
        """Optimize parameters."""
        pass
    
    def _evaluate_single_combination(self, params: Dict[str, Any], data: pd.DataFrame) -> Dict[str, Any]:
        """Evaluate a single parameter combination."""
        try:
            # Create strategy instance
            strategy = self.strategy_class()
            strategy.set_params(**params)
            
            # Run backtest
            results = self.engine.run(strategy, data, verbose=False)
            
            # Calculate metrics
            metrics = MetricsCalculator.calculate(results)
            
            # Calculate objective value
            objective_value = self.objective_function(metrics)
            
            return {
                'parameters': params,
                'metrics': metrics,
                'objective_value': objective_value,
                'results': results,
                'success': True,
                'error': None
            }
            
        except Exception as e:
            return {
                'parameters': params,
                'metrics': None,
                'objective_value': float('-inf'),
                'results': None,
                'success': False,
                'error': str(e)
            }
    
    def _run_parallel_optimization(self, data: pd.DataFrame, 
                                  combinations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Run optimization in parallel."""
        results = []
        
        if self.max_workers == 1:
            # Single-threaded execution
            for params in combinations:
                result = self._evaluate_single_combination(params, data)
                results.append(result)
        else:
            # Multi-threaded execution
            with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
                # Submit all jobs
                future_to_params = {
                    executor.submit(self._evaluate_single_combination, params, data): params
                    for params in combinations
                }
                
                # Collect results
                for future in as_completed(future_to_params):
                    result = future.result()
                    results.append(result)
        
        return results