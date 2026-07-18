import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { ChevronDown, ChevronUp } from 'lucide-react';
import Button from './Button';
import LoadingSkeleton from './LoadingSkeleton';
import EmptyState from './EmptyState';

export interface DataTableColumn<T> {
  key: string;
  header: string;
  sortable?: boolean;
  width?: string;
  render: (row: T) => React.ReactNode;
  sortValue?: (row: T) => string | number;
}

interface DataTableProps<T> {
  columns: DataTableColumn<T>[];
  data: T[];
  rowKey: (row: T) => string;
  isLoading?: boolean;
  pageSize?: number;
  hasNextPage?: boolean;
  onLoadMore?: () => void;
  emptyTitle?: string;
  emptyDescription?: string;
  virtualized?: boolean;
  rowHeight?: number;
  maxHeight?: number;
}

function DataTable<T>({
  columns,
  data,
  rowKey,
  isLoading = false,
  pageSize = 25,
  hasNextPage = false,
  onLoadMore,
  emptyTitle = 'No records',
  emptyDescription,
  virtualized = true,
  rowHeight = 48,
  maxHeight = 480,
}: DataTableProps<T>) {
  const [sortKey, setSortKey] = useState<string | null>(null);
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('asc');
  const [visibleCount, setVisibleCount] = useState(pageSize);
  const scrollRef = useRef<HTMLDivElement>(null);

  const sortedData = useMemo(() => {
    if (!sortKey) return data;
    const column = columns.find((c) => c.key === sortKey);
    if (!column?.sortValue) return data;
    return [...data].sort((a, b) => {
      const av = column.sortValue!(a);
      const bv = column.sortValue!(b);
      if (av < bv) return sortDir === 'asc' ? -1 : 1;
      if (av > bv) return sortDir === 'asc' ? 1 : -1;
      return 0;
    });
  }, [columns, data, sortDir, sortKey]);

  const pagedData = sortedData.slice(0, visibleCount);

  const handleSort = (key: string) => {
    if (sortKey === key) {
      setSortDir((d) => (d === 'asc' ? 'desc' : 'asc'));
    } else {
      setSortKey(key);
      setSortDir('asc');
    }
  };

  const handleScroll = useCallback(() => {
    const el = scrollRef.current;
    if (!el || !virtualized) return;
    const nearBottom = el.scrollTop + el.clientHeight >= el.scrollHeight - rowHeight * 2;
    if (nearBottom && visibleCount < sortedData.length) {
      setVisibleCount((c) => Math.min(c + pageSize, sortedData.length));
    }
  }, [pageSize, rowHeight, sortedData.length, virtualized, visibleCount]);

  useEffect(() => {
    setVisibleCount(pageSize);
  }, [data, pageSize]);

  if (isLoading) {
    return <LoadingSkeleton variant="table" rows={5} />;
  }

  if (data.length === 0) {
    return <EmptyState title={emptyTitle} description={emptyDescription} />;
  }

  return (
    <div className="overflow-hidden rounded-lg border border-gray-200 bg-white dark:border-gray-700 dark:bg-gray-900">
      <div
        ref={scrollRef}
        onScroll={handleScroll}
        className="overflow-auto"
        style={{ maxHeight: virtualized ? maxHeight : undefined }}
      >
        <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead className="sticky top-0 bg-gray-50 dark:bg-gray-800">
            <tr>
              {columns.map((col) => (
                <th
                  key={col.key}
                  scope="col"
                  style={{ width: col.width }}
                  className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-gov-slate"
                >
                  {col.sortable ? (
                    <button
                      type="button"
                      onClick={() => handleSort(col.key)}
                      className="inline-flex items-center gap-1 hover:text-navy-600"
                    >
                      {col.header}
                      {sortKey === col.key &&
                        (sortDir === 'asc' ? <ChevronUp size={14} /> : <ChevronDown size={14} />)}
                    </button>
                  ) : (
                    col.header
                  )}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100 dark:divide-gray-800">
            {pagedData.map((row) => (
              <tr
                key={rowKey(row)}
                className="hover:bg-blue-50/50 dark:hover:bg-gray-800/80"
                style={{ height: rowHeight }}
              >
                {columns.map((col) => (
                  <td key={col.key} className="px-4 py-3 text-sm text-gray-900 dark:text-gray-100">
                    {col.render(row)}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {(hasNextPage || visibleCount < sortedData.length) && (
        <div className="border-t border-gray-200 px-4 py-3 dark:border-gray-700">
          <Button
            variant="secondary"
            size="sm"
            onClick={() => {
              if (onLoadMore) {
                onLoadMore();
              } else {
                setVisibleCount((c) => c + pageSize);
              }
            }}
          >
            Load more
          </Button>
        </div>
      )}
    </div>
  );
}

export default DataTable;
