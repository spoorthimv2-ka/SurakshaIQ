import React from 'react';
import { Brain, RefreshCw } from 'lucide-react';
import { Card, Button, Badge } from 'shared/components';
import AITransparency from 'shared/components/ai-transparency/AITransparency';
import type { AITransparencyProps } from 'shared/components/ai-transparency/AITransparency';
import clsx from 'clsx';

export interface AIPanelProps extends AITransparencyProps {
  title: string;
  children: React.ReactNode;
  isLoading?: boolean;
  isError?: boolean;
  errorMessage?: string;
  onRetry?: () => void;
  onRefresh?: () => void;
  emptyMessage?: string;
  className?: string;
}

const AIPanel: React.FC<AIPanelProps> = ({
  title,
  children,
  isLoading = false,
  isError = false,
  errorMessage = 'Unable to generate AI insight.',
  onRetry,
  onRefresh,
  emptyMessage,
  className,
  ...transparency
}) => {
  return (
    <Card className={clsx('flex flex-col', className)}>
      <div className="flex items-center justify-between border-b border-gray-200 p-4 dark:border-gray-700">
        <div className="flex items-center gap-2">
          <Brain size={18} className="text-viz-blue" />
          <h3 className="font-semibold text-navy-700 dark:text-white">{title}</h3>
          {transparency.isFallback && <Badge variant="warning">Locally Generated</Badge>}
        </div>
        <div className="flex items-center gap-2">
          {(onRetry || onRefresh) && (
            <Button
              variant="ghost"
              size="sm"
              onClick={onRetry || onRefresh}
              className="inline-flex items-center gap-1 text-xs"
            >
              <RefreshCw size={14} />
              Retry
            </Button>
          )}
        </div>
      </div>

      <div className="flex-1 p-4">
        {isLoading && (
          <div className="flex items-center justify-center py-8">
            <div className="flex items-center gap-2 text-sm text-gov-slate">
              <div className="h-4 w-4 animate-spin rounded-full border-2 border-viz-blue border-t-transparent" />
              Generating intelligence...
            </div>
          </div>
        )}

        {isError && !isLoading && (
          <div className="rounded-lg border border-alert-red/30 bg-red-50 p-4 dark:bg-red-900/20">
            <p className="text-sm text-alert-red">{errorMessage}</p>
            {onRetry && (
              <Button variant="ghost" size="sm" onClick={onRetry} className="mt-2">
                Retry
              </Button>
            )}
          </div>
        )}

        {!isLoading && !isError && React.Children.count(children) === 0 && (
          <div className="py-8 text-center text-sm text-gov-slate">
            {emptyMessage || 'No AI insight available.'}
          </div>
        )}

        {!isLoading && !isError && React.Children.count(children) > 0 && <div className="space-y-3">{children}</div>}
      </div>

      <AITransparency {...transparency} />
    </Card>
  );
};

export default AIPanel;
