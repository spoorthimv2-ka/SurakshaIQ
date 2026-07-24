import React from 'react';
import { AlertTriangle, MapPin, Clock } from 'lucide-react';

interface LiveIntelligenceFeedProps {
  title: string;
  items: {
    id: string;
    severity: 'critical' | 'high' | 'medium' | 'low';
    time: string;
    location: string;
    description: string;
  }[];
}

const severityColors: Record<'critical' | 'high' | 'medium' | 'low', string> = {
  critical: 'alert-red',
  high: 'alert-orange',
  medium: 'alert-yellow',
  low: 'data-green',
};

const severityLabels: Record<'critical' | 'high' | 'medium' | 'low', string> = {
  critical: 'Critical',
  high: 'High',
  medium: 'Medium',
  low: 'Low',
};

const LiveIntelligenceFeed: React.FC<LiveIntelligenceFeedProps> = ({ title, items }) => {
  return (
    <div className="space-y-4">
      <div className="flex items-center gap-3">
        <AlertTriangle size={20} className="text-alert-red" />
        <h2 className="text-lg font-semibold text-navy-700 dark:text-white">{title}</h2>
      </div>
      <div className="space-y-3">
        {items.map((item) => (
          <div key={item.id} className="border border-gray-200 rounded-lg p-4 dark:border-gray-700">
            <div className="flex items-start gap-3">
              <div className="flex-shrink-0 flex h-3 w-3 items-center justify-center">
                <span className={`text-${severityColors[item.severity]}-600 text-xs font-bold uppercase`}>
                  {severityLabels[item.severity]}
                </span>
              </div>
              <div className="flex-1 space-y-1">
                <p className="text-sm font-medium text-navy-700 dark:text-white">{item.description}</p>
                <div className="flex items-center gap-4 text-xs text-gov-slate dark:text-gray-400">
                  <MapPin size={14} className="text-navy-400" />
                  <span>{item.location}</span>
                  <Clock size={14} className="text-navy-400" />
                  <span>{item.time}</span>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default LiveIntelligenceFeed;