import React from 'react';
import { Outlet } from 'react-router-dom';
import { FilterBar } from 'shared/components';

const DashboardLayout: React.FC = () => {
  return (
    <div className="space-y-6">
      <FilterBar />
      <Outlet />
    </div>
  );
};

export default DashboardLayout;
