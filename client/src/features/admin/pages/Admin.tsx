import React, { useMemo, useState } from 'react';
import { Card, Tabs, DataTable, KpiCard, LoadingSkeleton, EmptyState, AlertBanner, Modal, Badge, Button, ConfirmDialog } from 'shared/components';
import type { DataTableColumn } from 'shared/components';
import { useUsers, useRoles, useAdminStatistics, useAuditLogs, useCreateUser, useUpdateUser, useDeleteUser, useActivateUser, useDeactivateUser } from 'features/admin/hooks/useAdmin';
import type { AdminUser, AuditLog } from 'features/admin/hooks/useAdmin';
import toast from 'react-hot-toast';

const ROLE_VARIANT: Record<string, 'primary' | 'secondary' | 'success' | 'warning' | 'danger' | 'info'> = {
  SYSTEM_ADMINISTRATOR: 'danger',
  STATE_COMMAND: 'primary',
  RANGE_IG: 'info',
  DISTRICT_SP: 'warning',
  STATION_HOUSE_OFFICER: 'success',
  INVESTIGATING_OFFICER: 'secondary',
  CID_ANALYST: 'info',
};

const STATUS_VARIANT: Record<string, 'success' | 'secondary' | 'danger'> = {
  ACTIVE: 'success',
  INACTIVE: 'secondary',
  ARCHIVED: 'danger',
};

const emptyUser = {
  name: '',
  email: '',
  role: '',
  district: '',
  station: '',
  status: 'ACTIVE',
};

