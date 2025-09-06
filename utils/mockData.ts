import { BacktestResult, PerformanceMetrics, Trade, EquityCurvePoint, DashboardData } from '@/types/backtest';

// Mock data for development
export const mockBacktestResults: BacktestResult[] = [
  {
    id: '1',
    name: 'Moving Average Crossover',
    strategy: 'SMA_CROSSOVER',
    startDate: '2023-01-01',
    endDate: '2023-12-31',
    initialCapital: 100000,
    finalValue: 125000,
    totalReturn: 25.0,
    annualizedReturn: 22.5,
    sharpeRatio: 1.45,
    maxDrawdown: -8.2,
    winRate: 0.62,
    profitFactor: 1.8,
    totalTrades: 145,
    avgTradeDuration: 7.2,
    status: 'completed',
    createdAt: '2023-01-01T00:00:00Z',
    updatedAt: '2023-12-31T23:59:59Z',
  },
  {
    id: '2',
    name: 'ATR Breakout Strategy',
    strategy: 'ATR_BREAKOUT',
    startDate: '2023-01-01',
    endDate: '2023-12-31',
    initialCapital: 100000,
    finalValue: 118500,
    totalReturn: 18.5,
    annualizedReturn: 17.2,
    sharpeRatio: 1.32,
    maxDrawdown: -12.1,
    winRate: 0.58,
    profitFactor: 1.6,
    totalTrades: 98,
    avgTradeDuration: 9.8,
    status: 'completed',
    createdAt: '2023-01-01T00:00:00Z',
    updatedAt: '2023-12-31T23:59:59Z',
  },
  {
    id: '3',
    name: 'RSI Mean Reversion',
    strategy: 'RSI_MEAN_REVERSION',
    startDate: '2024-01-01',
    endDate: '2024-09-06',
    initialCapital: 100000,
    finalValue: 87500,
    totalReturn: -12.5,
    annualizedReturn: -15.8,
    sharpeRatio: -0.65,
    maxDrawdown: -18.3,
    winRate: 0.45,
    profitFactor: 0.8,
    totalTrades: 156,
    avgTradeDuration: 4.5,
    status: 'completed',
    createdAt: '2024-01-01T00:00:00Z',
    updatedAt: '2024-09-06T12:00:00Z',
  },
];

export const mockPerformanceMetrics: PerformanceMetrics = {
  totalReturn: 25.0,
  annualizedReturn: 22.5,
  volatility: 15.2,
  sharpeRatio: 1.45,
  sortinoRatio: 2.1,
  calmarRatio: 2.7,
  maxDrawdown: -8.2,
  maxDrawdownDuration: 23,
  winRate: 0.62,
  lossRate: 0.38,
  profitFactor: 1.8,
  expectedValue: 172.5,
  totalTrades: 145,
  winningTrades: 90,
  losingTrades: 55,
  avgWin: 420.3,
  avgLoss: -233.8,
  largestWin: 1250.0,
  largestLoss: -890.0,
  avgTradeDuration: 7.2,
  avgWinDuration: 8.1,
  avgLossDuration: 5.8,
};

export const mockTrades: Trade[] = [
  {
    id: '1',
    symbol: 'AAPL',
    side: 'long',
    entryDate: '2023-12-01T09:30:00Z',
    exitDate: '2023-12-05T16:00:00Z',
    entryPrice: 189.50,
    exitPrice: 195.20,
    quantity: 100,
    pnl: 570.0,
    pnlPercent: 3.01,
    duration: 4,
    status: 'closed',
  },
  {
    id: '2',
    symbol: 'TSLA',
    side: 'long',
    entryDate: '2023-12-03T10:15:00Z',
    exitDate: '2023-12-08T15:30:00Z',
    entryPrice: 242.80,
    exitPrice: 248.90,
    quantity: 50,
    pnl: 305.0,
    pnlPercent: 2.51,
    duration: 5,
    status: 'closed',
  },
  {
    id: '3',
    symbol: 'MSFT',
    side: 'short',
    entryDate: '2023-12-04T11:00:00Z',
    exitDate: '2023-12-06T14:45:00Z',
    entryPrice: 375.20,
    exitPrice: 371.80,
    quantity: 30,
    pnl: 102.0,
    pnlPercent: 0.91,
    duration: 2,
    status: 'closed',
  },
  {
    id: '4',
    symbol: 'NVDA',
    side: 'long',
    entryDate: '2023-12-06T13:30:00Z',
    entryPrice: 465.80,
    quantity: 25,
    status: 'open',
  },
];

// Generate mock equity curve data
export const generateMockEquityCurve = (
  startDate: string,
  endDate: string,
  initialValue: number,
  finalValue: number
): EquityCurvePoint[] => {
  const start = new Date(startDate);
  const end = new Date(endDate);
  const totalDays = Math.floor((end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24));
  const dailyReturn = Math.pow(finalValue / initialValue, 1 / totalDays) - 1;
  
  const points: EquityCurvePoint[] = [];
  let currentValue = initialValue;
  let maxValue = initialValue;
  
  for (let i = 0; i <= totalDays; i += 7) { // Weekly points
    const currentDate = new Date(start.getTime() + i * 24 * 60 * 60 * 1000);
    
    // Add some randomness to make it more realistic
    const randomFactor = 1 + (Math.random() - 0.5) * 0.02; // ±1% random variation
    currentValue *= (1 + dailyReturn * 7) * randomFactor;
    
    maxValue = Math.max(maxValue, currentValue);
    const drawdown = ((currentValue - maxValue) / maxValue) * 100;
    
    points.push({
      date: currentDate.toISOString().split('T')[0],
      portfolioValue: Math.round(currentValue * 100) / 100,
      benchmark: Math.round(initialValue * Math.pow(1.08, i / 365) * 100) / 100, // 8% benchmark
      drawdown: Math.round(drawdown * 100) / 100,
    });
  }
  
  return points;
};

export const mockEquityCurve = generateMockEquityCurve('2023-01-01', '2023-12-31', 100000, 125000);

export const mockDashboardData: DashboardData = {
  results: mockBacktestResults,
  currentBacktest: mockBacktestResults[0],
  metrics: mockPerformanceMetrics,
  equityCurve: mockEquityCurve,
  trades: mockTrades,
  isLoading: false,
};