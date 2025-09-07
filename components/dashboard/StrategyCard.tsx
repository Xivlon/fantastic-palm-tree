import React from 'react';
import { StrategyTemplate } from '@/types/backtest';
import { TrendingUp, TrendingDown, BarChart3, Activity, Settings, Play } from 'lucide-react';

interface StrategyCardProps {
  strategy: StrategyTemplate;
  onSelect?: (strategy: StrategyTemplate) => void;
  onCreateBacktest?: (strategy: StrategyTemplate) => void;
  onEdit?: (strategy: StrategyTemplate) => void;
  isSelected?: boolean;
}

const StrategyCard: React.FC<StrategyCardProps> = ({ 
  strategy, 
  onSelect, 
  onCreateBacktest,
  onEdit,
  isSelected = false 
}) => {
  const getCategoryIcon = (category: StrategyTemplate['category']) => {
    const iconConfig = {
      trend: TrendingUp,
      mean_reversion: TrendingDown,
      momentum: Activity,
      volatility: BarChart3,
      arbitrage: BarChart3,
      custom: Settings,
    };
    return iconConfig[category] || BarChart3;
  };

  const getCategoryColor = (category: StrategyTemplate['category']) => {
    const colorConfig = {
      trend: 'text-blue-600 bg-blue-100',
      mean_reversion: 'text-green-600 bg-green-100',
      momentum: 'text-purple-600 bg-purple-100',
      volatility: 'text-orange-600 bg-orange-100',
      arbitrage: 'text-indigo-600 bg-indigo-100',
      custom: 'text-gray-600 bg-gray-100',
    };
    return colorConfig[category] || 'text-gray-600 bg-gray-100';
  };

  const getRiskColor = (risk: StrategyTemplate['riskLevel']) => {
    const riskConfig = {
      low: 'text-green-700 bg-green-100',
      medium: 'text-yellow-700 bg-yellow-100',
      high: 'text-red-700 bg-red-100',
    };
    return riskConfig[risk];
  };

  const formatPercent = (value: number) => {
    return `${value >= 0 ? '+' : ''}${value.toFixed(1)}%`;
  };

  const CategoryIcon = getCategoryIcon(strategy.category);

  return (
    <div 
      className={`bg-white rounded-lg shadow border-2 transition-all cursor-pointer hover:shadow-md ${
        isSelected ? 'border-primary-500 ring-2 ring-primary-200' : 'border-gray-200 hover:border-gray-300'
      }`}
      onClick={() => onSelect?.(strategy)}
    >
      <div className="p-6">
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center space-x-3">
            <div className={`p-2 rounded-lg ${getCategoryColor(strategy.category)}`}>
              <CategoryIcon className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">{strategy.displayName}</h3>
              <div className="flex items-center space-x-2 mt-1">
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${getRiskColor(strategy.riskLevel)}`}>
                  {strategy.riskLevel.toUpperCase()} RISK
                </span>
                <span className="text-xs text-gray-500">
                  {strategy.category.replace('_', ' ').toUpperCase()}
                </span>
              </div>
            </div>
          </div>
          
          {!strategy.isBuiltIn && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                onEdit?.(strategy);
              }}
              className="p-2 text-gray-400 hover:text-gray-600 transition-colors"
              title="Edit Strategy"
            >
              <Settings className="w-4 h-4" />
            </button>
          )}
        </div>

        {/* Description */}
        <p className="text-sm text-gray-600 mb-4 line-clamp-2">{strategy.description}</p>

        {/* Performance Stats */}
        {strategy.backtestResults && (
          <div className="grid grid-cols-2 gap-4 mb-4">
            <div className="bg-gray-50 rounded-lg p-3">
              <div className="text-xs text-gray-500 mb-1">Avg Return</div>
              <div className={`text-sm font-semibold ${
                strategy.backtestResults.avgReturn >= 0 ? 'text-success-600' : 'text-danger-600'
              }`}>
                {formatPercent(strategy.backtestResults.avgReturn)}
              </div>
            </div>
            <div className="bg-gray-50 rounded-lg p-3">
              <div className="text-xs text-gray-500 mb-1">Sharpe Ratio</div>
              <div className="text-sm font-semibold text-gray-900">
                {strategy.backtestResults.avgSharpe.toFixed(2)}
              </div>
            </div>
            <div className="bg-gray-50 rounded-lg p-3">
              <div className="text-xs text-gray-500 mb-1">Win Rate</div>
              <div className="text-sm font-semibold text-gray-900">
                {(strategy.backtestResults.winRate * 100).toFixed(0)}%
              </div>
            </div>
            <div className="bg-gray-50 rounded-lg p-3">
              <div className="text-xs text-gray-500 mb-1">Backtests</div>
              <div className="text-sm font-semibold text-gray-900">
                {strategy.backtestResults.count}
              </div>
            </div>
          </div>
        )}

        {/* Timeframes & Assets */}
        <div className="space-y-2 mb-4">
          <div>
            <span className="text-xs text-gray-500">Timeframes: </span>
            <span className="text-xs text-gray-700">
              {strategy.timeframe.slice(0, 3).join(', ')}
              {strategy.timeframe.length > 3 && ` +${strategy.timeframe.length - 3} more`}
            </span>
          </div>
          <div>
            <span className="text-xs text-gray-500">Assets: </span>
            <span className="text-xs text-gray-700">
              {strategy.assets.join(', ')}
            </span>
          </div>
        </div>

        {/* Actions */}
        <div className="flex space-x-2">
          <button
            onClick={(e) => {
              e.stopPropagation();
              onCreateBacktest?.(strategy);
            }}
            className="flex-1 bg-primary-600 hover:bg-primary-700 text-white px-3 py-2 rounded-md text-sm font-medium transition-colors flex items-center justify-center space-x-1"
          >
            <Play className="w-4 h-4" />
            <span>Run Backtest</span>
          </button>
          <button
            onClick={(e) => {
              e.stopPropagation();
              onSelect?.(strategy);
            }}
            className="px-3 py-2 border border-gray-300 text-gray-700 rounded-md text-sm font-medium hover:bg-gray-50 transition-colors"
          >
            Details
          </button>
        </div>
      </div>
    </div>
  );
};

export default StrategyCard;