import React from 'react';
import clsx from 'clsx';

interface LoadingSkeletonProps {
  variant?: 'page' | 'card' | 'table' | 'text';
  rows?: number;
  className?: string;
}

const LoadingSkeleton: React.FC<LoadingSkeletonProps> = ({
  variant = 'card',
  rows = 3,
  className,
}) => {
  const bar = 'animate-pulse rounded bg-gray-200 dark:bg-gray-700';

  if (variant === 'page') {
    return (
      <div className={clsx('w-full max-w-4xl space-y-4 p-6', className)}>
        <div className={clsx(bar, 'h-8 w-1/3')} />
        <div className={clsx(bar, 'h-4 w-1/2')} />
        <div className="grid grid-cols-3 gap-4 pt-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className={clsx(bar, 'h-24')} />
          ))}
        </div>
      </div>
    );
  }

  if (variant === 'table') {
    return (
      <div className={clsx('space-y-2', className)}>
        <div className={clsx(bar, 'h-10 w-full')} />
        {Array.from({ length: rows }).map((_, i) => (
          <div key={i} className={clsx(bar, 'h-12 w-full')} />
        ))}
      </div>
    );
  }

  if (variant === 'text') {
    return (
      <div className={clsx('space-y-2', className)}>
        {Array.from({ length: rows }).map((_, i) => (
          <div key={i} className={clsx(bar, 'h-4', i === rows - 1 ? 'w-2/3' : 'w-full')} />
        ))}
      </div>
    );
  }

  return <div className={clsx(bar, 'h-32 w-full', className)} />;
};

export default LoadingSkeleton;
