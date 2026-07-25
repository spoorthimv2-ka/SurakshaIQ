import React, { useState, useEffect, FormEvent } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from 'hooks/useAuth';
import toast from 'react-hot-toast';

const Login: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { isAuthenticated, loading, login } = useAuth();

  const [badgeNumber, setBadgeNumber] = useState('');
  const [badgeError, setBadgeError] = useState('');
  const [password, setPassword] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const from = (location.state as { from?: string })?.from ?? '/dashboard';

  useEffect(() => {
    if (isAuthenticated && !loading) {
      navigate(from, { replace: true });
    }
  }, [isAuthenticated, loading, from, navigate]);

  const validateBadgeNumber = (value: string) => {
    if (!value.trim()) return 'Badge Number is required';
    if (!/^KSP-[0-9]{6}$/.test(value)) return 'Badge Number must be in the format KSP-123456';
    return '';
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    const validationError = validateBadgeNumber(badgeNumber);
    if (validationError) {
      setBadgeError(validationError);
      return;
    }
    setBadgeError('');
    setSubmitting(true);
    try {
      await login(badgeNumber, password);
      navigate(from, { replace: true });
    } catch (error) {
      console.error('Login failed', error);
      toast.error('Invalid badge number or password. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-gray-900 to-gray-800 px-4">
        <div className="w-full max-w-md">
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-white mb-2">SurakshaIQ</h1>
            <p className="text-gray-400">Crime Analytics &amp; Predictive Dashboard</p>
          </div>
          <div className="rounded-lg bg-white p-8 shadow-xl dark:bg-gray-800">
            <div className="flex items-center justify-center space-x-2">
              <div className="h-2 w-2 animate-bounce rounded-full bg-amber-analytics [animation-delay:-0.3s]"></div>
              <div className="h-2 w-2 animate-bounce rounded-full bg-amber-analytics [animation-delay:-0.15s]"></div>
              <div className="h-2 w-2 animate-bounce rounded-full bg-amber-analytics"></div>
            </div>
            <p className="mt-4 text-center text-sm text-gov-slate">Restoring session...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="mb-6 text-center">
        <h2 className="text-lg font-semibold text-gray-900">Officer Sign In</h2>
        <p className="mt-1 text-sm text-gov-slate">Enter your credentials to access the dashboard</p>
      </div>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="badgeNumber" className="block text-sm font-medium text-gray-700">
            Badge Number
          </label>
          <input
            id="badgeNumber"
            type="text"
            inputMode="text"
            autoComplete="username"
            required
            value={badgeNumber}
            onChange={(e) => {
              setBadgeNumber(e.target.value.toUpperCase());
              if (badgeError) setBadgeError('');
            }}
            className={`mt-1 block w-full rounded-md border px-3 py-2 shadow-sm focus:outline-none focus:ring-1 focus:ring-amber-analytics dark:bg-gray-800 dark:text-white ${
              badgeError ? 'border-red-500 focus:border-red-500' : 'border-gray-300 focus:border-amber-analytics'
            }`}
            placeholder="KSP-123456"
          />
          {badgeError && (
            <p className="mt-1 text-sm text-red-600">{badgeError}</p>
          )}
        </div>
        <div>
          <label htmlFor="password" className="block text-sm font-medium text-gray-700">
            Password
          </label>
          <input
            id="password"
            type="password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-amber-analytics focus:outline-none focus:ring-1 focus:ring-amber-analytics dark:border-gray-700 dark:bg-gray-800 dark:text-white"
            placeholder="••••••••"
          />
        </div>
        <button
          type="submit"
          disabled={submitting}
          className="w-full rounded-md bg-amber-analytics px-4 py-2 text-sm font-medium text-white hover:bg-amber-analytics/90 focus:outline-none focus:ring-2 focus:ring-amber-analytics focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {submitting ? 'Signing in...' : 'Sign in'}
        </button>
      </form>
    </div>
  );
};

export default Login;
