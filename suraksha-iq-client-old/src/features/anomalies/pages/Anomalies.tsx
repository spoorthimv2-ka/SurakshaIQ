import React from 'react';
import { Card, AlertBanner, Badge } from 'shared/components';

const ANOMALY_SAMPLES = [
  { id: 'a1', title: 'Sudden spike in cybercrime — Bangalore Urban', severity: 'high' as const },
  { id: 'a2', title: 'Unusual night-time activity — Mysuru Rural', severity: 'medium' as const },
  { id: 'a3', title: 'Reporting delay anomaly — Belagavi', severity: 'low' as const },
];

const severityColor = {
  low: 'secondary' as const,
  medium: 'warning' as const,
  high: 'danger' as const,
  critical: 'danger' as const,
};

const Anomalies: React.FC = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-navy-700 dark:text-white">Anomaly Detection</h1>
        <p className="text-sm text-gov-slate">Statistical outliers and pattern deviations flagged by the analytics engine</p>
      </div>
      <AlertBanner
        variant="warning"
        title="3 anomalies detected in the last 24 hours"
        message="Review flagged patterns and assign investigating officers as needed."
      />
      <Card className="divide-y divide-gray-100 dark:divide-gray-800">
        {ANOMALY_SAMPLES.map((anomaly) => (
          <div key={anomaly.id} className="flex items-center justify-between p-4">
            <span className="text-sm font-medium text-navy-700 dark:text-white">{anomaly.title}</span>
            <Badge variant={severityColor[anomaly.severity]}>{anomaly.severity}</Badge>
          </div>
        ))}
      </Card>
    </div>
  );
};

export default Anomalies;
