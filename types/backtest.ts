export interface BacktestResult {
  id: string;
  name: string;
  strategy: string;
  startDate: string;
  endDate: string;
  initialCapital: number;
  finalValue: number;
  totalReturn: number;
  annualizedReturn: number;
  sharpeRatio: number;
  maxDrawdown: number;
  winRate: number;
  profitFactor: number;
  totalTrades: number;
  avgTradeDuration: number;
  status: 'running' | 'completed' | 'failed';
  createdAt: string;
  updatedAt: string;
}

export interface PerformanceMetrics {
  totalReturn: number;
  annualizedReturn: number;
  volatility: number;
  sharpeRatio: number;
  sortinoRatio: number;
  calmarRatio: number;
  maxDrawdown: number;
  maxDrawdownDuration: number;
  winRate: number;
  lossRate: number;
  profitFactor: number;
  expectedValue: number;
  totalTrades: number;
  winningTrades: number;
  losingTrades: number;
  avgWin: number;
  avgLoss: number;
  largestWin: number;
  largestLoss: number;
  avgTradeDuration: number;
  avgWinDuration: number;
  avgLossDuration: number;
}

export interface Trade {
  id: string;
  symbol: string;
  side: 'long' | 'short';
  entryDate: string;
  exitDate?: string;
  entryPrice: number;
  exitPrice?: number;
  quantity: number;
  pnl?: number;
  pnlPercent?: number;
  duration?: number;
  status: 'open' | 'closed';
}

export interface EquityCurvePoint {
  date: string;
  portfolioValue: number;
  benchmark?: number;
  drawdown: number;
}

export interface BacktestConfig {
  strategy: string;
  symbol: string;
  startDate: string;
  endDate: string;
  initialCapital: number;
  parameters: Record<string, any>;
  riskManagement: {
    maxDrawdown: number;
    positionSize: number;
    stopLoss?: number;
    takeProfit?: number;
  };
}

export interface DashboardData {
  results: BacktestResult[];
  currentBacktest?: BacktestResult;
  metrics?: PerformanceMetrics;
  equityCurve?: EquityCurvePoint[];
  trades?: Trade[];
  isLoading: boolean;
  error?: string;
}

export interface StrategyTemplate {
  id: string;
  name: string;
  displayName: string;
  description: string;
  category: 'trend' | 'mean_reversion' | 'momentum' | 'volatility' | 'arbitrage' | 'custom';
  parameters: StrategyParameter[];
  riskLevel: 'low' | 'medium' | 'high';
  timeframe: string[];
  assets: string[];
  createdAt: string;
  updatedAt: string;
  isBuiltIn: boolean;
  author?: string;
  backtestResults?: {
    count: number;
    avgReturn: number;
    avgSharpe: number;
    winRate: number;
  };
}

export interface StrategyParameter {
  name: string;
  displayName: string;
  type: 'number' | 'string' | 'boolean' | 'select' | 'range';
  defaultValue: any;
  description: string;
  constraints?: {
    min?: number;
    max?: number;
    step?: number;
    options?: string[];
  };
  required: boolean;
}

export interface StrategyInstance {
  id: string;
  templateId: string;
  name: string;
  parameters: Record<string, any>;
  status: 'draft' | 'active' | 'inactive' | 'testing';
  createdAt: string;
  updatedAt: string;
  backtestCount: number;
  lastBacktestId?: string;
}