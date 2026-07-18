import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Button, EmptyState } from 'shared/components';
import { Lock } from 'lucide-react';

const Forbidden: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100 px-4">
      <EmptyState
        icon={<Lock />}
        title="Access Denied"
        description="You do not have permission to access this resource."
        action={
          <Button onClick={() => navigate('/dashboard')} variant="primary">
            Go to Dashboard
          </Button>
        }
      />
    </div>
  );
};

export default Forbidden;
