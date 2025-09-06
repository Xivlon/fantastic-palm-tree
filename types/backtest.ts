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