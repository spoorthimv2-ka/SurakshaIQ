import React from 'react';
import { Card, DataTable } from 'shared/components';
import { RoleGate } from 'shared/auth';
import type { DataTableColumn } from 'shared/components';

interface OffenderRow {
  id: string;
  alias: string;
  caseCount: number;
  district: string;
  piiName: string;
}

const SAMPLE_OFFENDERS: OffenderRow[] = [
  { id: 'ro1', alias: 'Subject-A', caseCount: 7, district: 'Bangalore Urban', piiName: 'Ravi K.' },
  { id: 'ro2', alias: 'Subject-B', caseCount: 5, district: 'Mysuru', piiName: 'Suresh M.' },
  { id: 'ro3', alias: 'Subject-C', caseCount: 4, district: 'Belagavi', piiName: 'Anil P.' },
];

const columns: DataTableColumn<OffenderRow>[] = [
  { key: 'alias', header: 'Alias', sortable: true, sortValue: (r) => r.alias, render: (r) => r.alias },
  {
    key: 'name',
    header: 'Identity',
    render: (r) => (
      <RoleGate requirePii permissions={['view:pii']}>
        {r.piiName}
      </RoleGate>
    ),
  },
  { key: 'cases', header: 'Cases', sortable: true, sortValue: (r) => r.caseCount, render: (r) => r.caseCount },
  { key: 'district', header: 'District', render: (r) => r.district },
];

const RepeatOffenders: React.FC = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-navy-700 dark:text-white">Repeat Offenders</h1>
        <p className="text-sm text-gov-slate">Cross-case offender linkage and recidivism tracking</p>
      </div>
      <Card className="p-4">
        <DataTable columns={columns} data={SAMPLE_OFFENDERS} rowKey={(r) => r.id} virtualized={false} />
      </Card>
    </div>
  );
};

export default RepeatOffenders;
