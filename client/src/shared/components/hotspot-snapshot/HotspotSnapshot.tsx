import React from 'react';
import { MapPin, Flame } from 'lucide-react';

interface HotspotSnapshotProps {
  title: string;
  heatmapPreview: string;
  topHotspots: {
    rank: number;
    location: string;
    riskLevel: 'low' | 'medium' | 'high' | 'critical';
    change: number;
  }[];
}

const riskColors: Record<'low' | 'medium' | 'high' | 'critical', string> = {
  low: 'data-green',
  medium: 'data-yellow',
  high: 'alert-orange',
  critical: 'alert-red',
};

const HotspotSnapshot: React.FC<HotspotSnapshotProps> = ({ title, heatmapPreview, topHotspots }) => {
  return (
    <div className="space-y-4">
      <div className="flex items-center gap-3">
        <MapPin size={20} className="text-viz-blue" />
        <h2 className="text-lg font-semibold text-navy-700 dark:text-white">{title}</h2>
      </div>
      <div className="grid gap-4">
        <div className="aspect-w-16 aspect-h-9 bg-gray-100 rounded-lg overflow-hidden dark:bg-gray-800">
          <img
            src={heatmapPreview}
            alt="Heatmap preview"
            className="w-full h-full object-cover"
          />
        </div>
        <div className="space-y-3">
          {topHotspots.map((hotspot) => (
            <div key={hotspot.rank} className="flex items-start gap-3">
              <div className="flex-shrink-0 flex h-3 w-3 items-center justify-center">
                <span className={`text-xs font-bold text-white rounded-full bg-${riskColors[hotspot.riskLevel]}`}>
                  #{hotspot.rank}
                </span>
              </div>
              <div className="flex-1 space-y-1">
                <div className="flex justify-between">
                  <p className="text-sm font-medium text-navy-700 dark:text-white">{hotspot.location}</p>
                  <span className={`text-xs font-medium ${riskColors[hotspot.riskLevel]}-600`}>
                    {hotspot.riskLevel}
                  </span>
                </div>
                <div className="flex items-center gap-2 text-xs text-gov-slate dark:text-gray-400">
                  <Flame size={12} className={`text-${hotspot.change >= 0 ? 'data-green' : 'alert-red'}-600`} />
                  <span>
                    {hotspot.change >= 0 ? '+' : ''}{hotspot.change}%
                  </span>
                  <span>from last period</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default HotspotSnapshot;