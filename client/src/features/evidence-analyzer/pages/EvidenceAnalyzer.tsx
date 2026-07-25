import React, { useState, useCallback } from 'react';
import { Card, Button } from 'shared/components';
import toast from 'react-hot-toast';
import { useAiEvidenceSummary } from 'services/aiService';
import AIPanel from 'shared/components/ai-panel/AIPanel';
import { FileText, Users, MapPin, Car, Phone, CheckCircle2 } from 'lucide-react';

const EvidenceAnalyzer: React.FC = () => {
  const [documentType, setDocumentType] = useState('WITNESS_STATEMENT');
  const [content, setContent] = useState('');
  const [result, setResult] = useState<any>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const mutation = useAiEvidenceSummary();

  const handleAnalyze = useCallback(async () => {
    if (!content.trim()) {
      toast.error('Please provide document content');
      return;
    }
    setIsSubmitting(true);
    try {
      const res = await mutation.mutateAsync({ document_type: documentType, content: content.trim() });
      setResult(res);
      toast.success('Evidence analyzed');
    } catch {
      toast.error('Analysis failed');
    } finally {
      setIsSubmitting(false);
    }
  }, [content, documentType, mutation]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-navy-700 dark:text-white">Evidence Analyzer</h1>
        <p className="text-sm text-gov-slate">Upload and analyze FIRs, witness statements, and complaint documents</p>
      </div>

      <div className="grid grid-cols-12 gap-6">
        <div className="col-span-12 lg:col-span-4">
          <Card className="p-6">
            <h2 className="mb-4 text-lg font-semibold text-navy-700 dark:text-white">Document Input</h2>
            <div className="space-y-4">
              <div>
                <label className="mb-1 block text-sm font-medium text-gray-700">Document Type</label>
                <select
                  value={documentType}
                  onChange={(e) => setDocumentType(e.target.value)}
                  className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
                >
                  <option value="WITNESS_STATEMENT">Witness Statement</option>
                  <option value="FIR">First Information Report</option>
                  <option value="COMPLAINT">Complaint</option>
                  <option value="CHARGE_SHEET">Charge Sheet</option>
                  <option value="OTHER">Other</option>
                </select>
              </div>
              <div>
                <label className="mb-1 block text-sm font-medium text-gray-700">Document Content</label>
                <textarea
                  value={content}
                  onChange={(e) => setContent(e.target.value)}
                  rows={12}
                  className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
                  placeholder="Paste document text here..."
                />
              </div>
              <Button
                variant="primary"
                onClick={handleAnalyze}
                disabled={isSubmitting || mutation.isPending}
                className="w-full inline-flex items-center justify-center gap-2"
              >
                {isSubmitting || mutation.isPending ? (
                  <>
                    <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <FileText size={16} />
                    Analyze Document
                  </>
                )}
              </Button>
            </div>
          </Card>
        </div>

        <div className="col-span-12 lg:col-span-8">
          {result && (
            <AIPanel
              title="Evidence Summary"
              isFallback={result.isFallback}
              confidence={result.confidence}
              analyticsUsed={result.analyticsUsed}
              model={result.model}
              generatedAt={result.generatedAt}
              onRetry={handleAnalyze}
              isLoading={isSubmitting}
              isError={!!mutation.error}
              emptyMessage="No analysis result yet."
            >
              <div>
                <h4 className="text-sm font-medium text-navy-700 dark:text-white">Summary</h4>
                <p className="mt-1 rounded-lg border border-gray-200 bg-white p-3 text-sm text-gray-800 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-200">
                  {result.summary}
                </p>
              </div>

              <div>
                <h4 className="text-sm font-medium text-navy-700 dark:text-white">Extracted Entities</h4>
                <div className="mt-2 grid grid-cols-2 gap-3">
                  {Object.entries(result.extracted_entities || {}).map(([key, values]) => (
                    <div key={key} className="rounded-lg border border-gray-200 bg-white p-3 dark:border-gray-700 dark:bg-gray-900">
                      <div className="flex items-center gap-1 text-xs font-medium text-gov-slate capitalize">
                        {key === 'people' && <Users size={12} />}
                        {key === 'locations' && <MapPin size={12} />}
                        {key === 'vehicles' && <Car size={12} />}
                        {key === 'phones' && <Phone size={12} />}
                        {key}
                      </div>
                      <div className="mt-1 flex flex-wrap gap-1">
                        {Array.isArray(values) && values.length > 0 ? values.map((v: string, i: number) => (
                          <span key={i} className="rounded-full bg-viz-blue/10 px-2 py-0.5 text-xs text-viz-blue">{v}</span>
                        )) : (
                          <span className="text-xs text-gov-slate">None detected</span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <h4 className="flex items-center gap-2 text-sm font-medium text-navy-700 dark:text-white">
                  <CheckCircle2 size={14} />
                  Key Points
                </h4>
                <ul className="mt-2 space-y-1">
                  {result.key_points?.map((point: string, i: number) => (
                    <li key={i} className="flex items-start gap-2 text-sm text-gray-800 dark:text-gray-200">
                      <span className="mt-1.5 h-1.5 w-1.5 rounded-full bg-green-500" />
                      {point}
                    </li>
                  ))}
                </ul>
              </div>
            </AIPanel>
          )}
        </div>
      </div>
    </div>
  );
};

export default EvidenceAnalyzer;
