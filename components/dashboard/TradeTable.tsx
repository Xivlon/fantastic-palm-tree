import React from 'react';
import { Trade } from '@/types/backtest';
import { ArrowUp, ArrowDown, Clock, DollarSign } from 'lucide-react';

interface TradeTableProps {
  trades: Trade[];
  maxRows?: number;
}

const TradeTable: React.FC<TradeTableProps> = ({ trades, maxRows = 10 }) => {
  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(value);
  };

  const formatPercent = (value: number) => {
    return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getSideIcon = (side: 'long' | 'short') => {
    return side === 'long' ? (
      <ArrowUp className="w-4 h-4 text-success-600" />
    ) : (
      <ArrowDown className="w-4 h-4 text-danger-600" />
    );
  };

  const getSideColor = (side: 'long' | 'short') => {
    return side === 'long' ? 'text-success-600' : 'text-danger-600';
  };

  const getPnLColor = (pnl: number) => {
    return pnl >= 0 ? 'text-success-600' : 'text-danger-600';
  };

  const getStatusBadge = (status: 'open' | 'closed') => {
    const config = {
      open: { bg: 'bg-blue-100', text: 'text-blue-800' },
      closed: { bg: 'bg-gray-100', text: 'text-gray-800' },
    };

    const { bg, text } = config[status];

    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${bg} ${text}`}>
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </span>
    );
  };

  const displayTrades = maxRows ? trades.slice(0, maxRows) : trades;

  return (
    <div className="bg-white rounded-lg shadow overflow-hidden">
      <div className="px-6 py-4 border-b border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900">Recent Trades</h3>
      </div>
      
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Symbol
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Side
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Entry
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Exit
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Quantity
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                P&L
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Duration
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {displayTrades.length === 0 ? (
              <tr>
                <td colSpan={8} className="px-6 py-8 text-center text-gray-500">
                  No trades found
                </td>
              </tr>
            ) : (
              displayTrades.map((trade) => (
                <tr key={trade.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {trade.symbol}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <div className={`flex items-center ${getSideColor(trade.side)}`}>
                      {getSideIcon(trade.side)}
                      <span className="ml-1 capitalize">{trade.side}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    <div>
                      <div className="font-medium">{formatCurrency(trade.entryPrice)}</div>
                      <div className="text-gray-500 text-xs">{formatDate(trade.entryDate)}</div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {trade.exitPrice ? (
                      <div>
                        <div className="font-medium">{formatCurrency(trade.exitPrice)}</div>
                        <div className="text-gray-500 text-xs">
                          {trade.exitDate ? formatDate(trade.exitDate) : '-'}
                        </div>
                      </div>
                    ) : (
                      <span className="text-gray-400">-</span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {trade.quantity}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    {trade.pnl !== undefined ? (
                      <div>
                        <div className={`font-medium ${getPnLColor(trade.pnl)}`}>
                          {formatCurrency(trade.pnl)}
                        </div>
                        {trade.pnlPercent !== undefined && (
                          <div className={`text-xs ${getPnLColor(trade.pnl)}`}>
                            {formatPercent(trade.pnlPercent)}
                          </div>
                        )}
                      </div>
                    ) : (
                      <span className="text-gray-400">-</span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {trade.duration ? (
                      <div className="flex items-center">
                        <Clock className="w-4 h-4 mr-1 text-gray-400" />
                        {trade.duration}d
                      </div>
                    ) : (
                      <span className="text-gray-400">-</span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {getStatusBadge(trade.status)}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
      
      {trades.length > maxRows && (
        <div className="px-6 py-3 bg-gray-50 border-t border-gray-200">
          <p className="text-sm text-gray-500">
            Showing {maxRows} of {trades.length} trades
          </p>
        </div>
      )}
    </div>
  );
};

export default TradeTable;