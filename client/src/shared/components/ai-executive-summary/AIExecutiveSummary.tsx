import React from 'react';
import { Brain, ChartBar } from 'lucide-react';

interface AIExecutiveSummaryProps {
  title: string;
  insights: string[];
}

const AIExecutiveSummary: React.FC<AIExecutiveSummaryProps> = ({ title, insights }) => {
  return (
    <div className="space-y-4">
      <div className="flex items-center gap-3">
        <Brain size={20} className="text-viz-blue" />
        <h2 className="text-lg font-semibold text-navy-700 dark:text-white">{title}</h2>
      </div>
      <ul className="space-y-2 text-sm text-gov-slate dark:text-gray-400">
        {insights.map((insight, index) => (
          <li key={index} className="flex items-start gap-3">
            <div className="flex-shrink-0 flex h-3 w-3 items-center justify-center bg-viz-blue/10 text-viz-blue rounded-full shrink-0">
              <ChartBar size={10} />
            </div>
            <p>{insight}</p>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default AIExecutiveSummary;