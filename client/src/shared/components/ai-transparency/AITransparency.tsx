import React from 'react';
import { Info, Clock, Cpu, BarChart2, AlertTriangle } from 'lucide-react';
import clsx from 'clsx';

export interface AITransparencyProps {
  confidence?: number;
  analyticsUsed?: string[];
  model?: string | null;
  generatedAt?: string;
  isFallback?: boolean;
  className?: string;
}

const AITransparency: React.FC<AITransparencyProps> = ({
  confidence,
  analyticsUsed,
  model,
  generatedAt,
  isFallback = false,
  className,
}) => {
  if (!confidence && !analyticsUsed?.length && !model && !generatedAt) {
    return null;
  }

  return (
    <div className={clsx('mt-3 rounded-lg border border-gray-200 bg-gray-50 p-3 text-xs dark:border-gray-700 dark:bg-gray-800', className)}>
      <div className="flex flex-wrap items-center gap-x-4 gap-y-1">
        {isFallback && (
          <span className="inline-flex items-center gap-1 text-amber-600 dark:text-amber-400">
            <AlertTriangle size={12} />
            Locally Generated (fallback)
          </span>
        )}
        {confidence !== undefined && (
          <span className="inline-flex items-center gap-1 text-gray-600 dark:text-gray-400">
            <BarChart2 size={12} />
            {(confidence * 100).toFixed(0)}% confident
          </span>
        )}
        {model && (
          <span className="inline-flex items-center gap-1 text-gray-600 dark:text-gray-400">
            <Cpu size={12} />
            {model}
          </span>
        )}
        {generatedAt && (
          <span className="inline-flex items-center gap-1 text-gray-600 dark:text-gray-400">
            <Clock size={12} />
            {new Date(generatedAt).toLocaleString()}
          </span>
        )}
        {analyticsUsed && analyticsUsed.length > 0 && (
          <span className="inline-flex items-center gap-1 text-gray-600 dark:text-gray-400">
            <Info size={12} />
            Sources: {analyticsUsed.join(', ')}
          </span>
        )}
      </div>
    </div>
  );
};

export default AITransparency;
