import React, { useState, useEffect } from 'react';
import Layout from '@/components/layout/Layout';
import BacktestList from '@/components/dashboard/BacktestList';
import MetricsCard from '@/components/dashboard/MetricsCard';
import EquityCurveChart from '@/components/charts/EquityCurveChart';
import DrawdownChart from '@/components/charts/DrawdownChart';
import TradeTable from '@/components/dashboard/TradeTable';
import { BacktestResult, PerformanceMetrics, Trade, EquityCurvePoint } from '@/types/backtest';
import { mockBacktestResults, mockPerformanceMetrics, mockTrades, mockEquityCurve } from '@/utils/mockData';
import { Search, Filter, Download, BarChart3, TrendingUp, Activity } from 'lucide-react';

const BacktestsPage: React.FC = () => {
  const [backtests, setBacktests] = useState<BacktestResult[]>(mockBacktestResults);
  const [selectedBacktest, setSelectedBacktest] = useState<BacktestResult | null>(null);
  const [metrics, setMetrics] = useState<PerformanceMetrics | null>(null);
  const [trades, setTrades] = useState<Trade[]>([]);
  const [equityCurve, setEquityCurve] = useState<EquityCurvePoint[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<'all' | 'completed' | 'running' | 'failed'>('all');
  const [sortBy, setSortBy] = useState<'date' | 'return' | 'sharpe'>('date');

  // Filter and sort backtests
  const filteredBacktests = backtests
    .filter(backtest => {
      const matchesSearch = backtest.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           backtest.strategy.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesStatus = statusFilter === 'all' || backtest.status === statusFilter;
      return matchesSearch && matchesStatus;
    })
    .sort((a, b) => {
      switch (sortBy) {
        case 'return':
          return b.totalReturn - a.totalReturn;
        case 'sharpe':
          return b.sharpeRatio - a.sharpeRatio;
        case 'date':
        default:
          return new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime();
      }
    });

  useEffect(() => {
    // Set initial selected backtest
    if (filteredBacktests.length > 0 && !selectedBacktest) {
      setSelectedBacktest(filteredBacktests[0]);
    }
  }, [filteredBacktests, selectedBacktest]);

  useEffect(() => {
    // Load data for selected backtest
    if (selectedBacktest) {
      // In a real app, this would fetch data for the specific backtest
      setMetrics(mockPerformanceMetrics);
      setTrades(mockTrades);
      setEquityCurve(mockEquityCurve);
    }
  }, [selectedBacktest]);

  const handleBacktestSelect = (backtest: BacktestResult) => {
    setSelectedBacktest(backtest);
  };

  const handleExport = () => {
    if (selectedBacktest) {
      console.log('Exporting backtest:', selectedBacktest.id);
      // Implementation for export functionality
    }
  };

  return (
    <Layout title="Backtests - Fantastic Palm Tree">
      <div className="px-4">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Backtest Analysis</h1>
            <p className="text-gray-600 mt-1">
              Comprehensive analysis and comparison of your trading strategy backtests
            </p>
          </div>
          
          <div className="flex space-x-4">
            <button
              onClick={handleExport}
              disabled={!selectedBacktest}
              className="bg-gray-600 hover:bg-gray-700 disabled:opacity-50 text-white px-4 py-2 rounded-lg font-medium transition-colors flex items-center space-x-2"
            >
              <Download className="w-4 h-4" />
              <span>Export</span>
            </button>
          </div>
        </div>

        {/* Search and Filters */}
        <div className="bg-white rounded-lg shadow mb-6 p-6">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between space-y-4 md:space-y-0 md:space-x-4">
            {/* Search */}
            <div className="flex-1 max-w-md">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                <input
                  type="text"
                  placeholder="Search backtests..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
              </div>
            </div>

            {/* Filters */}
            <div className="flex space-x-4">
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value as any)}
                className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              >
                <option value="all">All Status</option>
                <option value="completed">Completed</option>
                <option value="running">Running</option>
                <option value="failed">Failed</option>
              </select>

              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as any)}
                className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              >
                <option value="date">Sort by Date</option>
                <option value="return">Sort by Return</option>
                <option value="sharpe">Sort by Sharpe Ratio</option>
              </select>
            </div>
          </div>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <BarChart3 className="w-8 h-8 text-primary-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Total Backtests</p>
                <p className="text-2xl font-bold text-gray-900">{backtests.length}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <Activity className="w-8 h-8 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Completed</p>
                <p className="text-2xl font-bold text-gray-900">
                  {backtests.filter(b => b.status === 'completed').length}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <TrendingUp className="w-8 h-8 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Avg Return</p>
                <p className="text-2xl font-bold text-gray-900">
                  {(backtests.reduce((sum, b) => sum + b.totalReturn, 0) / backtests.length).toFixed(1)}%
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <Activity className="w-8 h-8 text-purple-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Best Sharpe</p>
                <p className="text-2xl font-bold text-gray-900">
                  {Math.max(...backtests.map(b => b.sharpeRatio)).toFixed(2)}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Backtest List */}
          <div className="lg:col-span-1">
            <BacktestList
              backtests={filteredBacktests}
              onSelect={handleBacktestSelect}
              selectedId={selectedBacktest?.id}
            />
          </div>

          {/* Detailed Analysis */}
          <div className="lg:col-span-2 space-y-8">
            {selectedBacktest ? (
              <>
                {/* Selected Backtest Header */}
                <div className="bg-white rounded-lg shadow p-6">
                  <h2 className="text-xl font-bold text-gray-900 mb-2">
                    {selectedBacktest.name}
                  </h2>
                  <p className="text-gray-600 mb-4">
                    Strategy: {selectedBacktest.strategy} | 
                    Period: {new Date(selectedBacktest.startDate).toLocaleDateString()} - {new Date(selectedBacktest.endDate).toLocaleDateString()}
                  </p>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div>
                      <span className="text-gray-500">Initial Capital:</span>
                      <p className="font-semibold">${selectedBacktest.initialCapital.toLocaleString()}</p>
                    </div>
                    <div>
                      <span className="text-gray-500">Final Value:</span>
                      <p className="font-semibold">${selectedBacktest.finalValue.toLocaleString()}</p>
                    </div>
                    <div>
                      <span className="text-gray-500">Total Return:</span>
                      <p className={`font-semibold ${selectedBacktest.totalReturn >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {selectedBacktest.totalReturn >= 0 ? '+' : ''}{selectedBacktest.totalReturn.toFixed(2)}%
                      </p>
                    </div>
                    <div>
                      <span className="text-gray-500">Sharpe Ratio:</span>
                      <p className="font-semibold">{selectedBacktest.sharpeRatio.toFixed(2)}</p>
                    </div>
                  </div>
                </div>

                {/* Performance Metrics */}
                {metrics && (
                  <MetricsCard metrics={metrics} />
                )}

                {/* Charts */}
                <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
                  <div className="bg-white rounded-lg shadow p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Equity Curve</h3>
                    <EquityCurveChart data={equityCurve} />
                  </div>
                  
                  <div className="bg-white rounded-lg shadow p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Drawdown Analysis</h3>
                    <DrawdownChart data={equityCurve} />
                  </div>
                </div>

                {/* Trade Analysis */}
                <div className="bg-white rounded-lg shadow">
                  <div className="px-6 py-4 border-b border-gray-200">
                    <h3 className="text-lg font-semibold text-gray-900">Trade Analysis</h3>
                  </div>
                  <TradeTable trades={trades} />
                </div>
              </>
            ) : (
              <div className="bg-white rounded-lg shadow p-12 text-center">
                <BarChart3 className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  Select a Backtest
                </h3>
                <p className="text-gray-500">
                  Choose a backtest from the list to view detailed analysis and performance metrics.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default BacktestsPage;