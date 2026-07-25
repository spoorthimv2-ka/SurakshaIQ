import React, { useState, useCallback } from 'react';
import { Card, Button, DataTable, Badge } from 'shared/components';
import type { DataTableColumn } from 'shared/components';
import toast from 'react-hot-toast';
import { useAiTimeline } from 'services/aiService';
import AIPanel from 'shared/components/ai-panel/AIPanel';
import { Clock, GitBranch } from 'lucide-react';

const Timeline: React.FC = () => {
  const [incidentDescription, setIncidentDescription] = useState('');
  const [result, setResult] = useState<any>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const mutation = useAiTimeline();

  const handleGenerate = useCallback(async () => {
    if (!incidentDescription.trim()) {
      toast.error('Please provide an incident description');
      return;
    }
    setIsSubmitting(true);
    try {
      const res = await mutation.mutateAsync({ incident_description: incidentDescription.trim() });
      setResult(res);
      toast.success('Timeline generated');
    } catch {
      toast.error('Timeline generation failed');
    } finally {
      setIsSubmitting(false);
    }
  }, [incidentDescription, mutation]);

  const columns: DataTableColumn<any>[] = [
    {
      key: 'timestamp',
      header: 'Timestamp',
      sortable: true,
      sortValue: (row) => row.timestamp,
      render: (row) => <span className="font-mono text-xs">{row.timestamp}</span>,
    },
    {
      key: 'event',
      header: 'Event',
      render: (row) => <span className="text-sm">{row.event}</span>,
    },
    {
      key: 'actor',
      header: 'Actor',
      render: (row) => <Badge variant="info">{row.actor}</Badge>,
    },
    {
      key: 'evidence',
      header: 'Evidence',
      render: (row) => <span className="text-xs text-gov-slate">{row.evidence}</span>,
    },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-navy-700 dark:text-white">Incident Timeline</h1>
        <p className="text-sm text-gov-slate">Convert incident descriptions into chronological investigative timelines</p>
      </div>

      <div className="grid grid-cols-12 gap-6">
        <div className="col-span-12 lg:col-span-4">
          <Card className="p-6">
            <h2 className="mb-4 text-lg font-semibold text-navy-700 dark:text-white">Incident Description</h2>
            <div className="space-y-4">
              <textarea
                value={incidentDescription}
                onChange={(e) => setIncidentDescription(e.target.value)}
                rows={10}
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
                placeholder="Describe the incident chronologically. Include dates, times, actors, and evidence references..."
              />
              <Button
                variant="primary"
                onClick={handleGenerate}
                disabled={isSubmitting || mutation.isPending}
                className="w-full inline-flex items-center justify-center gap-2"
              >
                {isSubmitting || mutation.isPending ? (
                  <>
                    <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                    Generating...
                  </>
                ) : (
                  <>
                    <Clock size={16} />
                    Generate Timeline
                  </>
                )}
              </Button>
            </div>
          </Card>
        </div>

        <div className="col-span-12 lg:col-span-8">
          {result && (
            <AIPanel
              title="Investigative Timeline"
              isFallback={result.isFallback}
              confidence={result.confidence}
              analyticsUsed={result.analyticsUsed}
              model={result.model}
              generatedAt={result.generatedAt}
              onRetry={handleGenerate}
              isLoading={isSubmitting}
              isError={!!mutation.error}
              emptyMessage="No timeline generated yet."
            >
              {result.events && result.events.length > 0 && (
                <div className="mb-4 overflow-hidden rounded-lg border border-gray-200 dark:border-gray-700">
                  <DataTable
                    columns={columns}
                    data={result.events}
                    rowKey={(row: any) => String(row.timestamp)}
                    emptyTitle="No events"
                    emptyDescription="Timeline events will appear here."
                    virtualized={false}
                  />
                </div>
              )}

              {result.narrative && (
                <div className="rounded-lg border border-gray-200 bg-white p-4 dark:border-gray-700 dark:bg-gray-900">
                  <h4 className="flex items-center gap-2 text-sm font-medium text-navy-700 dark:text-white">
                    <GitBranch size={14} />
                    Narrative
                  </h4>
                  <p className="mt-2 text-sm text-gray-800 dark:text-gray-200">{result.narrative}</p>
                </div>
              )}
            </AIPanel>
          )}
        </div>
      </div>
    </div>
  );
};

export default Timeline;
