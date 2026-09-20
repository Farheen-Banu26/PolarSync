import React from 'react';

export const StatusBadge = ({ status = 'info', label, size = 'sm' }) => {
  const styles = {
    nominal: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
    online: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
    warning: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
    critical: 'bg-rose-500/15 text-rose-400 border-rose-500/40',
    offline: 'bg-rose-500/15 text-rose-400 border-rose-500/40',
    info: 'bg-sky-500/10 text-sky-400 border-sky-500/30',
    neutral: 'bg-slate-700/30 text-slate-300 border-slate-600/40',
  };

  const sizeClasses = {
    xs: 'px-2 py-0.5 text-[10px]',
    sm: 'px-2.5 py-1 text-xs',
    md: 'px-3 py-1.5 text-sm',
  };

  const currentStyle = styles[status.toLowerCase()] || styles.info;
  const currentSize = sizeClasses[size] || sizeClasses.sm;

  return (
    <span
      className={`inline-flex items-center gap-1.5 font-mono font-medium rounded-full border ${currentStyle} ${currentSize}`}
    >
      <span className="w-1.5 h-1.5 rounded-full bg-current animate-pulse" />
      {label || status.toUpperCase()}
    </span>
  );
};

export default StatusBadge;
