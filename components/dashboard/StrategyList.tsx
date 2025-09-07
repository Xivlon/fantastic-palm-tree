import React, { useState } from 'react';
import { StrategyTemplate } from '@/types/backtest';
import StrategyCard from './StrategyCard';
import { Search, Filter, Plus } from 'lucide-react';

interface StrategyListProps {
  strategies: StrategyTemplate[];
  onSelectStrategy?: (strategy: StrategyTemplate) => void;
  onCreateBacktest?: (strategy: StrategyTemplate) => void;
  onEditStrategy?: (strategy: StrategyTemplate) => void;
  onCreateStrategy?: () => void;
  selectedStrategyId?: string;
}

const StrategyList: React.FC<StrategyListProps> = ({
  strategies,
  onSelectStrategy,
  onCreateBacktest,
  onEditStrategy,
  onCreateStrategy,
  selectedStrategyId,
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState<string>('all');
  const [riskFilter, setRiskFilter] = useState<string>('all');

  const categories = [
    { value: 'all', label: 'All Categories' },
    { value: 'trend', label: 'Trend Following' },
    { value: 'mean_reversion', label: 'Mean Reversion' },
    { value: 'momentum', label: 'Momentum' },
    { value: 'volatility', label: 'Volatility' },
    { value: 'arbitrage', label: 'Arbitrage' },
    { value: 'custom', label: 'Custom' },
  ];

  const riskLevels = [
    { value: 'all', label: 'All Risk Levels' },
    { value: 'low', label: 'Low Risk' },
    { value: 'medium', label: 'Medium Risk' },
    { value: 'high', label: 'High Risk' },
  ];

  const filteredStrategies = strategies.filter((strategy) => {
    const matchesSearch = strategy.displayName.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         strategy.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = categoryFilter === 'all' || strategy.category === categoryFilter;
    const matchesRisk = riskFilter === 'all' || strategy.riskLevel === riskFilter;

    return matchesSearch && matchesCategory && matchesRisk;
  });

  const groupedStrategies = {
    builtin: filteredStrategies.filter(s => s.isBuiltIn),
    custom: filteredStrategies.filter(s => !s.isBuiltIn),
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Trading Strategies</h2>
          <p className="text-gray-600 mt-1">
            Discover and manage your trading strategies
          </p>
        </div>
        <button
          onClick={onCreateStrategy}
          className="bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-lg font-medium transition-colors flex items-center space-x-2"
        >
          <Plus className="w-4 h-4" />
          <span>Create Strategy</span>
        </button>
      </div>

      {/* Search and Filters */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <input
              type="text"
              placeholder="Search strategies..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
            />
          </div>

          {/* Category Filter */}
          <div className="relative">
            <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <select
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500 appearance-none"
            >
              {categories.map((category) => (
                <option key={category.value} value={category.value}>
                  {category.label}
                </option>
              ))}
            </select>
          </div>

          {/* Risk Filter */}
          <div>
            <select
              value={riskFilter}
              onChange={(e) => setRiskFilter(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500 appearance-none"
            >
              {riskLevels.map((risk) => (
                <option key={risk.value} value={risk.value}>
                  {risk.label}
                </option>
              ))}
            </select>
          </div>

          {/* Results Count */}
          <div className="flex items-center justify-end">
            <span className="text-sm text-gray-500">
              {filteredStrategies.length} strateg{filteredStrategies.length === 1 ? 'y' : 'ies'}
            </span>
          </div>
        </div>
      </div>

      {/* Built-in Strategies */}
      {groupedStrategies.builtin.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Built-in Strategies</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
            {groupedStrategies.builtin.map((strategy) => (
              <StrategyCard
                key={strategy.id}
                strategy={strategy}
                onSelect={onSelectStrategy}
                onCreateBacktest={onCreateBacktest}
                onEdit={onEditStrategy}
                isSelected={strategy.id === selectedStrategyId}
              />
            ))}
          </div>
        </div>
      )}

      {/* Custom Strategies */}
      {groupedStrategies.custom.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Custom Strategies</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
            {groupedStrategies.custom.map((strategy) => (
              <StrategyCard
                key={strategy.id}
                strategy={strategy}
                onSelect={onSelectStrategy}
                onCreateBacktest={onCreateBacktest}
                onEdit={onEditStrategy}
                isSelected={strategy.id === selectedStrategyId}
              />
            ))}
          </div>
        </div>
      )}

      {/* Empty State */}
      {filteredStrategies.length === 0 && (
        <div className="text-center py-12">
          <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <Search className="w-8 h-8 text-gray-400" />
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">No strategies found</h3>
          <p className="text-gray-600 mb-4">
            Try adjusting your search terms or filters to find what you&apos;re looking for.
          </p>
          <button
            onClick={() => {
              setSearchTerm('');
              setCategoryFilter('all');
              setRiskFilter('all');
            }}
            className="text-primary-600 hover:text-primary-700 font-medium"
          >
            Clear filters
          </button>
        </div>
      )}
    </div>
  );
};

export default StrategyList;