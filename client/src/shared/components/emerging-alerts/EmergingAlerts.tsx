import React from 'react';
import { AlertTriangle, MapPin, Clock } from 'lucide-react';

interface Alert {
  id: string;
  title: string;
  location: string;
  time: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  suggestedAction: string;
}

interface EmergingAlertsProps {
  title: string;
  alerts: Alert[];
}

const severityColors: Record<'critical' | 'high' | 'medium' | 'low', string> = {
  critical: 'alert-red',
  high: 'alert-orange',
  medium: 'alert-yellow',
  low: 'data-green',
};

const EmergingAlerts: React.FC<EmergingAlertsProps> = ({ title, alerts }) => {
  return (
    <div className="space-y-4">
      <div className="flex items-center gap-3">
        <AlertTriangle size={20} className="text-alert-red" />
        <h2 className="text-lg font-semibold text-navy-700 dark:text-white">{title}</h2>
      </div>
      <div className="space-y-3">
        {alerts.map((alert) => (
          <div key={alert.id} className="border border-gray-200 rounded-lg p-4 dark:border-gray-700">
            <div className="flex items-start gap-3">
              <div className="flex-shrink-0 flex h-3 w-3 items-center justify-center">
                <span className={`text-xs font-bold text-white rounded-full bg-${severityColors[alert.severity]}`}>
                  {alert.severity.toUpperCase()}
                </span>
              </div>
              <div className="flex-1 space-y-1">
                <h3 className="text-sm font-medium text-navy-700 dark:text-white">{alert.title}</h3>
                <p className="text-sm text-gov-slate dark:text-gray-400">{alert.suggestedAction}</p>
              </div>
            </div>
            <div className="mt-2 flex items-center gap-4 text-xs text-gov-slate dark:text-gray-400">
              <MapPin size={12} className="text-navy-400" />
              <span>{alert.location}</span>
              <Clock size={12} className="text-navy-400" />
              <span>{alert.time}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default EmergingAlerts;