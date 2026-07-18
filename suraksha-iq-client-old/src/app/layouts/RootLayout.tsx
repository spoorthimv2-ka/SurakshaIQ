import React from 'react';
import { Outlet } from 'react-router-dom';
import { RouterProviders } from 'shared/providers';

const RootLayout: React.FC = () => {
  return (
    <RouterProviders>
      <Outlet />
    </RouterProviders>
  );
};

export default RootLayout;
