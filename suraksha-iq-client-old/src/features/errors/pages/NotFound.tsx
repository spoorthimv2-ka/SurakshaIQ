import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Button, EmptyState } from 'shared/components';

const NotFound: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100 px-4">
      <EmptyState
        icon={<span className="text-6xl">404</span>}
        title="Page Not Found"
        description="The page you are looking for does not exist."
        action={
          <Button onClick={() => navigate('/')} variant="primary">
            Go Home
          </Button>
        }
      />
    </div>
  );
};

export default NotFound;
