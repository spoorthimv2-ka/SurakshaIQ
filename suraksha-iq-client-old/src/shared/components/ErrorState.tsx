import React from 'react';
import { AlertTriangle } from 'lucide-react';
import Button from './Button';

interface ErrorStateProps {
  title?: string;
  description?: string;
  onRetry?: () => void;
}

const ErrorState: React.FC<ErrorStateProps> = ({
  title = 'Something went wrong',
  description = 'We could not load this data. Please try again.',
  onRetry,
}) => {
  return (
    <div className="flex flex-col items-center justify-center py-12 text-center">
      <AlertTriangle className="mb-4 text-alert-red" size={48} />
      <h3 className="mb-2 text-lg font-semibold text-gray-900 dark:text-white">{title}</h3>
      <p className="mb-4 max-w-md text-gray-600 dark:text-gray-400">{description}</p>
      {onRetry && (
        <Button variant="secondary" onClick={onRetry}>
          Retry
        </Button>
      )}
    </div>
  );
};

export default ErrorState;
