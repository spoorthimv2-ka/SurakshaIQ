import React, { useMemo, useState, useCallback } from 'react';
import { Card, DataTable, KpiCard, LoadingSkeleton, EmptyState, AlertBanner, Modal, Badge, Button } from 'shared/components';
import type { DataTableColumn } from 'shared/components';
import { useAlerts, useAlertSummary, useActiveAlerts, useAcknowledgeAlert, useResolveAlert } from 'features/alerts/hooks/useAlerts';
import type { AlertRecord } from 'features/alerts/hooks/useAlerts';
import toast from 'react-hot-toast';

const SEVERITY_VARIANT: Record<string, 'primary' | 'secondary' | 'success' | 'warning' | 'danger' | 'info'> = {
  INFO: 'info',
  LOW: 'secondary',
  MEDIUM: 'warning',
  HIGH: 'danger',
  CRITICAL: 'danger',
};

const STATUS_VARIANT: Record<string, 'primary' | 'secondary' | 'success' | 'warning' | 'danger' | 'info'> = {
  ACTIVE: 'danger',
  ACKNOWLEDGED: 'warning',
  RESOLVED: 'success',
};

const Alerts: React.FC = () => {
  const [filters, setFilters] = useState({
    severity: '',
    status: '',
    district_id: '',
    station_id: '',
  });
  const [selectedAlert, setSelectedAlert] = useState<AlertRecord | null>(null);
  const [acknowledgingId, setAcknowledgingId] = useState<string | null>(null);
  const [resolvingId, setResolvingId] = useState<string | null>(null);

  const { data: alerts, isLoading: alertsLoading, error: alertsError } = useAlerts({
    ...(filters.severity ? { severity: filters.severity } : {}),
    ...(filters.status ? { status: filters.status } : {}),
    limit: 100,
    offset: 0,
  });

  const { data: activeAlerts, isLoading: activeLoading } = useActiveAlerts(100, 0, {
    district_id: filters.district_id || undefined,
    station_id: filters.station_id || undefined,
    severity: filters.severity || undefined,
    status: filters.status || undefined,
  });
  const { data: summary, isLoading: summaryLoading } = useAlertSummary();
  const acknowledgeMutation = useAcknowledgeAlert();
  const resolveMutation = useResolveAlert();

  const activeAlertList = useMemo(() => activeAlerts ?? [], [activeAlerts]);
  const alertList = useMemo(() => alerts ?? [], [alerts]);

  const columns = useMemo<DataTableColumn<AlertRecord>[]>(() => [
    { key: 'title', header: 'Title', render: (r) => r.title },
    {
      key: 'severity',
      header: 'Severity',
      render: (r) => <Badge variant={SEVERITY_VARIANT[r.severity] ?? 'secondary'}>{r.severity}</Badge>,
    },
    {
      key: 'status',
      header: 'Status',
      render: (r) => <Badge variant={STATUS_VARIANT[r.status] ?? 'secondary'}>{r.status}</Badge>,
    },
    {
      key: 'source',
      header: 'Source',
      render: (r) => r.source,
    },
    {
      key: 'district_id',
      header: 'District',
      render: (r) => r.district_id || '-',
    },
    {
      key: 'station_id',
      header: 'Station',
      render: (r) => r.station_id || '-',
    },
    {
      key: 'CREATEDTIME',
      header: 'Created',
      render: (r) => (r.CREATEDTIME ? new Date(r.CREATEDTIME).toLocaleDateString() : '-'),
    },
    {
      key: 'actions',
      header: 'Actions',
      render: (r) => (
        <div className="flex gap-2">
          {r.status === 'ACTIVE' && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => handleAcknowledge(r)}
              disabled={acknowledgingId === r.ROWID || resolvingId === r.ROWID}
            >
              Acknowledge
            </Button>
          )}
          {r.status !== 'RESOLVED' && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => handleResolve(r)}
              disabled={acknowledgingId === r.ROWID || resolvingId === r.ROWID}
            >
              Resolve
            </Button>
          )}
        </div>
      ),
    },
  ], [acknowledgingId, resolvingId]);

  const handleAcknowledge = useCallback(async (alert: AlertRecord) => {
    setAcknowledgingId(alert.ROWID);
    try {
      await acknowledgeMutation.mutateAsync(alert.ROWID);
      toast.success('Alert acknowledged');
      setSelectedAlert(null);
    } catch {
      toast.error('Failed to acknowledge alert');
    } finally {
      setAcknowledgingId(null);
    }
  }, [acknowledgeMutation]);

  const handleResolve = useCallback(async (alert: AlertRecord) => {
    setResolvingId(alert.ROWID);
    try {
      await resolveMutation.mutateAsync(alert.ROWID);
      toast.success('Alert resolved');
      setSelectedAlert(null);
    } catch {
      toast.error('Failed to resolve alert');
    } finally {
      setResolvingId(null);
    }
  }, [resolveMutation]);

  const clearFilters = useCallback(() => {
    setFilters({ severity: '', status: '', district_id: '', station_id: '' });
  }, []);

  if (alertsError) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-navy-700 dark:text-white">Alerts</h1>
          <p className="text-sm text-gov-slate">Real-time operational alerts and threshold notifications</p>
        </div>
        <AlertBanner variant="error" title="Failed to load alerts" message="Unable to fetch alerts. Please try again later." />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-navy-700 dark:text-white">Alerts</h1>
        <p className="text-sm text-gov-slate">Real-time operational alerts and threshold notifications</p>
      </div>

      {summaryLoading ? (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <Card key={i} className="p-5">
              <LoadingSkeleton variant="card" />
            </Card>
          ))}
        </div>
      ) : summary ? (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
          <KpiCard label="Total Alerts" value={summary.total_alerts} accent="navy" />
          <KpiCard label="Active Alerts" value={summary.active_alerts} accent="red" />
          <KpiCard label="Critical Alerts" value={summary.critical_alerts} accent="red" />
          <KpiCard label="Resolved Alerts" value={summary.resolved_alerts} accent="green" />
        </div>
      ) : null}

      <Card className="p-4">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">Severity</label>
            <select
              value={filters.severity}
              onChange={(e) => setFilters((f) => ({ ...f, severity: e.target.value }))}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
            >
              <option value="">All Severities</option>
              <option value="INFO">Info</option>
              <option value="LOW">Low</option>
              <option value="MEDIUM">Medium</option>
              <option value="HIGH">High</option>
              <option value="CRITICAL">Critical</option>
            </select>
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">Status</label>
            <select
              value={filters.status}
              onChange={(e) => setFilters((f) => ({ ...f, status: e.target.value }))}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
            >
              <option value="">All Statuses</option>
              <option value="ACTIVE">Active</option>
              <option value="ACKNOWLEDGED">Acknowledged</option>
              <option value="RESOLVED">Resolved</option>
            </select>
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">District ID</label>
            <input
              type="text"
              value={filters.district_id}
              onChange={(e) => setFilters((f) => ({ ...f, district_id: e.target.value }))}
              placeholder="District ID"
              className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
            />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">Station ID</label>
            <input
              type="text"
              value={filters.station_id}
              onChange={(e) => setFilters((f) => ({ ...f, station_id: e.target.value }))}
              placeholder="Station ID"
              className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
            />
          </div>
          <div className="flex items-end">
            <button
              type="button"
              onClick={clearFilters}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
            >
              Clear Filters
            </button>
          </div>
        </div>
      </Card>

      <Card className="p-6">
        <h2 className="mb-4 text-lg font-semibold text-navy-700 dark:text-white">Active Alerts</h2>
        {activeLoading ? (
          <LoadingSkeleton variant="table" rows={5} />
        ) : activeAlertList.length > 0 ? (
          <DataTable
            columns={columns}
            data={activeAlertList}
            rowKey={(r) => r.ROWID}
            emptyTitle="No active alerts"
            emptyDescription="Active alerts will appear here."
            virtualized={false}
          />
        ) : (
          <EmptyState title="No active alerts" description="Active alerts will appear here." />
        )}
      </Card>

      <Card className="p-6">
        <h2 className="mb-4 text-lg font-semibold text-navy-700 dark:text-white">All Alerts</h2>
        {alertsLoading ? (
          <LoadingSkeleton variant="table" rows={5} />
        ) : alertList.length > 0 ? (
          <DataTable
            columns={columns}
            data={alertList}
            rowKey={(r) => r.ROWID}
            emptyTitle="No alerts found"
            emptyDescription="Alerts will appear here when generated."
            virtualized={false}
          />
        ) : (
          <EmptyState title="No alerts found" description="Alerts will appear here when generated." />
        )}
      </Card>

      {/* Details Modal */}
      <Modal
        isOpen={!!selectedAlert}
        onClose={() => setSelectedAlert(null)}
        title={selectedAlert ? `Alert Details — ${selectedAlert.title}` : 'Alert Details'}
        footer={
          <div className="flex justify-end gap-2">
            <button
              type="button"
              onClick={() => setSelectedAlert(null)}
              className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
            >
              Close
            </button>
            {selectedAlert?.status === 'ACTIVE' && selectedAlert && (
              <Button
                variant="primary"
                onClick={() => handleAcknowledge(selectedAlert)}
                disabled={acknowledgingId === selectedAlert.ROWID || resolvingId === selectedAlert.ROWID}
              >
                Acknowledge
              </Button>
            )}
            {selectedAlert?.status !== 'RESOLVED' && selectedAlert && (
              <Button
                variant="primary"
                onClick={() => handleResolve(selectedAlert)}
                disabled={acknowledgingId === selectedAlert.ROWID || resolvingId === selectedAlert.ROWID}
              >
                Resolve
              </Button>
            )}
          </div>
        }
      >
        {selectedAlert && (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <span className="text-sm font-medium text-gray-700">Title</span>
                <p className="text-sm text-gray-900">{selectedAlert.title}</p>
              </div>
              <div>
                <span className="text-sm font-medium text-gray-700">Severity</span>
                <Badge variant={SEVERITY_VARIANT[selectedAlert.severity] ?? 'secondary'}>{selectedAlert.severity}</Badge>
              </div>
              <div>
                <span className="text-sm font-medium text-gray-700">Status</span>
                <Badge variant={STATUS_VARIANT[selectedAlert.status] ?? 'secondary'}>{selectedAlert.status}</Badge>
              </div>
              <div>
                <span className="text-sm font-medium text-gray-700">Source</span>
                <p className="text-sm text-gray-900">{selectedAlert.source}</p>
              </div>
              <div>
                <span className="text-sm font-medium text-gray-700">District</span>
                <p className="text-sm text-gray-900">{selectedAlert.district_id || '-'}</p>
              </div>
              <div>
                <span className="text-sm font-medium text-gray-700">Station</span>
                <p className="text-sm text-gray-900">{selectedAlert.station_id || '-'}</p>
              </div>
              <div>
                <span className="text-sm font-medium text-gray-700">Entity Type</span>
                <p className="text-sm text-gray-900">{selectedAlert.entity_type || '-'}</p>
              </div>
              <div>
                <span className="text-sm font-medium text-gray-700">Entity ID</span>
                <p className="text-sm text-gray-900">{selectedAlert.entity_id || '-'}</p>
              </div>
              <div className="col-span-2">
                <span className="text-sm font-medium text-gray-700">Description</span>
                <p className="text-sm text-gray-900">{selectedAlert.description}</p>
              </div>
              {selectedAlert.recommended_action && (
                <div className="col-span-2">
                  <span className="text-sm font-medium text-gray-700">Recommended Action</span>
                  <p className="text-sm text-gray-900">{selectedAlert.recommended_action}</p>
                </div>
              )}
              <div>
                <span className="text-sm font-medium text-gray-700">Created</span>
                <p className="text-sm text-gray-900">{new Date(selectedAlert.CREATEDTIME).toLocaleString()}</p>
              </div>
              <div>
                <span className="text-sm font-medium text-gray-700">Modified</span>
                <p className="text-sm text-gray-900">{new Date(selectedAlert.MODIFIEDTIME).toLocaleString()}</p>
              </div>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default Alerts;
