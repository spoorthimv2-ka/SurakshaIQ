import React, { useState, useCallback } from 'react';
import { Card, Button, Badge } from 'shared/components';
import toast from 'react-hot-toast';
import { useAiReport } from 'services/aiService';
import AIPanel from 'shared/components/ai-panel/AIPanel';
import { FileText, Download, Printer } from 'lucide-react';
import { useReportTypes, useGenerateReport } from 'features/reports/hooks/useReports';

const AiReports: React.FC = () => {
  const [reportType, setReportType] = useState('SITUATIONAL');
  const [scope, setScope] = useState('{"district_id": "bangalore-urban"}');
  const [filters, setFilters] = useState('{"status": "ACTIVE"}');
  const [title, setTitle] = useState('');
  const [result, setResult] = useState<any>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const aiMutation = useAiReport();
  const generateMutation = useGenerateReport();
  const { data: reportTypes } = useReportTypes();

  const handleGenerate = useCallback(async () => {
    if (!title.trim()) {
      toast.error('Please provide a report title');
      return;
    }
    setIsSubmitting(true);
    try {
      let scopeObj: Record<string, unknown> = {};
      let filtersObj: Record<string, unknown> = {};
      try { scopeObj = JSON.parse(scope); } catch { /* ignore */ }
      try { filtersObj = JSON.parse(filters); } catch { /* ignore */ }

      const res = await aiMutation.mutateAsync({
        title: title.trim(),
        report_type: reportType,
        scope: scopeObj,
        filters: filtersObj,
      });
      setResult(res);
      toast.success('AI report generated');
    } catch {
      toast.error('Report generation failed');
    } finally {
      setIsSubmitting(false);
    }
  }, [title, reportType, scope, filters, aiMutation]);

  const handleSaveAsReport = useCallback(async () => {
    if (!result) return;
    try {
      await generateMutation.mutateAsync({
        name: result.title || title || 'AI Report',
        report_type: reportType,
        parameters_json: { scope, filters },
      });
      toast.success('Report saved successfully');
    } catch {
      toast.error('Failed to save report');
    }
  }, [result, title, reportType, scope, filters, generateMutation]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-navy-700 dark:text-white">AI Intelligence Reports</h1>
        <p className="text-sm text-gov-slate">Generate structured intelligence reports using dashboard analytics</p>
      </div>

      <div className="grid grid-cols-12 gap-6">
        <div className="col-span-12 lg:col-span-4">
          <Card className="p-6">
            <h2 className="mb-4 text-lg font-semibold text-navy-700 dark:text-white">Report Configuration</h2>
            <div className="space-y-4">
              <div>
                <label className="mb-1 block text-sm font-medium text-gray-700">Report Title</label>
                <input
                  type="text"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
                  placeholder="Weekly Situational Report"
                />
              </div>
              <div>
                <label className="mb-1 block text-sm font-medium text-gray-700">Report Type</label>
                <select
                  value={reportType}
                  onChange={(e) => setReportType(e.target.value)}
                  className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
                >
                  {reportTypes?.map((t: any) => (
                    <option key={t.type} value={t.type}>{t.label}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="mb-1 block text-sm font-medium text-gray-700">Scope (JSON)</label>
                <textarea
                  value={scope}
                  onChange={(e) => setScope(e.target.value)}
                  rows={3}
                  className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm font-mono"
                />
              </div>
              <div>
                <label className="mb-1 block text-sm font-medium text-gray-700">Filters (JSON)</label>
                <textarea
                  value={filters}
                  onChange={(e) => setFilters(e.target.value)}
                  rows={3}
                  className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm font-mono"
                />
              </div>
              <Button
                variant="primary"
                onClick={handleGenerate}
                disabled={isSubmitting || aiMutation.isPending}
                className="w-full inline-flex items-center justify-center gap-2"
              >
                {isSubmitting || aiMutation.isPending ? (
                  <>
                    <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                    Generating...
                  </>
                ) : (
                  <>
                    <FileText size={16} />
                    Generate AI Report
                  </>
                )}
              </Button>
            </div>
          </Card>
        </div>

        <div className="col-span-12 lg:col-span-8">
          {result && (
            <AIPanel
              title={result.title || 'AI Report'}
              isFallback={result.isFallback}
              confidence={result.confidence}
              analyticsUsed={result.analyticsUsed}
              model={result.model}
              generatedAt={result.generatedAt}
              onRetry={handleGenerate}
              isLoading={isSubmitting}
              isError={!!aiMutation.error}
              emptyMessage="No report generated yet."
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Badge variant="info">{result.format}</Badge>
                  <span className="text-xs text-gov-slate">ID: {result.reportId}</span>
                </div>
                <div className="flex gap-2">
                  <Button variant="ghost" size="sm" onClick={() => window.print()} className="inline-flex items-center gap-1">
                    <Printer size={14} />
                    Print
                  </Button>
                  <Button variant="ghost" size="sm" onClick={handleSaveAsReport} className="inline-flex items-center gap-1">
                    <Download size={14} />
                    Save
                  </Button>
                </div>
              </div>

              <div className="rounded-lg border border-gray-200 bg-white p-4 dark:border-gray-700 dark:bg-gray-900">
                <pre className="whitespace-pre-wrap text-sm text-gray-800 dark:text-gray-200">
                  {result.content}
                </pre>
              </div>

              {result.sections && result.sections.length > 0 && (
                <div className="space-y-2">
                  <h4 className="text-sm font-medium text-navy-700 dark:text-white">Sections</h4>
                  {result.sections.map((section: any, i: number) => (
                    <div key={i} className="rounded-lg border border-gray-200 bg-white p-3 dark:border-gray-700 dark:bg-gray-900">
                      <h5 className="text-sm font-medium text-navy-700 dark:text-white">{section.title}</h5>
                      <p className="mt-1 text-sm text-gray-800 dark:text-gray-200">{section.content}</p>
                    </div>
                  ))}
                </div>
              )}
            </AIPanel>
          )}
        </div>
      </div>
    </div>
  );
};

export default AiReports;
