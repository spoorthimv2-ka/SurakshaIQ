import React from 'react';
import clsx from 'clsx';
import { TrendingDown, TrendingUp, Minus } from 'lucide-react';

interface StatDeltaProps {
  value: number;
  suffix?: string;
  className?: string;
}

const StatDelta: React.FC<StatDeltaProps> = ({ value, suffix = '%', className }) => {
  const type = value > 0 ? 'increase' : value < 0 ? 'decrease' : 'neutral';

  const styles = {
    increase: 'text-data-green',
    decrease: 'text-alert-red',
    neutral: 'text-gov-slate',
  };

  const Icon = type === 'increase' ? TrendingUp : type === 'decrease' ? TrendingDown : Minus;

  return (
    <span className={clsx('inline-flex items-center gap-1 text-sm font-medium', styles[type], className)}>
      <Icon size={14} />
      {Math.abs(value)}
      {suffix}
    </span>
  );
};

export default StatDelta;
