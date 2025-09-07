import { BacktestResult, PerformanceMetrics, Trade, EquityCurvePoint, DashboardData, StrategyTemplate, StrategyInstance } from '@/types/backtest';

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

// Mock Strategy Templates
export const mockStrategyTemplates: StrategyTemplate[] = [
  {
    id: 'sma_crossover',
    name: 'SMA_CROSSOVER',
    displayName: 'Simple Moving Average Crossover',
    description: 'A classic trend-following strategy that generates buy signals when a fast SMA crosses above a slow SMA, and sell signals when it crosses below.',
    category: 'trend',
    parameters: [
      {
        name: 'fast_period',
        displayName: 'Fast SMA Period',
        type: 'number',
        defaultValue: 10,
        description: 'Period for the fast moving average',
        constraints: { min: 5, max: 50, step: 1 },
        required: true,
      },
      {
        name: 'slow_period',
        displayName: 'Slow SMA Period',
        type: 'number',
        defaultValue: 20,
        description: 'Period for the slow moving average',
        constraints: { min: 20, max: 200, step: 1 },
        required: true,
      },
      {
        name: 'stop_loss',
        displayName: 'Stop Loss (%)',
        type: 'number',
        defaultValue: 5.0,
        description: 'Stop loss percentage',
        constraints: { min: 1.0, max: 20.0, step: 0.1 },
        required: false,
      },
    ],
    riskLevel: 'medium',
    timeframe: ['1m', '5m', '15m', '1h', '4h', '1d'],
    assets: ['stocks', 'forex', 'crypto'],
    createdAt: '2023-01-01T00:00:00Z',
    updatedAt: '2023-01-01T00:00:00Z',
    isBuiltIn: true,
    author: 'System',
    backtestResults: {
      count: 45,
      avgReturn: 18.3,
      avgSharpe: 1.35,
      winRate: 0.62,
    },
  },
  {
    id: 'atr_breakout',
    name: 'ATR_BREAKOUT',
    displayName: 'ATR Breakout Strategy',
    description: 'A volatility-based breakout strategy that enters positions when price breaks above/below dynamic support/resistance levels based on Average True Range.',
    category: 'momentum',
    parameters: [
      {
        name: 'atr_period',
        displayName: 'ATR Period',
        type: 'number',
        defaultValue: 14,
        description: 'Period for calculating ATR',
        constraints: { min: 10, max: 30, step: 1 },
        required: true,
      },
      {
        name: 'atr_multiplier',
        displayName: 'ATR Multiplier',
        type: 'number',
        defaultValue: 2.0,
        description: 'Multiplier for ATR to determine breakout levels',
        constraints: { min: 1.0, max: 5.0, step: 0.1 },
        required: true,
      },
      {
        name: 'lookback_period',
        displayName: 'Lookback Period',
        type: 'number',
        defaultValue: 20,
        description: 'Period to look back for high/low levels',
        constraints: { min: 10, max: 50, step: 1 },
        required: true,
      },
    ],
    riskLevel: 'high',
    timeframe: ['15m', '1h', '4h', '1d'],
    assets: ['stocks', 'crypto', 'commodities'],
    createdAt: '2023-01-15T00:00:00Z',
    updatedAt: '2023-01-15T00:00:00Z',
    isBuiltIn: true,
    author: 'System',
    backtestResults: {
      count: 32,
      avgReturn: 24.1,
      avgSharpe: 1.42,
      winRate: 0.58,
    },
  },
  {
    id: 'rsi_mean_reversion',
    name: 'RSI_MEAN_REVERSION',
    displayName: 'RSI Mean Reversion',
    description: 'A mean reversion strategy that buys when RSI is oversold and sells when overbought, with additional filters for trend confirmation.',
    category: 'mean_reversion',
    parameters: [
      {
        name: 'rsi_period',
        displayName: 'RSI Period',
        type: 'number',
        defaultValue: 14,
        description: 'Period for RSI calculation',
        constraints: { min: 10, max: 30, step: 1 },
        required: true,
      },
      {
        name: 'oversold_level',
        displayName: 'Oversold Level',
        type: 'number',
        defaultValue: 30,
        description: 'RSI level considered oversold',
        constraints: { min: 20, max: 40, step: 1 },
        required: true,
      },
      {
        name: 'overbought_level',
        displayName: 'Overbought Level',
        type: 'number',
        defaultValue: 70,
        description: 'RSI level considered overbought',
        constraints: { min: 60, max: 80, step: 1 },
        required: true,
      },
      {
        name: 'use_trend_filter',
        displayName: 'Use Trend Filter',
        type: 'boolean',
        defaultValue: true,
        description: 'Use 200-period SMA as trend filter',
        required: false,
      },
    ],
    riskLevel: 'low',
    timeframe: ['1h', '4h', '1d'],
    assets: ['stocks', 'forex'],
    createdAt: '2023-02-01T00:00:00Z',
    updatedAt: '2023-02-01T00:00:00Z',
    isBuiltIn: true,
    author: 'System',
    backtestResults: {
      count: 28,
      avgReturn: 15.7,
      avgSharpe: 1.28,
      winRate: 0.67,
    },
  },
  {
    id: 'bollinger_bands',
    name: 'BOLLINGER_BANDS',
    displayName: 'Bollinger Bands Strategy',
    description: 'A volatility-based strategy using Bollinger Bands to identify overbought/oversold conditions and potential reversal points.',
    category: 'volatility',
    parameters: [
      {
        name: 'bb_period',
        displayName: 'BB Period',
        type: 'number',
        defaultValue: 20,
        description: 'Period for Bollinger Bands calculation',
        constraints: { min: 10, max: 50, step: 1 },
        required: true,
      },
      {
        name: 'bb_std',
        displayName: 'Standard Deviations',
        type: 'number',
        defaultValue: 2.0,
        description: 'Number of standard deviations for bands',
        constraints: { min: 1.0, max: 3.0, step: 0.1 },
        required: true,
      },
      {
        name: 'squeeze_threshold',
        displayName: 'Squeeze Threshold',
        type: 'number',
        defaultValue: 0.05,
        description: 'Threshold for detecting BB squeeze',
        constraints: { min: 0.01, max: 0.10, step: 0.01 },
        required: false,
      },
    ],
    riskLevel: 'medium',
    timeframe: ['15m', '1h', '4h', '1d'],
    assets: ['stocks', 'forex', 'crypto'],
    createdAt: '2023-03-01T00:00:00Z',
    updatedAt: '2023-03-01T00:00:00Z',
    isBuiltIn: true,
    author: 'System',
    backtestResults: {
      count: 22,
      avgReturn: 12.4,
      avgSharpe: 1.15,
      winRate: 0.59,
    },
  },
];

