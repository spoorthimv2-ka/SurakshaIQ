import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { Card, KpiCard, ChartContainer } from 'shared/components';

const DISTRICT_METRICS = [
  { month: 'Jan', cases: 320 },
  { month: 'Feb', cases: 345 },
  { month: 'Mar', cases: 310 },
  { month: 'Apr', cases: 358 },
];

const DistrictDetail: React.FC = () => {
  const { districtId } = useParams<{ districtId: string }>();
  const displayName = districtId?.replace(/-/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase()) ?? 'District';

  return (
    <div className="space-y-6">
      <div>
        <Link to="/dashboard" className="text-sm text-viz-blue hover:underline">
          ← Back to Dashboard
        </Link>
        <h1 className="mt-2 text-2xl font-bold text-navy-700 dark:text-white">{displayName}</h1>
        <p className="text-sm text-gov-slate">District-level drilldown and comparative analytics</p>
      </div>
      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        <KpiCard label="Total Cases (YTD)" value="1,247" delta={3.2} accent="navy" />
        <KpiCard label="Resolution Rate" value="68%" delta={2.1} accent="green" />
        <KpiCard label="Risk Index" value="72.1" delta={-1.4} accent="amber" />
      </div>
      <ChartContainer
        title={`${displayName} — Monthly Case Volume`}
        type="bar"
        data={DISTRICT_METRICS}
        xKey="month"
        series={[{ key: 'cases', color: '#1a365d', label: 'Cases' }]}
      />
      <Card className="p-6">
        <h2 className="text-lg font-semibold text-navy-700 dark:text-white">Station Breakdown</h2>
        <p className="mt-2 text-sm text-gov-slate">
          Station-level metrics for {displayName} will load from the districts API when connected to the backend gateway.
        </p>
      </Card>
    </div>
  );
};

export default DistrictDetail;
