import { NavLink } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { api } from '../../api/client';
import { Badge } from '../ui/badge';
import { 
  Sparkles, 
  BarChart3, 
  Search, 
  Target, 
  TrendingUp, 
  Zap, 
  Trophy,
  Activity
} from 'lucide-react';
import './Sidebar.css';

const navItems = [
  { path: '/',                    icon: Sparkles,   label: 'Home' },
  { path: '/executive-overview',  icon: BarChart3,  label: 'Executive Overview' },
  { path: '/customer-lookup',     icon: Search,     label: 'Customer Lookup' },
  { path: '/segment-deep-dive',   icon: Target,     label: 'Segment Deep Dive' },
  { path: '/segment-migration',   icon: TrendingUp, label: 'Segment Migration' },
  { path: '/campaign-simulator',  icon: Zap,        label: 'Campaign Simulator' },
  { path: '/model-performance',   icon: Trophy,     label: 'Model Performance' },
];

export default function Sidebar() {
  const [apiOnline, setApiOnline] = useState(false);

  useEffect(() => {
    api.health()
      .then(() => setApiOnline(true))
      .catch(() => setApiOnline(false));
    
    // Poll every 30s
    const interval = setInterval(() => {
      api.health()
        .then(() => setApiOnline(true))
        .catch(() => setApiOnline(false));
    }, 30000);
    
    return () => clearInterval(interval);
  }, []);

  return (
    <aside className="sidebar flex flex-col justify-between border-r border-border bg-card">
      <div>
        {/* Header Brand */}
        <div className="sidebar-header px-6 py-6 border-b border-border">
          <div className="flex items-center gap-2">
            <div className="flex items-center justify-center size-8 rounded-lg bg-emerald-50 text-emerald-600">
              <Sparkles className="size-4.5" />
            </div>
            <div>
              <div className="sidebar-logo-text text-sm font-bold tracking-tight text-foreground">
                🔮 Customer Intelligence
              </div>
              <div className="sidebar-logo-sub text-[10px] font-bold text-muted-foreground tracking-wider uppercase">
                Retention Platform v2.0
              </div>
            </div>
          </div>
        </div>

        {/* Navigation Section */}
        <nav className="sidebar-nav px-4 py-6 flex flex-col gap-1.5">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                end={item.path === '/'}
                className={({ isActive }) => 
                  `nav-link group flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 
                  ${isActive 
                    ? 'bg-slate-100 text-slate-900 font-semibold shadow-xs' 
                    : 'text-slate-500 hover:bg-slate-50 hover:text-slate-900'
                  }`
                }
              >
                {({ isActive }) => (
                  <>
                    <Icon className={`size-4.5 transition-colors duration-200 ${
                      isActive 
                        ? 'text-emerald-600' 
                        : 'text-slate-400 group-hover:text-slate-600'
                    }`} />
                    <span>{item.label}</span>
                  </>
                )}
              </NavLink>
            );
          })}
        </nav>
      </div>

      {/* Footer Section */}
      <div className="sidebar-footer-container">
        {/* API Status Banner */}
        <div className="api-status-wrapper px-4 pb-2">
          <Badge 
            variant={apiOnline ? "default" : "destructive"} 
            className="w-full justify-start gap-2.5 px-3 py-2 font-medium text-xs rounded-lg border-none"
            style={{
              backgroundColor: apiOnline ? 'rgba(16, 185, 129, 0.08)' : 'rgba(239, 68, 68, 0.08)',
              color: apiOnline ? 'var(--accent-emerald)' : 'var(--accent-red)',
            }}
          >
            <div className="flex items-center justify-center size-5 rounded-md bg-white shadow-xs">
              <Activity className={`size-3 ${apiOnline ? 'text-emerald-600' : 'text-red-500'}`} />
            </div>
            <span className="flex-1 text-left">{apiOnline ? 'FastAPI Connected' : 'API Offline'}</span>
            <div className={`size-1.5 rounded-full ${apiOnline ? 'bg-emerald-500 animate-pulse' : 'bg-red-500'}`} />
          </Badge>
        </div>

        {/* Attribution */}
        <div className="sidebar-footer px-6 py-4 border-t border-border bg-slate-50/50">
          <div className="sidebar-footer-text text-[10px] text-muted-foreground text-center leading-relaxed">
            Built with React + FastAPI<br />
            <span className="font-semibold text-slate-600">Rohil Verma © 2026</span>
          </div>
        </div>
      </div>
    </aside>
  );
}
