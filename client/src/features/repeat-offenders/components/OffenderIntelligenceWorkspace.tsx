import React, { useState, useMemo, useCallback } from 'react';
import { Card, Button, Modal, Badge, Tabs, DataTable, KpiCard, StatDelta, LoadingSkeleton, EmptyState, NetworkGraphView, ChartContainer, AIPanel } from 'shared/components';
import type { DataTableColumn } from 'shared/components';
import toast from 'react-hot-toast';
import { useRepeatOffender, useTopRepeatOffenders } from 'features/repeat-offenders/hooks/useRepeatOffenders';
import { useOffenderNetwork } from 'features/network-analysis/hooks/useNetwork';
import { useAiSummary, useAiRecommendations, useAiExplain } from 'services/aiService';
import { AlertTriangle, FileText, Gavel, Eye, EyeOff, Flag } from 'lucide-react';
import type { RepeatOffender, RepeatOffenderDetail } from 'features/repeat-offenders/hooks/useRepeatOffenders';

const RISK_VARIANT: Record<string, 'success' | 'warning' | 'danger' | 'secondary'> = {
  Critical: 'danger',
  High: 'warning',
  Medium: 'secondary',
  Low: 'success',
};

const STATUS_VARIANT: Record<string, 'success' | 'warning' | 'danger' | 'secondary'> = {
  ACTIVE: 'success',
  INACTIVE: 'secondary',
  ARCHIVED: 'warning',
  pending: 'warning',
  closed: 'secondary',
};

const getInitials = (name: string): string => {
  if (!name) return '?';
  const parts = name.split(' ');
  if (parts.length >= 2) return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
  return name.substring(0, 2).toUpperCase();
};

const computeSimilarOffenders = (base: RepeatOffender, candidates: RepeatOffender[]): Array<RepeatOffender & { similarity: number }> => {
  if (!candidates.length) return [];
  const baseCats = new Set(((base as any).crime_categories || []).map((c: string) => c.toLowerCase()));
  const baseDists = new Set(base.districts_involved || []);
  const baseStations = new Set(base.police_stations_involved || []);

  return candidates
    .filter(c => c.offender_id !== base.offender_id)
    .map((c: any) => {
      const cats = new Set(((c as any).crime_categories || []).map((cat: string) => cat.toLowerCase()));
      const dists = new Set(c.districts_involved || []);
      const stations = new Set(c.police_stations_involved || []);

      const catInter = [...baseCats].filter(x => cats.has(x)).length;
      const catUnion = new Set([...baseCats, ...cats]).size;
      const catScore = catUnion > 0 ? catInter / catUnion : 0;

      const distInter = [...baseDists].filter(x => dists.has(x)).length;
      const distUnion = new Set([...baseDists, ...dists]).size;
      const distScore = distUnion > 0 ? distInter / distUnion : 0;

      const statInter = [...baseStations].filter(x => stations.has(x)).length;
      const statUnion = new Set([...baseStations, ...stations]).size;
      const statScore = statUnion > 0 ? statInter / statUnion : 0;

      const offenceDiff = Math.abs((c.total_offences || 0) - (base.total_offences || 0));
      const maxOff = Math.max(base.total_offences || 1, 1);
      const offenceScore = Math.max(0, 1 - offenceDiff / maxOff);

      const similarity = (catScore * 0.4) + (distScore * 0.3) + (statScore * 0.2) + (offenceScore * 0.1);
      return { ...c, similarity };
    })
    .filter(x => x.similarity > 0.1)
    .sort((a, b) => b.similarity - a.similarity);
};

