import React from 'react';
import { Outlet } from 'react-router-dom';

const DashboardLayout: React.FC = () => {
  const [analyzed, setAnalyzed] = React.useState(false);

  return (
    <div className="space-y-6">
         <Outlet context={{ analyzed, setAnalyzed }} />
    </div>
  );
};

export default DashboardLayout;
