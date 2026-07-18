import React from 'react';
import toast from 'react-hot-toast';
import { AlertTriangle, Info, CheckCircle, XCircle } from 'lucide-react';

type AlertToastSeverity = 'info' | 'success' | 'warning' | 'error';

const icons: Record<AlertToastSeverity, React.ReactNode> = {
  info: <Info size={18} className="text-viz-blue" />,
  success: <CheckCircle size={18} className="text-data-green" />,
  warning: <AlertTriangle size={18} className="text-amber-analytics" />,
  error: <XCircle size={18} className="text-alert-red" />,
};

export function showAlertToast(
  message: string,
  severity: AlertToastSeverity = 'info',
  duration = 4000
): void {
  toast.custom(
    (t) => (
      <div
        className={`flex items-center gap-3 rounded-lg border border-gray-200 bg-white px-4 py-3 shadow-lg ${
          t.visible ? 'animate-enter' : 'animate-leave'
        }`}
      >
        {icons[severity]}
        <span className="text-sm text-gray-900">{message}</span>
      </div>
    ),
    { duration }
  );
}

export default showAlertToast;
