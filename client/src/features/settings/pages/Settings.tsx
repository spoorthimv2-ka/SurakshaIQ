import React, { useState } from 'react';
import { Card, Tabs, DataTable, LoadingSkeleton, EmptyState, AlertBanner, Badge, Button } from 'shared/components';
import type { DataTableColumn } from 'shared/components';
import { useUserSettings, useUpdateUserSettings, useSystemSettings, useNotifications, useNotificationSummary, useMarkNotificationRead, useDismissNotification, useClearAllNotifications, useExportData, useGenerateAIReport } from 'features/settings/hooks/useSettings';
import type { UserSettings, Notification } from 'shared/api';
import toast from 'react-hot-toast';
import { Download, Brain, Trash2, Check, X } from 'lucide-react';

const severityVariant: Record<string, 'success' | 'warning' | 'danger' | 'info' | 'secondary'> = {
  low: 'success',
  medium: 'warning',
  high: 'danger',
  info: 'info',
  critical: 'danger',
};

const Settings: React.FC = () => {
  const { data: userSettings, isLoading: userLoading, error: userError } = useUserSettings();
  const { data: systemSettings, isLoading: systemLoading } = useSystemSettings();
  const { data: notifications, isLoading: notifLoading } = useNotifications();
  const { data: summary } = useNotificationSummary();
  const updateMutation = useUpdateUserSettings();
  const markReadMutation = useMarkNotificationRead();
  const dismissMutation = useDismissNotification();
  const clearAllMutation = useClearAllNotifications();
  const exportMutation = useExportData();
  const aiReportMutation = useGenerateAIReport();

  const [local, setLocal] = useState<Partial<UserSettings>>({});
  const [reportType, setReportType] = useState('executive');
  const [exportFormat, setExportFormat] = useState('csv');
  const [generatedContent, setGeneratedContent] = useState<string | null>(null);

  const notificationColumns: DataTableColumn<Notification>[] = [
    { key: 'type', header: 'Type', render: (n) => n.type.replace('_', ' ') },
    { key: 'title', header: 'Title', render: (n) => n.title },
    { key: 'message', header: 'Message', render: (n) => n.message },
    {
      key: 'severity',
      header: 'Severity',
      render: (n) => <Badge variant={severityVariant[n.severity] ?? 'secondary'}>{n.severity}</Badge>,
    },
    {
      key: 'read',
      header: 'Status',
      render: (n) => <Badge variant={n.read ? 'secondary' : 'info'}>{n.read ? 'Read' : 'Unread'}</Badge>,
    },
    {
      key: 'created_at',
      header: 'Received',
      render: (n) => (n.created_at ? new Date(n.created_at).toLocaleString() : '-'),
    },
    {
      key: 'actions',
      header: 'Actions',
      render: (n) => (
        <div className="flex gap-2">
          {!n.read && (
            <Button variant="ghost" size="sm" onClick={() => markReadMutation.mutate(n.notification_id)}>
              <Check size={14} />
            </Button>
          )}
          <Button variant="ghost" size="sm" onClick={() => dismissMutation.mutate(n.notification_id)}>
            <X size={14} />
          </Button>
        </div>
      ),
    },
  ];

  const handleSaveSettings = async () => {
    try {
      await updateMutation.mutateAsync(local);
      toast.success('Settings saved');
    } catch {
      toast.error('Failed to save settings');
    }
  };

  const handleExport = async () => {
    try {
      const result = await exportMutation.mutateAsync({
        report_type: 'dashboard',
        format: exportFormat,
        data: { headers: ['id', 'name', 'status'], rows: [{ id: '1', name: 'Sample', status: 'active' }] },
      });
      if (result.content) {
        const blob = new Blob([result.content], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = result.filename;
        a.click();
        URL.revokeObjectURL(url);
      }
      toast.success('Export completed');
    } catch {
      toast.error('Export failed');
    }
  };

  const handleAIReport = async () => {
    try {
      const result = await aiReportMutation.mutateAsync({
        report_type: reportType,
        scope: {},
        analytics: {},
        format: 'text',
      });
      setGeneratedContent(result.content);
      toast.success('AI report generated');
    } catch {
      toast.error('AI report generation failed');
    }
  };

  if (userError) {
    return (
      <div className="space-y-6">
        <h1 className="text-2xl font-bold text-navy-700 dark:text-white">Settings</h1>
        <AlertBanner variant="error" title="Failed to load settings" message="Unable to fetch settings. Please try again later." />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-navy-700 dark:text-white">Settings</h1>
        <p className="text-sm text-gov-slate">Manage your preferences, notifications, exports, and AI reports</p>
      </div>

      <Tabs
        items={[
          {
            id: 'profile',
            label: 'Profile & Preferences',
            content: (
              <Card className="p-6">
                <h2 className="mb-4 text-lg font-semibold text-navy-700 dark:text-white">User Settings</h2>
                {userLoading ? (
                  <LoadingSkeleton variant="card" />
                ) : userSettings ? (
                  <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                    <div>
                      <label className="mb-1 block text-sm font-medium text-gray-700">Theme</label>
                      <select
                        value={(local.theme ?? userSettings.theme)}
                        onChange={(e) => setLocal((s) => ({ ...s, theme: e.target.value }))}
                        className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
                      >
                        <option value="light">Light</option>
                        <option value="dark">Dark</option>
                      </select>
                    </div>
                    <div>
                      <label className="mb-1 block text-sm font-medium text-gray-700">Language</label>
                      <select
                        value={(local.language ?? userSettings.language)}
                        onChange={(e) => setLocal((s) => ({ ...s, language: e.target.value }))}
                        className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
                      >
                        <option value="en">English</option>
                        <option value="hi">Hindi</option>
                        <option value="kn">Kannada</option>
                      </select>
                    </div>
                    <div>
                      <label className="mb-1 block text-sm font-medium text-gray-700">Timezone</label>
                      <select
                        value={(local.timezone ?? userSettings.timezone)}
                        onChange={(e) => setLocal((s) => ({ ...s, timezone: e.target.value }))}
                        className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
                      >
                        <option value="Asia/Kolkata">India (IST)</option>
                        <option value="Asia/Dubai">Dubai (GST)</option>
                        <option value="UTC">UTC</option>
                      </select>
                    </div>
                    <div className="flex items-center gap-2">
                      <input
                        id="notifications"
                        type="checkbox"
                        checked={(local.notifications_enabled ?? userSettings.notifications_enabled)}
                        onChange={(e) => setLocal((s) => ({ ...s, notifications_enabled: e.target.checked }))}
                        className="h-4 w-4 rounded border-gray-300"
                      />
                      <label htmlFor="notifications" className="text-sm text-gray-700">Enable notifications</label>
                    </div>
                    <div className="flex items-center gap-2">
                      <input
                        id="email_alerts"
                        type="checkbox"
                        checked={(local.email_alerts ?? userSettings.email_alerts)}
                        onChange={(e) => setLocal((s) => ({ ...s, email_alerts: e.target.checked }))}
                        className="h-4 w-4 rounded border-gray-300"
                      />
                      <label htmlFor="email_alerts" className="text-sm text-gray-700">Email alerts</label>
                    </div>
                    <div className="flex items-center gap-2">
                      <input
                        id="push"
                        type="checkbox"
                        checked={(local.push_notifications ?? userSettings.push_notifications)}
                        onChange={(e) => setLocal((s) => ({ ...s, push_notifications: e.target.checked }))}
                        className="h-4 w-4 rounded border-gray-300"
                      />
                      <label htmlFor="push" className="text-sm text-gray-700">Push notifications</label>
                    </div>
                    <div className="flex items-center gap-2">
                      <input
                        id="ai_suggestions"
                        type="checkbox"
                        checked={(local.ai_suggestions ?? userSettings.ai_suggestions)}
                        onChange={(e) => setLocal((s) => ({ ...s, ai_suggestions: e.target.checked }))}
                        className="h-4 w-4 rounded border-gray-300"
                      />
                      <label htmlFor="ai_suggestions" className="text-sm text-gray-700">AI suggestions</label>
                    </div>
                  </div>
                ) : (
                  <EmptyState title="No settings" description="Settings will appear here." />
                )}
                <div className="mt-4 flex justify-end">
                  <Button variant="primary" onClick={handleSaveSettings} disabled={updateMutation.isPending}>
                    {updateMutation.isPending ? 'Saving...' : 'Save Settings'}
                  </Button>
                </div>
              </Card>
            ),
          },
          {
            id: 'notifications',
            label: `Notifications ${summary?.unread ? `(${summary.unread})` : ''}`,
            content: (
              <Card className="p-6">
                <div className="mb-4 flex items-center justify-between">
                  <h2 className="text-lg font-semibold text-navy-700 dark:text-white">Notifications</h2>
                  <Button variant="ghost" size="sm" onClick={() => clearAllMutation.mutate()} disabled={clearAllMutation.isPending}>
                    <Trash2 size={14} />
                    Clear all
                  </Button>
                </div>
                {notifLoading ? (
                  <LoadingSkeleton variant="table" rows={3} />
                ) : notifications && notifications.length > 0 ? (
                  <DataTable columns={notificationColumns} data={notifications} rowKey={(n) => n.notification_id} emptyTitle="No notifications" emptyDescription="Notifications will appear here." virtualized={false} />
                ) : (
                  <EmptyState title="No notifications" description="You're all caught up!" />
                )}
              </Card>
            ),
          },
          {
            id: 'exports',
            label: 'Export',
            content: (
              <Card className="p-6">
                <h2 className="mb-4 text-lg font-semibold text-navy-700 dark:text-white">Export Data</h2>
                <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
                  <div>
                    <label className="mb-1 block text-sm font-medium text-gray-700">Report Type</label>
                    <select
                      value={reportType}
                      onChange={(e) => setReportType(e.target.value)}
                      className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
                    >
                      <option value="executive">Executive</option>
                      <option value="operational">Operational</option>
                      <option value="district">District</option>
                      <option value="station">Station</option>
                      <option value="crime_trend">Crime Trend</option>
                      <option value="repeat_offender">Repeat Offender</option>
                      <option value="network">Network Intelligence</option>
                      <option value="predictive">Predictive Intelligence</option>
                    </select>
                  </div>
                  <div>
                    <label className="mb-1 block text-sm font-medium text-gray-700">Format</label>
                    <select
                      value={exportFormat}
                      onChange={(e) => setExportFormat(e.target.value)}
                      className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
                    >
                      <option value="csv">CSV</option>
                      <option value="json">JSON</option>
                      <option value="print">Print-friendly</option>
                    </select>
                  </div>
                  <div className="flex items-end">
                    <Button variant="primary" onClick={handleExport} disabled={exportMutation.isPending} className="w-full">
                      <Download size={16} />
                      {exportMutation.isPending ? 'Exporting...' : 'Export'}
                    </Button>
                  </div>
                </div>
              </Card>
            ),
          },
          {
            id: 'ai-reports',
            label: 'AI Reports',
            content: (
              <Card className="p-6">
                <h2 className="mb-4 text-lg font-semibold text-navy-700 dark:text-white">AI Report Generator</h2>
                <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
                  <div>
                    <label className="mb-1 block text-sm font-medium text-gray-700">Report Type</label>
                    <select
                      value={reportType}
                      onChange={(e) => setReportType(e.target.value)}
                      className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
                    >
                      <option value="executive">Executive Summary</option>
                      <option value="operational">Operational Summary</option>
                      <option value="predictive">Predictive Intelligence</option>
                    </select>
                  </div>
                  <div className="flex items-end">
                    <Button variant="primary" onClick={handleAIReport} disabled={aiReportMutation.isPending} className="w-full">
                      <Brain size={16} />
                      {aiReportMutation.isPending ? 'Generating...' : 'Generate AI Report'}
                    </Button>
                  </div>
                </div>
                {generatedContent && (
                  <div className="mt-4">
                    <h3 className="mb-2 font-semibold text-navy-700 dark:text-white">Generated Report</h3>
                    <div className="rounded-lg border border-gray-200 bg-gray-50 p-4 dark:border-gray-700 dark:bg-gray-800">
                      <pre className="whitespace-pre-wrap text-sm text-gray-800 dark:text-gray-200">{generatedContent}</pre>
                    </div>
                  </div>
                )}
                {aiReportMutation.data && !generatedContent && (
                  <div className="mt-4">
                    <h3 className="mb-2 font-semibold text-navy-700 dark:text-white">Generated Report</h3>
                    <div className="rounded-lg border border-gray-200 bg-gray-50 p-4 dark:border-gray-700 dark:bg-gray-800">
                      <pre className="whitespace-pre-wrap text-sm text-gray-800 dark:text-gray-200">{aiReportMutation.data.content}</pre>
                    </div>
                  </div>
                )}
              </Card>
            ),
          },
          {
            id: 'system',
            label: 'System',
            content: (
              <Card className="p-6">
                <h2 className="mb-4 text-lg font-semibold text-navy-700 dark:text-white">System Settings</h2>
                {systemLoading ? (
                  <LoadingSkeleton variant="table" rows={3} />
                ) : systemSettings && systemSettings.length > 0 ? (
                  <DataTable
                    columns={[
                      { key: 'key', header: 'Key', render: (s) => s.key },
                      { key: 'value', header: 'Value', render: (s) => String(s.value) },
                      { key: 'description', header: 'Description', render: (s) => s.description },
                      { key: 'updated_at', header: 'Updated', render: (s) => (s.updated_at ? new Date(s.updated_at).toLocaleString() : '-') },
                    ]}
                    data={systemSettings}
                    rowKey={(s) => s.key}
                    emptyTitle="No system settings"
                    virtualized={false}
                  />
                ) : (
                  <EmptyState title="No system settings" description="System settings will appear here." />
                )}
              </Card>
            ),
          },
        ]}
      />
    </div>
  );
};

export default Settings;
