import React, { useMemo, useState, useCallback } from 'react';
import { Card, DataTable, KpiCard, LoadingSkeleton, EmptyState, AlertBanner, Tabs, Badge, Button, AIPanel } from 'shared/components';
import { NetworkGraphView } from 'shared/components';
import {
  useAdvancedNetwork,
  useAdvancedNetworkSearch,
  useNetworkAnalytics,
  useNetworkTimeline,
} from 'features/network-analysis/hooks/useNetwork';
import { useAiExplain } from 'services/aiService';
import { Play, Pause, SkipBack, Filter, Shield } from 'lucide-react';
import type {
  NetworkNode,
} from 'shared/api';

const TYPE_COLORS: Record<string, string> = {
  Offender: '#dc2626',
  Crime: '#ea580c',
  FIR: '#ca8a04',
  District: '#2563eb',
  PoliceStation: '#059669',
  Officer: '#7c3aed',
  Vehicle: '#0891b2',
  Victim: '#db2777',
  Location: '#d97706',
};

const EDGE_COLORS: Record<string, string> = {
  co_offender: '#dc2626',
  family: '#7c3aed',
  phone: '#0891b2',
  vehicle: '#059669',
  financial: '#d97706',
  location: '#2563eb',
  suspect: '#ea580c',
  witness: '#059669',
  acquaintance: '#64748b',
  unknown: '#94a3b8',
  committed: '#dc2626',
  registered_in: '#ca8a04',
  investigated_by: '#7c3aed',
  occurred_at: '#2563eb',
  belongs_to: '#64748b',
  related_to: '#d97706',
  operates_in: '#0891b2',
  known_at: '#059669',
  uses: '#db2777',
};

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
};

