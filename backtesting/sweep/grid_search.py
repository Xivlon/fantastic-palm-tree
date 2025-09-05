import pandas as pd

from .optimizer import ParameterOptimizer
from .parameter_space import ParameterSpace
from .results import OptimizationResults


class GridSearchOptimizer(ParameterOptimizer):
    """Grid search parameter optimizer."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def optimize(
        self, data: pd.DataFrame, parameter_space: ParameterSpace, verbose: bool = True
    ) -> OptimizationResults:
        """Run grid search optimization.

        Args:
            data: Market data for backtesting
            parameter_space: Parameter space to search
            verbose: Print progress information

        Returns:
            OptimizationResults object
        """
        combinations = parameter_space.get_combinations()

        if verbose:
            print("Starting grid search optimization")
            print(f"Parameter space size: {len(combinations)} combinations")
            print(f"Using {self.max_workers or 'all available'} workers")

        # Run optimization
        results = self._run_parallel_optimization(data, combinations)

        if verbose:
            successful_results = [r for r in results if r["success"]]
            failed_results = [r for r in results if not r["success"]]
            print(
                f"Completed: {len(successful_results)} successful, {len(failed_results)} failed"
            )

        # Create optimization results
        optimization_results = OptimizationResults(
            results=results,
            parameter_space=parameter_space,
            optimizer_type="grid_search",
        )

        if verbose:
            best_result = optimization_results.get_best_result()
            if best_result:
                print(f"Best objective value: {best_result['objective_value']:.4f}")
                print(f"Best parameters: {best_result['parameters']}")

        return optimization_results


class RandomSearchOptimizer(ParameterOptimizer):
    """Random search parameter optimizer."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def optimize(
        self,
        data: pd.DataFrame,
        parameter_space: ParameterSpace,
        n_iterations: int = 100,
        verbose: bool = True,
    ) -> OptimizationResults:
        """Run random search optimization.

        Args:
            data: Market data for backtesting
            parameter_space: Parameter space to search
            n_iterations: Number of random combinations to try
            verbose: Print progress information

        Returns:
            OptimizationResults object
        """
        import random

        all_combinations = parameter_space.get_combinations()

        if n_iterations >= len(all_combinations):
            # If we want more iterations than possible combinations, use all
            selected_combinations = all_combinations
        else:
            # Randomly sample combinations
            selected_combinations = random.sample(all_combinations, n_iterations)

        if verbose:
            print("Starting random search optimization")
            print(
                f"Trying {len(selected_combinations)} combinations out of {len(all_combinations)} possible"
            )
            print(f"Using {self.max_workers or 'all available'} workers")

        # Run optimization
        results = self._run_parallel_optimization(data, selected_combinations)

        if verbose:
            successful_results = [r for r in results if r["success"]]
            failed_results = [r for r in results if not r["success"]]
            print(
                f"Completed: {len(successful_results)} successful, {len(failed_results)} failed"
            )

        # Create optimization results
        optimization_results = OptimizationResults(
            results=results,
            parameter_space=parameter_space,
            optimizer_type="random_search",
        )

        if verbose:
            best_result = optimization_results.get_best_result()
            if best_result:
                print(f"Best objective value: {best_result['objective_value']:.4f}")
                print(f"Best parameters: {best_result['parameters']}")

        return optimization_results
