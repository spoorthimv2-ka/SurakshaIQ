import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from 'shared/auth';
import { Button } from 'shared/components';
import toast from 'react-hot-toast';

const MFAChallenge: React.FC = () => {
  const navigate = useNavigate();
  const { mfaChallenge, isLoading, getPendingUserId } = useAuth();
  const [mfaCode, setMfaCode] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (mfaCode.length !== 6) {
        throw new Error('MFA code must be 6 digits');
      }
      const userId = sessionStorage.getItem('pending_mfa_user') ?? getPendingUserId();
      if (!userId) {
        throw new Error('Session expired. Please sign in again.');
      }
      await mfaChallenge(userId, mfaCode);
      navigate('/dashboard', { replace: true });
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'MFA verification failed');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="mb-6 text-center">
        <h2 className="text-lg font-semibold text-gray-900">Multi-Factor Authentication</h2>
        <p className="mt-1 text-sm text-gov-slate">
          Required for access to victim, accused, and juvenile PII
        </p>
      </div>
      <div>
        <label htmlFor="mfaCode" className="mb-1 block text-sm font-medium text-gray-700">
          MFA Code
        </label>
        <input
          id="mfaCode"
          type="text"
          inputMode="numeric"
          maxLength={6}
          required
          value={mfaCode}
          onChange={(e) => setMfaCode(e.target.value.replace(/\D/g, ''))}
          className="w-full rounded-lg border border-gray-300 px-4 py-2 text-center text-2xl tracking-widest focus:outline-none focus:ring-2 focus:ring-navy-500"
          placeholder="000000"
          autoComplete="one-time-code"
        />
      </div>
      <Button type="submit" isLoading={isLoading} className="w-full">
        Verify & Continue
      </Button>
    </form>
  );
};

export default MFAChallenge;
