import React from 'react';
import { Brain, RefreshCw, ShieldCheck, ShieldAlert, ShieldX } from 'lucide-react';
import { Badge } from 'shared/components';

export interface ExecutiveBriefing {
  overallRisk: string;
  executiveSummary: string;
  keyFindings: string[];
  recommendedActions: string[];
  confidence: number;
  generatedAt: string;
  isFallback?: boolean;
}

interface AIExecutiveSummaryProps {
  title: string;
  briefing?: ExecutiveBriefing | null;
  isLoading?: boolean;
  isError?: boolean;
  onRefresh?: () => void;
}

const RiskIcon: React.FC<{ risk: string }> = ({ risk }) => {
  const lower = risk.toLowerCase();
  if (lower === 'high') return <ShieldX size={18} className="text-alert-red" />;
  if (lower === 'medium') return <ShieldAlert size={18} className="text-amber-500" />;
  return <ShieldCheck size={18} className="text-green-600" />;
};

const AIExecutiveSummary: React.FC<AIExecutiveSummaryProps> = ({
  title,
  briefing,
  isLoading = false,
  isError = false,
  onRefresh,
}) => {
  if (isLoading) {
    return (
      <div className="space-y-4">
        <div className="flex items-center gap-3">
          <Brain size={20} className="text-viz-blue" />
          <h2 className="text-lg font-semibold text-navy-700 dark:text-white">{title}</h2>
        </div>
        <div className="rounded-lg border border-gray-200 bg-gray-50 p-4 dark:border-gray-700 dark:bg-gray-800">
          <p className="text-sm text-gov-slate">Generating intelligence...</p>
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="space-y-4">
        <div className="flex items-center gap-3">
          <Brain size={20} className="text-viz-blue" />
          <h2 className="text-lg font-semibold text-navy-700 dark:text-white">{title}</h2>
        </div>
        <div className="rounded-lg border border-alert-red/30 bg-red-50 p-4 dark:bg-red-900/20">
          <p className="text-sm text-alert-red">Unable to generate AI briefing.</p>
          {onRefresh && (
            <button
              type="button"
              onClick={onRefresh}
              className="mt-3 inline-flex items-center gap-2 rounded-lg border border-gray-300 px-3 py-1.5 text-xs font-medium text-gray-700 hover:bg-gray-50 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-700"
            >
              <RefreshCw size={14} />
              Refresh
            </button>
          )}
        </div>
      </div>
    );
  }

  if (!briefing) {
    return (
      <div className="space-y-4">
        <div className="flex items-center gap-3">
          <Brain size={20} className="text-viz-blue" />
          <h2 className="text-lg font-semibold text-navy-700 dark:text-white">{title}</h2>
        </div>
        <div className="rounded-lg border border-gray-200 bg-gray-50 p-4 dark:border-gray-700 dark:bg-gray-800">
          <p className="text-sm text-gov-slate">No intelligence briefing available.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Brain size={20} className="text-viz-blue" />
          <h2 className="text-lg font-semibold text-navy-700 dark:text-white">{title}</h2>
          {briefing.isFallback && (
            <Badge variant="warning">Locally Generated</Badge>
          )}
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <RiskIcon risk={briefing.overallRisk} />
            <span className="text-sm font-medium text-navy-700 dark:text-white">{briefing.overallRisk} Risk</span>
          </div>
          <span className="text-xs text-gov-slate">
            {(briefing.confidence * 100).toFixed(0)}% confident
          </span>
          {onRefresh && (
            <button
              type="button"
              onClick={onRefresh}
              className="inline-flex items-center gap-1 rounded-lg border border-gray-300 px-2 py-1 text-xs font-medium text-gray-700 hover:bg-gray-50 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-700"
            >
              <RefreshCw size={14} />
              Refresh
            </button>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        <div className="rounded-lg border border-gray-200 bg-white p-4 dark:border-gray-700 dark:bg-gray-900">
          <h3 className="text-sm font-semibold text-navy-700 dark:text-white">Executive Summary</h3>
          <p className="mt-2 text-sm text-gray-800 dark:text-gray-200">{briefing.executiveSummary}</p>
        </div>
        <div className="space-y-4">
          <div className="rounded-lg border border-gray-200 bg-white p-4 dark:border-gray-700 dark:bg-gray-900">
            <h3 className="text-sm font-semibold text-navy-700 dark:text-white">Key Findings</h3>
            <ul className="mt-2 space-y-2 text-sm text-gray-800 dark:text-gray-200">
              {briefing.keyFindings.map((finding, index) => (
                <li key={index} className="flex items-start gap-2">
                  <span className="mt-1 h-1.5 w-1.5 rounded-full bg-viz-blue" />
                  <span>{finding}</span>
                </li>
              ))}
            </ul>
          </div>
          <div className="rounded-lg border border-gray-200 bg-white p-4 dark:border-gray-700 dark:bg-gray-900">
            <h3 className="text-sm font-semibold text-navy-700 dark:text-white">Recommended Actions</h3>
            <ul className="mt-2 space-y-2 text-sm text-gray-800 dark:text-gray-200">
              {briefing.recommendedActions.map((action, index) => (
                <li key={index} className="flex items-start gap-2">
                  <span className="mt-1 h-1.5 w-1.5 rounded-full bg-green-500" />
                  <span>{action}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>

      <div className="flex items-center justify-between text-xs text-gov-slate">
        <span>
          Generated at {new Date(briefing.generatedAt).toLocaleString()}
        </span>
      </div>
    </div>
  );
};

export default AIExecutiveSummary;
