import React from 'react';
import clsx from 'clsx';
import Card from './Card';
import StatDelta from './StatDelta';

interface KpiCardProps {
  label: string;
  value: string | number;
  delta?: number;
  icon?: React.ReactNode;
  accent?: 'navy' | 'amber' | 'purple' | 'blue' | 'red' | 'green';
  className?: string;
}

const accentColors = {
  navy: 'border-l-navy-500',
  amber: 'border-l-amber-analytics',
  purple: 'border-l-geo-purple',
  blue: 'border-l-viz-blue',
  red: 'border-l-alert-red',
  green: 'border-l-data-green',
};

const KpiCard: React.FC<KpiCardProps> = ({
  label,
  value,
  delta,
  icon,
  accent = 'navy',
  className,
}) => {
  return (
    <Card className={clsx('border-l-4 p-5', accentColors[accent], className)}>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium text-gov-slate dark:text-gray-400">{label}</p>
          <p className="mt-1 font-kpi text-3xl font-bold text-navy-700 dark:text-white">{value}</p>
          {delta !== undefined && <StatDelta value={delta} className="mt-2" />}
        </div>
        {icon && <div className="text-gov-slate dark:text-gray-400">{icon}</div>}
      </div>
    </Card>
  );
};

export default KpiCard;
