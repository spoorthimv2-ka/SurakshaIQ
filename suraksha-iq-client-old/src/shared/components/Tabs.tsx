import React, { useState } from 'react';
import clsx from 'clsx';

interface TabItem {
  id: string;
  label: string;
  content: React.ReactNode;
}

interface TabsProps {
  items: TabItem[];
  defaultTab?: string;
}

const Tabs: React.FC<TabsProps> = ({ items, defaultTab }) => {
  const [activeTab, setActiveTab] = useState(defaultTab || items[0]?.id || '');

  return (
    <div className="w-full">
      <div className="flex border-b border-gray-200">
        {items.map((item) => (
          <button
            key={item.id}
            onClick={() => setActiveTab(item.id)}
            className={clsx(
              'px-4 py-2 font-medium text-sm transition-colors',
              activeTab === item.id
                ? 'text-blue-600 border-b-2 border-blue-600'
                : 'text-gray-600 hover:text-gray-900'
            )}
          >
            {item.label}
          </button>
        ))}
      </div>
      <div className="mt-4">
        {items.find((item) => item.id === activeTab)?.content}
      </div>
    </div>
  );
};

export default Tabs;