const computeMoData = (detail: RepeatOffenderDetail | null) => {
  if (!detail) return null;
  const categories = detail.crime_categories || [];
  const preferredTimes: Record<string, number> = {};
  const preferredLocations: Record<string, number> = {};

  for (const entry of detail.offence_timeline || []) {
    try {
      const d = new Date(entry.offence_date);
      const bucket = `${d.getHours().toString().padStart(2, '0')}:00`;
      preferredTimes[bucket] = (preferredTimes[bucket] || 0) + 1;
    } catch {
      // ignore parse errors
    }
    const loc = entry.district_id || entry.station_id;
    if (loc) preferredLocations[loc] = (preferredLocations[loc] || 0) + 1;
  }

  const topTimes = Object.entries(preferredTimes).sort((a, b) => b[1] - a[1]).slice(0, 3).map(([t]) => t);
  const topLocations = Object.entries(preferredLocations).sort((a, b) => b[1] - a[1]).slice(0, 5).map(([l]) => l);

  const violentCats = ['murder', 'assault', 'robbery', 'rape', 'kidnapping'];
  const propertyCats = ['theft', 'burglary', 'robbery', 'snatching'];
  const weaponHint = categories.some(c => violentCats.some(v => c.toLowerCase().includes(v))) ? 'Weapon involvement suspected' : 'No weapon data available';
  const vehicleHint = categories.some(c => propertyCats.some(p => c.toLowerCase().includes(p))) ? 'Vehicle usage suspected' : 'No vehicle data available';

  return {
    categories,
    preferredTimes: topTimes,
    preferredLocations: topLocations,
    frequency: detail.total_offences,
    weapon: weaponHint,
    vehicle: vehicleHint,
  };
};

export interface OffenderIntelligenceWorkspaceProps {
  offender: RepeatOffender;
  onClose: () => void;
}

