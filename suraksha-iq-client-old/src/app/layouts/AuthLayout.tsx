import React from 'react';
import { Outlet } from 'react-router-dom';
import { Card } from 'shared/components';

const AuthLayout: React.FC = () => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-900 to-gray-800 px-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">SurakshaIQ</h1>
          <p className="text-gray-400">Crime Analytics & Predictive Dashboard</p>
        </div>
        <Card>
          <div className="p-8">
            <Outlet />
          </div>
        </Card>
      </div>
    </div>
  );
};

export default AuthLayout;
