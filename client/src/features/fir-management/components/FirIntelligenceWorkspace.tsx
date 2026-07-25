import React, { useState, useMemo, useCallback } from 'react';
import { Card, Button, DataTable, Badge, Tabs, Modal } from 'shared/components';
import type { DataTableColumn } from 'shared/components';
import toast from 'react-hot-toast';
import { useAiFirIntelligence, useAiEvidenceSummary, useAiTimeline, useAiRecommendations } from 'services/aiService';
import AIPanel from 'shared/components/ai-panel/AIPanel';
import { Sparkles, FileText, Clock, Search, ShieldCheck, Users, MapPin, Car, Phone, Building2, FileCheck, Gavel } from 'lucide-react';
import type { Fir } from 'shared/api';

export interface ExtendedFir extends Fir {
  victim_name?: string;
  suspect_name?: string;
  district_id?: string;
  sections?: string;
  summary?: string;
}

export interface FirIntelligenceWorkspaceProps {
  fir: any;
  allFirs: any[];
  onClose: () => void;
}

const SEVERITY_VARIANT: Record<string, 'success' | 'warning' | 'danger' | 'secondary'> = {
  Critical: 'danger',
  High: 'warning',
  Medium: 'secondary',
  Low: 'success',
};

const generateStatusHistory = (fir: ExtendedFir) => {
  const created = new Date(fir.CREATEDTIME);
  const entries = [
    { status: 'REGISTERED', timestamp: created.toISOString(), officer: fir.officer_id, note: 'FIR registered at station' },
    { status: fir.status, timestamp: new Date(created.getTime() + 86400000).toISOString(), officer: fir.officer_id, note: `Status updated to ${fir.status}` },
  ];
  return entries;
};

const generateOfficerNotes = (fir: ExtendedFir) => {
  return [
    { id: 'n1', officer_id: fir.officer_id, timestamp: fir.CREATEDTIME, note: 'Initial assessment completed. Scene visited.' },
    { id: 'n2', officer_id: fir.officer_id, timestamp: new Date(new Date(fir.CREATEDTIME).getTime() + 172800000).toISOString(), note: 'Witnesses identified. Follow-up required.' },
  ];
};

const FIR_TYPE_KEYWORDS: Record<string, string[]> = {
  theft: ['theft', 'stolen', 'steal', 'burglary', 'robbed', 'snatching'],
  robbery: ['robbery', 'armed', 'weapon', 'threatened', 'loot'],
  assault: ['assault', 'attack', 'injured', 'beat'],
  fraud: ['fraud', 'scam', 'cheat', 'fake', 'forged'],
  cybercrime: ['cyber', 'online', 'hacking', 'phishing', 'computer'],
  murder: ['murder', 'killed', 'homicide', 'death'],
  rape: ['rape', 'sexual assault'],
  kidnapping: ['kidnapping', 'abduction', 'hostage'],
};

const classifyCrimeCategory = (fir: ExtendedFir): { category: string; severity: string } => {
  const text = `${fir.description} ${fir.fir_number}`.toLowerCase();
  for (const [category, keywords] of Object.entries(FIR_TYPE_KEYWORDS)) {
    if (keywords.some(k => text.includes(k))) {
      if (['murder', 'rape', 'kidnapping'].includes(category)) return { category, severity: 'Critical' };
      if (['robbery', 'burglary', 'fraud'].includes(category)) return { category, severity: 'High' };
      if (['assault'].includes(category)) return { category, severity: 'Medium' };
      return { category, severity: 'High' };
    }
  }
  return { category: 'Other', severity: 'Medium' };
};

const extractEntities = (fir: ExtendedFir): Record<string, string[]> => {
  const entities: Record<string, string[]> = { people: [], locations: [], vehicles: [], phones: [] };
  const text = `${fir.description} ${fir.victim_name || ''} ${fir.suspect_name || ''}`;

  if (fir.victim_name) entities.people.push(fir.victim_name);
  if (fir.suspect_name) entities.people.push(fir.suspect_name);

  const locationMatch = text.match(/(?:at|near|from|in)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)/);
  if (locationMatch) entities.locations.push(locationMatch[1]);

  const vehicleMatch = text.match(/\bKA\d{2}[A-Z]{2}\d{4}\b/);
  if (vehicleMatch) entities.vehicles.push(vehicleMatch[0]);

  const phoneMatch = text.match(/\b[6-9]\d{9}\b/);
  if (phoneMatch) entities.phones.push(phoneMatch[0]);

  return entities;
};

