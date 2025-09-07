import React, { useState, useEffect } from 'react';
import Layout from '@/components/layout/Layout';
import StrategyList from '@/components/dashboard/StrategyList';
import { StrategyTemplate, StrategyInstance } from '@/types/backtest';
import { mockStrategyTemplates, mockStrategyInstances } from '@/utils/mockData';
import { Settings, TrendingUp, Users, BookOpen, BarChart3, Activity } from 'lucide-react';

const StrategiesPage: React.FC = () => {
  const [strategies, setStrategies] = useState<StrategyTemplate[]>([]);
  const [instances, setInstances] = useState<StrategyInstance[]>([]);
  const [selectedStrategy, setSelectedStrategy] = useState<StrategyTemplate | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Load strategies data
    const loadStrategies = async () => {
      setIsLoading(true);
      
      // Simulate API call - in real app this would fetch from backend
      try {
        // For now, use mock data
        setStrategies(mockStrategyTemplates);
        setInstances(mockStrategyInstances);
      } catch (error) {
        console.error('Failed to load strategies:', error);
      } finally {
        setIsLoading(false);
      }
    };

    loadStrategies();
  }, []);

  const handleSelectStrategy = (strategy: StrategyTemplate) => {
    setSelectedStrategy(strategy);
  };

  const handleCreateBacktest = (strategy: StrategyTemplate) => {
    // Navigate to create backtest page with strategy pre-selected
    console.log('Creating backtest for strategy:', strategy.name);
    // In a real app: router.push(`/dashboard/backtests/create?strategy=${strategy.id}`);
  };

  const handleEditStrategy = (strategy: StrategyTemplate) => {
    // Navigate to strategy editor
    console.log('Editing strategy:', strategy.name);
    // In a real app: router.push(`/dashboard/strategies/edit/${strategy.id}`);
  };

  const handleCreateStrategy = () => {
    // Navigate to strategy creation page
    console.log('Creating new strategy');
    // In a real app: router.push('/dashboard/strategies/create');
  };

  const getCategoryStats = () => {
    const stats = strategies.reduce((acc, strategy) => {
      acc[strategy.category] = (acc[strategy.category] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    return [
      { label: 'Trend Following', count: stats.trend || 0, icon: TrendingUp, color: 'text-blue-600' },
      { label: 'Mean Reversion', count: stats.mean_reversion || 0, icon: Activity, color: 'text-green-600' },
      { label: 'Momentum', count: stats.momentum || 0, icon: BarChart3, color: 'text-purple-600' },
      { label: 'Volatility', count: stats.volatility || 0, icon: BarChart3, color: 'text-orange-600' },
    ];
  };

  const activeInstances = instances.filter(i => i.status === 'active').length;
  const totalBacktests = instances.reduce((sum, instance) => sum + instance.backtestCount, 0);

  if (isLoading) {
    return (
      <Layout title="Strategies - Fantastic Palm Tree">
        <div className="px-4">
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout title="Strategies - Fantastic Palm Tree">
      <div className="px-4">
        {/* Overview Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="p-2 bg-primary-100 rounded-lg">
                <BookOpen className="w-6 h-6 text-primary-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Strategies</p>
                <p className="text-2xl font-bold text-gray-900">{strategies.length}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="p-2 bg-green-100 rounded-lg">
                <Settings className="w-6 h-6 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Active Instances</p>
                <p className="text-2xl font-bold text-gray-900">{activeInstances}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="p-2 bg-blue-100 rounded-lg">
                <BarChart3 className="w-6 h-6 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Backtests</p>
                <p className="text-2xl font-bold text-gray-900">{totalBacktests}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="p-2 bg-purple-100 rounded-lg">
                <Users className="w-6 h-6 text-purple-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Categories</p>
                <p className="text-2xl font-bold text-gray-900">{getCategoryStats().filter(s => s.count > 0).length}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Category Breakdown */}
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Strategy Categories</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {getCategoryStats().map((category, index) => (
              <div key={index} className="flex items-center space-x-3">
                <category.icon className={`w-5 h-5 ${category.color}`} />
                <div>
                  <p className="text-sm font-medium text-gray-900">{category.label}</p>
                  <p className="text-xs text-gray-500">{category.count} strategies</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Strategy List */}
        <StrategyList
          strategies={strategies}
          onSelectStrategy={handleSelectStrategy}
          onCreateBacktest={handleCreateBacktest}
          onEditStrategy={handleEditStrategy}
          onCreateStrategy={handleCreateStrategy}
          selectedStrategyId={selectedStrategy?.id}
        />

        {/* Strategy Details Modal/Panel - Could be implemented later */}
        {selectedStrategy && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-auto">
              <div className="p-6">
                <div className="flex justify-between items-start mb-4">
                  <h2 className="text-xl font-bold text-gray-900">{selectedStrategy.displayName}</h2>
                  <button
                    onClick={() => setSelectedStrategy(null)}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    ×
                  </button>
                </div>
                
                <div className="space-y-4">
                  <div>
                    <h3 className="font-medium text-gray-900 mb-2">Description</h3>
                    <p className="text-gray-600">{selectedStrategy.description}</p>
                  </div>
                  
                  <div>
                    <h3 className="font-medium text-gray-900 mb-2">Parameters</h3>
                    <div className="space-y-2">
                      {selectedStrategy.parameters.map((param, index) => (
                        <div key={index} className="bg-gray-50 p-3 rounded">
                          <div className="flex justify-between items-start">
                            <div>
                              <p className="font-medium text-sm">{param.displayName}</p>
                              <p className="text-xs text-gray-600">{param.description}</p>
                            </div>
                            <span className="text-sm text-gray-900">
                              Default: {param.defaultValue?.toString()}
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
                
                <div className="flex space-x-3 mt-6">
                  <button
                    onClick={() => handleCreateBacktest(selectedStrategy)}
                    className="flex-1 bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-md font-medium"
                  >
                    Run Backtest
                  </button>
                  <button
                    onClick={() => setSelectedStrategy(null)}
                    className="px-4 py-2 border border-gray-300 text-gray-700 rounded-md font-medium hover:bg-gray-50"
                  >
                    Close
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
};

export default StrategiesPage;