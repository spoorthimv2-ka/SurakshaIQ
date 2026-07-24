import React, { useMemo, useState, useCallback } from 'react';
import { Card, DataTable, KpiCard, LoadingSkeleton, EmptyState, AlertBanner, Modal } from 'shared/components';
import type { DataTableColumn } from 'shared/components';
import { NetworkGraphView } from 'shared/components';
import { useNetwork, useNetworkStatistics, useNetworkSearch } from 'features/network-analysis/hooks/useNetwork';
import type { NetworkNode, NetworkEdge } from 'shared/api';

const TYPE_COLORS: Record<string, string> = {
  Offender: '#ef4444',
  Crime: '#f97316',
  FIR: '#eab308',
  District: '#3b82f6',
  PoliceStation: '#10b981',
  Officer: '#8b5cf6',
  Vehicle: '#06b6d4',
  Victim: '#ec4899',
  Location: '#f59e0b',
};

const NetworkAnalysis: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedNode, setSelectedNode] = useState<NetworkNode | null>(null);
  const [selectedTypes, setSelectedTypes] = useState<string[]>([]);
  const [minConnections, setMinConnections] = useState(0);
  const [crimeCategory, setCrimeCategory] = useState('');
  const [useCluster, setUseCluster] = useState(false);

  const { data: graph, isLoading: graphLoading, error: graphError } = useNetwork(500);
  const { data: statistics, isLoading: statsLoading } = useNetworkStatistics();
  const { data: searchResults, isLoading: searchLoading } = useNetworkSearch(searchQuery, 50);

  const nodes = graph?.nodes ?? [];
  const edges = graph?.edges ?? [];
  const stats = graph?.statistics ?? statistics;

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

  const filteredNodeIds = useMemo(() => {
    const ids = new Set<string>();
    nodes.forEach((n) => {
      if (selectedTypes.length > 0 && !selectedTypes.includes(n.type)) return;
      if (minConnections > 0 && (degreeMap.get(n.id) || 0) < minConnections) return;
      if (crimeCategory && n.type === 'Crime' && n.properties?.crime_type !== crimeCategory) return;
      ids.add(n.id);
    });
    return ids;
  }, [nodes, selectedTypes, minConnections, crimeCategory, degreeMap]);

  const filteredEdges = useMemo(
    () => edges.filter((e) => {
      const sid = String((e.source as any)?.id ?? e.source);
      const tid = String((e.target as any)?.id ?? e.target);
      return filteredNodeIds.has(sid) && filteredNodeIds.has(tid);
    }),
    [edges, filteredNodeIds],
  );

  const filteredNodes = useMemo(() => nodes.filter((n) => filteredNodeIds.has(n.id)), [nodes, filteredNodeIds]);

  const displayNodes = useMemo(() => {
    if (!useCluster || filteredNodes.length <= 100) return filteredNodes;
    const groups = new Map<string, NetworkNode[]>();
    filteredNodes.forEach((n) => {
      const arr = groups.get(n.type) || [];
      arr.push(n);
      groups.set(n.type, arr);
    });
    return Array.from(groups.entries()).map(([type, members]) => ({
      id: `cluster-${type}`,
      label: `${type} (${members.length})`,
      type,
      properties: { isCluster: true, memberCount: members.length },
    }));
  }, [filteredNodes, useCluster]);

  const displayEdges = useMemo(() => {
    if (!useCluster || filteredNodes.length <= 100) return filteredEdges;
    const seen = new Set<string>();
    const clusterEdges: NetworkEdge[] = [];
    filteredEdges.forEach((e) => {
      const sid = String((e.source as any)?.id ?? e.source);
      const tid = String((e.target as any)?.id ?? e.target);
      const sNode = filteredNodes.find((n) => n.id === sid);
      const tNode = filteredNodes.find((n) => n.id === tid);
      if (!sNode || !tNode) return;
      if (sNode.type === tNode.type) return;
      const key = [sNode.type, tNode.type].sort().join('|');
      if (seen.has(key)) return;
      seen.add(key);
      clusterEdges.push({
        source: `cluster-${sNode.type}`,
        target: `cluster-${tNode.type}`,
        type: e.type,
      });
    });
    return clusterEdges;
  }, [filteredEdges, filteredNodes, useCluster]);

  const crimeCategories = useMemo(() => {
    const cats = new Set<string>();
    nodes.forEach((n) => {
      if (n.type === 'Crime' && n.properties?.crime_type) cats.add(n.properties.crime_type as string);
    });
    return Array.from(cats).sort();
  }, [nodes]);

  const highlightedIds = useMemo(() => {
    if (!searchResults) return new Set<string>();
    return new Set(searchResults.nodes.map((n) => n.id));
  }, [searchResults]);

  const handleNodeClick = useCallback((node: NetworkNode) => {
    const full = nodes.find((n) => n.id === node.id) || node;
    setSelectedNode(full);
  }, [nodes]);

  const columns: DataTableColumn<NetworkNode>[] = [
    { key: 'label', header: 'Label', render: (r) => r.label },
    { key: 'type', header: 'Type', render: (r) => r.type },
  ];

  const edgeColumns: DataTableColumn<NetworkEdge>[] = [
    { key: 'source', header: 'Source', render: (r) => String((r.source as any)?.id ?? r.source) },
    { key: 'target', header: 'Target', render: (r) => String((r.target as any)?.id ?? r.target) },
    { key: 'type', header: 'Type', render: (r) => r.type ?? '-' },
  ];

  if (graphError) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-navy-700 dark:text-white">Network Analysis</h1>
          <p className="text-sm text-gov-slate">Link and graph analysis for criminal network mapping</p>
        </div>
        <AlertBanner variant="error" title="Failed to load network" message="Unable to fetch network data. Please try again later." />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-navy-700 dark:text-white">Network Analysis</h1>
        <p className="text-sm text-gov-slate">Link and graph analysis for criminal network mapping</p>
      </div>

      {statsLoading ? (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <Card key={i} className="p-5">
              <LoadingSkeleton variant="card" />
            </Card>
          ))}
        </div>
      ) : stats ? (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
          <KpiCard label="Total Nodes" value={stats.total_nodes} accent="navy" />
          <KpiCard label="Total Connections" value={stats.total_edges} accent="blue" />
          <KpiCard label="Connected Offenders" value={stats.connected_offenders} accent="red" />
          <KpiCard label="Connected Stations" value={stats.connected_stations} accent="purple" />
        </div>
      ) : null}

      <Card className="p-4">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-end">
          <div className="flex-1">
            <label className="mb-1 block text-sm font-medium text-gray-700">Search Network</label>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search offenders, crimes, stations, districts..."
              className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
            />
          </div>
        </div>
      </Card>

      {searchQuery.trim().length > 0 && (
        <Card className="p-6">
          <h2 className="mb-4 text-lg font-semibold text-navy-700 dark:text-white">Search Results</h2>
          {searchLoading ? (
            <LoadingSkeleton variant="table" rows={5} />
          ) : searchResults && searchResults.nodes.length > 0 ? (
            <DataTable
              columns={columns}
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

      <Card className="p-4">
        <div className="flex flex-wrap items-center gap-4">
          <div className="flex items-center gap-2">
            <label className="text-sm font-medium text-gray-700">Entity Type</label>
            <select
              multiple
              value={selectedTypes}
              onChange={(e) => {
                const opts = Array.from(e.target.selectedOptions).map((o) => o.value);
                setSelectedTypes(opts);
              }}
              className="rounded-lg border border-gray-300 px-2 py-1.5 text-sm"
            >
              {Array.from(new Set(nodes.map((n) => n.type))).map((t) => (
                <option key={t} value={t}>
                  {t}
                </option>
              ))}
            </select>
          </div>
          <div className="flex items-center gap-2">
            <label className="text-sm font-medium text-gray-700">Min Connections</label>
            <input
              type="range"
              min="0"
              max="10"
              value={minConnections}
              onChange={(e) => setMinConnections(Number(e.target.value))}
              className="h-2"
            />
            <span className="text-sm text-gray-600">{minConnections}</span>
          </div>
          <div className="flex items-center gap-2">
            <label className="text-sm font-medium text-gray-700">Category</label>
            <select
              value={crimeCategory}
              onChange={(e) => setCrimeCategory(e.target.value)}
              className="rounded-lg border border-gray-300 px-2 py-1.5 text-sm"
            >
              <option value="">All</option>
              {crimeCategories.map((c) => (
                <option key={c} value={c}>
                  {c}
                </option>
              ))}
            </select>
          </div>
          {filteredNodes.length > 100 && (
            <button
              type="button"
              onClick={() => setUseCluster((v) => !v)}
              className="rounded-lg border border-gray-300 px-3 py-1.5 text-sm font-medium hover:bg-gray-50"
            >
              {useCluster ? 'Expand All' : 'Cluster View'}
            </button>
          )}
        </div>
        <div className="mt-3 flex flex-wrap gap-4">
          {Object.entries(TYPE_COLORS).map(([type, color]) => (
            <div key={type} className="flex items-center gap-2 text-sm text-gray-700">
              <span className="inline-block h-3 w-3 rounded-full" style={{ backgroundColor: color }} />
              <span>{type}</span>
            </div>
          ))}
        </div>
      </Card>

      <Card className="p-4">
        <h2 className="mb-4 text-lg font-semibold text-navy-700 dark:text-white">Network Graph</h2>
        {graphLoading ? (
          <LoadingSkeleton variant="card" />
        ) : displayNodes.length > 0 ? (
          <div className="h-[500px] w-full">
            <NetworkGraphView
              nodes={displayNodes}
              edges={displayEdges}
              width={800}
              height={500}
              onNodeClick={handleNodeClick}
              highlightedIds={highlightedIds.size > 0 ? highlightedIds : undefined}
            />
          </div>
        ) : (
          <EmptyState title="No network data" description="Network graph will appear here when data is available." />
        )}
      </Card>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <Card className="p-6">
          <h2 className="mb-4 text-lg font-semibold text-navy-700 dark:text-white">Nodes</h2>
          {graphLoading ? (
            <LoadingSkeleton variant="table" rows={5} />
          ) : nodes.length > 0 ? (
            <DataTable
              columns={columns}
              data={nodes}
              rowKey={(r) => r.id}
              emptyTitle="No nodes"
              emptyDescription="Nodes will appear here."
              virtualized={false}
            />
          ) : (
            <EmptyState title="No nodes" description="Nodes will appear here." />
          )}
        </Card>

        <Card className="p-6">
          <h2 className="mb-4 text-lg font-semibold text-navy-700 dark:text-white">Connections</h2>
          {graphLoading ? (
            <LoadingSkeleton variant="table" rows={5} />
          ) : edges.length > 0 ? (
            <DataTable
              columns={edgeColumns}
              data={edges}
              rowKey={(r) => `${String((r.source as any)?.id ?? r.source)}-${String((r.target as any)?.id ?? r.target)}`}
              emptyTitle="No connections"
              emptyDescription="Connections will appear here."
              virtualized={false}
            />
          ) : (
            <EmptyState title="No connections" description="Connections will appear here." />
          )}
        </Card>
      </div>

      <Modal
        isOpen={!!selectedNode}
        onClose={() => setSelectedNode(null)}
        title={selectedNode ? `Node Details — ${selectedNode.label}` : 'Node Details'}
        footer={
          <div className="flex justify-end">
            <button
              type="button"
              onClick={() => setSelectedNode(null)}
              className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
            >
              Close
            </button>
          </div>
        }
      >
        {selectedNode && (
          <div className="space-y-3 text-sm">
            <div>
              <span className="font-medium text-gray-700">ID:</span>
              <p className="text-gray-900">{selectedNode.id}</p>
            </div>
            <div>
              <span className="font-medium text-gray-700">Label:</span>
              <p className="text-gray-900">{selectedNode.label}</p>
            </div>
            <div>
              <span className="font-medium text-gray-700">Type:</span>
              <p className="text-gray-900">{selectedNode.type}</p>
            </div>
            <div>
              <span className="font-medium text-gray-700">Connections:</span>
              <p className="text-gray-900">{degreeMap.get(selectedNode.id) ?? 0}</p>
            </div>
            {selectedNode.properties?.isCluster && (
              <div>
                <span className="font-medium text-gray-700">Cluster Size:</span>
                <p className="text-gray-900">{selectedNode.properties.memberCount as number} items</p>
              </div>
            )}
            {selectedNode.properties && Object.keys(selectedNode.properties).length > 0 && (
              <div>
                <span className="font-medium text-gray-700">Properties:</span>
                <pre className="mt-1 overflow-auto rounded-lg bg-gray-50 p-3 text-xs text-gray-800 dark:bg-gray-800 dark:text-gray-200">
                  {JSON.stringify(selectedNode.properties, null, 2)}
                </pre>
              </div>
            )}
          </div>
        )}
      </Modal>
    </div>
  );
};

export default NetworkAnalysis;