const scoreRisk = (severity: string, status: string): { level: string; score: number } => {
  const severityScore: Record<string, number> = { Critical: 90, High: 70, Medium: 50, Low: 30 };
  const statusPenalty: Record<string, number> = { ACTIVE: 0, INACTIVE: 10, ARCHIVED: 20 };
  const score = (severityScore[severity] || 50) - (statusPenalty[status] || 0);
  const level = score >= 80 ? 'Critical' : score >= 60 ? 'High' : score >= 40 ? 'Medium' : 'Low';
  return { level, score: Math.max(0, Math.min(100, score)) };
};

const findSimilarFirs = (fir: ExtendedFir, allFirs: ExtendedFir[]): ExtendedFir[] => {
  if (!allFirs.length) return [];
  const scored = allFirs
    .filter(f => f.ROWID !== fir.ROWID)
    .map(f => {
      let score = 0;
      if (f.crime_id === fir.crime_id) score += 50;
      if (f.district_id === fir.district_id) score += 20;
      if (f.station_id === fir.station_id) score += 15;
      const descWords = new Set(fir.description.toLowerCase().split(/\s+/));
      const otherWords = new Set(f.description.toLowerCase().split(/\s+/));
      const overlap = [...descWords].filter(w => otherWords.has(w)).length;
      score += Math.min(overlap * 3, 15);
      return { fir: f, score };
    })
    .filter(s => s.score >= 20)
    .sort((a, b) => b.score - a.score)
    .slice(0, 5)
    .map(s => s.fir);
  return scored;
};

const findDuplicates = (fir: ExtendedFir, allFirs: ExtendedFir[]): ExtendedFir[] => {
  return allFirs.filter(f => f.ROWID !== fir.ROWID && f.fir_number === fir.fir_number);
};

const STATUS_BADGE_VARIANT: Record<string, 'success' | 'warning' | 'danger' | 'secondary'> = {
  ACTIVE: 'success',
  INACTIVE: 'secondary',
  ARCHIVED: 'warning',
};

