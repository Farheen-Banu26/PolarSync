import React from 'react';
import { Database, Wifi, Clock } from 'lucide-react';

export const CacheIndicator = ({ isCached = false, cachedAt = null }) => {
  if (!isCached) {
    return (
      <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 font-mono text-[11px]">
        <Wifi className="w-3 h-3" />
        <span>LIVE TELEMETRY</span>
      </div>
    );
  }

  const formatTime = (ts) => {
    if (!ts) return 'recently';
    try {
      const d = new Date(ts);
      return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    } catch {
      return 'cached';
    }
  };

  return (
    <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-amber-500/15 border border-amber-500/40 text-amber-300 font-mono text-[11px]">
      <Database className="w-3 h-3 text-amber-400" />
      <span>CACHED (IndexedDB • {formatTime(cachedAt)})</span>
    </div>
  );
};

export default CacheIndicator;
