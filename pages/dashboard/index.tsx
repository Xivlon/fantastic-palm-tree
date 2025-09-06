import React, { useState, useEffect } from 'react';
import Layout from '@/components/layout/Layout';
import MetricsCard from '@/components/dashboard/MetricsCard';
import EquityCurveChart from '@/components/charts/EquityCurveChart';
import DrawdownChart from '@/components/charts/DrawdownChart';
import BacktestList from '@/components/dashboard/BacktestList';
import TradeTable from '@/components/dashboard/TradeTable';
import { DashboardData, BacktestResult } from '@/types/backtest';
import { mockDashboardData } from '@/utils/mockData';
import { Activity, RefreshCw } from 'lucide-react';

const DashboardPage: React.FC = () => {
  const [data, setData] = useState<DashboardData>(mockDashboardData);
  const [selectedBacktest, setSelectedBacktest] = useState<BacktestResult | null>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [isRunningBacktest, setIsRunningBacktest] = useState(false);

  useEffect(() => {
    // Set initial selected backtest
    if (data.results.length > 0 && !selectedBacktest) {
      setSelectedBacktest(data.results[0]);
    }
  }, [data.results, selectedBacktest]);

  useEffect(() => {
    // Load initial data from backend or mock
    const loadInitialData = async () => {
      if (process.env.USE_LOCAL_MOCK === 'true') {
        setData({ ...mockDashboardData });
      } else {
        try {
          const response = await fetch('http://localhost:8000/api/backtest?endpoint=dashboard');
          if (response.ok) {
            const freshData = await response.json();
            setData(freshData);
            console.log('✅ Initial data loaded from Python backend');
          } else {
            throw new Error(`HTTP error! status: ${response.status}`);
          }
        } catch (error) {
          console.error('❌ Failed to load from Python backend, using mock data:', error);
          setData({ ...mockDashboardData });
        }
      }
    };

    loadInitialData();
  }, []); // Run once on mount

  const handleRefresh = async () => {
    setIsRefreshing(true);
    
    // Simulate API call delay
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Check if we should use local mock or connect to Python backend
    if (process.env.USE_LOCAL_MOCK === 'true') {
      setData({ ...mockDashboardData });
    } else {
      // Connect to Python backend API
      try {
        const response = await fetch('http://localhost:8000/api/backtest?endpoint=dashboard');
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const freshData = await response.json();
        setData(freshData);
        console.log('✅ Successfully connected to Python backend:', freshData.results?.length || 0, 'backtests loaded');
      } catch (error) {
        console.error('❌ Failed to connect to Python backend, falling back to mock data:', error);
        // Fallback to mock data if Python backend is not available
        setData({ ...mockDashboardData });
      }
    }
    
    setIsRefreshing(false);
  };

  const handleBacktestSelect = (backtest: BacktestResult) => {
    setSelectedBacktest(backtest);
  };

  const handleRunNewBacktest = async () => {
    if (process.env.USE_LOCAL_MOCK === 'true') {
      console.log('Mock mode - would run new backtest');
      return;
    }

    setIsRunningBacktest(true);
    try {
      const response = await fetch('http://localhost:8000/api/backtest', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: `ATR Strategy ${new Date().toLocaleTimeString()}`,
          strategy: 'ATR_BREAKOUT',
          startDate: '2023-01-01',
          endDate: '2023-12-31',
          initialCapital: 100000,
          parameters: {
            atr_period: 14
          }
        })
      });

      if (response.ok) {
        const result = await response.json();
        console.log('✅ New backtest started:', result.backtest.id);
        
        // Refresh data to show the new running backtest
        setTimeout(() => {
          handleRefresh();
        }, 1000);
      } else {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
    } catch (error) {
      console.error('❌ Failed to start new backtest:', error);
    }
    setIsRunningBacktest(false);
  };

  return (
    <Layout title="Dashboard - Fantastic Palm Tree">
      <div className="px-4">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Backtesting Dashboard</h1>
            <p className="text-gray-600 mt-1">
              Monitor your trading strategies and analyze performance metrics
            </p>
            <div className="mt-2 flex items-center space-x-2">
              <div className={`px-2 py-1 rounded-full text-xs font-medium ${
                process.env.USE_LOCAL_MOCK === 'true' 
                  ? 'bg-yellow-100 text-yellow-800' 
                  : 'bg-green-100 text-green-800'
              }`}>
                {process.env.USE_LOCAL_MOCK === 'true' ? '🔄 Mock Data Mode' : '🔥 Live Backend Connected'}
              </div>
            </div>
          </div>
          
          <div className="space-x-4">
            <button
              onClick={handleRunNewBacktest}
              disabled={isRunningBacktest}
              className="bg-success-600 hover:bg-success-700 disabled:opacity-50 text-white px-4 py-2 rounded-lg font-medium transition-colors"
            >
              {isRunningBacktest ? 'Running...' : 'Run New Backtest'}
            </button>
            
            <button
              onClick={handleRefresh}
              disabled={isRefreshing}
              className="bg-primary-600 hover:bg-primary-700 disabled:opacity-50 text-white px-4 py-2 rounded-lg font-medium transition-colors flex items-center space-x-2"
            >
              <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} />
              <span>Refresh</span>
            </button>
          </div>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <Activity className="w-8 h-8 text-primary-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Total Backtests</p>
                <p className="text-2xl font-bold text-gray-900">{data.results.length}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <Activity className="w-8 h-8 text-success-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Running</p>
                <p className="text-2xl font-bold text-gray-900">
                  {data.results.filter(r => r.status === 'running').length}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <Activity className="w-8 h-8 text-success-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Completed</p>
                <p className="text-2xl font-bold text-gray-900">
                  {data.results.filter(r => r.status === 'completed').length}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <Activity className="w-8 h-8 text-danger-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Failed</p>
                <p className="text-2xl font-bold text-gray-900">
                  {data.results.filter(r => r.status === 'failed').length}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column - Backtest List */}
          <div className="lg:col-span-1">
            <BacktestList
              backtests={data.results}
              onSelect={handleBacktestSelect}
              selectedId={selectedBacktest?.id}
            />
          </div>

          {/* Right Column - Details */}
          <div className="lg:col-span-2 space-y-8">
            {selectedBacktest && (
              <>
                {/* Selected Backtest Header */}
                <div className="bg-white rounded-lg shadow p-6">
                  <h2 className="text-xl font-bold text-gray-900 mb-2">
                    {selectedBacktest.name}
                  </h2>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div>
                      <p className="text-gray-500">Strategy</p>
                      <p className="font-medium">{selectedBacktest.strategy}</p>
                    </div>
                    <div>
                      <p className="text-gray-500">Period</p>
                      <p className="font-medium">
                        {new Date(selectedBacktest.startDate).toLocaleDateString()} - 
                        {new Date(selectedBacktest.endDate).toLocaleDateString()}
                      </p>
                    </div>
                    <div>
                      <p className="text-gray-500">Total Return</p>
                      <p className={`font-medium ${
                        selectedBacktest.totalReturn >= 0 ? 'text-success-600' : 'text-danger-600'
                      }`}>
                        {selectedBacktest.totalReturn >= 0 ? '+' : ''}{selectedBacktest.totalReturn.toFixed(2)}%
                      </p>
                    </div>
                    <div>
                      <p className="text-gray-500">Sharpe Ratio</p>
                      <p className="font-medium">{selectedBacktest.sharpeRatio.toFixed(2)}</p>
                    </div>
                  </div>
                </div>

                {/* Performance Metrics */}
                {data.metrics && <MetricsCard metrics={data.metrics} />}

                {/* Charts */}
                <div className="space-y-6">
                  {data.equityCurve && (
                    <div className="bg-white rounded-lg shadow p-6">
                      <h3 className="text-lg font-semibold text-gray-900 mb-4">Equity Curve</h3>
                      <EquityCurveChart data={data.equityCurve} />
                    </div>
                  )}

                  {data.equityCurve && (
                    <div className="bg-white rounded-lg shadow p-6">
                      <h3 className="text-lg font-semibold text-gray-900 mb-4">Drawdown Analysis</h3>
                      <DrawdownChart data={data.equityCurve} />
                    </div>
                  )}
                </div>

                {/* Recent Trades */}
                {data.trades && <TradeTable trades={data.trades} maxRows={5} />}
              </>
            )}
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default DashboardPage;