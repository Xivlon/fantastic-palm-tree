import React from 'react';
import { PerformanceMetrics } from '@/types/backtest';

interface MetricsCardProps {
  metrics: PerformanceMetrics;
}

const MetricsCard: React.FC<MetricsCardProps> = ({ metrics }) => {
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

  const formatNumber = (value: number, decimals: number = 2) => {
    return value.toFixed(decimals);
  };

  const getColorClass = (value: number, isInverse: boolean = false) => {
    if (isInverse) {
      return value < 0 ? 'text-success-600' : 'text-danger-600';
    }
    return value >= 0 ? 'text-success-600' : 'text-danger-600';
  };

  const metricGroups = [
    {
      title: 'Returns',
      metrics: [
        { label: 'Total Return', value: formatPercent(metrics.totalReturn), color: getColorClass(metrics.totalReturn) },
        { label: 'Annualized Return', value: formatPercent(metrics.annualizedReturn), color: getColorClass(metrics.annualizedReturn) },
        { label: 'Volatility', value: formatPercent(metrics.volatility), color: 'text-gray-900' },
      ]
    },
    {
      title: 'Risk Metrics',
      metrics: [
        { label: 'Sharpe Ratio', value: formatNumber(metrics.sharpeRatio), color: getColorClass(metrics.sharpeRatio) },
        { label: 'Sortino Ratio', value: formatNumber(metrics.sortinoRatio), color: getColorClass(metrics.sortinoRatio) },
        { label: 'Calmar Ratio', value: formatNumber(metrics.calmarRatio), color: getColorClass(metrics.calmarRatio) },
        { label: 'Max Drawdown', value: formatPercent(metrics.maxDrawdown), color: getColorClass(metrics.maxDrawdown, true) },
      ]
    },
    {
      title: 'Trade Statistics',
      metrics: [
        { label: 'Total Trades', value: metrics.totalTrades.toString(), color: 'text-gray-900' },
        { label: 'Win Rate', value: formatPercent(metrics.winRate * 100), color: getColorClass(metrics.winRate) },
        { label: 'Profit Factor', value: formatNumber(metrics.profitFactor), color: getColorClass(metrics.profitFactor - 1) },
        { label: 'Expected Value', value: formatCurrency(metrics.expectedValue), color: getColorClass(metrics.expectedValue) },
      ]
    },
    {
      title: 'Trade Analysis',
      metrics: [
        { label: 'Avg Win', value: formatCurrency(metrics.avgWin), color: 'text-success-600' },
        { label: 'Avg Loss', value: formatCurrency(metrics.avgLoss), color: 'text-danger-600' },
        { label: 'Largest Win', value: formatCurrency(metrics.largestWin), color: 'text-success-600' },
        { label: 'Largest Loss', value: formatCurrency(metrics.largestLoss), color: 'text-danger-600' },
      ]
    }
  ];

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-6">Performance Metrics</h3>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {metricGroups.map((group, groupIndex) => (
          <div key={groupIndex} className="space-y-4">
            <h4 className="text-sm font-medium text-gray-500 uppercase tracking-wider">
              {group.title}
            </h4>
            <div className="space-y-3">
              {group.metrics.map((metric, metricIndex) => (
                <div key={metricIndex} className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">{metric.label}</span>
                  <span className={`text-sm font-medium ${metric.color}`}>
                    {metric.value}
                  </span>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default MetricsCard;