import React from 'react';

export const LoadingState = ({ message = 'Synchronizing PolarSync Platform...' }) => {
  return (
    <div className="polar-glass p-8 rounded-xl border border-slate-800 flex flex-col items-center justify-center min-h-[220px] text-center">
      <div className="w-10 h-10 border-2 border-sky-500/20 border-t-sky-400 rounded-full animate-spin mb-4" />
      <p className="text-sm font-mono text-sky-400 font-medium">{message}</p>
      <p className="text-xs text-slate-500 mt-1">Polling backend telemetry stream</p>
    </div>
  );
};

export default LoadingState;
