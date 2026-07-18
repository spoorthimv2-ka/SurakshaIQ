import React from 'react';
import clsx from 'clsx';
import { AlertTriangle, Info, XCircle } from 'lucide-react';
import IconButton from './IconButton';
import { X } from 'lucide-react';

type AlertBannerVariant = 'info' | 'warning' | 'error';

interface AlertBannerProps {
  title: string;
  message?: string;
  variant?: AlertBannerVariant;
  onDismiss?: () => void;
  action?: React.ReactNode;
  className?: string;
}

const variantStyles: Record<AlertBannerVariant, string> = {
  info: 'border-viz-blue/30 bg-blue-50 text-navy-700',
  warning: 'border-amber-analytics/30 bg-amber-50 text-amber-900',
  error: 'border-alert-red/30 bg-red-50 text-red-900',
};

const variantIcons: Record<AlertBannerVariant, React.ReactNode> = {
  info: <Info size={20} />,
  warning: <AlertTriangle size={20} />,
  error: <XCircle size={20} />,
};

const AlertBanner: React.FC<AlertBannerProps> = ({
  title,
  message,
  variant = 'info',
  onDismiss,
  action,
  className,
}) => {
  return (
    <div
      role="alert"
      className={clsx(
        'flex items-start gap-3 rounded-lg border px-4 py-3',
        variantStyles[variant],
        className
      )}
    >
      <div className="mt-0.5 shrink-0">{variantIcons[variant]}</div>
      <div className="flex-1">
        <p className="font-semibold">{title}</p>
        {message && <p className="mt-1 text-sm opacity-90">{message}</p>}
        {action && <div className="mt-2">{action}</div>}
      </div>
      {onDismiss && (
        <IconButton icon={<X size={16} />} onClick={onDismiss} aria-label="Dismiss alert" />
      )}
    </div>
  );
};

export default AlertBanner;
