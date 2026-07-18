import React from 'react';

interface EmptyStateProps {
  icon?: React.ReactNode;
  title: string;
  description?: string;
  action?: React.ReactNode;
}

const EmptyState: React.FC<EmptyStateProps> = ({
  icon,
  title,
  description,
  action,
}) => {
  return (
    <div className="flex flex-col items-center justify-center py-12">
      {icon && <div className="mb-4 text-gray-400 text-5xl">{icon}</div>}
      <h3 className="mb-2 text-lg font-semibold text-gray-900">{title}</h3>
      {description && <p className="mb-4 text-gray-600 text-center max-w-md">{description}</p>}
      {action && <div>{action}</div>}
    </div>
  );
};

export default EmptyState;
