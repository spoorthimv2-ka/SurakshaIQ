import React, { useMemo, useState } from 'react';
import { Card, DataTable, KpiCard, LoadingSkeleton, EmptyState, AlertBanner, Modal } from 'shared/components';
import type { DataTableColumn } from 'shared/components';
import { NetworkGraphView } from 'shared/components';
import { useNetwork, useNetworkStatistics, useNetworkSearch } from 'features/network-analysis/hooks/useNetwork';
import type { NetworkNode, NetworkEdge } from 'shared/api';

const NetworkAnalysis: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedNode, setSelectedNode] = useState<NetworkNode | null>(null);

  const { data: graph, isLoading: graphLoading, error: graphError } = useNetwork(500);
  const { data: statistics, isLoading: statsLoading } = useNetworkStatistics();
  const { data: searchResults, isLoading: searchLoading } = useNetworkSearch(searchQuery, 50);

  const nodes = graph?.nodes ?? [];
  const edges = graph?.edges ?? [];
  const stats = graph?.statistics ?? statistics;

  const graphEdges: NetworkEdge[] = useMemo(
    () =>
      edges.map((e) => ({
        ...e,
        weight: 1,
      })),
    [edges]
  );

  const columns: DataTableColumn<NetworkNode>[] = [
    { key: 'label', header: 'Label', render: (r) => r.label },
    { key: 'type', header: 'Type', render: (r) => r.type },
  ];

  const edgeColumns: DataTableColumn<NetworkEdge>[] = [
    { key: 'source', header: 'Source', render: (r) => r.source },
    { key: 'target', header: 'Target', render: (r) => r.target },
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
        <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
          <div className="flex flex-1 flex-col gap-4 sm:flex-row sm:items-end">
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
        </div>
      </Card>

      {searchQuery.trim().length > 0 && (
        <Card className="p-6">
          <h2 className="mb-4 text-lg font-semibold text-navy-700 dark:text-white">Search Results</h2>
          {searchLoading ? (
            <LoadingSkeleton variant="table" rows={5} />
          ) : searchResults && searchResults.nodes.length > 0 ? (
            <div className="space-y-4">
              <DataTable
                columns={columns}
                data={searchResults.nodes}
                rowKey={(r) => r.id}
                emptyTitle="No search results"
                emptyDescription="Try a different search term."
                virtualized={false}
              />
            </div>
          ) : (
            <EmptyState title="No search results" description="Try a different search term." />
          )}
        </Card>
      )}

      <Card className="p-4">
        <h2 className="mb-4 text-lg font-semibold text-navy-700 dark:text-white">Network Graph</h2>
        {graphLoading ? (
          <LoadingSkeleton variant="card" />
        ) : nodes.length > 0 ? (
          <div className="overflow-x-auto">
            <NetworkGraphView nodes={nodes} edges={graphEdges} width={800} height={420} onNodeClick={setSelectedNode} />
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
              rowKey={(r) => `${r.source}-${r.target}`}
              emptyTitle="No connections"
              emptyDescription="Connections will appear here."
              virtualized={false}
            />
          ) : (
            <EmptyState title="No connections" description="Connections will appear here." />
          )}
        </Card>
      </div>

      {/* Details Modal */}
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
