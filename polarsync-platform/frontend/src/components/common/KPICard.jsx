import React from 'react';

export const KPICard = ({
  label,
  value,
  subtext,
  icon: Icon,
  status = 'neutral',
  badgeText,
}) => {
  return (
    <div className="polar-glass p-5 rounded-xl border border-slate-800 hover:border-sky-500/30 transition-all duration-200 polar-card-glow">
      <div className="flex items-center justify-between gap-2 mb-2">
        <span className="text-xs font-semibold tracking-wider text-slate-400 uppercase">
          {label}
        </span>
        {Icon && (
          <div className="p-2 rounded-lg bg-slate-800/80 text-sky-400 border border-slate-700/50">
            <Icon className="w-4 h-4" />
          </div>
        )}
      </div>

      <div className="flex items-baseline gap-3 my-1">
        <span className="text-2xl lg:text-3xl font-bold font-mono text-slate-100">
          {value}
        </span>
        {badgeText && (
          <span className="text-xs font-mono font-medium px-2 py-0.5 rounded bg-slate-800 text-sky-300 border border-slate-700">
            {badgeText}
          </span>
        )}
      </div>

      {subtext && (
        <p className="text-xs text-slate-400 mt-2 font-medium">
          {subtext}
        </p>
      )}
    </div>
  );
};

export default KPICard;
