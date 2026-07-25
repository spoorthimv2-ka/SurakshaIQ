import React from 'react';
import { MapPin, Flame, TrendingUp, Activity } from 'lucide-react';

interface HotspotSnapshotProps {
  title: string;
  topHotspots: {
    rank: number;
    location: string;
    station?: string;
    riskLevel: 'low' | 'medium' | 'high' | 'critical';
    crimeCount: number;
    hotspotScore: number;
    trend: string;
  }[];
}

const HotspotSnapshot: React.FC<HotspotSnapshotProps> = ({ title, topHotspots }) => {
  return (
    <div className="space-y-4">
      <div className="flex items-center gap-3">
        <MapPin size={20} className="text-viz-blue" />
        <h2 className="text-lg font-semibold text-navy-700 dark:text-white">{title}</h2>
      </div>
      {topHotspots.length === 0 ? (
        <div className="text-center py-6 text-gray-500 dark:text-gray-400">No hotspot data available</div>
      ) : (
        <div className="space-y-3">
          {topHotspots.map((hotspot) => (
            <div key={hotspot.rank} className="flex items-start gap-3 rounded-lg border border-gray-200 p-3 dark:border-gray-700">
              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-navy-100 text-sm font-bold text-navy-700 dark:bg-navy-800 dark:text-white">
                {hotspot.rank}
              </div>
              <div className="flex-1">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-navy-700 dark:text-white">{hotspot.location}</p>
                    {hotspot.station && (
                      <p className="text-xs text-gov-slate">{hotspot.station}</p>
                    )}
                  </div>
                  <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                    hotspot.riskLevel === 'critical' ? 'bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300' :
                    hotspot.riskLevel === 'high' ? 'bg-orange-100 text-orange-700 dark:bg-orange-900 dark:text-orange-300' :
                    hotspot.riskLevel === 'medium' ? 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300' :
                    'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300'
                  }`}>
                    {hotspot.riskLevel}
                  </span>
                </div>
                <div className="mt-2 flex items-center gap-4 text-xs text-gov-slate">
                  <span className="flex items-center gap-1">
                    <Activity size={12} />
                    Crimes: {hotspot.crimeCount}
                  </span>
                  <span className="flex items-center gap-1">
                    <TrendingUp size={12} />
                    Score: {hotspot.hotspotScore.toFixed(1)}
                  </span>
                  <span className="flex items-center gap-1">
                    <Flame size={12} />
                    Trend: {hotspot.trend}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default HotspotSnapshot;