import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { EquityCurvePoint } from '@/types/backtest';

interface EquityCurveChartProps {
  data: EquityCurvePoint[];
  height?: number;
}

const EquityCurveChart: React.FC<EquityCurveChartProps> = ({ data, height = 400 }) => {
  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
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
            tickFormatter={formatCurrency}
            domain={['dataMin - 5000', 'dataMax + 5000']}
          />
          <Tooltip
            labelFormatter={(value) => `Date: ${formatDate(value)}`}
            formatter={(value: number, name: string) => [
              formatCurrency(value),
              name === 'portfolioValue' ? 'Portfolio Value' : 
              name === 'benchmark' ? 'Benchmark' : name
            ]}
            contentStyle={{
              backgroundColor: 'white',
              border: '1px solid #ccc',
              borderRadius: '6px',
            }}
          />
          <Legend />
          <Line
            type="monotone"
            dataKey="portfolioValue"
            stroke="#2563eb"
            strokeWidth={2}
            dot={false}
            name="Portfolio Value"
          />
          {data[0]?.benchmark !== undefined && (
            <Line
              type="monotone"
              dataKey="benchmark"
              stroke="#64748b"
              strokeWidth={1}
              strokeDasharray="5 5"
              dot={false}
              name="Benchmark"
            />
          )}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default EquityCurveChart;