// Mock Strategy Instances
export const mockStrategyInstances: StrategyInstance[] = [
  {
    id: 'inst_1',
    templateId: 'sma_crossover',
    name: 'My SMA Strategy - Conservative',
    parameters: {
      fast_period: 10,
      slow_period: 30,
      stop_loss: 3.0,
    },
    status: 'active',
    createdAt: '2023-06-01T00:00:00Z',
    updatedAt: '2023-06-15T00:00:00Z',
    backtestCount: 8,
    lastBacktestId: '1',
  },
  {
    id: 'inst_2',
    templateId: 'atr_breakout',
    name: 'ATR Breakout - Aggressive',
    parameters: {
      atr_period: 14,
      atr_multiplier: 2.5,
      lookback_period: 15,
    },
    status: 'testing',
    createdAt: '2023-07-01T00:00:00Z',
    updatedAt: '2023-07-10T00:00:00Z',
    backtestCount: 3,
    lastBacktestId: '2',
  },
  {
    id: 'inst_3',
    templateId: 'rsi_mean_reversion',
    name: 'RSI Scalping Strategy',
    parameters: {
      rsi_period: 12,
      oversold_level: 25,
      overbought_level: 75,
      use_trend_filter: false,
    },
    status: 'draft',
    createdAt: '2023-08-01T00:00:00Z',
    updatedAt: '2023-08-01T00:00:00Z',
    backtestCount: 0,
  },
];