import React from 'react';
import { Outlet, NavLink, useNavigate } from 'react-router-dom';
import { Menu, Bell, LogOut, Moon, Sun } from 'lucide-react';
import { useAuth } from 'shared/auth';
import { useUIStore, useAlertStore } from 'shared/state';
import { IconButton } from 'shared/components';
import { getVisibleNavItems } from 'shared/config/navigation';
import { useTheme } from 'shared/providers/ThemeProvider';
import { buildVersion } from 'config/env';
import { ROLE_LABELS } from 'shared/auth/types';

const AppShellLayout: React.FC = () => {
  const { officer, logout } = useAuth();
  const { sidebarCollapsed, toggleSidebar } = useUIStore();
  const { unreadCount } = useAlertStore();
  const { theme, toggleTheme } = useTheme();
  const navigate = useNavigate();

  const visibleItems = getVisibleNavItems(officer?.role);

  const jurisdictionLabel = officer?.jurisdiction
    ? `${officer.jurisdiction.type}${officer.jurisdiction.districtId ? `: ${officer.jurisdiction.districtId}` : ''}`
    : 'Karnataka State';

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <div className="flex h-screen bg-gray-100 dark:bg-gray-950">
      <aside
        className={`flex flex-col border-r border-gray-200 bg-navy-700 transition-all duration-300 dark:border-gray-800 ${
          sidebarCollapsed ? 'w-20' : 'w-64'
        }`}
      >
        <div className="flex items-center justify-between border-b border-navy-600 p-4">
          {!sidebarCollapsed && (
            <div>
              <h2 className="text-lg font-bold text-white">SurakshaIQ</h2>
              <p className="text-xs text-navy-100">Karnataka Police</p>
            </div>
          )}
          <button
            type="button"
            onClick={toggleSidebar}
            className="text-navy-100 hover:text-white"
            aria-label="Toggle sidebar"
          >
            <Menu size={20} />
          </button>
        </div>
        <nav className="flex-1 space-y-1 p-3">
          {visibleItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `block rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-amber-analytics/20 text-amber-analytics'
                    : 'text-navy-100 hover:bg-navy-600 hover:text-white'
                }`
              }
              title={sidebarCollapsed ? item.label : undefined}
            >
              {sidebarCollapsed ? item.label.charAt(0) : item.label}
            </NavLink>
          ))}
        </nav>
      </aside>

      <div className="flex flex-1 flex-col">
        <header className="flex items-center justify-between border-b border-gray-200 bg-white px-6 py-4 dark:border-gray-800 dark:bg-gray-900">
          <div>
            <h1 className="text-xl font-bold text-navy-700 dark:text-white">
              {officer?.designation ?? 'Command Dashboard'}
            </h1>
            <p className="text-sm text-gov-slate">
              {officer ? `${officer.rank} · ${ROLE_LABELS[officer.role]}` : ''} · {jurisdictionLabel}
            </p>
          </div>
          <div className="flex items-center gap-2">
            <IconButton
              icon={theme === 'dark' ? <Sun size={20} /> : <Moon size={20} />}
              onClick={toggleTheme}
              aria-label="Toggle theme"
            />
            <div className="relative">
              <IconButton
                icon={<Bell size={20} />}
                onClick={() => navigate('/alerts')}
                aria-label="View alerts"
              />
              {unreadCount > 0 && (
                <span className="absolute -right-1 -top-1 rounded-full bg-alert-red px-1.5 py-0.5 text-xs font-bold text-white">
                  {unreadCount}
                </span>
              )}
            </div>
            <button
              type="button"
              onClick={handleLogout}
              className="flex items-center gap-2 rounded-lg px-3 py-2 text-sm text-gov-slate hover:bg-gray-100 dark:hover:bg-gray-800"
            >
              <LogOut size={18} />
              <span className="hidden sm:inline">Sign out</span>
            </button>
          </div>
        </header>

        <main className="flex-1 overflow-auto">
          <div className="p-6">
            <Outlet />
          </div>
        </main>

        <footer className="border-t border-gray-200 bg-white px-6 py-3 text-center text-xs text-gov-slate dark:border-gray-800 dark:bg-gray-900">
          SurakshaIQ v{buildVersion} · Karnataka State Police · Crime Analytics Platform
        </footer>
      </div>
    </div>
  );
};

export default AppShellLayout;
