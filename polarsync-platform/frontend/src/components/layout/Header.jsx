import React, { useState } from 'react';
import { useConnectivity } from '../../context/ConnectivityContext';
import { useAuth } from '../../context/AuthContext';
import { User, Shield, ChevronDown, Wifi, WifiOff, RefreshCw, Check } from 'lucide-react';

export const Header = () => {
  const { networkStatus } = useConnectivity();
  const { currentUser, availableRoles, switchRole } = useAuth();
  const [dropdownOpen, setDropdownOpen] = useState(false);

  const roles = availableRoles.length > 0 ? availableRoles : [
    { username: 'commander', role: 'Expedition Commander', full_name: 'Dr. Rajesh Sharma', station: 'Maitri-II Main Station' },
    { username: 'logistics', role: 'Logistics Officer', full_name: 'Lt. Col. Vikram Rao', station: 'Maitri-II Main Station' },
    { username: 'safety', role: 'Medical/Safety Officer', full_name: 'Dr. Ananya Sen (MD)', station: 'Maitri-II Main Station' },
    { username: 'operator', role: 'Field Operator', full_name: 'Suresh Patel', station: 'Camp Alpha (Schirmacher)' },
    { username: 'admin', role: 'Administrator', full_name: 'Central Admin', station: 'NCPOR HQ (Goa)' },
    { username: 'viewer', role: 'Viewer', full_name: 'Observer', station: 'Remote Observer' }
  ];

  return (
    <header className="h-16 bg-[#0b0f19] border-b border-slate-800/80 px-6 flex items-center justify-between shrink-0 relative z-30">
      {/* Title & Subtitle */}
      <div>
        <div className="flex items-center gap-2.5">
          <h2 className="text-base font-bold text-slate-100 font-mono tracking-tight">
            PolarSync Command Center
          </h2>
          <span className="text-[10px] font-mono font-semibold px-2 py-0.5 rounded bg-sky-500/10 text-sky-400 border border-sky-500/30">
            SIH26062
          </span>
        </div>
        <p className="text-xs text-slate-400 hidden sm:block">
          Integrated Polar Expedition Logistics and Asset Management System
        </p>
      </div>

      {/* Status & User Actions */}
      <div className="flex items-center gap-4">
        {/* Network & Backend Status Badge */}
        <div
          className={`flex items-center gap-2 px-3 py-1 rounded-full border text-xs font-mono font-medium transition-colors ${
            networkStatus === 'OFFLINE'
              ? 'bg-amber-500/15 text-amber-300 border-amber-500/30'
              : networkStatus === 'SYNCING'
              ? 'bg-sky-500/15 text-sky-300 border-sky-500/30'
              : networkStatus === 'SYNC_ERROR'
              ? 'bg-rose-500/15 text-rose-400 border-rose-500/30'
              : 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
          }`}
          title={
            networkStatus === 'OFFLINE'
              ? 'Offline Mode — Local IndexedDB cache operational'
              : 'FastAPI Backend Online & Synced'
          }
        >
          {networkStatus === 'OFFLINE' ? (
            <WifiOff className="w-3.5 h-3.5 text-amber-400" />
          ) : networkStatus === 'SYNCING' ? (
            <RefreshCw className="w-3.5 h-3.5 text-sky-400 animate-spin" />
          ) : (
            <Wifi className="w-3.5 h-3.5 text-emerald-400" />
          )}
          <span>
            {networkStatus === 'OFFLINE'
              ? 'OFFLINE (CACHED)'
              : networkStatus === 'SYNCING'
              ? 'SYNCING...'
              : 'ONLINE'}
          </span>
        </div>

        {/* Role Switcher Dropdown */}
        <div className="relative">
          <button
            onClick={() => setDropdownOpen(!dropdownOpen)}
            className="flex items-center gap-2.5 pl-3 pr-2 py-1.5 rounded-lg border border-slate-800 bg-slate-900/80 hover:bg-slate-800 transition-colors text-left font-mono"
          >
            <div className="w-7 h-7 rounded-full bg-sky-950 border border-sky-500/40 flex items-center justify-center text-sky-400">
              <User className="w-3.5 h-3.5" />
            </div>
            <div className="hidden lg:block">
              <div className="text-xs font-semibold text-slate-100 flex items-center gap-1.5">
                {currentUser?.role || 'Expedition Commander'}
                <ChevronDown className="w-3 h-3 text-slate-400" />
              </div>
              <div className="text-[10px] text-slate-400">
                {currentUser?.full_name || 'Dr. Rajesh Sharma'}
              </div>
            </div>
          </button>

          {dropdownOpen && (
            <div className="absolute right-0 mt-2 w-64 rounded-xl polar-glass border border-slate-700 shadow-2xl p-2 z-50 animate-fade-in font-mono text-xs">
              <div className="px-3 py-2 text-[10px] font-bold text-slate-400 uppercase tracking-wider border-b border-slate-800 mb-1 flex items-center gap-1.5">
                <Shield className="w-3 h-3 text-sky-400" /> Switch Operational Role (RBAC)
              </div>
              <div className="space-y-1">
                {roles.map((r) => {
                  const isActive = currentUser?.username === r.username;
                  return (
                    <button
                      key={r.username}
                      onClick={() => {
                        switchRole(r.username);
                        setDropdownOpen(false);
                      }}
                      className={`w-full text-left px-3 py-2 rounded-lg flex items-center justify-between transition-colors ${
                        isActive
                          ? 'bg-sky-500/20 text-sky-300 border border-sky-500/30'
                          : 'hover:bg-slate-800/80 text-slate-300'
                      }`}
                    >
                      <div>
                        <div className="font-bold">{r.role}</div>
                        <div className="text-[10px] text-slate-400">{r.full_name}</div>
                      </div>
                      {isActive && <Check className="w-3.5 h-3.5 text-sky-400" />}
                    </button>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};

export default Header;
