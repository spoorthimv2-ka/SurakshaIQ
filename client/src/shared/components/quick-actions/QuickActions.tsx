import React from 'react';
import { Search } from 'lucide-react';

interface QuickAction {
  id: string;
  label: string;
  description: string;
  icon: React.ComponentType<{ size?: number; className?: string }>;
  onClick?: () => void;
}

interface QuickActionsProps {
  title: string;
  actions: QuickAction[];
  columns?: number; // number of columns in the grid (default 3)
}

const QuickActions: React.FC<QuickActionsProps> = ({ title, actions, columns = 3 }) => {
  return (
    <div className="space-y-4">
      <div className="flex items-center gap-3">
        <Search size={20} className="text-viz-blue" />
        <h2 className="text-lg font-semibold text-navy-700 dark:text-white">{title}</h2>
      </div>
      <div className={`grid gap-4 ${columns === 2 ? 'grid-cols-2' : columns === 3 ? 'grid-cols-3' : 'grid-cols-4'}`}>
        {actions.map((action) => (
          <button
            key={action.id}
            type="button"
            onClick={action.onClick}
            className="border border-gray-200 rounded-lg p-4 dark:border-gray-700 flex flex-col items-center text-center transition-colors hover:bg-gray-50 dark:hover:bg-gray-800 text-left w-full"
          >
            <div className="flex h-10 w-10 items-center justify-center mb-3">
              <action.icon size={20} className="text-viz-blue" />
            </div>
            <h3 className="text-sm font-medium text-navy-700 dark:text-white">{action.label}</h3>
            <p className="text-xs text-gov-slate dark:text-gray-400">{action.description}</p>
          </button>
        ))}
      </div>
    </div>
  );
};

export default QuickActions;