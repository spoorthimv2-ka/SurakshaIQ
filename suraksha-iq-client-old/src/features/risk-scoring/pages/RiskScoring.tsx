import React from 'react';
import { Card, KpiCard, ChartContainer } from 'shared/components';

const RISK_DATA = [
  { district: 'Bangalore', score: 78 },
  { district: 'Mysuru', score: 54 },
  { district: 'Belagavi', score: 61 },
  { district: 'Mangaluru', score: 47 },
  { district: 'Hubballi', score: 52 },
];

const RiskScoring: React.FC = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-navy-700 dark:text-white">Risk Scoring</h1>
        <p className="text-sm text-gov-slate">Composite risk indices by district, station, and entity</p>
      </div>
      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        <KpiCard label="State Risk Index" value="62.4" delta={1.8} accent="amber" />
        <KpiCard label="High-Risk Districts" value="4" accent="red" />
        <KpiCard label="Entities Scored (30d)" value="1,284" delta={12.3} accent="green" />
      </div>
      <ChartContainer
        title="District Risk Scores"
        type="bar"
        data={RISK_DATA}
        xKey="district"
        series={[{ key: 'score', color: '#f59e0b', label: 'Risk Score' }]}
      />
      <Card className="p-6">
        <h2 className="text-lg font-semibold text-navy-700 dark:text-white">Scoring Methodology</h2>
        <p className="mt-2 text-sm text-gov-slate">
          Risk scores combine case frequency, severity weighting, recidivism patterns, and temporal acceleration factors.
        </p>
      </Card>
    </div>
  );
};

export default RiskScoring;
