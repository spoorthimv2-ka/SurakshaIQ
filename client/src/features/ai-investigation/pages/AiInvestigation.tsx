import React, { useState, useCallback } from 'react';
import { Card, Button, Badge } from 'shared/components';
import toast from 'react-hot-toast';
import { useAiFirIntelligence, useAiRecommendations } from 'services/aiService';
import AIPanel from 'shared/components/ai-panel/AIPanel';
import { Sparkles, FileText, ListChecks, AlertTriangle } from 'lucide-react';

const SEVERITY_VARIANT: Record<string, 'success' | 'warning' | 'danger' | 'secondary'> = {
  Critical: 'danger',
  High: 'warning',
  Medium: 'secondary',
  Low: 'success',
};

const AiInvestigation: React.FC = () => {
  const [firText, setFirText] = useState('');
  const [firNumber, setFirNumber] = useState('');
  const [district, setDistrict] = useState('');
  const [station, setStation] = useState('');
  const [status, setStatus] = useState('ACTIVE');
  const [sections, setSections] = useState('');
  const [victim, setVictim] = useState('');
  const [suspect, setSuspect] = useState('');
  const [result, setResult] = useState<any>(null);
  const [recommendations, setRecommendations] = useState<string[]>([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const firIntelligenceMutation = useAiFirIntelligence();
  const recommendationsMutation = useAiRecommendations();

  const handleAnalyze = useCallback(async () => {
    if (!firText.trim()) {
      toast.error('Please provide FIR description or text');
      return;
    }
    setIsAnalyzing(true);
    try {
      const res = await firIntelligenceMutation.mutateAsync({
        fir_number: firNumber || undefined,
        description: firText,
        sections: sections || undefined,
        victim_name: victim || undefined,
        suspect_name: suspect || undefined,
        district_id: district || undefined,
        station_id: station || undefined,
        status,
      });
      setResult(res);
      toast.success('FIR analyzed successfully');
    } catch (e) {
      toast.error('Analysis failed');
    } finally {
      setIsAnalyzing(false);
    }
  }, [firText, firNumber, sections, victim, suspect, district, station, status, firIntelligenceMutation]);

  const handleLoadSimilar = useCallback(async () => {
    if (!result?.modus_operandi) {
      toast.error('Analyze an FIR first to find similar cases');
      return;
    }
    setIsAnalyzing(true);
    try {
      const res = await recommendationsMutation.mutateAsync({
        analytics: { modus_operandi: result.modus_operandi, crime_category: result.crime_category },
      });
      setRecommendations(res.recommendations?.map((r: any) => r.description || r.title) ?? []);
    } catch {
      toast.error('Failed to load similar cases');
    } finally {
      setIsAnalyzing(false);
    }
  }, [result, recommendationsMutation]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-navy-700 dark:text-white">AI FIR Investigation</h1>
        <p className="text-sm text-gov-slate">Upload or paste FIR text to extract structured intelligence</p>
      </div>

      <div className="grid grid-cols-12 gap-6">
        <div className="col-span-12 lg:col-span-5">
          <Card className="p-6">
            <h2 className="mb-4 text-lg font-semibold text-navy-700 dark:text-white">FIR Input</h2>
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="mb-1 block text-sm font-medium text-gray-700">FIR Number</label>
                  <input
                    type="text"
                    value={firNumber}
                    onChange={(e) => setFirNumber(e.target.value)}
                    className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
                    placeholder="FIR-2024-001"
                  />
                </div>
                <div>
                  <label className="mb-1 block text-sm font-medium text-gray-700">Status</label>
                  <select
                    value={status}
                    onChange={(e) => setStatus(e.target.value)}
                    className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
                  >
                    <option value="ACTIVE">Active</option>
                    <option value="INACTIVE">Inactive</option>
                    <option value="ARCHIVED">Archived</option>
                  </select>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="mb-1 block text-sm font-medium text-gray-700">District</label>
                  <input
                    type="text"
                    value={district}
                    onChange={(e) => setDistrict(e.target.value)}
                    className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
                    placeholder="bangalore-urban"
                  />
                </div>
                <div>
                  <label className="mb-1 block text-sm font-medium text-gray-700">Station</label>
                  <input
                    type="text"
                    value={station}
                    onChange={(e) => setStation(e.target.value)}
                    className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
                    placeholder="S1"
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="mb-1 block text-sm font-medium text-gray-700">Victim</label>
                  <input
                    type="text"
                    value={victim}
                    onChange={(e) => setVictim(e.target.value)}
                    className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
                  />
                </div>
                <div>
                  <label className="mb-1 block text-sm font-medium text-gray-700">Suspect</label>
                  <input
                    type="text"
                    value={suspect}
                    onChange={(e) => setSuspect(e.target.value)}
                    className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
                  />
                </div>
              </div>
              <div>
                <label className="mb-1 block text-sm font-medium text-gray-700">IPC Sections</label>
                <input
                  type="text"
                  value={sections}
                  onChange={(e) => setSections(e.target.value)}
                  className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
                  placeholder="IPC 380, 420"
                />
              </div>
              <div>
                <label className="mb-1 block text-sm font-medium text-gray-700">FIR Description</label>
                <textarea
                  value={firText}
                  onChange={(e) => setFirText(e.target.value)}
                  rows={8}
                  className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
                  placeholder="Paste or type the FIR description here..."
                />
              </div>
              <div className="flex gap-2">
                <Button
                  variant="primary"
                  onClick={handleAnalyze}
                  disabled={isAnalyzing || firIntelligenceMutation.isPending}
                  className="inline-flex items-center gap-2"
                >
                  {isAnalyzing || firIntelligenceMutation.isPending ? (
                    <>
                      <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                      Analyzing...
                    </>
                  ) : (
                    <>
                      <Sparkles size={16} />
                      Analyze FIR
                    </>
                  )}
                </Button>
                {result && (
                  <Button variant="secondary" onClick={handleLoadSimilar} disabled={isAnalyzing}>
                    Find Similar Cases
                  </Button>
                )}
              </div>
            </div>
          </Card>
        </div>

        <div className="col-span-12 lg:col-span-7 space-y-6">
          {result && (
            <>
              <AIPanel
                title="Crime Intelligence"
                isFallback={result.isFallback}
                confidence={result.confidence}
                analyticsUsed={result.analyticsUsed}
                model={result.model}
                generatedAt={result.generatedAt}
                onRetry={handleAnalyze}
                isLoading={isAnalyzing}
                isError={!!firIntelligenceMutation.error}
              >
                <div className="grid grid-cols-2 gap-4">
                  <div className="flex items-center gap-2">
                    <FileText size={16} className="text-viz-blue" />
                    <div>
                      <p className="text-xs text-gov-slate">Category</p>
                      <p className="text-sm font-medium text-navy-700 dark:text-white capitalize">{result.crime_category}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <AlertTriangle size={16} className="text-alert-red" />
                    <div>
                      <p className="text-xs text-gov-slate">Severity</p>
                      <Badge variant={SEVERITY_VARIANT[result.severity] ?? 'secondary'}>{result.severity}</Badge>
                    </div>
                  </div>
                </div>

                <div>
                  <h4 className="text-sm font-medium text-navy-700 dark:text-white">Modus Operandi</h4>
                  <p className="mt-1 text-sm text-gray-800 dark:text-gray-200">{result.modus_operandi}</p>
                </div>

                <div>
                  <h4 className="text-sm font-medium text-navy-700 dark:text-white">Extracted Entities</h4>
                  <div className="mt-2 flex flex-wrap gap-2">
                  {Object.entries(result.entities || {}).map(([key, values]) => (
                    Array.isArray(values) && values.length > 0 && (
                      <div key={key} className="rounded-lg border border-gray-200 bg-white p-2 dark:border-gray-700 dark:bg-gray-900">
                        <p className="text-xs font-medium text-gov-slate capitalize">{key}</p>
                        <div className="mt-1 flex flex-wrap gap-1">
                          {values.map((v: string, i: number) => (
                            <span key={i} className="rounded-full bg-viz-blue/10 px-2 py-0.5 text-xs text-viz-blue">{v}</span>
                          ))}
                        </div>
                      </div>
                    )
                  ))}
                  </div>
                </div>

                <div>
                  <h4 className="flex items-center gap-2 text-sm font-medium text-navy-700 dark:text-white">
                    <ListChecks size={14} />
                    Investigation Suggestions
                  </h4>
                  <ul className="mt-2 space-y-1">
                    {result.investigation_suggestions?.map((s: string, i: number) => (
                      <li key={i} className="flex items-start gap-2 text-sm text-gray-800 dark:text-gray-200">
                        <span className="mt-1.5 h-1.5 w-1.5 rounded-full bg-green-500" />
                        {s}
                      </li>
                    ))}
                  </ul>
                </div>
              </AIPanel>

              {recommendations.length > 0 && (
                <Card className="p-6">
                  <h3 className="mb-3 text-sm font-semibold text-navy-700 dark:text-white">Similar Cases & Next Actions</h3>
                  <ul className="space-y-2">
                    {recommendations.map((r, i) => (
                      <li key={i} className="flex items-start gap-2 text-sm text-gray-800 dark:text-gray-200">
                        <span className="mt-1.5 h-1.5 w-1.5 rounded-full bg-viz-blue" />
                        {r}
                      </li>
                    ))}
                  </ul>
                </Card>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default AiInvestigation;
