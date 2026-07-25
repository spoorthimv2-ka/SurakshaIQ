import React from 'react';
import { Sparkles, Loader2 } from 'lucide-react';
import { Button } from 'shared/components';
import clsx from 'clsx';

export interface ExplainButtonProps {
  onClick: () => void;
  isLoading?: boolean;
  label?: string;
  className?: string;
  disabled?: boolean;
}

const ExplainButton: React.FC<ExplainButtonProps> = ({
  onClick,
  isLoading = false,
  label = 'Explain with AI',
  className,
  disabled = false,
}) => {
  return (
    <Button
      variant="ghost"
      size="sm"
      onClick={onClick}
      disabled={disabled || isLoading}
      className={clsx('inline-flex items-center gap-1.5 text-xs', className)}
      title="Generate AI explanation for this widget"
    >
      {isLoading ? (
        <Loader2 size={14} className="animate-spin" />
      ) : (
        <Sparkles size={14} />
      )}
      {label}
    </Button>
  );
};

export default ExplainButton;
