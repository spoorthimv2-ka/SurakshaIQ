import React, { useEffect, useMemo, useState } from 'react';
import { Card, Button, Modal, ConfirmDialog, Badge, DataTable, AlertBanner } from 'shared/components';
import type { DataTableColumn } from 'shared/components';
import { districtsApi } from 'shared/api';
import { useFirs, useCreateFir, useUpdateFir, useDeleteFir } from 'features/fir-management/hooks/useFirs';
import toast from 'react-hot-toast';

const STATUS_OPTIONS = [
  { value: '', label: 'All Statuses' },
  { value: 'ACTIVE', label: 'Active' },
  { value: 'INACTIVE', label: 'Inactive' },
  { value: 'ARCHIVED', label: 'Archived' },
] as const;

const STATUS_BADGE_VARIANT: Record<string, 'success' | 'secondary' | 'warning'> = {
  ACTIVE: 'success',
  INACTIVE: 'secondary',
  ARCHIVED: 'warning',
};

interface FirRow {
  ROWID: string;
  fir_number: string;
  crime_id: string;
  station_id: string;
  officer_id: string;
  description: string;
  status: 'ACTIVE' | 'INACTIVE' | 'ARCHIVED';
  CREATEDTIME: string;
}

interface FirFormData {
  fir_number: string;
  crime_id: string;
  station_id: string;
  officer_id: string;
  description: string;
  status: 'ACTIVE' | 'INACTIVE' | 'ARCHIVED';
}

const emptyForm: FirFormData = {
  fir_number: '',
  crime_id: '',
  station_id: '',
  officer_id: '',
  description: '',
  status: 'ACTIVE',
};

