import React from 'react';
import clsx from 'clsx';
import { X } from 'lucide-react';

interface DrawerProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  children: React.ReactNode;
  position?: 'left' | 'right';
}

const Drawer: React.FC<DrawerProps> = ({
  isOpen,
  onClose,
  title,
  children,
  position = 'right',
}) => {
  if (!isOpen) return null;

  const positionClasses = {
    left: 'left-0',
    right: 'right-0',
  };

  return (
    <>
      <div
        className="fixed inset-0 z-40 bg-black bg-opacity-50"
        onClick={onClose}
      />
      <div
        className={clsx(
          'fixed top-0 bottom-0 z-50 w-64 bg-white shadow-lg transform transition-transform duration-300',
          positionClasses[position],
          isOpen ? 'translate-x-0' : (position === 'left' ? '-translate-x-full' : 'translate-x-full')
        )}
      >
        {title && (
          <div className="flex items-center justify-between border-b border-gray-200 px-6 py-4">
            <h2 className="text-lg font-semibold">{title}</h2>
            <button onClick={onClose} className="text-gray-500 hover:text-gray-700">
              <X size={20} />
            </button>
          </div>
        )}
        <div className="px-6 py-4 overflow-y-auto h-full">{children}</div>
      </div>
    </>
  );
};

export default Drawer;
