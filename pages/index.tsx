import React from 'react';
import Link from 'next/link';
import Layout from '@/components/layout/Layout';
import { Activity, BarChart3, TrendingUp, Clock } from 'lucide-react';

const HomePage: React.FC = () => {
  return (
    <Layout title="Fantastic Palm Tree - Advanced Backtesting Framework">
      <div className="px-4 py-8">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Fantastic Palm Tree
          </h1>
          <p className="text-xl text-gray-600 mb-8">
            Advanced Backtesting Framework for Professional Trading Strategies
          </p>
          <div className="flex justify-center space-x-4">
            <Link
              href="/dashboard"
              className="bg-primary-600 hover:bg-primary-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
            >
              Open Dashboard
            </Link>
            <Link
              href="/dashboard/backtests"
              className="bg-white hover:bg-gray-50 text-gray-900 border border-gray-300 px-6 py-3 rounded-lg font-medium transition-colors"
            >
              View Backtests
            </Link>
          </div>
        </div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
          <div className="bg-white rounded-lg shadow p-6 text-center">
            <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mx-auto mb-4">
              <BarChart3 className="w-6 h-6 text-primary-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Comprehensive Backtesting
            </h3>
            <p className="text-gray-600 text-sm">
              Full-featured backtesting with realistic market simulation and order management
            </p>
          </div>

          <div className="bg-white rounded-lg shadow p-6 text-center">
            <div className="w-12 h-12 bg-success-100 rounded-lg flex items-center justify-center mx-auto mb-4">
              <TrendingUp className="w-6 h-6 text-success-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Professional Metrics
            </h3>
            <p className="text-gray-600 text-sm">
              20+ metrics including Sharpe ratio, Sortino ratio, VaR, and detailed trade statistics
            </p>
          </div>

          <div className="bg-white rounded-lg shadow p-6 text-center">
            <div className="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center mx-auto mb-4">
              <Activity className="w-6 h-6 text-yellow-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Real-time Dashboard
            </h3>
            <p className="text-gray-600 text-sm">
              Interactive dashboard with live charts, equity curves, and performance monitoring
            </p>
          </div>

          <div className="bg-white rounded-lg shadow p-6 text-center">
            <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mx-auto mb-4">
              <Clock className="w-6 h-6 text-purple-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Historical Analysis
            </h3>
            <p className="text-gray-600 text-sm">
              Detailed historical trade analysis with drawdown tracking and risk management
            </p>
          </div>
        </div>

        {/* Quick Start */}
        <div className="bg-white rounded-lg shadow p-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Quick Start Guide</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="space-y-4">
              <div className="w-8 h-8 bg-primary-600 text-white rounded-full flex items-center justify-center font-bold">
                1
              </div>
              <h3 className="text-lg font-semibold text-gray-900">Setup Strategy</h3>
              <p className="text-gray-600">
                Configure your trading strategy parameters, risk management rules, and backtesting period.
              </p>
            </div>

            <div className="space-y-4">
              <div className="w-8 h-8 bg-primary-600 text-white rounded-full flex items-center justify-center font-bold">
                2
              </div>
              <h3 className="text-lg font-semibold text-gray-900">Run Backtest</h3>
              <p className="text-gray-600">
                Execute the backtest with historical market data and monitor real-time progress.
              </p>
            </div>

            <div className="space-y-4">
              <div className="w-8 h-8 bg-primary-600 text-white rounded-full flex items-center justify-center font-bold">
                3
              </div>
              <h3 className="text-lg font-semibold text-gray-900">Analyze Results</h3>
              <p className="text-gray-600">
                Review comprehensive metrics, equity curves, trade statistics, and risk analysis.
              </p>
            </div>
          </div>
        </div>

        {/* Development Mode Notice */}
        {process.env.USE_LOCAL_MOCK === 'true' && (
          <div className="mt-8 bg-yellow-50 border border-yellow-200 rounded-lg p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <Activity className="w-5 h-5 text-yellow-600" />
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-yellow-800">
                  Development Mode Active
                </h3>
                <div className="mt-2 text-sm text-yellow-700">
                  <p>
                    The dashboard is running in local mock mode with sample data. 
                    To enable full backend integration, set <code className="bg-yellow-100 px-1 rounded">USE_LOCAL_MOCK=false</code> 
                    and ensure your Python backtesting service is running.
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
};

export default HomePage;