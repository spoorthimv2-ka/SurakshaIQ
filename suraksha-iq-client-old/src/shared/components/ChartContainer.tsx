import React from 'react';
import clsx from 'clsx';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  Legend,
} from 'recharts';

export type ChartType = 'line' | 'bar';

interface ChartContainerProps {
  title?: string;
  type?: ChartType;
  data: Array<Record<string, string | number>>;
  xKey: string;
  series: Array<{ key: string; color: string; label?: string }>;
  height?: number;
  className?: string;
}

const ChartContainer: React.FC<ChartContainerProps> = ({
  title,
  type = 'line',
  data,
  xKey,
  series,
  height = 320,
  className,
}) => {
  return (
    <div className={clsx('rounded-lg border border-gray-200 bg-white p-4 dark:border-gray-700 dark:bg-gray-900', className)}>
      {title && <h3 className="mb-4 text-sm font-semibold text-navy-700 dark:text-white">{title}</h3>}
      <ResponsiveContainer width="100%" height={height}>
        {type === 'line' ? (
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
            <XAxis dataKey={xKey} tick={{ fontSize: 12 }} />
            <YAxis tick={{ fontSize: 12 }} />
            <RechartsTooltip />
            <Legend />
            {series.map((s) => (
              <Line key={s.key} type="monotone" dataKey={s.key} stroke={s.color} name={s.label ?? s.key} strokeWidth={2} dot={false} />
            ))}
          </LineChart>
        ) : (
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
            <XAxis dataKey={xKey} tick={{ fontSize: 12 }} />
            <YAxis tick={{ fontSize: 12 }} />
            <RechartsTooltip />
            <Legend />
            {series.map((s) => (
              <Bar key={s.key} dataKey={s.key} fill={s.color} name={s.label ?? s.key} />
            ))}
          </BarChart>
        )}
      </ResponsiveContainer>
    </div>
  );
};

export default ChartContainer;
