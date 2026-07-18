import React, { useState } from 'react';
import Modal from './Modal';
import Button from './Button';

interface ConfirmDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void | Promise<void>;
  title: string;
  message: string;
  confirmLabel?: string;
  cancelLabel?: string;
  destructive?: boolean;
  requireReauth?: boolean;
  onReauthenticate?: (password: string) => Promise<boolean>;
}

const ConfirmDialog: React.FC<ConfirmDialogProps> = ({
  isOpen,
  onClose,
  onConfirm,
  title,
  message,
  confirmLabel = 'Confirm',
  cancelLabel = 'Cancel',
  destructive = false,
  requireReauth = false,
  onReauthenticate,
}) => {
  const [password, setPassword] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleConfirm = async () => {
    setIsSubmitting(true);
    setError(null);
    try {
      if (requireReauth && onReauthenticate) {
        const verified = await onReauthenticate(password);
        if (!verified) {
          setError('Re-authentication failed. Please verify your password.');
          return;
        }
      }
      await onConfirm();
      setPassword('');
      onClose();
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={title}
      footer={
        <div className="flex justify-end gap-2">
          <Button variant="ghost" onClick={onClose} disabled={isSubmitting}>
            {cancelLabel}
          </Button>
          <Button
            variant={destructive ? 'danger' : 'primary'}
            onClick={handleConfirm}
            isLoading={isSubmitting}
          >
            {confirmLabel}
          </Button>
        </div>
      }
    >
      <p className="text-sm text-gray-600">{message}</p>
      {requireReauth && (
        <div className="mt-4">
          <label htmlFor="confirm-password" className="mb-1 block text-sm font-medium text-gray-700">
            Confirm your password
          </label>
          <input
            id="confirm-password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
            autoComplete="current-password"
          />
          {error && <p className="mt-2 text-sm text-alert-red">{error}</p>}
        </div>
      )}
    </Modal>
  );
};

export default ConfirmDialog;
