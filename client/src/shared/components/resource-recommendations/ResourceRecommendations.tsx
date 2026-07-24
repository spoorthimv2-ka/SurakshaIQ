import React from 'react';
import { TrendingUp } from 'lucide-react';

interface ResourceRecommendation {
  id: string;
  title: string;
  description: string;
  priority: 'high' | 'medium' | 'low';
  icon: React.ComponentType<{ size?: number; className?: string }>;
}

interface ResourceRecommendationsProps {
  title: string;
  recommendations: ResourceRecommendation[];
}

const priorityColors: Record<'high' | 'medium' | 'low', string> = {
  high: 'alert-red',
  medium: 'alert-yellow',
  low: 'data-green',
};

const ResourceRecommendations: React.FC<ResourceRecommendationsProps> = ({
  title,
  recommendations,
}) => {
  return (
    <div className="space-y-4">
      <div className="flex items-center gap-3">
        <TrendingUp size={20} className="text-viz-blue" />
        <h2 className="text-lg font-semibold text-navy-700 dark:text-white">{title}</h2>
      </div>
      <div className="space-y-3">
        {recommendations.map((rec) => (
          <div key={rec.id} className="border border-gray-200 rounded-lg p-4 dark:border-gray-700">
            <div className="flex items-start gap-3">
              <div className="flex-shrink-0 flex h-3 w-3 items-center justify-center">
                <rec.icon size={16} className={`text-${priorityColors[rec.priority]}-600`} />
              </div>
              <div className="flex-1 space-y-1">
                <h3 className="text-sm font-medium text-navy-700 dark:text-white">{rec.title}</h3>
                <p className="text-sm text-gov-slate dark:text-gray-400 break-words">{rec.description}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ResourceRecommendations;