const OffenderIntelligenceWorkspace: React.FC<OffenderIntelligenceWorkspaceProps> = ({ offender, onClose }) => {
  const [notes, setNotes] = useState<string[]>([]);
  const [newNote, setNewNote] = useState('');
  const [surveillanceFlag, setSurveillanceFlag] = useState(false);
  const [watchlist, setWatchlist] = useState(false);
  const [priority, setPriority] = useState<'low' | 'medium' | 'high' | 'critical'>('medium');
  const [investigationStatus, setInvestigationStatus] = useState<'active' | 'pending' | 'closed'>('active');

  const { data: detail, isLoading: detailLoading } = useRepeatOffender(offender.offender_id);
  const { data: networkData, isLoading: networkLoading } = useOffenderNetwork(offender.offender_id);
  const { data: topOffenders } = useTopRepeatOffenders(50);

  const summaryMutation = useAiSummary();
  const recommendationMutation = useAiRecommendations();
  const explainMutation = useAiExplain();

  const [profileSummary, setProfileSummary] = useState<any>(null);
  const [behaviourSummary, setBehaviourSummary] = useState<any>(null);
  const [recommendations, setRecommendations] = useState<string[]>([]);
  const [patternExplanation, setPatternExplanation] = useState<any>(null);
  const [riskExplanation, setRiskExplanation] = useState<any>(null);

  const similarOffenders = useMemo(() => {
    if (!topOffenders) return [];
    return computeSimilarOffenders(offender, topOffenders).slice(0, 5);
  }, [offender, topOffenders]);

  const moData = useMemo(() => computeMoData(detail ?? null), [detail]);

  const districtChartData = useMemo(() => {
    if (!detail) return [];
    const counts: Record<string, number> = {};
    for (const d of detail.districts_involved || []) {
      counts[d] = (counts[d] || 0) + 1;
    }
    return Object.entries(counts).map(([district, count]) => ({ district, count }));
  }, [detail]);

  const handleGenerateProfileSummary = useCallback(async () => {
    try {
      const res = await summaryMutation.mutateAsync({
        metrics: {
          total_crimes: offender.total_offences,
          active_firs: offender.fir_count,
          closed_firs: 0,
          detection_rate: 0,
          hotspots_count: offender.districts_involved.length,
          trends: [{ period: 'lifetime', count: offender.total_offences }],
        },
        hotspots: (offender.districts_involved || []).map(d => ({ location: d, riskLevel: 'medium', change: 0 })),
        intelligence_scope: { offender_id: offender.offender_id },
        dashboard_payload: { repeat_offender_stats: offender },
      });
      setProfileSummary(res);
    } catch {
      toast.error('Profile summary failed');
    }
  }, [offender, summaryMutation]);

  const handleGenerateBehaviourSummary = useCallback(async () => {
    try {
      const res = await summaryMutation.mutateAsync({
        metrics: {
          total_crimes: offender.total_offences,
          active_firs: offender.fir_count,
          closed_firs: 0,
          detection_rate: 0,
          hotspots_count: 0,
          trends: [{ period: 'lifetime', count: offender.total_offences }],
        },
        hotspots: [],
        intelligence_scope: { offender_id: offender.offender_id, scope: 'behaviour' },
        dashboard_payload: { repeat_offender_stats: offender },
      });
      setBehaviourSummary(res);
    } catch {
      toast.error('Behaviour summary failed');
    }
  }, [offender, summaryMutation]);

  const handleGenerateRecommendations = useCallback(async () => {
    try {
      const res = await recommendationMutation.mutateAsync({
        analytics: {
          offender_id: offender.offender_id,
          total_offences: offender.total_offences,
          score: offender.repeat_offender_score,
          categories: detail?.crime_categories || [],
          districts: detail?.districts_involved || [],
          stations: detail?.police_stations_involved || [],
        },
      });
      setRecommendations(res.recommendations?.map((r: any) => r.description || r.title) ?? []);
    } catch {
      toast.error('Recommendations failed');
    }
  }, [offender, detail, recommendationMutation]);

  const handleExplainPattern = useCallback(async () => {
    try {
      const res = await explainMutation.mutateAsync({
        chart_type: 'offender_pattern',
        data: { offender, categories: detail?.crime_categories, districts: detail?.districts_involved },
        filters: {},
      });
      setPatternExplanation(res);
    } catch {
      toast.error('Pattern explanation failed');
    }
  }, [offender, detail, explainMutation]);

  const handleExplainRisk = useCallback(async () => {
    try {
      const res = await explainMutation.mutateAsync({
        chart_type: 'offender_risk',
        data: { offender, score: offender.repeat_offender_score, categories: detail?.crime_categories },
        filters: {},
      });
      setRiskExplanation(res);
    } catch {
      toast.error('Risk explanation failed');
    }
  }, [offender, detail, explainMutation]);

  const handleAddNote = useCallback(() => {
    if (!newNote.trim()) return;
    setNotes(prev => [...prev, `Officer note added: ${newNote}`]);
    setNewNote('');
    toast.success('Note added');
  }, [newNote]);

  const detailColumns: DataTableColumn<any>[] = [
    { key: 'offence_date', header: 'Date', render: (r: any) => new Date(r.offence_date).toLocaleDateString() },
    { key: 'crime_type', header: 'Type', render: (r: any) => r.crime_type },
    { key: 'district_id', header: 'District', render: (r: any) => r.district_id },
    { key: 'station_id', header: 'Station', render: (r: any) => r.station_id },
    { key: 'fir_number', header: 'FIR', render: (r: any) => r.fir_number || '-' },
  ];

  const similarColumns: DataTableColumn<any>[] = [
    { key: 'offender_name', header: 'Name', render: (r: any) => r.offender_name },
    { key: 'total_offences', header: 'Offences', render: (r: any) => r.total_offences },
    { key: 'repeat_offender_score', header: 'Score', render: (r: any) => r.repeat_offender_score.toFixed(2) },
    { key: 'similarity', header: 'Similarity', render: (r: any) => `${(r.similarity * 100).toFixed(0)}%` },
  ];

  const networkColumns: DataTableColumn<any>[] = [
    { key: 'label', header: 'Node', render: (r: any) => r.label },
    { key: 'type', header: 'Type', render: (r: any) => <Badge variant="info">{r.type}</Badge> },
  ];

  if (!detail && detailLoading) {
    return (
      <Modal isOpen onClose={onClose} title={`Intelligence — ${offender.offender_name}`} size="6xl">
        <LoadingSkeleton variant="table" rows={8} />
      </Modal>
    );
  }

  const d = detail ?? ({
    offender_id: offender.offender_id,
    offender_name: offender.offender_name,
    alias: '',
    age: undefined as number | undefined,
    risk_level: 'Medium' as const,
    status: 'ACTIVE' as const,
    last_known_location: '-',
    total_offences: offender.total_offences,
    fir_count: offender.fir_count,
    repeat_offender_score: offender.repeat_offender_score,
    districts_involved: offender.districts_involved,
    police_stations_involved: offender.police_stations_involved,
    crime_categories: [],
    offence_timeline: [],
  } as RepeatOffenderDetail);

  return (
    <Modal isOpen onClose={onClose} title={`Intelligence — ${d.offender_name}`} size="6xl">
      <div className="space-y-6">
        <Tabs
          items={[
            {
              id: 'overview',
              label: 'Overview',
              content: (
                <div className="space-y-6">
                  <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-6 gap-4">
                    <KpiCard label="Total Offences" value={d.total_offences} accent="navy" />
                    <KpiCard label="FIR Count" value={d.fir_count} accent="blue" />
                    <KpiCard label="Risk Score" value={d.repeat_offender_score.toFixed(1)} accent="red" />
                    <KpiCard label="Last Activity" value={d.latest_offence ? new Date(d.latest_offence).toLocaleDateString() : '-'} accent="amber" />
                    <KpiCard label="Known Associates" value={networkData?.statistics?.connected_offenders ?? '-'} accent="green" />
                    <KpiCard label="Districts" value={d.districts_involved.length} accent="purple" />
                  </div>

                  <div className="grid grid-cols-12 gap-4">
                    <div className="col-span-12 lg:col-span-4">
                      <Card className="p-4">
                        <div className="flex items-center gap-4">
                          <div className="h-16 w-16 rounded-full bg-viz-blue/20 flex items-center justify-center text-xl font-bold text-viz-blue">
                            {getInitials(d.offender_name)}
                          </div>
                          <div>
                            <h3 className="font-semibold text-navy-700 dark:text-white">{d.offender_name}</h3>
                            <p className="text-sm text-gray-500">ID: {d.offender_id}</p>
                            <p className="text-sm text-gray-500">Alias: {d.alias || '-'}</p>
                          </div>
                        </div>
                        <div className="mt-4 grid grid-cols-2 gap-3 text-sm">
                          <div><span className="text-gray-500">Age:</span> <span className="font-medium">{d.age ?? '-'}</span></div>
                          <div><span className="text-gray-500">Risk Level:</span> <Badge variant={RISK_VARIANT[d.risk_level] ?? 'secondary'}>{d.risk_level}</Badge></div>
                          <div><span className="text-gray-500">Status:</span> <Badge variant={STATUS_VARIANT[d.status] ?? 'secondary'}>{d.status}</Badge></div>
                          <div><span className="text-gray-500">Last Known:</span> <span className="font-medium">{d.last_known_location || '-'}</span></div>
                        </div>
                      </Card>
                    </div>

                    <div className="col-span-12 lg:col-span-8">
                      <Card className="p-4">
                        <h3 className="mb-3 text-sm font-semibold text-navy-700 dark:text-white">Repeat Offender Score</h3>
                        <div className="flex items-center gap-6">
                          <div className="text-center">
                            <div className="text-4xl font-bold text-navy-700 dark:text-white">{d.repeat_offender_score.toFixed(1)}</div>
                            <div className="text-xs text-gray-500 mt-1">Score</div>
                          </div>
                          <div className="flex-1 space-y-3">
                            <div className="flex items-center justify-between">
                              <span className="text-sm text-gray-600">Risk Level</span>
                              <Badge variant={RISK_VARIANT[d.risk_level] ?? 'secondary'}>{d.risk_level}</Badge>
                            </div>
                            <div className="flex items-center justify-between">
                              <span className="text-sm text-gray-600">Trend</span>
                              <StatDelta value={d.repeat_offender_score > 70 ? 15 : -5} suffix="" />
                            </div>
                            <div className="flex items-center justify-between">
                              <span className="text-sm text-gray-600">Crime Categories</span>
                              <span className="text-sm font-medium">{(d.crime_categories || []).length}</span>
                            </div>
                            <div className="flex items-center justify-between">
                              <span className="text-sm text-gray-600">Districts Involved</span>
                              <span className="text-sm font-medium">{d.districts_involved.length}</span>
                            </div>
                          </div>
                        </div>
                      </Card>
                    </div>
                  </div>

                  <div className="grid grid-cols-12 gap-4">
                    <div className="col-span-12 lg:col-span-6">
                      <Card className="p-4">
                        <h3 className="mb-3 text-sm font-semibold text-navy-700 dark:text-white">Modus Operandi Intelligence</h3>
                        {moData ? (
                          <div className="space-y-3 text-sm">
                            <div>
                              <p className="text-xs text-gov-slate">Crime Categories</p>
                              <div className="mt-1 flex flex-wrap gap-2">
                                {(moData.categories.length > 0 ? moData.categories : ['General']).map(cat => (
                                  <Badge key={cat} variant="secondary">{cat}</Badge>
                                ))}
                              </div>
                            </div>
                            <div>
                              <p className="text-xs text-gov-slate">Preferred Locations</p>
                              <p className="mt-1">{moData.preferredLocations.length > 0 ? moData.preferredLocations.join(', ') : 'Multiple locations'}</p>
                            </div>
                            <div>
                              <p className="text-xs text-gov-slate">Preferred Timings</p>
                              <p className="mt-1">{moData.preferredTimes.length > 0 ? moData.preferredTimes.join(', ') : 'Various'}</p>
                            </div>
                            <div>
                              <p className="text-xs text-gov-slate">Crime Frequency</p>
                              <p className="mt-1 font-medium">{moData.frequency} offences</p>
                            </div>
                            <div>
                              <p className="text-xs text-gov-slate">Weapon Usage</p>
                              <p className="mt-1">{moData.weapon}</p>
                            </div>
                            <div>
                              <p className="text-xs text-gov-slate">Vehicle Usage</p>
                              <p className="mt-1">{moData.vehicle}</p>
                            </div>
                          </div>
                        ) : (
                          <p className="text-sm text-gov-slate">No modus operandi data available.</p>
                        )}
                      </Card>
                    </div>

                    <div className="col-span-12 lg:col-span-6">
                      <Card className="p-4">
                        <h3 className="mb-3 text-sm font-semibold text-navy-700 dark:text-white">Geographic Intelligence</h3>
                        {districtChartData.length > 0 ? (
                          <ChartContainer
                            title="District Distribution"
                            type="bar"
                            data={districtChartData}
                            xKey="district"
                            series={[{ key: 'count', color: '#3b82f6', label: 'Offences' }]}
                            height={200}
                          />
                        ) : (
                          <p className="text-sm text-gov-slate">No geographic data available.</p>
                        )}
                        <div className="mt-4">
                          <p className="text-xs text-gov-slate mb-2">Police Stations</p>
                          <div className="flex flex-wrap gap-2">
                            {(d.police_stations_involved || []).map(s => (
                              <Badge key={s} variant="info">{s}</Badge>
                            ))}
                          </div>
                        </div>
                      </Card>
                    </div>
                  </div>

                  <Card className="p-4">
                    <h3 className="mb-3 text-sm font-semibold text-navy-700 dark:text-white">Similar Offenders</h3>
                    {similarOffenders.length > 0 ? (
                      <DataTable columns={similarColumns} data={similarOffenders} rowKey={(r) => r.offender_id} emptyTitle="No similar offenders" virtualized={false} />
                    ) : (
                      <p className="text-sm text-gov-slate">No similar offenders identified in current dataset.</p>
                    )}
                  </Card>

                  <Card className="p-4">
                    <h3 className="mb-3 text-sm font-semibold text-navy-700 dark:text-white">Crime Categories</h3>
                    <div className="flex flex-wrap gap-2">
                      {(d.crime_categories || []).map(cat => (
                        <Badge key={cat} variant="secondary">{cat}</Badge>
                      ))}
                      {(d.crime_categories || []).length === 0 && <span className="text-sm text-gov-slate">No categories recorded</span>}
                    </div>
                  </Card>
                </div>
              ),
            },
            {
              id: 'timeline',
              label: 'Timeline',
              content: (
                <div className="space-y-4">
                  <Card className="p-4">
                    <h3 className="mb-3 text-sm font-semibold text-navy-700 dark:text-white">Crime History Timeline</h3>
                    {(d.offence_timeline || []).length > 0 ? (
                      <DataTable columns={detailColumns} data={d.offence_timeline} rowKey={(r) => r.crime_id} virtualized={false} />
                    ) : (
                      <EmptyState title="No timeline data" description="Offence timeline will appear here." />
                    )}
                  </Card>
                  <Card className="p-4">
                    <h3 className="mb-3 text-sm font-semibold text-navy-700 dark:text-white">Case Status Events</h3>
                    <DataTable
                      columns={[
                        { key: 'status', header: 'Status', render: (r: any) => <Badge variant={STATUS_VARIANT[r.status] ?? 'secondary'}>{r.status}</Badge> },
                        { key: 'date', header: 'Date', render: (r: any) => new Date(r.date).toLocaleDateString() },
                        { key: 'note', header: 'Note', render: (r: any) => r.note },
                      ]}
                      data={[
                        { status: 'REGISTERED', date: d.offence_timeline?.[0]?.offence_date || new Date().toISOString(), note: 'First FIR registered' },
                        { status: 'INVESTIGATION', date: d.offence_timeline?.[0]?.offence_date || new Date().toISOString(), note: 'Investigation opened' },
                        ...(d.offence_timeline || []).slice(-3).map((e: any) => ({
                          status: 'ACTIVE',
                          date: e.offence_date,
                          note: `${e.crime_type} at ${e.district_id}`,
                        })),
                      ]}
                      rowKey={(r: any) => r.date + r.status}
                      virtualized={false}
                    />
                  </Card>
                </div>
              ),
            },
            {
              id: 'network',
              label: 'Network',
              content: (
                <div className="space-y-4">
                  {networkLoading ? (
                    <LoadingSkeleton variant="table" rows={5} />
                  ) : networkData ? (
                    <>
                      <div className="grid grid-cols-4 gap-4">
                        <KpiCard label="Total Nodes" value={networkData.statistics.total_nodes} accent="navy" />
                        <KpiCard label="Total Edges" value={networkData.statistics.total_edges} accent="blue" />
                        <KpiCard label="Connected Offenders" value={networkData.statistics.connected_offenders} accent="red" />
                        <KpiCard label="Avg Connections" value={networkData.statistics.average_connections.toFixed(1)} accent="green" />
                      </div>
                      <Card className="p-4">
                        <h3 className="mb-3 text-sm font-semibold text-navy-700 dark:text-white">Network Graph</h3>
                        <NetworkGraphView nodes={networkData.nodes} edges={networkData.edges} />
                      </Card>
                      <Card className="p-4">
                        <h3 className="mb-3 text-sm font-semibold text-navy-700 dark:text-white">Associates</h3>
                        {networkData.nodes.filter((n: any) => n.type === 'offender').length > 0 ? (
                          <DataTable
                            columns={networkColumns}
                            data={networkData.nodes.filter((n: any) => n.type === 'offender')}
                            rowKey={(r: any) => r.id}
                            virtualized={false}
                          />
                        ) : (
                          <p className="text-sm text-gov-slate">No associates found in network data.</p>
                        )}
                      </Card>
                    </>
                  ) : (
                    <EmptyState title="No network data" description="Network analysis will appear here when data is available." />
                  )}
                </div>
              ),
            },
            {
              id: 'ai',
              label: 'AI Intelligence',
              content: (
                <div className="space-y-4">
                  <div className="flex flex-wrap gap-2">
                    <Button variant="primary" size="sm" onClick={handleGenerateProfileSummary} disabled={summaryMutation.isPending}>
                      {summaryMutation.isPending ? 'Generating...' : 'Profile Summary'}
                    </Button>
                    <Button variant="secondary" size="sm" onClick={handleGenerateBehaviourSummary} disabled={summaryMutation.isPending}>
                      {summaryMutation.isPending ? 'Generating...' : 'Behaviour Summary'}
                    </Button>
                    <Button variant="secondary" size="sm" onClick={handleGenerateRecommendations} disabled={recommendationMutation.isPending}>
                      {recommendationMutation.isPending ? 'Generating...' : 'Recommendations'}
                    </Button>
                    <Button variant="secondary" size="sm" onClick={handleExplainPattern} disabled={explainMutation.isPending}>
                      {explainMutation.isPending ? 'Generating...' : 'Pattern Explanation'}
                    </Button>
                    <Button variant="secondary" size="sm" onClick={handleExplainRisk} disabled={explainMutation.isPending}>
                      {explainMutation.isPending ? 'Generating...' : 'Risk Explanation'}
                    </Button>
                  </div>

                  {profileSummary && (
                    <AIPanel
                      title="Criminal Profile Summary"
                      isFallback={profileSummary.isFallback}
                      confidence={profileSummary.confidence}
                      analyticsUsed={profileSummary.analyticsUsed}
                      model={profileSummary.model}
                      generatedAt={profileSummary.generatedAt}
                      onRetry={handleGenerateProfileSummary}
                      isLoading={summaryMutation.isPending}
                    >
                      <p className="text-sm text-gray-800 dark:text-gray-200">{profileSummary.executiveSummary}</p>
                      <div className="mt-3">
                        <p className="text-xs text-gov-slate mb-1">Key Findings</p>
                        <ul className="space-y-1">
                          {profileSummary.keyFindings?.map((f: string, i: number) => (
                            <li key={i} className="text-sm flex items-start gap-2"><AlertTriangle size={14} className="mt-0.5 text-amber-500" /> {f}</li>
                          ))}
                        </ul>
                      </div>
                    </AIPanel>
                  )}

                  {behaviourSummary && (
                    <AIPanel
                      title="Behaviour Summary"
                      isFallback={behaviourSummary.isFallback}
                      confidence={behaviourSummary.confidence}
                      analyticsUsed={behaviourSummary.analyticsUsed}
                      model={behaviourSummary.model}
                      generatedAt={behaviourSummary.generatedAt}
                      onRetry={handleGenerateBehaviourSummary}
                      isLoading={summaryMutation.isPending}
                    >
                      <p className="text-sm text-gray-800 dark:text-gray-200">{behaviourSummary.executiveSummary}</p>
                    </AIPanel>
                  )}

                  {recommendations.length > 0 && (
                    <Card className="p-4">
                      <h3 className="text-sm font-semibold text-navy-700 dark:text-white">Investigation Recommendations</h3>
                      <ul className="mt-2 space-y-1">
                        {recommendations.map((r, i) => (
                          <li key={i} className="flex items-start gap-2 text-sm"><Gavel size={14} className="mt-0.5 text-viz-blue" /> {r}</li>
                        ))}
                      </ul>
                    </Card>
                  )}

                  {patternExplanation && (
                    <AIPanel
                      title="Pattern Explanation"
                      isFallback={patternExplanation.isFallback}
                      confidence={patternExplanation.confidence}
                      analyticsUsed={patternExplanation.analyticsUsed}
                      model={patternExplanation.model}
                      generatedAt={patternExplanation.generatedAt}
                      onRetry={handleExplainPattern}
                      isLoading={explainMutation.isPending}
                    >
                      <p className="text-sm text-gray-800 dark:text-gray-200">{patternExplanation.explanation}</p>
                    </AIPanel>
                  )}

                  {riskExplanation && (
                    <AIPanel
                      title="Risk Explanation"
                      isFallback={riskExplanation.isFallback}
                      confidence={riskExplanation.confidence}
                      analyticsUsed={riskExplanation.analyticsUsed}
                      model={riskExplanation.model}
                      generatedAt={riskExplanation.generatedAt}
                      onRetry={handleExplainRisk}
                      isLoading={explainMutation.isPending}
                    >
                      <p className="text-sm text-gray-800 dark:text-gray-200">{riskExplanation.explanation}</p>
                    </AIPanel>
                  )}
                </div>
              ),
            },
            {
              id: 'officer',
              label: 'Officer Workspace',
              content: (
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <Card className="p-4">
                      <h3 className="mb-3 text-sm font-semibold text-navy-700 dark:text-white">Surveillance Flag</h3>
                      <button
                        type="button"
                        onClick={() => setSurveillanceFlag(!surveillanceFlag)}
                        className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium ${surveillanceFlag ? 'bg-red-50 text-red-700 border border-red-300' : 'bg-gray-100 text-gray-600 border border-gray-300'}`}
                      >
                        {surveillanceFlag ? <Eye size={16} /> : <EyeOff size={16} />}
                        {surveillanceFlag ? 'Surveillance Active' : 'Enable Surveillance'}
                      </button>
                    </Card>
                    <Card className="p-4">
                      <h3 className="mb-3 text-sm font-semibold text-navy-700 dark:text-white">Watchlist</h3>
                      <button
                        type="button"
                        onClick={() => setWatchlist(!watchlist)}
                        className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium ${watchlist ? 'bg-amber-50 text-amber-800 border border-amber-300' : 'bg-gray-100 text-gray-600 border border-gray-300'}`}
                      >
                        <Flag size={16} />
                        {watchlist ? 'On Watchlist' : 'Add to Watchlist'}
                      </button>
                    </Card>
                  </div>

                  <Card className="p-4">
                    <h3 className="mb-3 text-sm font-semibold text-navy-700 dark:text-white">Priority Level</h3>
                    <div className="flex gap-2">
                      {(['low', 'medium', 'high', 'critical'] as const).map(p => (
                        <button
                          key={p}
                          type="button"
                          onClick={() => setPriority(p)}
                          className={`px-4 py-2 rounded-lg text-sm font-medium capitalize ${priority === p ? 'ring-2 ring-offset-2' : 'bg-gray-100 text-gray-600'}`}
                          style={priority === p ? { backgroundColor: p === 'critical' ? '#fee2e2' : p === 'high' ? '#fef3c7' : p === 'medium' ? '#dbeafe' : '#d1fae5' } : {}}
                        >
                          {p}
                        </button>
                      ))}
                    </div>
                  </Card>

                  <Card className="p-4">
                    <h3 className="mb-3 text-sm font-semibold text-navy-700 dark:text-white">Investigation Status</h3>
                    <select
                      value={investigationStatus}
                      onChange={(e) => setInvestigationStatus(e.target.value as 'active' | 'pending' | 'closed')}
                      className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
                    >
                      <option value="active">Active</option>
                      <option value="pending">Pending</option>
                      <option value="closed">Closed</option>
                    </select>
                  </Card>

                  <Card className="p-4">
                    <h3 className="mb-3 text-sm font-semibold text-navy-700 dark:text-white">Officer Notes</h3>
                    <div className="space-y-2">
                      {notes.map((n, i) => (
                        <div key={i} className="flex items-start gap-2 text-sm">
                          <FileText size={14} className="mt-0.5 text-viz-blue" />
                          <span className="text-gray-800">{n}</span>
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
              ),
            },
          ]}
        />
      </div>
    </Modal>
  );
};

export default OffenderIntelligenceWorkspace;
