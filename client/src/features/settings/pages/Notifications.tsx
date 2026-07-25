import React from 'react';
import { Card, Tabs, DataTable, LoadingSkeleton, EmptyState, Badge, Button } from 'shared/components';
import type { DataTableColumn } from 'shared/components';
import { useNotifications, useNotificationSummary, useMarkNotificationRead, useDismissNotification, useClearAllNotifications } from 'features/settings/hooks/useSettings';
import type { Notification } from 'shared/api';
import toast from 'react-hot-toast';
import { Check, X, Trash2 } from 'lucide-react';

const severityVariant: Record<string, 'success' | 'warning' | 'danger' | 'info' | 'secondary'> = {
  low: 'success',
  medium: 'warning',
  high: 'danger',
  info: 'info',
  critical: 'danger',
};

const Notifications: React.FC = () => {
  const { data: notifications, isLoading: allLoading, refetch: refetchAll } = useNotifications(false);
  const { data: unread, isLoading: unreadLoading, refetch: refetchUnread } = useNotifications(true);
  const { data: summary } = useNotificationSummary();
  const markReadMutation = useMarkNotificationRead();
  const dismissMutation = useDismissNotification();
  const clearAllMutation = useClearAllNotifications();

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
            <Button variant="ghost" size="sm" onClick={() => markReadMutation.mutate(n.notification_id, { onSuccess: () => { refetchAll(); refetchUnread(); } })}>
              <Check size={14} />
            </Button>
          )}
          <Button variant="ghost" size="sm" onClick={() => dismissMutation.mutate(n.notification_id, { onSuccess: () => { refetchAll(); refetchUnread(); } })}>
            <X size={14} />
          </Button>
        </div>
      ),
    },
  ];

  const handleClearAll = async () => {
    try {
      await clearAllMutation.mutateAsync();
      toast.success('All notifications cleared');
      refetchAll();
      refetchUnread();
    } catch {
      toast.error('Failed to clear notifications');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-navy-700 dark:text-white">Notifications</h1>
          <p className="text-sm text-gov-slate">
            {summary ? `${summary.unread} unread of ${summary.total} total` : 'Stay updated with alerts and recommendations'}
          </p>
        </div>
        <Button variant="ghost" size="sm" onClick={handleClearAll} disabled={clearAllMutation.isPending}>
          <Trash2 size={16} />
          Clear all
        </Button>
      </div>

      <Tabs
        items={[
          {
            id: 'all',
            label: 'All',
            content: (
              <Card className="p-6">
                {allLoading ? (
                  <LoadingSkeleton variant="table" rows={5} />
                ) : notifications && notifications.length > 0 ? (
                  <DataTable columns={notificationColumns} data={notifications} rowKey={(n) => n.notification_id} virtualized={false} />
                ) : (
                  <EmptyState title="No notifications" description="You're all caught up!" />
                )}
              </Card>
            ),
          },
          {
            id: 'unread',
            label: `Unread ${summary?.unread ? `(${summary.unread})` : ''}`,
            content: (
              <Card className="p-6">
                {unreadLoading ? (
                  <LoadingSkeleton variant="table" rows={5} />
                ) : unread && unread.length > 0 ? (
                  <DataTable columns={notificationColumns} data={unread} rowKey={(n) => n.notification_id} virtualized={false} />
                ) : (
                  <EmptyState title="No unread notifications" description="You're all caught up!" />
                )}
              </Card>
            ),
          },
        ]}
      />
    </div>
  );
};

export default Notifications;
