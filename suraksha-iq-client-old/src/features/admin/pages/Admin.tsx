import React from 'react';
import { Card, Tabs, DataTable } from 'shared/components';
import type { DataTableColumn } from 'shared/components';

interface UserRow {
  id: string;
  name: string;
  email: string;
  role: string;
  active: boolean;
}

const SAMPLE_USERS: UserRow[] = [
  { id: 'u1', name: 'Dr. Rajesh Kumar', email: 'dgp@karnataka.gov.in', role: 'STATE_COMMAND', active: true },
  { id: 'u2', name: 'Priya Sharma', email: 'admin@karnataka.gov.in', role: 'ADMIN', active: true },
  { id: 'u3', name: 'Inspector Rao', email: 'rao@karnataka.gov.in', role: 'STATION_OFFICER', active: true },
];

const userColumns: DataTableColumn<UserRow>[] = [
  { key: 'name', header: 'Name', sortable: true, sortValue: (r) => r.name, render: (r) => r.name },
  { key: 'email', header: 'Email', render: (r) => r.email },
  { key: 'role', header: 'Role', render: (r) => r.role },
  { key: 'active', header: 'Status', render: (r) => (r.active ? 'Active' : 'Inactive') },
];

const Admin: React.FC = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-navy-700 dark:text-white">Administration</h1>
        <p className="text-sm text-gov-slate">User management, role assignments, and alert rule configuration</p>
      </div>
      <Tabs
        items={[
          {
            id: 'users',
            label: 'Users & Roles',
            content: (
              <Card className="p-4">
                <DataTable columns={userColumns} data={SAMPLE_USERS} rowKey={(r) => r.id} virtualized={false} />
              </Card>
            ),
          },
          {
            id: 'alert-rules',
            label: 'Alert Rules',
            content: (
              <Card className="p-6">
                <h2 className="text-lg font-semibold text-navy-700 dark:text-white">Alert Rule Engine</h2>
                <p className="mt-2 text-sm text-gov-slate">
                  Configure threshold-based alert rules for hotspot intensity, anomaly detection, and risk score changes.
                </p>
              </Card>
            ),
          },
        ]}
      />
    </div>
  );
};

export default Admin;