const Admin: React.FC = () => {
  const [filters, setFilters] = useState({ role: '', status: '' });
  const [userForm, setUserForm] = useState({ ...emptyUser });
  const [editingUser, setEditingUser] = useState<AdminUser | null>(null);
  const [viewingUser, setViewingUser] = useState<AdminUser | null>(null);
  const [deletingUser, setDeletingUser] = useState<AdminUser | null>(null);
  const [isFormOpen, setIsFormOpen] = useState(false);

  const { data: users, isLoading: usersLoading, error: usersError } = useUsers({
    ...(filters.role ? { role: filters.role } : {}),
    ...(filters.status ? { status: filters.status } : {}),
    limit: 100,
    offset: 0,
  });
  const { data: statistics } = useAdminStatistics();
  const { data: roles } = useRoles();
  const { data: auditLogs } = useAuditLogs({ limit: 50 });
  const createMutation = useCreateUser();
  const updateMutation = useUpdateUser();
  const deleteMutation = useDeleteUser();
  const activateMutation = useActivateUser();
  const deactivateMutation = useDeactivateUser();

  const userList = useMemo(() => users ?? [], [users]);
  const logsList = useMemo(() => auditLogs ?? [], [auditLogs]);

  const userColumns: DataTableColumn<AdminUser>[] = [
    { key: 'name', header: 'Name', sortable: true, sortValue: (r) => r.name, render: (r) => r.name },
    { key: 'email', header: 'Email', render: (r) => r.email },
    {
      key: 'role',
      header: 'Role',
      render: (r) => <Badge variant={ROLE_VARIANT[r.role] ?? 'secondary'}>{r.role}</Badge>,
    },
    {
      key: 'district',
      header: 'District',
      render: (r) => r.district || '-',
    },
    {
      key: 'station',
      header: 'Station',
      render: (r) => r.station || '-',
    },
    {
      key: 'status',
      header: 'Status',
      render: (r) => <Badge variant={STATUS_VARIANT[r.status] ?? 'secondary'}>{r.status}</Badge>,
    },
    {
      key: 'actions',
      header: 'Actions',
      render: (r) => (
        <div className="flex gap-2">
          <Button variant="ghost" size="sm" onClick={() => setViewingUser(r)}>
            View
          </Button>
          <Button variant="ghost" size="sm" onClick={() => { setEditingUser(r); setUserForm({ name: r.name, email: r.email, role: r.role, district: r.district || '', station: r.station || '', status: r.status }); setIsFormOpen(true); }}>
            Edit
          </Button>
          {r.status === 'ACTIVE' ? (
            <Button variant="ghost" size="sm" onClick={() => deactivateMutation.mutate(r.user_id)}>
              Deactivate
            </Button>
          ) : (
            <Button variant="ghost" size="sm" onClick={() => activateMutation.mutate(r.user_id)}>
              Activate
            </Button>
          )}
          <Button variant="ghost" size="sm" onClick={() => setDeletingUser(r)}>
            Delete
          </Button>
        </div>
      ),
    },
  ];

  const auditColumns: DataTableColumn<AuditLog>[] = [
    { key: 'action', header: 'Action', render: (r) => r.action },
    { key: 'user', header: 'User', render: (r) => r.user },
    { key: 'target', header: 'Target', render: (r) => r.target },
    {
      key: 'timestamp',
      header: 'Timestamp',
      render: (r) => (r.timestamp ? new Date(r.timestamp).toLocaleString() : '-'),
    },
  ];

  const handleCreate = async () => {
    try {
      await createMutation.mutateAsync(userForm);
      toast.success('User created successfully');
      setIsFormOpen(false);
      setUserForm({ ...emptyUser });
    } catch {
      toast.error('Failed to create user');
    }
  };

  const handleUpdate = async () => {
    if (!editingUser) return;
    try {
      await updateMutation.mutateAsync({ id: editingUser.user_id, data: userForm });
      toast.success('User updated successfully');
      setIsFormOpen(false);
      setEditingUser(null);
      setUserForm({ ...emptyUser });
    } catch {
      toast.error('Failed to update user');
    }
  };

  const handleDelete = async () => {
    if (!deletingUser) return;
    try {
      await deleteMutation.mutateAsync(deletingUser.user_id);
      toast.success('User deleted successfully');
      setDeletingUser(null);
    } catch {
      toast.error('Failed to delete user');
    }
  };

  const openCreate = () => {
    setEditingUser(null);
    setUserForm({ ...emptyUser });
    setIsFormOpen(true);
  };

  if (usersError) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-navy-700 dark:text-white">Administration</h1>
          <p className="text-sm text-gov-slate">User management, role assignments, and alert rule configuration</p>
        </div>
        <AlertBanner variant="error" title="Failed to load users" message="Unable to fetch users. Please try again later." />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-navy-700 dark:text-white">Administration</h1>
        <p className="text-sm text-gov-slate">User management, role assignments, and alert rule configuration</p>
      </div>

      {statistics && (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
          <KpiCard label="Total Users" value={statistics.total_users} accent="navy" />
          <KpiCard label="Active Users" value={statistics.active_users} accent="green" />
          <KpiCard label="Inactive Users" value={statistics.inactive_users} accent="red" />
          <KpiCard label="Total Roles" value={roles?.length ?? 0} accent="blue" />
        </div>
      )}

      <Tabs
        items={[
          {
            id: 'users',
            label: 'Users & Roles',
            content: (
              <div className="space-y-6">
                <Card className="p-4">
                  <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
                    <div>
                      <label className="mb-1 block text-sm font-medium text-gray-700">Role</label>
                      <select
                        value={filters.role}
                        onChange={(e) => setFilters((f) => ({ ...f, role: e.target.value }))}
                        className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
                      >
                        <option value="">All Roles</option>
                        {roles?.map((r) => (
                          <option key={r.id} value={r.id}>
                            {r.label}
                          </option>
                        ))}
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
                        <option value="INACTIVE">Inactive</option>
                      </select>
                    </div>
                    <div className="flex items-end">
                      <Button variant="primary" onClick={openCreate} className="w-full">
                        Create User
                      </Button>
                    </div>
                  </div>
                </Card>

                <Card className="p-6">
                  <h2 className="mb-4 text-lg font-semibold text-navy-700 dark:text-white">Users</h2>
                  {usersLoading ? (
                    <LoadingSkeleton variant="table" rows={5} />
                  ) : userList.length > 0 ? (
                    <DataTable
                      columns={userColumns}
                      data={userList}
                      rowKey={(r) => r.user_id}
                      emptyTitle="No users found"
                      emptyDescription="Create a user to get started."
                      virtualized={false}
                    />
                  ) : (
                    <EmptyState title="No users found" description="Create a user to get started." />
                  )}
                </Card>
              </div>
            ),
          },
          {
            id: 'audit-logs',
            label: 'Audit Logs',
            content: (
              <Card className="p-6">
                <h2 className="mb-4 text-lg font-semibold text-navy-700 dark:text-white">Audit Logs</h2>
                {logsList.length > 0 ? (
                  <DataTable
                    columns={auditColumns}
                    data={logsList}
                    rowKey={(r) => r.log_id}
                    emptyTitle="No audit logs"
                    emptyDescription="Audit logs will appear here."
                    virtualized={false}
                  />
                ) : (
                  <EmptyState title="No audit logs" description="Audit logs will appear here." />
                )}
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

      {/* User Form Modal */}
      <Modal
        isOpen={isFormOpen}
        onClose={() => { setIsFormOpen(false); setEditingUser(null); setUserForm({ ...emptyUser }); }}
        title={editingUser ? 'Edit User' : 'Create User'}
        footer={
          <div className="flex justify-end gap-2">
            <Button variant="ghost" onClick={() => { setIsFormOpen(false); setEditingUser(null); setUserForm({ ...emptyUser }); }}>
              Cancel
            </Button>
            <Button
              variant="primary"
              onClick={editingUser ? handleUpdate : handleCreate}
              disabled={createMutation.isPending || updateMutation.isPending || !userForm.name || !userForm.email || !userForm.role}
            >
              {editingUser ? 'Update' : 'Create'}
            </Button>
          </div>
        }
      >
        <div className="space-y-4">
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">Name</label>
            <input
              type="text"
              value={userForm.name}
              onChange={(e) => setUserForm((f) => ({ ...f, name: e.target.value }))}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
            />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">Email</label>
            <input
              type="email"
              value={userForm.email}
              onChange={(e) => setUserForm((f) => ({ ...f, email: e.target.value }))}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
            />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">Role</label>
            <select
              value={userForm.role}
              onChange={(e) => setUserForm((f) => ({ ...f, role: e.target.value }))}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
            >
              <option value="">Select role</option>
              {roles?.map((r) => (
                <option key={r.id} value={r.id}>
                  {r.label}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">District</label>
            <input
              type="text"
              value={userForm.district}
              onChange={(e) => setUserForm((f) => ({ ...f, district: e.target.value }))}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
            />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">Station</label>
            <input
              type="text"
              value={userForm.station}
              onChange={(e) => setUserForm((f) => ({ ...f, station: e.target.value }))}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
            />
          </div>
        </div>
      </Modal>

      {/* User Details Modal */}
      <Modal
        isOpen={!!viewingUser}
        onClose={() => { setViewingUser(null); }}
        title={viewingUser ? `User Details — ${viewingUser.name}` : 'User Details'}
        footer={
          <div className="flex justify-end gap-2">
            <Button variant="ghost" onClick={() => { setViewingUser(null); }}>
              Close
            </Button>
            {viewingUser && (
              <Button variant="primary" onClick={() => { setEditingUser(viewingUser); setUserForm({ name: viewingUser.name, email: viewingUser.email, role: viewingUser.role, district: viewingUser.district || '', station: viewingUser.station || '', status: viewingUser.status }); setViewingUser(null); setIsFormOpen(true); }}>
                Edit
              </Button>
            )}
          </div>
        }
      >
        {viewingUser && (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <span className="text-sm font-medium text-gray-700">Name</span>
                <p className="text-sm text-gray-900">{viewingUser.name}</p>
              </div>
              <div>
                <span className="text-sm font-medium text-gray-700">Email</span>
                <p className="text-sm text-gray-900">{viewingUser.email}</p>
              </div>
              <div>
                <span className="text-sm font-medium text-gray-700">Role</span>
                <Badge variant={ROLE_VARIANT[viewingUser.role] ?? 'secondary'}>{viewingUser.role}</Badge>
              </div>
              <div>
                <span className="text-sm font-medium text-gray-700">Status</span>
                <Badge variant={STATUS_VARIANT[viewingUser.status] ?? 'secondary'}>{viewingUser.status}</Badge>
              </div>
              <div>
                <span className="text-sm font-medium text-gray-700">District</span>
                <p className="text-sm text-gray-900">{viewingUser.district || '-'}</p>
              </div>
              <div>
                <span className="text-sm font-medium text-gray-700">Station</span>
                <p className="text-sm text-gray-900">{viewingUser.station || '-'}</p>
              </div>
              <div>
                <span className="text-sm font-medium text-gray-700">User ID</span>
                <p className="text-sm text-gray-900">{viewingUser.user_id}</p>
              </div>
              <div>
                <span className="text-sm font-medium text-gray-700">Officer ID</span>
                <p className="text-sm text-gray-900">{viewingUser.officer_id || '-'}</p>
              </div>
              <div>
                <span className="text-sm font-medium text-gray-700">Created At</span>
                <p className="text-sm text-gray-900">{new Date(viewingUser.created_at).toLocaleString()}</p>
              </div>
              <div>
                <span className="text-sm font-medium text-gray-700">Updated At</span>
                <p className="text-sm text-gray-900">{new Date(viewingUser.updated_at).toLocaleString()}</p>
              </div>
            </div>
          </div>
        )}
      </Modal>

      {/* Delete Confirm Dialog */}
      <ConfirmDialog
        isOpen={!!deletingUser}
        onClose={() => setDeletingUser(null)}
        onConfirm={handleDelete}
        title="Delete User"
        message={`Are you sure you want to delete ${deletingUser?.name}? This action cannot be undone.`}
        confirmLabel="Delete"
        destructive
      />
    </div>
  );
};

export default Admin;
