import React, { useEffect } from 'react';
import { Card, AlertBanner, Badge } from 'shared/components';
import { useAlertStore } from 'shared/state';

const SAMPLE_ALERTS = [
  { id: 'al1', title: 'Hotspot threshold exceeded — Bangalore Central', severity: 'critical' as const, read: false },
  { id: 'al2', title: 'Repeat offender match — Mysuru', severity: 'high' as const, read: false },
  { id: 'al3', title: 'Report export completed', severity: 'low' as const, read: true },
];

const severityVariant = {
  low: 'secondary' as const,
  medium: 'warning' as const,
  high: 'danger' as const,
  critical: 'danger' as const,
};

const Alerts: React.FC = () => {
  const { addAlert, markAsRead } = useAlertStore();

  useEffect(() => {
    SAMPLE_ALERTS.filter((a) => !a.read).forEach((a) =>
      addAlert({
        id: a.id,
        title: a.title,
        description: '',
        severity: a.severity,
        timestamp: Date.now(),
        read: false,
      })
    );
  }, [addAlert]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-navy-700 dark:text-white">Alerts</h1>
        <p className="text-sm text-gov-slate">Real-time operational alerts and threshold notifications</p>
      </div>
      <AlertBanner
        variant="error"
        title="Critical alert active"
        message="Review Bangalore Central hotspot threshold breach immediately."
      />
      <Card className="divide-y divide-gray-100 dark:divide-gray-800">
        {SAMPLE_ALERTS.map((alert) => (
          <button
            key={alert.id}
            type="button"
            onClick={() => markAsRead(alert.id)}
            className="flex w-full items-center justify-between p-4 text-left hover:bg-gray-50 dark:hover:bg-gray-800"
          >
            <div>
              <p className={`text-sm font-medium ${alert.read ? 'text-gov-slate' : 'text-navy-700 dark:text-white'}`}>
                {alert.title}
              </p>
            </div>
            <Badge variant={severityVariant[alert.severity]}>{alert.severity}</Badge>
          </button>
        ))}
      </Card>
    </div>
  );
};

export default Alerts;
