import { NavLink, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';

const navItems = [
  { to: '/dashboard', icon: '⬡', label: 'Dashboard' },
  { to: '/customers', icon: '👥', label: 'Customers' },
  { to: '/activity',  icon: '📋', label: 'Activity Log' },
  { to: '/demo',      icon: '▶', label: 'Demo Controls' },
];

export default function Sidebar() {
  const { banker, logout } = useAuthStore();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <>
      {/* ── Sidebar ───────────────────────────────────────────────────────── */}
      <aside className="
        fixed left-0 top-0 h-screen z-40
        w-60 xl:w-60 lg:w-14
        flex flex-col
        bg-bg-surface border-r border-bm-border
        transition-all duration-300
      ">
        {/* Logo */}
        <div className="h-16 flex items-center px-5 border-b border-bm-border">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-accent-primary to-accent-purple flex items-center justify-center text-white font-bold text-sm">
              B
            </div>
            <span className="font-bold text-text-primary text-lg tracking-tight lg:hidden xl:block">
              BankMind
            </span>
          </div>
        </div>

        {/* Nav */}
        <nav className="flex-1 px-3 py-4 space-y-1">
          {navItems.map(({ to, icon, label }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-150
                ${isActive
                  ? 'bg-accent-primary/10 text-accent-primary border-l-2 border-accent-primary'
                  : 'text-text-secondary hover:text-text-primary hover:bg-bg-elevated'
                }`
              }
            >
              <span className="text-base w-5 text-center flex-shrink-0">{icon}</span>
              <span className="lg:hidden xl:block">{label}</span>
            </NavLink>
          ))}
        </nav>

        {/* Bottom: banker info */}
        <div className="p-3 border-t border-bm-border">
          <div className="flex items-center gap-3 px-2 py-2">
            <div className="w-8 h-8 rounded-full bg-accent-primary/20 text-accent-primary flex items-center justify-center text-xs font-bold flex-shrink-0">
              {banker?.name?.[0] || 'B'}
            </div>
            <div className="min-w-0 lg:hidden xl:block">
              <p className="text-xs font-medium text-text-primary truncate">{banker?.name || 'Demo Banker'}</p>
              <p className="text-xs text-text-muted truncate">{banker?.email || ''}</p>
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="mt-2 w-full text-left flex items-center gap-3 px-3 py-2 rounded-lg text-xs text-text-muted hover:text-accent-danger hover:bg-accent-danger/5 transition-colors"
          >
            <span className="w-5 text-center">→</span>
            <span className="lg:hidden xl:block">Logout</span>
          </button>
        </div>
      </aside>

      {/* ── Mobile warning ──────────────────────────────────────────────────── */}
      <div className="fixed top-0 left-0 right-0 z-50 hidden max-lg:flex items-center gap-2 bg-accent-warning/10 border-b border-accent-warning/30 text-accent-warning text-xs px-4 py-2">
        <span>⚠</span>
        <span>BankMind is optimized for desktop (1280px+). Some features may appear compressed.</span>
      </div>
    </>
  );
}
