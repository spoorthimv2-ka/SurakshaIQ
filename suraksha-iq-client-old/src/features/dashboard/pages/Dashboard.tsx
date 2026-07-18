import React from 'react';
import { Activity, AlertTriangle, FileText, MapPin, Shield } from 'lucide-react';
import { KpiCard, Card, AlertBanner } from 'shared/components';
import { useAuth } from 'shared/auth';
import { useFilterStore } from 'shared/state';

const Dashboard: React.FC = () => {
  const { officer } = useAuth();
  const { jurisdiction, dateRange } = useFilterStore();

  const filterSummary = [
    jurisdiction ? `Jurisdiction: ${jurisdiction}` : null,
    dateRange ? `${dateRange.start} – ${dateRange.end}` : null,
  ]
    .filter(Boolean)
    .join(' · ');

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-navy-700 dark:text-white">Command Overview</h1>
        <p className="text-sm text-gov-slate">
          Welcome, {officer?.name ?? 'Officer'}
          {filterSummary ? ` · ${filterSummary}` : ''}
        </p>
      </div>

      <AlertBanner
        variant="info"
        title="Live intelligence feed active"
        message="Dashboard metrics reflect aggregated crime data scoped to your jurisdiction."
      />

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
        <KpiCard label="Total Cases (30d)" value="12,847" delta={4.2} icon={<FileText size={24} />} accent="navy" />
        <KpiCard label="Active Hotspots" value="156" delta={-2.1} icon={<MapPin size={24} />} accent="purple" />
        <KpiCard label="Open Alerts" value="23" delta={8.5} icon={<AlertTriangle size={24} />} accent="red" />
        <KpiCard label="Risk Index" value="67.4" delta={1.3} icon={<Shield size={24} />} accent="amber" />
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <Card className="p-6">
          <div className="mb-4 flex items-center gap-2">
            <Activity size={20} className="text-viz-blue" />
            <h2 className="text-lg font-semibold text-navy-700 dark:text-white">Operational Status</h2>
          </div>
          <ul className="space-y-3 text-sm text-gov-slate">
            <li className="flex justify-between border-b border-gray-100 pb-2 dark:border-gray-800">
              <span>Anomaly detections (24h)</span>
              <span className="font-semibold text-navy-700 dark:text-white">14</span>
            </li>
            <li className="flex justify-between border-b border-gray-100 pb-2 dark:border-gray-800">
              <span>Repeat offender matches</span>
              <span className="font-semibold text-navy-700 dark:text-white">8</span>
            </li>
            <li className="flex justify-between">
              <span>Pending report exports</span>
              <span className="font-semibold text-navy-700 dark:text-white">3</span>
            </li>
          </ul>
        </Card>

        <Card className="p-6">
          <h2 className="mb-4 text-lg font-semibold text-navy-700 dark:text-white">Jurisdiction Scope</h2>
          <p className="text-sm text-gov-slate">
            Data visibility is restricted to your assigned{' '}
            <strong>{officer?.jurisdiction.type ?? 'STATE'}</strong> scope. Use the filter bar to
            drill down within authorized boundaries.
          </p>
        </Card>
      </div>
    </div>
  );
};

export default Dashboard;