const FirManagement: React.FC = () => {
  const [filters, setFilters] = useState({
    keyword: '',
    fir_number: '',
    district_id: '',
    station_id: '',
    officer_id: '',
    status: '',
    date_from: '',
    date_to: '',
  });
  const [debouncedKeyword, setDebouncedKeyword] = useState('');
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingFir, setEditingFir] = useState<FirRow | null>(null);
  const [viewingFir, setViewingFir] = useState<FirRow | null>(null);
  const [deletingFir, setDeletingFir] = useState<FirRow | null>(null);
  const [formData, setFormData] = useState<FirFormData>(emptyForm);
  const [formError, setFormError] = useState<string | null>(null);
  const [districts, setDistricts] = useState<{ id: string; name: string }[]>([]);
  const [districtsLoading, setDistrictsLoading] = useState(true);

  const { data: firs, isLoading, error, refetch } = useFirs({
    ...(debouncedKeyword ? { keyword: debouncedKeyword } : {}),
    ...(filters.fir_number ? { fir_number: filters.fir_number } : {}),
    ...(filters.district_id ? { district_id: filters.district_id } : {}),
    ...(filters.station_id ? { station_id: filters.station_id } : {}),
    ...(filters.officer_id ? { officer_id: filters.officer_id } : {}),
    ...(filters.status ? { status: filters.status } : {}),
    ...(filters.date_from ? { date_from: filters.date_from } : {}),
    ...(filters.date_to ? { date_to: filters.date_to } : {}),
    limit: 100,
    offset: 0,
  });

  const createMutation = useCreateFir();
  const updateMutation = useUpdateFir();
  const deleteMutation = useDeleteFir();

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedKeyword(filters.keyword), 300);
    return () => clearTimeout(timer);
  }, [filters.keyword]);

  useEffect(() => {
    const fetchDistricts = async () => {
      try {
        const res = await districtsApi.list();
        setDistricts(res.data.map((d) => ({ id: d.id, name: d.name })));
      } catch {
        // silent
      } finally {
        setDistrictsLoading(false);
      }
    };
    fetchDistricts();
  }, []);

  const columns: DataTableColumn<FirRow>[] = [
    {
      key: 'fir_number',
      header: 'FIR Number',
      sortable: true,
      sortValue: (r) => r.fir_number,
      render: (r) => (
        <button
          type="button"
          onClick={() => setViewingFir(r)}
          className="text-left font-medium text-blue-600 hover:text-blue-800 dark:text-blue-400"
        >
          {r.fir_number}
        </button>
      ),
    },
    { key: 'crime_id', header: 'Crime ID', render: (r) => r.crime_id },
    { key: 'station_id', header: 'Station', render: (r) => r.station_id },
    { key: 'officer_id', header: 'Officer', render: (r) => r.officer_id },
    {
      key: 'status',
      header: 'Status',
      render: (r) => (
        <Badge variant={STATUS_BADGE_VARIANT[r.status] ?? 'secondary'}>{r.status}</Badge>
      ),
    },
    {
      key: 'CREATEDTIME',
      header: 'Created',
      sortable: true,
      sortValue: (r) => r.CREATEDTIME,
      render: (r) => new Date(r.CREATEDTIME).toLocaleDateString(),
    },
    {
      key: 'actions',
      header: 'Actions',
      render: (r) => (
        <div className="flex gap-2">
          <Button variant="ghost" size="sm" onClick={() => handleEdit(r)}>
            Edit
          </Button>
          <Button variant="ghost" size="sm" onClick={() => setDeletingFir(r)} className="text-alert-red">
            Delete
          </Button>
        </div>
      ),
    },
  ];

  const openCreate = () => {
    setEditingFir(null);
    setFormData(emptyForm);
    setFormError(null);
    setIsFormOpen(true);
  };

  const handleEdit = (fir: FirRow) => {
    setEditingFir(fir);
    setFormData({
      fir_number: fir.fir_number,
      crime_id: fir.crime_id,
      station_id: fir.station_id,
      officer_id: fir.officer_id,
      description: fir.description,
      status: fir.status,
    });
    setFormError(null);
    setIsFormOpen(true);
  };

  const handleCloseForm = () => {
    setIsFormOpen(false);
    setEditingFir(null);
    setFormData(emptyForm);
    setFormError(null);
  };

  const validateForm = (): boolean => {
    if (!formData.fir_number.trim()) {
      setFormError('FIR number is required');
      return false;
    }
    if (!formData.crime_id.trim()) {
      setFormError('Crime ID is required');
      return false;
    }
    if (!formData.station_id.trim()) {
      setFormError('Police station is required');
      return false;
    }
    if (!formData.officer_id.trim()) {
      setFormError('Investigating officer is required');
      return false;
    }
    if (!formData.description.trim()) {
      setFormError('Description is required');
      return false;
    }
    setFormError(null);
    return true;
  };

  const handleSubmit = async () => {
    if (!validateForm()) return;

    try {
      if (editingFir) {
        await updateMutation.mutateAsync({
          id: editingFir.ROWID,
          data: {
            fir_number: formData.fir_number,
            crime_id: formData.crime_id,
            station_id: formData.station_id,
            officer_id: formData.officer_id,
            description: formData.description,
            status: formData.status,
          },
        });
        toast.success('FIR updated successfully');
      } else {
        await createMutation.mutateAsync({
          fir_number: formData.fir_number,
          crime_id: formData.crime_id,
          station_id: formData.station_id,
          officer_id: formData.officer_id,
          description: formData.description,
          status: formData.status,
        });
        toast.success('FIR created successfully');
      }
      handleCloseForm();
      refetch();
    } catch (err: unknown) {
      const message =
        err && typeof err === 'object' && 'response' in err
          ? (err as { response?: { data?: { detail?: string } } }).response?.data?.detail
          : 'Operation failed';
      setFormError(message ?? 'Operation failed');
    }
  };

  const handleDelete = async () => {
    if (!deletingFir) return;
    try {
      await deleteMutation.mutateAsync(deletingFir.ROWID);
      toast.success('FIR deleted successfully');
      setDeletingFir(null);
      refetch();
    } catch {
      toast.error('Failed to delete FIR');
    }
  };

  const clearFilters = () => {
    setFilters({
      keyword: '',
      fir_number: '',
      district_id: '',
      station_id: '',
      officer_id: '',
      status: '',
      date_from: '',
      date_to: '',
    });
    setDebouncedKeyword('');
  };

  const listRows: FirRow[] = useMemo(
    () =>
      (firs ?? []).map((f) => ({
        ROWID: f.ROWID,
        fir_number: f.fir_number,
        crime_id: f.crime_id,
        station_id: f.station_id,
        officer_id: f.officer_id,
        description: f.description,
        status: f.status,
        CREATEDTIME: f.CREATEDTIME,
      })),
    [firs],
  );

  const isSubmitting = createMutation.isPending || updateMutation.isPending || deleteMutation.isPending;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-navy-700 dark:text-white">FIR Management</h1>
          <p className="text-sm text-gov-slate">Create, view, and manage FIR records</p>
        </div>
        <Button onClick={openCreate}>Create FIR</Button>
      </div>

      {error && (
        <AlertBanner variant="error" title="Failed to load FIRs" message={error instanceof Error ? error.message : 'Unknown error'} />
      )}

      <Card className="p-4">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">Keyword</label>
            <input
              type="text"
              value={filters.keyword}
              onChange={(e) => setFilters((f) => ({ ...f, keyword: e.target.value }))}
              placeholder="Search FIRs..."
              className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
            />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">FIR Number</label>
            <input
              type="text"
              value={filters.fir_number}
              onChange={(e) => setFilters((f) => ({ ...f, fir_number: e.target.value }))}
              placeholder="FIR number"
              className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
            />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">District</label>
            <select
              value={filters.district_id}
              onChange={(e) => setFilters((f) => ({ ...f, district_id: e.target.value }))}
              disabled={districtsLoading}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm disabled:opacity-50"
            >
              <option value="">All Districts</option>
              {districts.map((d) => (
                <option key={d.id} value={d.id}>{d.name}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">Police Station</label>
            <input
              type="text"
              value={filters.station_id}
              onChange={(e) => setFilters((f) => ({ ...f, station_id: e.target.value }))}
              placeholder="Station ID"
              className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
            />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">Investigating Officer</label>
            <input
              type="text"
              value={filters.officer_id}
              onChange={(e) => setFilters((f) => ({ ...f, officer_id: e.target.value }))}
              placeholder="Officer ID"
              className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
            />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">Status</label>
            <select
              value={filters.status}
              onChange={(e) => setFilters((f) => ({ ...f, status: e.target.value }))}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
            >
              {STATUS_OPTIONS.map((s) => (
                <option key={s.value} value={s.value}>{s.label}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">Date From</label>
            <input
              type="date"
              value={filters.date_from}
              onChange={(e) => setFilters((f) => ({ ...f, date_from: e.target.value }))}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
            />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">Date To</label>
            <input
              type="date"
              value={filters.date_to}
              onChange={(e) => setFilters((f) => ({ ...f, date_to: e.target.value }))}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
            />
          </div>
          <div className="flex items-end">
            <Button variant="secondary" onClick={clearFilters} className="w-full">
              Clear Filters
            </Button>
          </div>
        </div>
      </Card>

      <DataTable
        columns={columns}
        data={listRows}
        rowKey={(r) => r.ROWID}
        isLoading={isLoading}
        emptyTitle="No FIRs found"
        emptyDescription="Try adjusting your filters or create a new FIR record."
        virtualized={false}
      />

      {/* Create / Edit Modal */}
      <Modal
        isOpen={isFormOpen}
        onClose={handleCloseForm}
        title={editingFir ? 'Edit FIR' : 'Create FIR'}
        footer={
          <div className="flex justify-end gap-2">
            <Button variant="ghost" onClick={handleCloseForm} disabled={isSubmitting}>
              Cancel
            </Button>
            <Button onClick={handleSubmit} isLoading={isSubmitting} disabled={isSubmitting}>
              {editingFir ? 'Update' : 'Create'}
            </Button>
          </div>
        }
      >
        <div className="space-y-4">
          {formError && <AlertBanner variant="error" title="Validation Error" message={formError} />}
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">FIR Number</label>
            <input
              type="text"
              value={formData.fir_number}
              onChange={(e) => setFormData((f) => ({ ...f, fir_number: e.target.value }))}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
            />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">Crime ID</label>
            <input
              type="text"
              value={formData.crime_id}
              onChange={(e) => setFormData((f) => ({ ...f, crime_id: e.target.value }))}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
            />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">Police Station</label>
            <input
              type="text"
              value={formData.station_id}
              onChange={(e) => setFormData((f) => ({ ...f, station_id: e.target.value }))}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
            />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">Investigating Officer</label>
            <input
              type="text"
              value={formData.officer_id}
              onChange={(e) => setFormData((f) => ({ ...f, officer_id: e.target.value }))}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
            />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">Description</label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData((f) => ({ ...f, description: e.target.value }))}
              rows={3}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
            />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">Status</label>
            <select
              value={formData.status}
              onChange={(e) => setFormData((f) => ({ ...f, status: e.target.value as FirFormData['status'] }))}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
            >
              {STATUS_OPTIONS.filter((s) => s.value !== '').map((s) => (
                <option key={s.value} value={s.value}>{s.label}</option>
              ))}
            </select>
          </div>
        </div>
      </Modal>

      {/* Detail Modal */}
      <Modal
        isOpen={!!viewingFir}
        onClose={() => setViewingFir(null)}
        title="FIR Details"
        footer={
          <div className="flex justify-end">
            <Button variant="ghost" onClick={() => setViewingFir(null)}>Close</Button>
          </div>
        }
      >
        {viewingFir && (
          <div className="space-y-3 text-sm">
            <div>
              <span className="font-medium text-gray-700">FIR Number:</span>
              <p className="text-gray-900">{viewingFir.fir_number}</p>
            </div>
            <div>
              <span className="font-medium text-gray-700">Crime ID:</span>
              <p className="text-gray-900">{viewingFir.crime_id}</p>
            </div>
            <div>
              <span className="font-medium text-gray-700">Police Station:</span>
              <p className="text-gray-900">{viewingFir.station_id}</p>
            </div>
            <div>
              <span className="font-medium text-gray-700">Investigating Officer:</span>
              <p className="text-gray-900">{viewingFir.officer_id}</p>
            </div>
            <div>
              <span className="font-medium text-gray-700">Description:</span>
              <p className="text-gray-900">{viewingFir.description}</p>
            </div>
            <div>
              <span className="font-medium text-gray-700">Status:</span>
              <Badge variant={STATUS_BADGE_VARIANT[viewingFir.status] ?? 'secondary'}>{viewingFir.status}</Badge>
            </div>
            <div>
              <span className="font-medium text-gray-700">Created:</span>
              <p className="text-gray-900">{new Date(viewingFir.CREATEDTIME).toLocaleString()}</p>
            </div>
          </div>
        )}
      </Modal>

      {/* Delete Confirmation */}
      <ConfirmDialog
        isOpen={!!deletingFir}
        onClose={() => setDeletingFir(null)}
        onConfirm={handleDelete}
        title="Delete FIR"
        message={`Are you sure you want to delete FIR "${deletingFir?.fir_number}"? This action cannot be undone.`}
        confirmLabel="Delete"
        destructive
      />
    </div>
  );
};

export default FirManagement;
