import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from 'shared/auth';
import { Button } from 'shared/components';
import toast from 'react-hot-toast';
import { enableMockMode } from 'config/env';

const Login: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { login, isLoading } = useAuth();
  const [formData, setFormData] = useState({ email: '', password: '' });

  const from = (location.state as { from?: string })?.from ?? '/dashboard';

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const result = await login(formData.email, formData.password);
      if (result.mfaRequired) {
        sessionStorage.setItem('pending_mfa_user', result.userId);
        navigate('/mfa-challenge');
      } else {
        navigate(from, { replace: true });
      }
    } catch (error) {
      const message = (error as { message?: string })?.message ?? 'Login failed';
      toast.error(message);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="mb-6 text-center">
        <h2 className="text-lg font-semibold text-gray-900">Officer Sign In</h2>
        <p className="mt-1 text-sm text-gov-slate">Zoho Catalyst Authentication</p>
      </div>
      <div>
        <label htmlFor="email" className="mb-1 block text-sm font-medium text-gray-700">
          Email
        </label>
        <input
          id="email"
          type="email"
          required
          value={formData.email}
          onChange={(e) => setFormData({ ...formData, email: e.target.value })}
          className="w-full rounded-lg border border-gray-300 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-navy-500"
          placeholder="officer@karnataka.gov.in"
          autoComplete="username"
        />
      </div>
      <div>
        <label htmlFor="password" className="mb-1 block text-sm font-medium text-gray-700">
          Password
        </label>
        <input
          id="password"
          type="password"
          required
          value={formData.password}
          onChange={(e) => setFormData({ ...formData, password: e.target.value })}
          className="w-full rounded-lg border border-gray-300 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-navy-500"
          placeholder="••••••••"
          autoComplete="current-password"
        />
      </div>
      {enableMockMode && (
        <p className="rounded-lg bg-blue-50 px-3 py-2 text-xs text-navy-600">
          Demo: dgp@karnataka.gov.in / demo1234 or admin@karnataka.gov.in / admin1234
        </p>
      )}
      <Button type="submit" isLoading={isLoading} className="w-full">
        Sign In
      </Button>
    </form>
  );
};

export default Login;