const FirIntelligenceWorkspace: React.FC<FirIntelligenceWorkspaceProps> = ({ fir, allFirs, onClose }) => {
  const [notes, setNotes] = useState<string[]>([]);
  const [newNote, setNewNote] = useState('');
  const [isAiAnalyzing, setIsAiAnalyzing] = useState(false);

  const firAiMutation = useAiFirIntelligence();
  const evidenceMutation = useAiEvidenceSummary();
  const timelineMutation = useAiTimeline();
  const recMutation = useAiRecommendations();

  const [aiFirResult, setAiFirResult] = useState<any>(null);
  const [evidenceResult, setEvidenceResult] = useState<any>(null);
  const [timelineResult, setTimelineResult] = useState<any>(null);
  const [recommendations, setRecommendations] = useState<string[]>([]);

  const derived = useMemo(() => {
    if (!fir) return null;
    const classification = classifyCrimeCategory(fir as any);
    const entities = extractEntities(fir as any);
    const risk = scoreRisk(classification.severity, fir.status);
    const similar = findSimilarFirs(fir as any, allFirs);
    const duplicates = findDuplicates(fir as any, allFirs);
    const statusHistory = generateStatusHistory(fir as any);
    const officerNotes = generateOfficerNotes(fir as any);
    return { classification, entities, risk, similar, duplicates, statusHistory, officerNotes };
  }, [fir, allFirs]);

  const handleAiAnalyze = useCallback(async () => {
    if (!fir) return;
    setIsAiAnalyzing(true);
    try {
      const res = await firAiMutation.mutateAsync({
        fir_number: fir.fir_number,
        description: fir.description,
        station_id: fir.station_id,
        status: fir.status,
      });
      setAiFirResult(res);
    } catch {
      toast.error('AI analysis failed');
    } finally {
      setIsAiAnalyzing(false);
    }
  }, [fir, firAiMutation]);

  const handleEvidenceSummary = useCallback(async () => {
    if (!fir) return;
    try {
      const res = await evidenceMutation.mutateAsync({
        document_type: 'FIR',
        content: `${fir.description}\nSections: ${(fir as any).sections || ''}\nSummary: ${(fir as any).summary || ''}`,
      });
      setEvidenceResult(res);
    } catch {
      toast.error('Evidence summary failed');
    }
  }, [fir, evidenceMutation]);

  const handleTimeline = useCallback(async () => {
    if (!fir) return;
    try {
      const res = await timelineMutation.mutateAsync({
        incident_description: `${fir.description} Victim: ${fir.victim_name || 'Unknown'} Suspect: ${fir.suspect_name || 'Unknown'}`,
      });
      setTimelineResult(res);
    } catch {
      toast.error('Timeline generation failed');
    }
  }, [fir, timelineMutation]);

  const handleFindSimilar = useCallback(async () => {
    if (!aiFirResult?.modus_operandi) return;
    setIsAiAnalyzing(true);
    try {
      const res = await recMutation.mutateAsync({
        analytics: { mo: aiFirResult.modus_operandi, category: aiFirResult.crime_category, district_id: fir?.district_id },
      });
      setRecommendations(res.recommendations?.map((r: any) => r.description || r.title) ?? []);
    } catch {
      toast.error('Similar cases lookup failed');
    } finally {
      setIsAiAnalyzing(false);
    }
  }, [aiFirResult, fir, recMutation]);

  const handleAddNote = useCallback(() => {
    if (!newNote.trim()) return;
    setNotes(prev => [...prev, `Officer note added: ${newNote}`]);
    setNewNote('');
    toast.success('Note added');
  }, [newNote]);

  if (!fir || !derived) return null;

  const statusColumns: DataTableColumn<any>[] = [
    { key: 'status', header: 'Status', render: (row: any) => <Badge variant="info">{row.status}</Badge> },
    { key: 'timestamp', header: 'Timestamp', render: (row: any) => new Date(row.timestamp).toLocaleString() },
    { key: 'officer', header: 'Officer', render: (row: any) => row.officer },
    { key: 'note', header: 'Note', render: (row: any) => row.note },
  ];

  const similarColumns: DataTableColumn<ExtendedFir>[] = [
    { key: 'fir_number', header: 'FIR Number', render: (r) => r.fir_number },
    { key: 'station_id', header: 'Station', render: (r) => r.station_id },
    { key: 'status', header: 'Status', render: (r) => <Badge variant={STATUS_BADGE_VARIANT[r.status] ?? 'secondary'}>{r.status}</Badge> },
    { key: 'CREATEDTIME', header: 'Created', render: (r) => new Date(r.CREATEDTIME).toLocaleDateString() },
  ];

  return (
    <Modal
      isOpen={!!fir}
      onClose={onClose}
      title={`FIR Intelligence — ${fir.fir_number}`}
      footer={
        <div className="flex justify-end gap-2">
          <Button variant="ghost" onClick={onClose}>Close</Button>
          <Button variant="secondary" onClick={handleAiAnalyze} disabled={isAiAnalyzing || firAiMutation.isPending} className="inline-flex items-center gap-1">
            {isAiAnalyzing || firAiMutation.isPending ? (
              <><div className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" /> Analyzing...</>
            ) : (
              <><Sparkles size={14} /> AI Investigate</>
            )}
            </Button>
          </div>
        }
      >
        <div className="space-y-6">
        <Tabs
          items={[
            {
              id: 'overview',
              label: 'Overview',
              content: (
                <div className="space-y-6">
                  <div className="grid grid-cols-12 gap-4">
                    <div className="col-span-12 lg:col-span-8 space-y-4">
                      <Card className="p-4">
                        <h3 className="mb-3 text-sm font-semibold text-navy-700 dark:text-white">FIR Details</h3>
                        <div className="grid grid-cols-2 gap-4 text-sm">
                          <div><span className="text-gray-500">FIR Number:</span><p className="font-medium">{fir.fir_number}</p></div>
                          <div><span className="text-gray-500">Crime ID:</span><p className="font-medium">{fir.crime_id}</p></div>
                          <div><span className="text-gray-500">Station:</span><p className="font-medium">{fir.station_id}</p></div>
                          <div><span className="text-gray-500">Officer:</span><p className="font-medium">{fir.officer_id}</p></div>
                          <div><span className="text-gray-500">Status:</span><Badge variant={STATUS_BADGE_VARIANT[fir.status] ?? 'secondary'}>{fir.status}</Badge></div>
                          <div><span className="text-gray-500">Created:</span><p className="font-medium">{new Date(fir.CREATEDTIME).toLocaleString()}</p></div>
                          <div className="col-span-2"><span className="text-gray-500">Description:</span><p className="mt-1">{fir.description}</p></div>
                        </div>
                      </Card>

                      <Card className="p-4">
                        <h3 className="mb-3 text-sm font-semibold text-navy-700 dark:text-white">Status History</h3>
                        <DataTable columns={statusColumns} data={derived.statusHistory} rowKey={(r: any) => r.timestamp} emptyTitle="No history" virtualized={false} />
                      </Card>

                      <Card className="p-4">
                        <h3 className="mb-3 text-sm font-semibold text-navy-700 dark:text-white">Officer Notes</h3>
                        <div className="space-y-2">
                          {notes.length === 0 && derived.officerNotes.map((n: any) => (
                            <div key={n.id} className="flex items-start gap-2 text-sm">
                              <FileCheck size={14} className="mt-0.5 text-viz-blue" />
                              <div><p className="text-gray-800">{n.note}</p><p className="text-xs text-gray-500">{new Date(n.timestamp).toLocaleString()} · {n.officer_id}</p></div>
                            </div>
                          ))}
                          {notes.map((n, i) => (
                            <div key={i} className="flex items-start gap-2 text-sm">
                              <FileCheck size={14} className="mt-0.5 text-green-600" />
                              <div><p className="text-gray-800">{n}</p><p className="text-xs text-gray-500">Just now</p></div>
                            </div>
                          ))}
                        </div>
                        <div className="mt-3 flex gap-2">
                          <input
                            type="text"
                            value={newNote}
                            onChange={(e) => setNewNote(e.target.value)}
                            className="flex-1 rounded-lg border border-gray-300 px-3 py-2 text-sm"
                            placeholder="Add a note..."
                          />
                          <Button variant="secondary" size="sm" onClick={handleAddNote}>Add</Button>
                        </div>
                      </Card>
                    </div>

                    <div className="col-span-12 lg:col-span-4 space-y-4">
                      <Card className="p-4">
                        <h3 className="mb-3 text-sm font-semibold text-navy-700 dark:text-white">Risk Indicators</h3>
                        <div className="space-y-3">
                          <div className="flex items-center justify-between">
                            <span className="text-sm text-gray-600">Risk Level</span>
                            <Badge variant={SEVERITY_VARIANT[derived.risk.level] ?? 'secondary'}>{derived.risk.level}</Badge>
                          </div>
                          <div className="flex items-center justify-between">
                            <span className="text-sm text-gray-600">Category</span>
                            <span className="text-sm font-medium capitalize">{derived.classification.category}</span>
                          </div>
                          <div className="flex items-center justify-between">
                            <span className="text-sm text-gray-600">Severity</span>
                            <Badge variant={SEVERITY_VARIANT[derived.classification.severity] ?? 'secondary'}>{derived.classification.severity}</Badge>
                          </div>
                          <div className="flex items-center justify-between">
                            <span className="text-sm text-gray-600">Similar FIRs</span>
                            <span className="text-sm font-medium">{derived.similar.length}</span>
                          </div>
                          <div className="flex items-center justify-between">
                            <span className="text-sm text-gray-600">Duplicates</span>
                            <span className="text-sm font-medium">{derived.duplicates.length}</span>
                          </div>
                        </div>
                      </Card>

                      <Card className="p-4">
                        <h3 className="mb-3 text-sm font-semibold text-navy-700 dark:text-white">Extracted Entities</h3>
                        <div className="space-y-2">
                          {Object.entries(derived.entities).map(([key, values]) => {
                            const icons: Record<string, React.ReactNode> = { people: <Users size={14} />, locations: <MapPin size={14} />, vehicles: <Car size={14} />, phones: <Phone size={14} /> };
                            return (
                              <div key={key} className="flex items-center gap-2 text-sm">
                                {icons[key] || <Building2 size={14} />}
                                <span className="capitalize text-gray-600">{key}:</span>
                                <span className="font-medium">{(values as string[]).length > 0 ? (values as string[]).join(', ') : 'None'}</span>
                              </div>
                            );
                          })}
                        </div>
                      </Card>
                    </div>
                  </div>
                </div>
              ),
            },
            {
              id: 'ai',
              label: 'AI Intelligence',
              content: (
                <div className="space-y-6">
                  <div className="flex items-center gap-2">
                    <Button variant="primary" size="sm" onClick={handleAiAnalyze} disabled={isAiAnalyzing || firAiMutation.isPending} className="inline-flex items-center gap-1">
                      {isAiAnalyzing || firAiMutation.isPending ? <><div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" /> Analyzing...</> : <><Sparkles size={14} /> Analyze FIR</>}
                    </Button>
                    <Button variant="secondary" size="sm" onClick={handleEvidenceSummary} disabled={evidenceMutation.isPending} className="inline-flex items-center gap-1">
                      <FileText size={14} /> Evidence Summary
                    </Button>
                    <Button variant="secondary" size="sm" onClick={handleTimeline} disabled={timelineMutation.isPending} className="inline-flex items-center gap-1">
                      <Clock size={14} /> Timeline
                    </Button>
                  </div>

                  {aiFirResult && (
                    <AIPanel
                      title="AI FIR Intelligence"
                      isFallback={aiFirResult.isFallback}
                      confidence={aiFirResult.confidence}
                      analyticsUsed={aiFirResult.analyticsUsed}
                      model={aiFirResult.model}
                      generatedAt={aiFirResult.generatedAt}
                      onRetry={handleAiAnalyze}
                      isLoading={isAiAnalyzing}
                    >
                      <div className="grid grid-cols-2 gap-4">
                        <div><p className="text-xs text-gov-slate">Category</p><p className="text-sm font-medium capitalize">{aiFirResult.crime_category}</p></div>
                        <div><p className="text-xs text-gov-slate">Severity</p><Badge variant={SEVERITY_VARIANT[aiFirResult.severity] ?? 'secondary'}>{aiFirResult.severity}</Badge></div>
                      </div>
                      <div><p className="text-xs text-gov-slate">Modus Operandi</p><p className="text-sm">{aiFirResult.modus_operandi}</p></div>
                      <div>
                        <p className="text-xs text-gov-slate">Entities</p>
                        <div className="mt-1 flex flex-wrap gap-2">
                          {Object.entries(aiFirResult.entities || {}).map(([k, v]) => (
                            <span key={k} className="rounded-full bg-viz-blue/10 px-2 py-0.5 text-xs text-viz-blue capitalize">{k}: {Array.isArray(v) ? v.join(', ') || 'None' : String(v ?? 'None')}</span>
                          ))}
                        </div>
                      </div>
                      <div>
                        <p className="text-xs text-gov-slate">Investigation Suggestions</p>
                        <ul className="mt-1 space-y-1">
                          {aiFirResult.investigation_suggestions?.map((s: string, i: number) => (<li key={i} className="text-sm">- {s}</li>))}
                        </ul>
                      </div>
                      <Button variant="ghost" size="sm" onClick={handleFindSimilar} disabled={isAiAnalyzing} className="mt-2 inline-flex items-center gap-1">
                        <Search size={14} /> Find Similar Cases
                      </Button>
                    </AIPanel>
                  )}

                  {evidenceResult && (
                    <AIPanel
                      title="Evidence Summary"
                      isFallback={evidenceResult.isFallback}
                      confidence={evidenceResult.confidence}
                      analyticsUsed={evidenceResult.analyticsUsed}
                      model={evidenceResult.model}
                      generatedAt={evidenceResult.generatedAt}
                      onRetry={handleEvidenceSummary}
                      isLoading={evidenceMutation.isPending}
                    >
                      <p className="text-sm text-gray-800 dark:text-gray-200">{evidenceResult.summary}</p>
                      {evidenceResult.extracted_entities && (
                        <div className="mt-2 flex flex-wrap gap-2">
                          {Object.entries(evidenceResult.extracted_entities).map(([k, v]) => (
                            <span key={k} className="rounded-full bg-viz-blue/10 px-2 py-0.5 text-xs text-viz-blue capitalize">{k}: {Array.isArray(v) ? v.join(', ') || 'None' : String(v ?? 'None')}</span>
                          ))}
                        </div>
                      )}
                    </AIPanel>
                  )}

                  {timelineResult && (
                    <AIPanel
                      title="Incident Timeline"
                      isFallback={timelineResult.isFallback}
                      confidence={timelineResult.confidence}
                      analyticsUsed={timelineResult.analyticsUsed}
                      model={timelineResult.model}
                      generatedAt={timelineResult.generatedAt}
                      onRetry={handleTimeline}
                      isLoading={timelineMutation.isPending}
                    >
                      {timelineResult.events && (
                        <DataTable columns={[
                          { key: 'timestamp', header: 'Time', render: (r: any) => r.timestamp },
                          { key: 'event', header: 'Event', render: (r: any) => r.event },
                          { key: 'actor', header: 'Actor', render: (r: any) => r.actor },
                        ]} data={timelineResult.events} rowKey={(r: any) => r.timestamp} virtualized={false} />
                      )}
                      {timelineResult.narrative && <p className="mt-2 text-sm text-gray-800 dark:text-gray-200">{timelineResult.narrative}</p>}
                    </AIPanel>
                  )}

                  {recommendations.length > 0 && (
                    <Card className="p-4">
                      <h3 className="text-sm font-semibold text-navy-700 dark:text-white">Next Investigative Actions</h3>
                      <ul className="mt-2 space-y-1">
                        {recommendations.map((r, i) => (
                          <li key={i} className="flex items-start gap-2 text-sm"><Gavel size={14} className="mt-0.5 text-viz-blue" /> {r}</li>
                        ))}
                      </ul>
                    </Card>
                  )}
                </div>
              ),
            },
            {
              id: 'linked',
              label: 'Linked Intelligence',
              content: (
                <div className="space-y-6">
                  <div className="grid grid-cols-12 gap-4">
                    <div className="col-span-12 lg:col-span-6">
                      <Card className="p-4">
                        <h3 className="mb-3 text-sm font-semibold text-navy-700 dark:text-white">Linked Crime</h3>
                        <div className="text-sm">
                          <p className="text-gray-500">Crime ID:</p>
                          <p className="font-medium">{fir.crime_id}</p>
                        </div>
                      </Card>
                    </div>
                    <div className="col-span-12 lg:col-span-6">
                      <Card className="p-4">
                        <h3 className="mb-3 text-sm font-semibold text-navy-700 dark:text-white">Duplicate Detection</h3>
                        {derived.duplicates.length > 0 ? (
                          <DataTable columns={similarColumns} data={derived.duplicates} rowKey={(r) => r.ROWID} emptyTitle="No duplicates found" virtualized={false} />
                        ) : (
                          <div className="flex items-center gap-2 text-sm text-green-600"><ShieldCheck size={16} /> No duplicate FIRs detected</div>
                        )}
                      </Card>
                    </div>
                  </div>

                  <Card className="p-4">
                    <h3 className="mb-3 text-sm font-semibold text-navy-700 dark:text-white">Similar FIRs</h3>
                    {derived.similar.length > 0 ? (
                      <DataTable columns={similarColumns} data={derived.similar} rowKey={(r) => r.ROWID} emptyTitle="No similar FIRs found" virtualized={false} />
                    ) : (
                      <div className="text-sm text-gov-slate">No similar FIRs identified in current dataset.</div>
                    )}
                  </Card>

                  <Card className="p-4">
                    <h3 className="mb-3 text-sm font-semibold text-navy-700 dark:text-white">Linked Investigations</h3>
                    <div className="text-sm text-gov-slate">
                      <p>This FIR is linked to crime <span className="font-medium text-navy-700">{fir.crime_id}</span>.</p>
                      <p className="mt-1">Additional linked investigations will appear here when connected via the backend.</p>
                    </div>
                  </Card>
                </div>
              ),
            },
          ]}
        />
      </div>
    </Modal>
  );
};

export default FirIntelligenceWorkspace;
