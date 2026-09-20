import React from 'react';

export const PageContainer = ({
  title,
  subtitle,
  badge,
  actions,
  children,
}) => {
  return (
    <div className="space-y-6">
      {/* Page Header Section */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 pb-4 border-b border-slate-800/80">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-xl md:text-2xl font-bold text-slate-100 tracking-tight">
              {title}
            </h1>
            {badge && (
              <span className="text-xs font-mono font-semibold px-2.5 py-0.5 rounded bg-sky-500/10 text-sky-400 border border-sky-500/30">
                {badge}
              </span>
            )}
          </div>
          {subtitle && (
            <p className="text-sm text-slate-400 mt-1">
              {subtitle}
            </p>
          )}
        </div>

        {actions && <div className="flex items-center gap-3">{actions}</div>}
      </div>

      {/* Main Content Area */}
      <div>{children}</div>
    </div>
  );
};

export default PageContainer;
