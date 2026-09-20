import React from 'react';
import { useLocation, Link } from 'react-router-dom';
import { ChevronRight, Home } from 'lucide-react';

const routeNameMap = {
  dashboard: 'Command Center',
  expedition: 'Expedition Planning',
  cargo: 'Cold-Chain Cargo',
  inventory: 'Inventory & Autonomy',
  personnel: 'Personnel Muster',
  assets: 'Asset Tracking',
  emergency: 'Emergency & SAR',
  connectivity: 'Satellite & Sync',
  alerts: 'Mission Alerts',
};

export const Breadcrumbs = () => {
  const location = useLocation();
  const pathSegments = location.pathname.split('/').filter(Boolean);

  return (
    <nav className="flex items-center gap-2 text-xs text-slate-400 font-mono mb-4">
      <Link
        to="/"
        className="flex items-center gap-1 hover:text-sky-400 transition-colors"
      >
        <Home className="w-3.5 h-3.5" />
        <span>POLARSYNC</span>
      </Link>

      {pathSegments.map((segment, idx) => {
        const routeTo = `/${pathSegments.slice(0, idx + 1).join('/')}`;
        const isLast = idx === pathSegments.length - 1;
        const displayName = routeNameMap[segment] || segment.toUpperCase();

        return (
          <React.Fragment key={routeTo}>
            <ChevronRight className="w-3 h-3 text-slate-600" />
            {isLast ? (
              <span className="text-sky-400 font-semibold">{displayName}</span>
            ) : (
              <Link to={routeTo} className="hover:text-sky-400 transition-colors">
                {displayName}
              </Link>
            )}
          </React.Fragment>
        );
      })}
    </nav>
  );
};

export default Breadcrumbs;
