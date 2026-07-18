import React from 'react';
import { Card, ChartContainer } from 'shared/components';

const FORECAST_DATA = [
  { month: 'Jan', cases: 420, forecast: 410 },
  { month: 'Feb', cases: 445, forecast: 430 },
  { month: 'Mar', cases: 460, forecast: 455 },
  { month: 'Apr', cases: 438, forecast: 470 },
  { month: 'May', cases: 0, forecast: 485 },
  { month: 'Jun', cases: 0, forecast: 492 },
];

const Trends: React.FC = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-navy-700 dark:text-white">Crime Trends & Forecasting</h1>
        <p className="text-sm text-gov-slate">Historical patterns and predictive trend analysis</p>
      </div>
      <ChartContainer
        title="Case Volume — Actual vs Forecast"
        type="line"
        data={FORECAST_DATA}
        xKey="month"
        series={[
          { key: 'cases', color: '#3b82f6', label: 'Actual' },
          { key: 'forecast', color: '#f59e0b', label: 'Forecast' },
        ]}
      />
      <Card className="p-6">
        <h2 className="text-lg font-semibold text-navy-700 dark:text-white">Forecast Models</h2>
        <p className="mt-2 text-sm text-gov-slate">
          Trend forecasts are generated from district-level time series aggregated by case category and jurisdiction scope.
        </p>
      </Card>
    </div>
  );
};

export default Trends;
