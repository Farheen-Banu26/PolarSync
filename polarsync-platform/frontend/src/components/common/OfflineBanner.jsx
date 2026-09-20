import React from 'react';
import { useConnectivity } from '../../context/ConnectivityContext';
import { WifiOff, RefreshCw, CheckCircle2, AlertCircle, Database } from 'lucide-react';

export const OfflineBanner = () => {
  const { networkStatus, pendingCount, syncNow, isOnline } = useConnectivity();

  if (networkStatus === 'ONLINE' && pendingCount === 0) {
    return null;
  }

  return (
    <div className={`w-full px-4 py-2 text-xs font-mono border-b flex flex-wrap items-center justify-between gap-3 transition-colors ${
      networkStatus === 'OFFLINE'
        ? 'bg-amber-950/40 border-amber-500/40 text-amber-200'
        : networkStatus === 'SYNCING'
        ? 'bg-sky-950/50 border-sky-500/40 text-sky-200'
        : networkStatus === 'SYNC_ERROR'
        ? 'bg-rose-950/40 border-rose-500/40 text-rose-200'
        : networkStatus === 'SYNCED'
        ? 'bg-emerald-950/40 border-emerald-500/40 text-emerald-200'
        : 'bg-slate-900 border-slate-800 text-slate-300'
    }`}>
      <div className="flex items-center gap-2.5">
        {networkStatus === 'OFFLINE' ? (
          <WifiOff className="w-4 h-4 text-amber-400 animate-pulse" />
        ) : networkStatus === 'SYNCING' ? (
          <RefreshCw className="w-4 h-4 text-sky-400 animate-spin" />
        ) : networkStatus === 'SYNCED' ? (
          <CheckCircle2 className="w-4 h-4 text-emerald-400" />
        ) : networkStatus === 'SYNC_ERROR' ? (
          <AlertCircle className="w-4 h-4 text-rose-400" />
        ) : (
          <Database className="w-4 h-4 text-sky-400" />
        )}

        <div>
          <span className="font-bold uppercase tracking-wider">
            {networkStatus === 'OFFLINE'
              ? 'OFFLINE MODE — USING LOCAL INDEXEDDB CACHE'
              : networkStatus === 'SYNCING'
              ? 'SYNCHRONIZING FIELD OPERATIONS...'
              : networkStatus === 'SYNCED'
              ? 'SYNCHRONIZATION COMPLETE — SERVER RECONCILED'
              : networkStatus === 'SYNC_ERROR'
              ? 'SYNC ISSUE DETECTED — CHECK QUEUE'
              : 'LOCAL OPERATIONAL QUEUE'}
          </span>
          {pendingCount > 0 && (
            <span className="ml-2 font-normal text-slate-300">
              ({pendingCount} local change{pendingCount > 1 ? 's' : ''} pending upload)
            </span>
          )}
        </div>
      </div>

      <div className="flex items-center gap-2">
        {pendingCount > 0 && (
          <button
            onClick={() => syncNow()}
            disabled={networkStatus === 'SYNCING'}
            className="px-3 py-1 rounded bg-sky-500/20 hover:bg-sky-500/30 text-sky-300 border border-sky-500/40 font-semibold transition cursor-pointer flex items-center gap-1.5"
          >
            <RefreshCw className={`w-3 h-3 ${networkStatus === 'SYNCING' ? 'animate-spin' : ''}`} />
            <span>Sync Now</span>
          </button>
        )}
      </div>
    </div>
  );
};

export default OfflineBanner;
