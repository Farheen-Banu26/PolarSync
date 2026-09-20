import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Compass,
  Package,
  Boxes,
  Users,
  Truck,
  AlertOctagon,
  Radio,
  Bell,
  Cpu,
  ShieldCheck,
} from 'lucide-react';

const navigationLinks = [
  { name: 'Command Center', path: '/dashboard', icon: LayoutDashboard },
  { name: 'Expedition Planning', path: '/expedition', icon: Compass },
  { name: 'Cargo Tracking', path: '/cargo', icon: Package },
  { name: 'Inventory & Autonomy', path: '/inventory', icon: Boxes },
  { name: 'Personnel Muster', path: '/personnel', icon: Users },
  { name: 'Asset Tracking', path: '/assets', icon: Truck },
  { name: 'Emergency Response', path: '/emergency', icon: AlertOctagon },
  { name: 'Connectivity & Sync', path: '/connectivity', icon: Radio },
  { name: 'Mission Alerts', path: '/alerts', icon: Bell },
];

export const Sidebar = () => {
  return (
    <aside className="w-64 bg-[#0b0f19] border-r border-slate-800/80 flex flex-col h-screen select-none shrink-0">
      {/* Branding Section */}
      <div className="p-5 border-b border-slate-800/80">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-sky-400 to-indigo-600 flex items-center justify-center font-bold text-white shadow-lg shadow-sky-500/20">
            ❄️
          </div>
          <div>
            <div className="text-base font-extrabold tracking-wider text-slate-100 font-mono">
              POLARSYNC
            </div>
            <div className="text-[11px] font-mono font-semibold text-sky-400 tracking-wider">
              SIH26062
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-1">
        <div className="px-3 pb-2 text-[10px] font-bold uppercase tracking-wider text-slate-400 font-mono">
          Operational Modules
        </div>
        {navigationLinks.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-medium transition-all duration-150 ${
                  isActive
                    ? 'bg-sky-500/15 text-sky-300 font-semibold border border-sky-500/30 shadow-sm shadow-sky-500/10'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                }`
              }
            >
              <Icon className="w-4 h-4 shrink-0" />
              <span>{item.name}</span>
            </NavLink>
          );
        })}
      </nav>

      {/* Bottom Status Block */}
      <div className="p-4 border-t border-slate-800/80 bg-slate-950/50 space-y-2">
        <div className="flex items-center justify-between text-xs">
          <span className="text-slate-400 flex items-center gap-1.5">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
            System Status
          </span>
          <span className="font-mono text-emerald-400 font-semibold text-[11px]">
            OPERATIONAL
          </span>
        </div>

        <div className="flex items-center justify-between text-xs pt-1 border-t border-slate-800/40">
          <span className="text-slate-400 flex items-center gap-1.5">
            <Cpu className="w-3.5 h-3.5 text-sky-400" />
            Simulator
          </span>
          <span className="font-mono text-sky-400 font-semibold text-[11px]">
            CONNECTED
          </span>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
