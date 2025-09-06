import { NextApiRequest, NextApiResponse } from 'next';
import { mockDashboardData, mockBacktestResults, mockPerformanceMetrics, mockTrades, mockEquityCurve } from '@/utils/mockData';

// This API route connects to external backtesting services
// For pure local mock mode, delete this file and keep USE_LOCAL_MOCK=true
export default function handler(req: NextApiRequest, res: NextApiResponse) {
  const { method } = req;

  switch (method) {
    case 'GET':
      return handleGet(req, res);
    case 'POST':
      return handlePost(req, res);
    default:
      res.setHeader('Allow', ['GET', 'POST']);
      res.status(405).end(`Method ${method} Not Allowed`);
  }
}

function handleGet(req: NextApiRequest, res: NextApiResponse) {
  const { endpoint } = req.query;

  switch (endpoint) {
    case 'results':
      return res.status(200).json({ results: mockBacktestResults });
    
    case 'metrics':
      const { id } = req.query;
      if (!id) {
        return res.status(400).json({ error: 'Backtest ID required' });
      }
      return res.status(200).json({ metrics: mockPerformanceMetrics });
    
    case 'trades':
      const { backtestId } = req.query;
      if (!backtestId) {
        return res.status(400).json({ error: 'Backtest ID required' });
      }
      return res.status(200).json({ trades: mockTrades });
    
    case 'equity-curve':
      const { testId } = req.query;
      if (!testId) {
        return res.status(400).json({ error: 'Backtest ID required' });
      }
      return res.status(200).json({ equityCurve: mockEquityCurve });
    
    case 'dashboard':
      return res.status(200).json(mockDashboardData);
    
    default:
      return res.status(404).json({ error: 'Endpoint not found' });
  }
}

function handlePost(req: NextApiRequest, res: NextApiResponse) {
  const { action } = req.body;

  switch (action) {
    case 'run_backtest':
      // Simulate running a new backtest
      const newBacktest = {
        id: Date.now().toString(),
        name: req.body.name || 'New Backtest',
        strategy: req.body.strategy || 'CUSTOM',
        startDate: req.body.startDate || '2024-01-01',
        endDate: req.body.endDate || '2024-12-31',
        initialCapital: req.body.initialCapital || 100000,
        finalValue: 0,
        totalReturn: 0,
        annualizedReturn: 0,
        sharpeRatio: 0,
        maxDrawdown: 0,
        winRate: 0,
        profitFactor: 0,
        totalTrades: 0,
        avgTradeDuration: 0,
        status: 'running' as const,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };
      
      return res.status(201).json({ backtest: newBacktest });
    
    case 'stop_backtest':
      const { id } = req.body;
      if (!id) {
        return res.status(400).json({ error: 'Backtest ID required' });
      }
      
      return res.status(200).json({ 
        message: 'Backtest stopped',
        id: id 
      });
    
    default:
      return res.status(400).json({ error: 'Invalid action' });
  }
}