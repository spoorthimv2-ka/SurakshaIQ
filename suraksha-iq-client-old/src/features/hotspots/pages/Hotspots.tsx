import React from 'react';
import { Card, MapCanvas, EmptyState } from 'shared/components';

const SAMPLE_MARKERS = [
  { id: 'h1', latitude: 12.9716, longitude: 77.5946, intensity: 85, label: 'Bangalore Central' },
  { id: 'h2', latitude: 12.2958, longitude: 76.6394, intensity: 62, label: 'Mysuru East' },
  { id: 'h3', latitude: 15.8497, longitude: 74.4977, intensity: 45, label: 'Belagavi North' },
];

const Hotspots: React.FC = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-navy-700 dark:text-white">Crime Hotspots</h1>
        <p className="text-sm text-gov-slate">Spatial and temporal hotspot analysis across Karnataka</p>
      </div>
      <Card className="overflow-hidden p-0">
        <MapCanvas markers={SAMPLE_MARKERS} zoom={7} />
      </Card>
      <Card className="p-6">
        <h2 className="mb-4 text-lg font-semibold text-navy-700 dark:text-white">Active Hotspot Zones</h2>
        <EmptyState
          title="Connect to analytics API"
          description="Hotspot clusters will populate from the hotspots API once the backend gateway is available."
        />
      </Card>
    </div>
  );
};

export default Hotspots;
