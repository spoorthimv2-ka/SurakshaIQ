import React from 'react';
import { Card, NetworkGraphView } from 'shared/components';
import type { NetworkNode, NetworkEdge } from 'shared/api';

const SAMPLE_NODES: NetworkNode[] = [
  { id: 'n1', label: 'Case-A', type: 'case' },
  { id: 'n2', label: 'Suspect-1', type: 'person' },
  { id: 'n3', label: 'Suspect-2', type: 'person' },
  { id: 'n4', label: 'Location-X', type: 'location' },
  { id: 'n5', label: 'Case-B', type: 'case' },
];

const SAMPLE_EDGES: NetworkEdge[] = [
  { source: 'n1', target: 'n2', weight: 3 },
  { source: 'n1', target: 'n4', weight: 2 },
  { source: 'n2', target: 'n3', weight: 4 },
  { source: 'n3', target: 'n5', weight: 2 },
  { source: 'n4', target: 'n5', weight: 1 },
];

const NetworkAnalysis: React.FC = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-navy-700 dark:text-white">Network Analysis</h1>
        <p className="text-sm text-gov-slate">Link and graph analysis for criminal network mapping</p>
      </div>
      <Card className="p-4">
        <NetworkGraphView nodes={SAMPLE_NODES} edges={SAMPLE_EDGES} width={800} height={420} />
      </Card>
    </div>
  );
};

export default NetworkAnalysis;
