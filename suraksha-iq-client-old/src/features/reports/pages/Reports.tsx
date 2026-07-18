import React from 'react';
import { Card, Tabs, MiniMap } from 'shared/components';

const Reports: React.FC = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-navy-700 dark:text-white">Reports</h1>
        <p className="text-sm text-gov-slate">Custom and scheduled report generation and export</p>
      </div>
      <Tabs
        items={[
          {
            id: 'custom',
            label: 'Custom Reports',
            content: (
              <Card className="p-6">
                <h2 className="text-lg font-semibold text-navy-700 dark:text-white">Generate Custom Report</h2>
                <p className="mt-2 text-sm text-gov-slate">
                  Configure jurisdiction, date range, and case categories to generate on-demand analytical reports.
                </p>
              </Card>
            ),
          },
          {
            id: 'scheduled',
            label: 'Scheduled Reports',
            content: (
              <Card className="p-6">
                <h2 className="text-lg font-semibold text-navy-700 dark:text-white">Scheduled Exports</h2>
                <p className="mt-2 text-sm text-gov-slate">
                  Manage recurring daily, weekly, and monthly report schedules for command review.
                </p>
              </Card>
            ),
          },
          {
            id: 'preview',
            label: 'Map Preview',
            content: (
              <Card className="p-4">
                <MiniMap
                  markers={[{ id: 'r1', latitude: 12.9716, longitude: 77.5946, label: 'Report Area' }]}
                  height={240}
                />
              </Card>
            ),
          },
        ]}
      />
    </div>
  );
};

export default Reports;
