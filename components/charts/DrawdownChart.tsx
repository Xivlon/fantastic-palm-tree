import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { EquityCurvePoint } from '@/types/backtest';

interface DrawdownChartProps {
  data: EquityCurvePoint[];
  height?: number;
}

const DrawdownChart: React.FC<DrawdownChartProps> = ({ data, height = 300 }) => {
  const formatPercent = (value: number) => {
    return `${value.toFixed(2)}%`;
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
    });
  };

  return (
    <div className="w-full">
      <ResponsiveContainer width="100%" height={height}>
        <LineChart
          data={data}
          margin={{
            top: 5,
            right: 30,
            left: 20,
            bottom: 5,
          }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis 
            dataKey="date" 
            tickFormatter={formatDate}
            interval="preserveStartEnd"
          />
          <YAxis 
            tickFormatter={formatPercent}
            domain={['dataMin - 1', 'dataMax + 1']}
          />
          <Tooltip
            labelFormatter={(value) => `Date: ${formatDate(value)}`}
            formatter={(value: number) => [formatPercent(value), 'Drawdown']}
            contentStyle={{
              backgroundColor: 'white',
              border: '1px solid #ccc',
              borderRadius: '6px',
            }}
          />
          <Line
            type="monotone"
            dataKey="drawdown"
            stroke="#dc2626"
            strokeWidth={2}
            dot={false}
            fill="#dc2626"
            fillOpacity={0.1}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default DrawdownChart;