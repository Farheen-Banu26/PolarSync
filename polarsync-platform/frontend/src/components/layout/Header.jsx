import React from 'react';
import { useConnectivity } from '../../context/ConnectivityContext';
import { User, Activity, Wifi, WifiOff, RefreshCw, Database } from 'lucide-react';

export const Header = () => {
  const { networkStatus, isOnline, pendingCount, syncNow } = useConnectivity();

  return (
    <header className="h-16 bg-[#0b0f19] border-b border-slate-800/80 px-6 flex items-center justify-between shrink-0">
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

        {/* User / Operator Header Profile */}
        <div className="flex items-center gap-2.5 pl-3 border-l border-slate-800">
          <div className="w-8 h-8 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-sky-400">
            <User className="w-4 h-4" />
          </div>
          <div className="hidden lg:block text-left">
            <div className="text-xs font-semibold text-slate-200">
              Expedition Cmdr
            </div>
            <div className="text-[10px] text-slate-400 font-mono">
              Base Maitri-II
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
