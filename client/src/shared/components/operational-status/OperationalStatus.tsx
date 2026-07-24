import React from 'react';
import { MapPin, Server, Clock, Brain } from 'lucide-react';

interface OperationalStatusProps {
  state: string;
  jurisdiction: string;
  casesMonitored: number;
  lastSync: string;
  aiStatus: string;
}

const OperationalStatus: React.FC<OperationalStatusProps> = ({
  state,
  jurisdiction,
  casesMonitored,
  lastSync,
  aiStatus,
}) => {
  return (
    <div className="flex flex-wrap items-center gap-4 px-4 py-2 bg-navy-50 dark:bg-navy-900/50 border-b border-navy-200 dark:border-navy-700">
      <div className="flex items-center gap-2 text-sm text-navy-600 dark:text-navy-300">
        <MapPin size={16} className="text-navy-400" />
        <span>{state}</span>
      </div>
      <div className="flex items-center gap-2 text-sm text-navy-600 dark:text-navy-300">
        <MapPin size={16} className="text-navy-400" />
        <span>{jurisdiction}</span>
      </div>
      <div className="flex items-center gap-2 text-sm text-navy-600 dark:text-navy-300">
        <Server size={16} className="text-navy-400" />
        <span>{casesMonitored}</span>
      </div>
      <div className="flex items-center gap-2 text-sm text-navy-600 dark:text-navy-300">
        <Clock size={16} className="text-navy-400" />
        <span>{lastSync}</span>
      </div>
      <div className="flex items-center gap-2 text-sm text-navy-600 dark:text-navy-300">
        <Brain size={16} className={`text-${aiStatus.toLowerCase() === 'active' ? 'data-green' : 'alert-red'}-600`} />
        <span>{aiStatus}</span>
      </div>
    </div>
  );
};

export default OperationalStatus;