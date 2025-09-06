import React from 'react';
import { BacktestResult } from '@/types/backtest';
import { Calendar, TrendingUp, TrendingDown, Activity } from 'lucide-react';

interface BacktestListProps {
  backtests: BacktestResult[];
  onSelect?: (backtest: BacktestResult) => void;
  selectedId?: string;
}

const BacktestList: React.FC<BacktestListProps> = ({ backtests, onSelect, selectedId }) => {
  const formatPercent = (value: number) => {
    return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  const getStatusBadge = (status: BacktestResult['status']) => {
    const statusConfig = {
      running: { bg: 'bg-yellow-100', text: 'text-yellow-800', icon: Activity },
      completed: { bg: 'bg-green-100', text: 'text-green-800', icon: TrendingUp },
      failed: { bg: 'bg-red-100', text: 'text-red-800', icon: TrendingDown },
    };

    const config = statusConfig[status];
    const Icon = config.icon;

    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${config.bg} ${config.text}`}>
        <Icon className="w-3 h-3 mr-1" />
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </span>
    );
  };

  const getReturnColor = (totalReturn: number) => {
    return totalReturn >= 0 ? 'text-success-600' : 'text-danger-600';
  };

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="px-6 py-4 border-b border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900">Recent Backtests</h3>
      </div>
      
      <div className="divide-y divide-gray-200">
        {backtests.length === 0 ? (
          <div className="px-6 py-8 text-center">
            <p className="text-gray-500">No backtests found</p>
          </div>
        ) : (
          backtests.map((backtest) => (
            <div
              key={backtest.id}
              className={`px-6 py-4 cursor-pointer hover:bg-gray-50 transition-colors ${
                selectedId === backtest.id ? 'bg-primary-50 border-l-4 border-primary-600' : ''
              }`}
              onClick={() => onSelect?.(backtest)}
            >
              <div className="flex items-center justify-between">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="text-sm font-medium text-gray-900 truncate">
                      {backtest.name}
                    </h4>
                    {getStatusBadge(backtest.status)}
                  </div>
                  
                  <div className="flex items-center text-sm text-gray-500 space-x-4">
                    <span className="flex items-center">
                      <Calendar className="w-4 h-4 mr-1" />
                      {formatDate(backtest.startDate)} - {formatDate(backtest.endDate)}
                    </span>
                    <span>{backtest.strategy}</span>
                  </div>
                  
                  <div className="mt-2 flex items-center justify-between">
                    <div className="flex space-x-4 text-sm">
                      <span className="text-gray-600">
                        Initial: {formatCurrency(backtest.initialCapital)}
                      </span>
                      <span className="text-gray-600">
                        Final: {formatCurrency(backtest.finalValue)}
                      </span>
                    </div>
                    
                    <div className="flex items-center space-x-3">
                      <span className={`text-sm font-medium ${getReturnColor(backtest.totalReturn)}`}>
                        {formatPercent(backtest.totalReturn)}
                      </span>
                      <span className="text-sm text-gray-500">
                        Sharpe: {backtest.sharpeRatio.toFixed(2)}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default BacktestList;