const NetworkAnalysis: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchType, setSearchType] = useState<'offender' | 'fir' | 'vehicle' | 'phone' | 'address' | 'alias'>('offender');
  const [selectedNode, setSelectedNode] = useState<NetworkNode | null>(null);
  const [crimeCategory, setCrimeCategory] = useState('');
  const [districtId, setDistrictId] = useState('');
  const [stationId, setStationId] = useState('');
  const [relationshipType, setRelationshipType] = useState('');
  const [riskLevel, setRiskLevel] = useState('');
  const [activeInvestigations, setActiveInvestigations] = useState<boolean | undefined>(undefined);
  const [timePeriod, setTimePeriod] = useState('');
  const [showFilters, setShowFilters] = useState(true);
  const [expandedNodes, setExpandedNodes] = useState<Set<string>>(new Set());
  const [timelineDate, setTimelineDate] = useState<string | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [aiExplanation, setAiExplanation] = useState<any>(null);

  const { data: advancedGraph, isLoading: graphLoading, error: graphError } = useAdvancedNetwork({
    crime_category: crimeCategory || undefined,
    district_id: districtId || undefined,
    station_id: stationId || undefined,
    relationship_type: relationshipType || undefined,
    risk_level: riskLevel || undefined,
    active_investigations: activeInvestigations,
  });

  const { data: searchResults, isLoading: searchLoading } = useAdvancedNetworkSearch(searchQuery, 50);
  const { data: analytics, isLoading: analyticsLoading } = useNetworkAnalytics();
  const { data: timelineData } = useNetworkTimeline();
  const explainMutation = useAiExplain();

  const graph = advancedGraph || { nodes: [], edges: [], statistics: { total_nodes: 0, total_edges: 0, connected_offenders: 0, connected_stations: 0, connected_districts: 0, average_connections: 0 }, communities: [], centrality: {} };
  const nodes = graph.nodes;
  const edges = graph.edges;
  const stats = graph.statistics;

  const degreeMap = useMemo(() => {
    const map = new Map<string, number>();
    edges.forEach((e) => {
      const sid = String((e.source as any)?.id ?? e.source);
      const tid = String((e.target as any)?.id ?? e.target);
      map.set(sid, (map.get(sid) || 0) + 1);
      map.set(tid, (map.get(tid) || 0) + 1);
    });
    return map;
  }, [edges]);

  const crimeCategories = useMemo(() => {
    const cats = new Set<string>();
    nodes.forEach((n) => {
      if (n.type === 'Crime' && n.properties?.crime_type) cats.add(n.properties.crime_type as string);
    });
    return Array.from(cats).sort();
  }, [nodes]);

  const districts = useMemo(() => {
    const d = new Set<string>();
    nodes.forEach((n) => {
      if (n.type === 'District') d.add(n.id);
    });
    return Array.from(d);
  }, [nodes]);

  const stations = useMemo(() => {
    const s = new Set<string>();
    nodes.forEach((n) => {
      if (n.type === 'PoliceStation') s.add(n.id);
    });
    return Array.from(s);
  }, [nodes]);

  const highlightedIds = useMemo(() => {
    if (!searchResults) return new Set<string>();
    return new Set(searchResults.nodes.map((n) => n.id));
  }, [searchResults]);

  const handleNodeClick = useCallback((node: NetworkNode) => {
    const full = nodes.find((n) => n.id === node.id) || node;
    setSelectedNode(full);
  }, [nodes]);

  const handleToggleNeighborhood = useCallback((nodeId: string) => {
    setExpandedNodes((prev) => {
      const next = new Set(prev);
      if (next.has(nodeId)) {
        if (next.size > 1) {
          next.delete(nodeId);
        }
      } else {
        next.add(nodeId);
      }
      return next;
    });
  }, []);

  const handlePlayTimeline = useCallback(() => {
    if (!timelineData?.timeline?.length) return;
    setIsPlaying(true);
    let index = 0;
    const dates = timelineData.timeline.map((t) => t.date).filter(Boolean);
    if (!dates.length) return;
    setTimelineDate(dates[0]);
    const interval = setInterval(() => {
      index++;
      if (index >= dates.length) {
        clearInterval(interval);
        setIsPlaying(false);
        return;
      }
      setTimelineDate(dates[index]);
    }, 600);
    return () => clearInterval(interval);
  }, [timelineData]);

  const handleDateSliderChange = useCallback((value: number) => {
    if (!timelineData?.timeline?.length) return;
    const dates = timelineData.timeline.map((t) => t.date).filter(Boolean);
    if (dates[value]) setTimelineDate(dates[value]);
  }, [timelineData]);

  const handleAiExplain = useCallback(async () => {
    if (!selectedNode) return;
    try {
      const res = await explainMutation.mutateAsync({
        chart_type: 'network_node',
        data: { node: selectedNode, degree: degreeMap.get(selectedNode.id) || 0, connections: edges.filter((e) => String((e.source as any)?.id ?? e.source) === selectedNode.id || String((e.target as any)?.id ?? e.target) === selectedNode.id) },
        filters: { crime_category: crimeCategory, risk_level: riskLevel },
      });
      setAiExplanation(res);
    } catch {
      // handled by mutation error state
    }
  }, [selectedNode, explainMutation, degreeMap, edges, crimeCategory, riskLevel]);

  const handleClearFilters = useCallback(() => {
    setCrimeCategory('');
    setDistrictId('');
    setStationId('');
    setRelationshipType('');
    setRiskLevel('');
    setActiveInvestigations(undefined);
    setTimePeriod('');
    setSearchQuery('');
    setSelectedNode(null);
    setExpandedNodes(new Set());
    setTimelineDate(null);
    setIsPlaying(false);
    setAiExplanation(null);
  }, []);

  const connectedEdgeCount = useMemo(() => {
    if (!selectedNode) return 0;
    return edges.filter((e) => String((e.source as any)?.id ?? e.source) === selectedNode.id || String((e.target as any)?.id ?? e.target) === selectedNode.id).length;
  }, [edges, selectedNode]);

  const associatedFirs = useMemo(() => {
    if (!selectedNode) return [];
    return nodes.filter((n) => {
      if (n.type !== 'FIR') return false;
      const edge = edges.find((e) => {
        const sid = String((e.source as any)?.id ?? e.source);
        const tid = String((e.target as any)?.id ?? e.target);
        return (sid === selectedNode.id && tid === n.id) || (tid === selectedNode.id && sid === n.id);
      });
      return !!edge;
    });
  }, [nodes, edges, selectedNode]);

  const associatedOffenders = useMemo(() => {
    if (!selectedNode) return [];
    return nodes.filter((n) => {
      if (n.type !== 'Offender') return false;
      if (n.id === selectedNode.id) return false;
      const edge = edges.find((e) => {
        const sid = String((e.source as any)?.id ?? e.source);
        const tid = String((e.target as any)?.id ?? e.target);
        return (sid === selectedNode.id && tid === n.id) || (tid === selectedNode.id && sid === n.id);
      });
      return !!edge;
    });
  }, [nodes, edges, selectedNode]);

  const relationshipSummary = useMemo(() => {
    if (!selectedNode) return [];
    const rels: Record<string, number> = {};
    edges.forEach((e) => {
      const sid = String((e.source as any)?.id ?? e.source);
      const tid = String((e.target as any)?.id ?? e.target);
      if (sid === selectedNode.id || tid === selectedNode.id) {
        rels[e.type || 'unknown'] = (rels[e.type || 'unknown'] || 0) + 1;
      }
    });
    return Object.entries(rels).map(([type, count]) => ({ type, count }));
  }, [edges, selectedNode]);

  if (graphError) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-navy-700 dark:text-white">Network Analysis</h1>
          <p className="text-sm text-gov-slate">Advanced criminal intelligence network visualization</p>
        </div>
        <AlertBanner variant="error" title="Failed to load network" message="Unable to fetch advanced network data. Please try again later." />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-navy-700 dark:text-white">Network Intelligence</h1>
        <p className="text-sm text-gov-slate">Advanced criminal network analysis and intelligence</p>
      </div>

      {graphLoading && (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <Card key={i} className="p-5">
              <LoadingSkeleton variant="card" />
            </Card>
          ))}
        </div>
      )}

      {!graphLoading && stats && (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
          <KpiCard label="Total Nodes" value={stats.total_nodes} accent="navy" />
          <KpiCard label="Total Connections" value={stats.total_edges} accent="blue" />
          <KpiCard label="Connected Offenders" value={stats.connected_offenders} accent="red" />
          <KpiCard label="Avg Connections" value={stats.average_connections.toFixed(1)} accent="purple" />
        </div>
      )}

      {searchQuery.trim().length > 0 && (
        <Card className="p-6">
          <h2 className="mb-4 text-lg font-semibold text-navy-700 dark:text-white">Search Results</h2>
          {searchLoading ? (
            <LoadingSkeleton variant="table" rows={5} />
          ) : searchResults && searchResults.nodes.length > 0 ? (
            <DataTable
              columns={[
                { key: 'label', header: 'Label', render: (r: any) => r.label },
                { key: 'type', header: 'Type', render: (r: any) => <Badge variant="info">{r.type}</Badge> },
              ]}
              data={searchResults.nodes}
              rowKey={(r) => r.id}
              emptyTitle="No search results"
              emptyDescription="Try a different search term."
              virtualized={false}
            />
          ) : (
            <EmptyState title="No search results" description="Try a different search term." />
          )}
        </Card>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {showFilters && (
          <div className="lg:col-span-3 space-y-4">
            <Card className="p-5">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-sm font-semibold text-navy-700 dark:text-white">Intelligence Filters</h2>
                <Button variant="ghost" size="sm" onClick={handleClearFilters} className="text-xs">Clear All</Button>
              </div>
              <div className="space-y-4">
                <div>
                  <label className="mb-1 block text-xs font-medium text-gray-700">Search</label>
                  <div className="flex gap-2">
                    <select
                      value={searchType}
                      onChange={(e) => setSearchType(e.target.value as any)}
                      className="rounded-lg border border-gray-300 px-2 py-1.5 text-xs"
                    >
                      <option value="offender">Offender</option>
                      <option value="fir">FIR</option>
                      <option value="vehicle">Vehicle</option>
                      <option value="phone">Phone</option>
                      <option value="address">Address</option>
                      <option value="alias">Alias</option>
                    </select>
                    <input
                      type="text"
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      placeholder={`Search ${searchType}...`}
                      className="flex-1 rounded-lg border border-gray-300 px-3 py-1.5 text-xs"
                    />
                  </div>
                </div>

                <div>
                  <label className="mb-1 block text-xs font-medium text-gray-700">Crime Category</label>
                  <select
                    value={crimeCategory}
                    onChange={(e) => setCrimeCategory(e.target.value)}
                    className="w-full rounded-lg border border-gray-300 px-2 py-1.5 text-xs"
                  >
                    <option value="">All Categories</option>
                    {crimeCategories.map((c) => (
                      <option key={c} value={c}>{c}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="mb-1 block text-xs font-medium text-gray-700">District</label>
                  <select
                    value={districtId}
                    onChange={(e) => setDistrictId(e.target.value)}
                    className="w-full rounded-lg border border-gray-300 px-2 py-1.5 text-xs"
                  >
                    <option value="">All Districts</option>
                    {districts.map((d) => (
                      <option key={d} value={d}>{d}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="mb-1 block text-xs font-medium text-gray-700">Police Station</label>
                  <select
                    value={stationId}
                    onChange={(e) => setStationId(e.target.value)}
                    className="w-full rounded-lg border border-gray-300 px-2 py-1.5 text-xs"
                  >
                    <option value="">All Stations</option>
                    {stations.map((s) => (
                      <option key={s} value={s}>{s}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="mb-1 block text-xs font-medium text-gray-700">Relationship Type</label>
                  <select
                    value={relationshipType}
                    onChange={(e) => setRelationshipType(e.target.value)}
                    className="w-full rounded-lg border border-gray-300 px-2 py-1.5 text-xs"
                  >
                    <option value="">All Types</option>
                    <option value="co_offender">Co-offender</option>
                    <option value="committed">Committed</option>
                    <option value="related_to">Related Crime</option>
                    <option value="occurred_at">Occurred At</option>
                    <option value="investigated_by">Investigated By</option>
                    <option value="registered_in">Registered In</option>
                    <option value="belongs_to">Belongs To</option>
                    <option value="known_at">Known At</option>
                  </select>
                </div>

                <div>
                  <label className="mb-1 block text-xs font-medium text-gray-700">Risk Level</label>
                  <select
                    value={riskLevel}
                    onChange={(e) => setRiskLevel(e.target.value)}
                    className="w-full rounded-lg border border-gray-300 px-2 py-1.5 text-xs"
                  >
                    <option value="">All</option>
                    <option value="Critical">Critical</option>
                    <option value="High">High</option>
                    <option value="Medium">Medium</option>
                    <option value="Low">Low</option>
                  </select>
                </div>

                <div>
                  <label className="mb-1 block text-xs font-medium text-gray-700">Active Investigations</label>
                  <select
                    value={activeInvestigations === undefined ? '' : activeInvestigations ? 'true' : 'false'}
                    onChange={(e) => {
                      const val = e.target.value;
                      if (val === '') setActiveInvestigations(undefined);
                      else setActiveInvestigations(val === 'true');
                    }}
                    className="w-full rounded-lg border border-gray-300 px-2 py-1.5 text-xs"
                  >
                    <option value="">All</option>
                    <option value="true">Active Only</option>
                    <option value="false">Closed Only</option>
                  </select>
                </div>

                <div>
                  <label className="mb-1 block text-xs font-medium text-gray-700">Time Period</label>
                  <input
                    type="text"
                    value={timePeriod}
                    onChange={(e) => setTimePeriod(e.target.value)}
                    placeholder="e.g., 2023-01-01:2024-12-31"
                    className="w-full rounded-lg border border-gray-300 px-2 py-1.5 text-xs"
                  />
                </div>
              </div>
            </Card>

            <Card className="p-4">
              <h3 className="text-xs font-semibold text-gray-700 mb-2">Legend</h3>
              <div className="space-y-1.5">
                {Object.entries(TYPE_COLORS).map(([type, color]) => (
                  <div key={type} className="flex items-center gap-2 text-xs text-gray-700">
                    <span className="inline-block h-2.5 w-2.5 rounded-full" style={{ backgroundColor: color }} />
                    <span>{type}</span>
                  </div>
                ))}
              </div>
            </Card>
          </div>
        )}

        <div className={showFilters ? 'lg:col-span-6' : 'lg:col-span-9'}>
          <Card className="p-4">
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-lg font-semibold text-navy-700 dark:text-white">Network Graph</h2>
              <button
                type="button"
                onClick={() => setShowFilters((v) => !v)}
                className="rounded-lg border border-gray-300 px-3 py-1.5 text-xs font-medium hover:bg-gray-50"
              >
                {showFilters ? <><Filter size={14} className="inline mr-1" />Hide Filters</> : <><Filter size={14} className="inline mr-1" />Filters</>}
              </button>
            </div>

            {graphLoading ? (
              <LoadingSkeleton variant="card" />
            ) : nodes.length > 0 ? (
              <>
                <div className="h-[650px] w-full rounded-lg border border-gray-200">
                  <NetworkGraphView
                    nodes={nodes}
                    edges={edges}
                    onNodeClick={handleNodeClick}
                    highlightedIds={highlightedIds.size > 0 ? highlightedIds : undefined}
                    onToggleNeighborhood={handleToggleNeighborhood}
                    expandedNodes={expandedNodes}
                  />
                </div>

                <div className="mt-4">
                  <h3 className="text-sm font-semibold text-gray-700 mb-2">Timeline Replay</h3>
                  <div className="flex items-center gap-3">
                    <button
                      type="button"
                      onClick={() => setIsPlaying(false)}
                      className="rounded-lg bg-white border border-gray-300 px-3 py-1.5 text-xs font-medium hover:bg-gray-50"
                    >
                      <SkipBack size={14} className="inline mr-1" />Reset
                    </button>
                    <button
                      type="button"
                      onClick={handlePlayTimeline}
                      className="rounded-lg bg-indigo-600 px-4 py-1.5 text-xs font-medium text-white hover:bg-indigo-700"
                    >
                      {isPlaying ? <><Pause size={14} className="inline mr-1" />Pause</> : <><Play size={14} className="inline mr-1" />Play</>}
                    </button>
                    <div className="flex-1">
                      <input
                        type="range"
                        min="0"
                        max={Math.max(0, (timelineData?.timeline?.length || 1) - 1)}
                        defaultValue="0"
                        onChange={(e) => handleDateSliderChange(Number(e.target.value))}
                        className="w-full"
                      />
                    </div>
                    <span className="text-xs text-gray-500 font-mono min-w-[100px]">
                      {timelineDate || 'All dates'}
                    </span>
                  </div>
                </div>
              </>
            ) : (
              <div className="h-[650px]">
                <EmptyState title="No network data" description="Network graph will appear here when data is available. Try adjusting your filters." />
              </div>
            )}
          </Card>

          <Card className="p-6 mt-6">
            <h2 className="mb-4 text-lg font-semibold text-navy-700 dark:text-white">Intelligence Analytics</h2>
            {analyticsLoading ? (
              <LoadingSkeleton variant="table" rows={5} />
            ) : analytics ? (
              <Tabs
                items={[
                  {
                    id: 'community',
                    label: 'Community Stats',
                    content: (
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <KpiCard label="Communities" value={analytics.community_stats.count} accent="navy" />
                        <KpiCard label="Avg Size" value={analytics.community_stats.avg_size} accent="blue" />
                        <KpiCard label="Largest" value={analytics.community_stats.largest_size} accent="red" />
                        <KpiCard label="Density" value={analytics.community_stats.density} accent="purple" />
                      </div>
                    ),
                  },
                  {
                    id: 'central',
                    label: 'Central Actors',
                    content: (
                      <DataTable
                        columns={[
                          { key: 'label', header: 'Actor', render: (r: any) => r.label },
                          { key: 'type', header: 'Type', render: (r: any) => <Badge variant="info">{r.type}</Badge> },
                          { key: 'score', header: 'Score', render: (r: any) => r.score.toFixed(3) },
                        ]}
                        data={analytics.central_actors}
                        rowKey={(r) => r.id}
                        emptyTitle="No central actors"
                        virtualized={false}
                      />
                    ),
                  },
                  {
                    id: 'connected',
                    label: 'Most Connected',
                    content: (
                      <DataTable
                        columns={[
                          { key: 'label', header: 'Entity', render: (r: any) => r.label },
                          { key: 'type', header: 'Type', render: (r: any) => <Badge variant="info">{r.type}</Badge> },
                          { key: 'connections', header: 'Connections', render: (r: any) => r.connections },
                        ]}
                        data={analytics.most_connected}
                        rowKey={(r) => r.id}
                        emptyTitle="No data"
                        virtualized={false}
                      />
                    ),
                  },
                  {
                    id: 'risk',
                    label: 'Highest Risk',
                    content: (
                      <div className="space-y-3">
                        {analytics.highest_risk_cluster && (
                          <div className="rounded-lg border border-red-200 bg-red-50 p-4">
                            <div className="flex items-center justify-between">
                              <div>
                                <p className="text-sm font-semibold text-red-900">{analytics.highest_risk_cluster.label}</p>
                                <p className="text-xs text-red-700">Size: {analytics.highest_risk_cluster.size} nodes</p>
                              </div>
                              <Badge variant="danger">Risk: {analytics.highest_risk_cluster.avg_risk.toFixed(2)}</Badge>
                            </div>
                          </div>
                        )}
                        {analytics.cluster_summaries?.map((cluster) => (
                          <div key={cluster.id} className="rounded-lg border border-gray-200 p-3">
                            <div className="flex items-center justify-between">
                              <p className="text-sm font-medium text-gray-800">{cluster.label}</p>
                              <Badge variant={STATUS_VARIANT[cluster.risk_level] || 'secondary'}>{cluster.risk_level}</Badge>
                            </div>
                            <p className="text-xs text-gray-500 mt-1">Nodes: {cluster.node_count} | Edges: {cluster.edge_count}</p>
                          </div>
                        ))}
                      </div>
                    ),
                  },
                  {
                    id: 'bridge',
                    label: 'Bridge Nodes',
                    content: (
                      <DataTable
                        columns={[
                          { key: 'label', header: 'Node', render: (r: any) => r.label },
                          { key: 'type', header: 'Type', render: (r: any) => <Badge variant="info">{r.type}</Badge> },
                          { key: 'connections', header: 'Connections', render: (r: any) => r.connections },
                        ]}
                        data={analytics.bridge_nodes}
                        rowKey={(r) => r.id}
                        emptyTitle="No bridge nodes"
                        virtualized={false}
                      />
                    ),
                  },
                ]}
              />
            ) : (
              <EmptyState title="No analytics" description="Analytics will appear here when data is available." />
            )}
          </Card>

          <Card className="p-6 mt-6">
            <h2 className="mb-4 text-lg font-semibold text-navy-700 dark:text-white">AI Intelligence</h2>
            {selectedNode ? (
              <div className="space-y-4">
                <div className="flex items-center gap-3">
                  <Shield size={20} className="text-indigo-600" />
                  <div>
                    <p className="text-sm font-medium text-gray-900">Selected: {selectedNode.label}</p>
                    <p className="text-xs text-gray-500">Type: {selectedNode.type} | Degree: {degreeMap.get(selectedNode.id) || 0}</p>
                  </div>
                </div>
                <Button variant="primary" size="sm" onClick={handleAiExplain} disabled={explainMutation.isPending}>
                  {explainMutation.isPending ? 'Generating...' : 'Generate AI Explanation'}
                </Button>
                {aiExplanation && (
                  <AIPanel
                    title="Network AI Explanation"
                    isFallback={aiExplanation.isFallback}
                    confidence={aiExplanation.confidence}
                    analyticsUsed={aiExplanation.analyticsUsed}
                    model={aiExplanation.model}
                    generatedAt={aiExplanation.generatedAt}
                    onRetry={handleAiExplain}
                    isLoading={explainMutation.isPending}
                  >
                    <p className="text-sm text-gray-800 dark:text-gray-200">{aiExplanation.explanation}</p>
                  </AIPanel>
                )}
              </div>
            ) : (
              <p className="text-sm text-gov-slate">Select a node in the graph to generate AI intelligence about it.</p>
            )}
          </Card>
        </div>

        {selectedNode && (
          <div className="lg:col-span-3">
            <Card className="p-5">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-sm font-semibold text-navy-700 dark:text-white">Node Intelligence</h2>
                <button
                  type="button"
                  onClick={() => setSelectedNode(null)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  ✕
                </button>
              </div>

              <Tabs
                items={[
                  {
                    id: 'overview',
                    label: 'Overview',
                    content: (
                      <div className="space-y-4">
                        <div className="flex items-center gap-3">
                          <div
                            className="h-12 w-12 rounded-full flex items-center justify-center text-lg font-bold text-white"
                            style={{ backgroundColor: TYPE_COLORS[selectedNode.type] || '#64748b' }}
                          >
                            {selectedNode.label.substring(0, 2).toUpperCase()}
                          </div>
                          <div>
                            <h3 className="text-sm font-semibold text-gray-900">{selectedNode.label}</h3>
                            <Badge variant="info">{selectedNode.type}</Badge>
                          </div>
                        </div>

                        <div className="grid grid-cols-2 gap-3 text-xs">
                          <div>
                            <p className="text-gray-500">ID</p>
                            <p className="font-mono text-gray-900 truncate">{selectedNode.id}</p>
                          </div>
                          <div>
                            <p className="text-gray-500">Risk Level</p>
                            <Badge variant={RISK_VARIANT[selectedNode.properties?.risk_level as string] || 'secondary'}>
                              {selectedNode.properties?.risk_level || 'Unknown'}
                            </Badge>
                          </div>
                          <div>
                            <p className="text-gray-500">Connections</p>
                            <p className="font-medium">{connectedEdgeCount}</p>
                          </div>
                          <div>
                            <p className="text-gray-500">Status</p>
                            <Badge variant={STATUS_VARIANT[selectedNode.properties?.status as string] || 'secondary'}>
                              {selectedNode.properties?.status || 'Unknown'}
                            </Badge>
                          </div>
                        </div>

                        <div>
                          <h4 className="text-xs font-medium text-gray-700 mb-2">Relationship Summary</h4>
                          <div className="space-y-1.5">
                            {relationshipSummary.map((rel) => (
                              <div key={rel.type} className="flex items-center justify-between text-xs">
                                <span className="inline-block h-2 w-4 rounded" style={{ backgroundColor: EDGE_COLORS[rel.type] || '#94a3b8' }} />
                                <span className="text-gray-700 capitalize flex-1 ml-2">{rel.type.replace(/_/g, ' ')}</span>
                                <span className="text-gray-500 font-mono">{rel.count}</span>
                              </div>
                            ))}
                            {relationshipSummary.length === 0 && (
                              <p className="text-xs text-gray-500">No relationships</p>
                            )}
                          </div>
                        </div>
                      </div>
                    ),
                  },
                  {
                    id: 'history',
                    label: 'History',
                    content: (
                      <div className="space-y-3">
                        <div>
                          <h4 className="text-xs font-medium text-gray-700 mb-2">Associated FIRs</h4>
                          {associatedFirs.length > 0 ? (
                            <div className="space-y-1.5">
                              {associatedFirs.slice(0, 10).map((fir) => (
                                <div key={fir.id} className="rounded-lg border border-gray-200 p-2">
                                  <p className="text-xs font-medium text-gray-900">{fir.label}</p>
                                  <p className="text-xs text-gray-500">{fir.properties?.fir_number || ''}</p>
                                </div>
                              ))}
                            </div>
                          ) : (
                            <p className="text-xs text-gray-500">No associated FIRs</p>
                          )}
                        </div>
                      </div>
                    ),
                  },
                  {
                    id: 'associates',
                    label: 'Associates',
                    content: (
                      <div className="space-y-3">
                        <h4 className="text-xs font-medium text-gray-700">Connected Offenders</h4>
                        {associatedOffenders.length > 0 ? (
                          <div className="space-y-1.5">
                            {associatedOffenders.slice(0, 10).map((off) => (
                              <div key={off.id} className="rounded-lg border border-gray-200 p-2 cursor-pointer hover:bg-gray-50" onClick={() => handleNodeClick(off)}>
                                <p className="text-xs font-medium text-gray-900">{off.label}</p>
                                <p className="text-xs text-gray-500">{off.type}</p>
                              </div>
                            ))}
                          </div>
                        ) : (
                          <p className="text-xs text-gray-500">No associated offenders</p>
                        )}
                      </div>
                    ),
                  },
                  {
                    id: 'ai',
                    label: 'AI',
                    content: (
                      <div className="space-y-3">
                        <Button variant="primary" size="sm" onClick={handleAiExplain} disabled={explainMutation.isPending} className="w-full">
                          {explainMutation.isPending ? 'Generating...' : 'Explain Pattern'}
                        </Button>
                        {aiExplanation && (
                          <div className="rounded-lg border border-indigo-200 bg-indigo-50 p-3">
                            <p className="text-xs font-medium text-indigo-900 mb-1">AI Explanation</p>
                            <p className="text-xs text-indigo-800">{aiExplanation.explanation}</p>
                            <p className="text-xs text-indigo-600 mt-1">Confidence: {(aiExplanation.confidence * 100).toFixed(0)}%</p>
                          </div>
                        )}
                      </div>
                    ),
                  },
                ]}
              />
            </Card>
          </div>
        )}
      </div>
    </div>
  );
};

export default NetworkAnalysis;
