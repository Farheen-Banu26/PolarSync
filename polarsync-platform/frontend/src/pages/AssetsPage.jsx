import React, { useState, useEffect, useMemo } from 'react';
import PageContainer from '../components/common/PageContainer';
import ScenarioSelector from '../components/common/ScenarioSelector';
import StatusBadge from '../components/common/StatusBadge';
import LoadingState from '../components/common/LoadingState';
import ErrorState from '../components/common/ErrorState';
import CacheIndicator from '../components/common/CacheIndicator';
import { useScenario } from '../context/ScenarioContext';
import { useConnectivity } from '../context/ConnectivityContext';
import { getAssets } from '../services/api';
import { Truck, Fuel, Battery, Compass, Plane, ShieldAlert, CheckCircle2, Filter } from 'lucide-react';

export const AssetsPage = () => {
  const { scenarioId, setScenarioId } = useScenario();
  const { performLocalOperation } = useConnectivity();
  const [assets, setAssets] = useState([]);
  const [filter, setFilter] = useState('ALL');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [localStatuses, setLocalStatuses] = useState({});

  const fetchAssets = async (scId) => {
    setLoading(true);
    setError(null);
    try {
      const data = await getAssets(scId);
      setAssets(Array.isArray(data) ? data : (data.assets || []));
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed to load assets');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAssets(scenarioId);
  }, [scenarioId]);

  const handleToggleAssetStatus = async (asset) => {
    const currentStatus = localStatuses[asset.id] || asset.status;
    const newStatus = currentStatus === 'AVAILABLE' ? 'IN_MISSION' : 'AVAILABLE';
    
    setLocalStatuses(prev => ({ ...prev, [asset.id]: newStatus }));

    await performLocalOperation('assets', 'UPDATE_STATUS', {
      asset_id: asset.id,
      status: newStatus
    });
  };

  // Filter logic
  const filteredAssets = useMemo(() => {
    if (filter === 'ALL') return assets;
    if (filter === 'VEHICLES') return assets.filter(a => a.type.includes('VEHICLE') || a.type.includes('TRUCK') || a.type.includes('SNOWMOBILE'));
    if (filter === 'AIRCRAFT') return assets.filter(a => a.type.includes('HELI') || a.type.includes('AIR') || a.type.includes('DRONE'));
    if (filter === 'AVAILABLE') return assets.filter(a => (localStatuses[a.id] || a.status) === 'AVAILABLE');
    if (filter === 'IN_MISSION') return assets.filter(a => (localStatuses[a.id] || a.status) === 'IN_TRANSIT' || (localStatuses[a.id] || a.status) === 'IN_MISSION' || a.speed_kmh > 0);
    if (filter === 'EMERGENCY') return assets.filter(a => (localStatuses[a.id] || a.status) === 'DISPATCHED_EMERGENCY');
    return assets;
  }, [assets, filter, localStatuses]);

  // Status counters
  const totalCount = assets.length;
  const availableCount = assets.filter(a => (localStatuses[a.id] || a.status) === 'AVAILABLE').length;
  const inTransitCount = assets.filter(a => (localStatuses[a.id] || a.status) === 'IN_TRANSIT' || (localStatuses[a.id] || a.status) === 'IN_MISSION' || a.speed_kmh > 0).length;
  const emergencyCount = assets.filter(a => (localStatuses[a.id] || a.status) === 'DISPATCHED_EMERGENCY').length;

  return (
    <PageContainer
      title="Asset & Vehicle Fleet Management"
      subtitle="Vehicle Kinematics, Telemetry, Fuel Optimization & Subsystem Diagnostics"
      badge="FLEET OPERATIONS"
    >
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <ScenarioSelector
          selectedScenario={scenarioId}
          onSelectScenario={setScenarioId}
          disabled={loading}
        />
        <CacheIndicator isCached={assets?._isCached} cachedAt={assets?._cachedAt} />
      </div>

      {loading && assets.length === 0 ? (
        <LoadingState message="Extracting fleet telemetry from simulation..." />
      ) : error && assets.length === 0 ? (
        <ErrorState message={error} onRetry={() => fetchAssets(scenarioId)} />
      ) : (
        <div className="space-y-6">
          {/* Fleet Metrics Strip */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 font-mono text-xs">
            <div className="polar-glass p-4 rounded-xl border border-slate-800 flex items-center justify-between">
              <div>
                <span className="text-slate-400">TOTAL DEPLOYED ASSETS</span>
                <div className="text-xl font-bold text-slate-100 mt-1">{totalCount} Units</div>
              </div>
              <Truck className="w-6 h-6 text-sky-400" />
            </div>

            <div className="polar-glass p-4 rounded-xl border border-emerald-500/30 bg-emerald-950/10 flex items-center justify-between">
              <div>
                <span className="text-emerald-400 font-semibold">AVAILABLE / STANDBY</span>
                <div className="text-xl font-bold text-emerald-300 mt-1">{availableCount} Assets</div>
              </div>
              <CheckCircle2 className="w-6 h-6 text-emerald-400" />
            </div>

            <div className="polar-glass p-4 rounded-xl border border-sky-500/30 bg-sky-950/10 flex items-center justify-between">
              <div>
                <span className="text-sky-400 font-semibold">IN MISSION / TRANSIT</span>
                <div className="text-xl font-bold text-sky-300 mt-1">{inTransitCount} Assets</div>
              </div>
              <Compass className="w-6 h-6 text-sky-400" />
            </div>

            <div className={`polar-glass p-4 rounded-xl border flex items-center justify-between ${
              emergencyCount > 0 ? 'border-amber-500/40 bg-amber-950/20 text-amber-300' : 'border-slate-800'
            }`}>
              <div>
                <span className={emergencyCount > 0 ? 'text-amber-400 font-bold' : 'text-slate-400'}>
                  SAR EMERGENCY DISPATCH
                </span>
                <div className={`text-xl font-bold mt-1 ${emergencyCount > 0 ? 'text-amber-400 animate-pulse' : 'text-slate-100'}`}>
                  {emergencyCount} Units
                </div>
              </div>
              <ShieldAlert className={`w-6 h-6 ${emergencyCount > 0 ? 'text-amber-400' : 'text-slate-600'}`} />
            </div>
          </div>

          {/* Asset Filters Bar */}
          <div className="flex flex-wrap items-center justify-between gap-3 p-3 rounded-xl bg-slate-900/90 border border-slate-800 font-mono text-xs">
            <div className="flex items-center gap-2 text-slate-400 font-semibold">
              <Filter className="w-4 h-4 text-sky-400" />
              <span>FILTER FLEET:</span>
            </div>

            <div className="flex flex-wrap items-center gap-1.5">
              {[
                { id: 'ALL', label: 'All Fleet' },
                { id: 'VEHICLES', label: 'Vehicles' },
                { id: 'AIRCRAFT', label: 'Aircraft' },
                { id: 'AVAILABLE', label: 'Available' },
                { id: 'IN_MISSION', label: 'In Mission' },
                { id: 'EMERGENCY', label: 'SAR Emergency' },
              ].map((f) => (
                <button
                  key={f.id}
                  onClick={() => setFilter(f.id)}
                  className={`px-3 py-1.5 rounded-lg transition ${
                    filter === f.id
                      ? 'bg-sky-500/20 text-sky-300 border border-sky-500/50 font-bold'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                  }`}
                >
                  {f.label}
                </button>
              ))}
            </div>
          </div>

          {/* Operational Fleet Table */}
          <div className="polar-glass rounded-xl border border-slate-800 overflow-hidden">
            <div className="p-4 border-b border-slate-800 flex justify-between items-center">
              <h3 className="text-sm font-bold font-mono text-sky-400 uppercase tracking-wider flex items-center gap-2">
                <Truck className="w-4 h-4" /> Operational Fleet Roster ({filteredAssets.length} Vehicles)
              </h3>
              <span className="text-xs font-mono text-slate-500">
                Scenario {scenarioId} Live Feed
              </span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs font-mono">
                <thead className="bg-slate-900/80 text-slate-400 uppercase border-b border-slate-800">
                  <tr>
                    <th className="p-3">Asset ID / Name</th>
                    <th className="p-3">Type</th>
                    <th className="p-3">Location Coordinates</th>
                    <th className="p-3">Speed / Heading</th>
                    <th className="p-3">Fuel Reserve</th>
                    <th className="p-3">Battery</th>
                    <th className="p-3">Route Progress</th>
                    <th className="p-3">Status</th>
                    <th className="p-3">Field Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {filteredAssets.map((v) => {
                    const isLowFuel = v.fuel_pct < 25;
                    const effectiveStatus = localStatuses[v.id] || v.status;

                    return (
                      <tr key={v.id} className="hover:bg-slate-800/40 transition">
                        <td className="p-3 font-bold text-slate-200">
                          <div>{v.name}</div>
                          <div className="text-[10px] text-slate-500">{v.id}</div>
                        </td>
                        <td className="p-3 text-slate-300">{v.type}</td>
                        <td className="p-3 text-sky-400">
                          {v.latitude.toFixed(4)}°, {v.longitude.toFixed(4)}°
                        </td>
                        <td className="p-3 text-slate-300">
                          {v.speed_kmh} km/h | {v.heading}°
                        </td>
                        <td className="p-3">
                          <div className="flex items-center gap-1.5">
                            <Fuel className={`w-3.5 h-3.5 ${isLowFuel ? 'text-rose-400' : 'text-amber-400'}`} />
                            <span className={`font-bold ${isLowFuel ? 'text-rose-400 font-bold' : 'text-slate-200'}`}>
                              {v.fuel_pct}% ({v.fuel_liters}L)
                            </span>
                          </div>
                        </td>
                        <td className="p-3">
                          <div className="flex items-center gap-1.5">
                            <Battery className="w-3.5 h-3.5 text-emerald-400" />
                            <span>{v.battery_pct}%</span>
                          </div>
                        </td>
                        <td className="p-3">
                          <div className="w-24 bg-slate-800 rounded-full h-2 overflow-hidden mb-1">
                            <div
                              className="bg-sky-500 h-full rounded-full transition-all"
                              style={{ width: `${Math.min(100, v.route_progress_pct)}%` }}
                            />
                          </div>
                          <span className="text-[10px] text-slate-400">{v.route_progress_pct}%</span>
                        </td>
                        <td className="p-3">
                          <StatusBadge
                            status={
                              effectiveStatus === 'AVAILABLE' || effectiveStatus === 'IN_TRANSIT'
                                ? 'nominal'
                                : effectiveStatus === 'DISPATCHED_EMERGENCY'
                                ? 'warning'
                                : 'neutral'
                            }
                            label={effectiveStatus}
                            size="xs"
                          />
                        </td>
                        <td className="p-3">
                          <button
                            onClick={() => handleToggleAssetStatus(v)}
                            className="px-2 py-1 rounded bg-slate-800 hover:bg-slate-700 text-sky-300 border border-slate-700 text-[10px] transition cursor-pointer"
                            title="Toggle local mission status"
                          >
                            Toggle Status
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </PageContainer>
  );
};

export default AssetsPage;
