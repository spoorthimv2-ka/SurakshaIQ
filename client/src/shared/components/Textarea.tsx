import React from 'react';
import clsx from 'clsx';

export interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  error?: string;
  className?: string;
}

const Textarea: React.FC<TextareaProps> = ({ label, error, className, ...props }) => {
  return (
    <div className={className}>
      {label && (
        <label className="mb-1 block text-sm font-medium text-gray-700">
          {label}
        </label>
      )}
      <textarea
        {...props}
        className={clsx(
          'w-full rounded-lg border px-3 py-2 text-sm focus:border-viz-blue focus:outline-none focus:ring-2 focus:ring-viz-blue/20',
          error ? 'border-alert-red' : 'border-gray-300',
          (props as any).className
        )}
      />
      {error && <p className="mt-1 text-xs text-alert-red">{error}</p>}
    </div>
  );
};

export default Textarea;
