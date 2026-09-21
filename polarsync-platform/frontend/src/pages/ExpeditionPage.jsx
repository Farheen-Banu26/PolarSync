import React, { useState, useEffect } from 'react';
import PageContainer from '../components/common/PageContainer';
import ScenarioSelector from '../components/common/ScenarioSelector';
import StatusBadge from '../components/common/StatusBadge';
import LoadingState from '../components/common/LoadingState';
import ErrorState from '../components/common/ErrorState';
import CacheIndicator from '../components/common/CacheIndicator';
import PolarMap from '../components/gis/PolarMap';
import { useScenario } from '../context/ScenarioContext';
import { getScenarioSummary, getMapTopology, getCargo, getAssets } from '../services/api';
import { Compass, MapPin, Route as RouteIcon, Shield, Clock, Truck, Package, Users } from 'lucide-react';

export const ExpeditionPage = () => {
  const { scenarioId, setScenarioId } = useScenario();
  const [summary, setSummary] = useState(null);
  const [mapData, setMapData] = useState(null);
  const [cargoList, setCargoList] = useState([]);
  const [assetsList, setAssetsList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = async (scId) => {
    setLoading(true);
    setError(null);
    try {
      const [sumRes, mapRes, cargoRes, assetsRes] = await Promise.all([
        getScenarioSummary(scId),
        getMapTopology(scId),
        getCargo(scId),
        getAssets(scId)
      ]);
      setSummary(sumRes);
      setMapData(mapRes);
      setCargoList(cargoRes.cargo || []);
      setAssetsList(assetsRes.assets || []);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed to load expedition planning data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData(scenarioId);
  }, [scenarioId]);

  return (
    <PageContainer
      title="Expedition Planning & Route Topology"
      subtitle="Geospatial Traverse Waypoints, Field Camps, Asset Assignments & Logistics Movements"
      badge="EXPEDITION OVERVIEW"
    >
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <ScenarioSelector
          selectedScenario={scenarioId}
          onSelectScenario={setScenarioId}
          disabled={loading}
        />
        <CacheIndicator isCached={summary?._isCached} cachedAt={summary?._cachedAt} />
      </div>

      {loading ? (
        <LoadingState message="Loading expedition topology and logistics manifests..." />
      ) : error ? (
        <ErrorState message={error} onRetry={() => fetchData(scenarioId)} />
      ) : (
        <div className="space-y-6">
          {/* Mission Overview */}
          <div className="polar-glass p-5 rounded-xl border border-slate-800">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-800 mb-4">
              <div>
                <h3 className="text-base font-bold font-mono text-slate-100">{summary?.name}</h3>
                <p className="text-xs text-slate-400 mt-0.5">{summary?.description}</p>
              </div>
              <StatusBadge
                status={summary?.readiness_status === 'EXCELLENT' ? 'nominal' : 'warning'}
                label={`READINESS: ${summary?.readiness_status}`}
                size="sm"
              />
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs font-mono">
              <div className="p-3 rounded-lg bg-slate-900/80 border border-slate-800">
                <span className="text-slate-500">SIMULATION HORIZON:</span>
                <div className="font-bold text-slate-200 mt-1">{summary?.total_ticks} Ticks ({summary?.minutes_simulated} min)</div>
              </div>
              <div className="p-3 rounded-lg bg-slate-900/80 border border-slate-800">
                <span className="text-slate-500">DETERMINISTIC SEED:</span>
                <div className="font-bold text-sky-400 mt-1">Seed #{summary?.random_seed}</div>
              </div>
              <div className="p-3 rounded-lg bg-slate-900/80 border border-slate-800">
                <span className="text-slate-500">DEPLOYED ASSETS:</span>
                <div className="font-bold text-slate-200 mt-1">{summary?.vehicles_count} Vehicles</div>
              </div>
              <div className="p-3 rounded-lg bg-slate-900/80 border border-slate-800">
                <span className="text-slate-500">EXPEDITION MEMBERS:</span>
                <div className="font-bold text-slate-200 mt-1">{summary?.personnel_count} Personnel</div>
              </div>
            </div>
          </div>

          {/* Route Map */}
          <div>
            <div className="flex items-center gap-2 mb-2 font-mono text-xs text-sky-400 font-bold uppercase">
              <Compass className="w-4 h-4" /> Traverse Corridors & Waypoints Map
            </div>
            <PolarMap
              locations={mapData?.locations || []}
              dangerZones={mapData?.danger_zones || []}
              routes={mapData?.routes || []}
              assets={mapData?.assets || []}
              personnel={mapData?.personnel || []}
              emergency={mapData?.emergency || null}
              height="620px"
            />
          </div>

          {/* Operational Locations & Route Overview Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Operational Locations */}
            <div className="polar-glass p-5 rounded-xl border border-slate-800">
              <h3 className="text-sm font-bold font-mono text-sky-400 uppercase tracking-wider mb-4 flex items-center gap-2">
                <MapPin className="w-4 h-4" /> Operational Locations ({mapData?.locations?.length || 0} Facilities)
              </h3>

              <div className="space-y-3 font-mono text-xs">
                {mapData?.locations?.map((loc) => (
                  <div key={loc.id} className="p-3 rounded-lg bg-slate-900/80 border border-slate-800">
                    <div className="flex items-center justify-between font-bold text-slate-200">
                      <span>{loc.name}</span>
                      <span className="text-sky-400 text-[11px]">{loc.type}</span>
                    </div>
                    <div className="text-slate-400 mt-1">
                      Coordinates: {loc.latitude.toFixed(4)}°, {loc.longitude.toFixed(4)}° | Elevation: {loc.elevation_m}m
                    </div>
                    {loc.facilities?.length > 0 && (
                      <div className="text-[11px] text-slate-500 mt-1">
                        Station Facilities: {loc.facilities.join(', ')}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Traverse Routes & Waypoints */}
            <div className="polar-glass p-5 rounded-xl border border-slate-800">
              <h3 className="text-sm font-bold font-mono text-sky-400 uppercase tracking-wider mb-4 flex items-center gap-2">
                <RouteIcon className="w-4 h-4" /> Traverse Corridors & Distance Matrix
              </h3>

              <div className="space-y-4 font-mono text-xs">
                <div className="space-y-2.5">
                  {mapData?.routes?.map((r) => (
                    <div key={r.id} className="p-3 rounded-lg bg-slate-900/80 border border-slate-800">
                      <div className="flex justify-between items-center font-bold text-slate-200">
                        <span>{r.name}</span>
                        <span className="text-sky-400">{r.distance_km} km</span>
                      </div>
                      <div className="text-[11px] text-slate-400 mt-1">
                        Corridor: {r.origin_id} → {r.destination_id} ({r.waypoints?.length || 0} Navigation Waypoints)
                      </div>
                    </div>
                  ))}
                </div>

                <div className="pt-2 border-t border-slate-800">
                  <div className="text-slate-400 text-[11px] font-bold mb-2">PROJECTED DANGER ZONES ON ROUTE:</div>
                  <div className="space-y-2">
                    {mapData?.danger_zones?.map((dz) => (
                      <div key={dz.id} className="p-2.5 rounded bg-slate-900/80 border border-rose-500/20 flex justify-between items-center">
                        <div>
                          <div className="text-rose-300 font-bold">{dz.name} ({dz.type})</div>
                          <div className="text-[10px] text-slate-500">Radius: {dz.radius_km} km • Severity: {dz.severity}</div>
                        </div>
                        <StatusBadge
                          status={dz.severity === 'CRITICAL' ? 'critical' : 'warning'}
                          label={dz.severity}
                          size="xs"
                        />
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Assigned Assets & Cargo Movements Strip */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 font-mono text-xs">
            {/* Assigned Fleet */}
            <div className="polar-glass p-5 rounded-xl border border-slate-800">
              <h3 className="text-sm font-bold text-sky-400 uppercase tracking-wider mb-3 flex items-center gap-2">
                <Truck className="w-4 h-4" /> Assigned Assets ({assetsList.length} Vehicles)
              </h3>
              <div className="space-y-2">
                {assetsList.map((a) => (
                  <div key={a.id} className="p-2.5 rounded bg-slate-900/80 border border-slate-800 flex justify-between items-center">
                    <div>
                      <span className="font-bold text-slate-200">{a.name}</span>
                      <span className="text-slate-500 text-[10px] ml-2">({a.type})</span>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className="text-slate-400">Fuel: {a.fuel_pct}%</span>
                      <StatusBadge
                        status={a.status === 'AVAILABLE' ? 'nominal' : 'warning'}
                        label={a.status}
                        size="xs"
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Cargo Manifest Movements */}
            <div className="polar-glass p-5 rounded-xl border border-slate-800">
              <h3 className="text-sm font-bold text-sky-400 uppercase tracking-wider mb-3 flex items-center gap-2">
                <Package className="w-4 h-4" /> Logistics Manifest ({cargoList.length} Payloads)
              </h3>
              <div className="space-y-2">
                {cargoList.map((c) => (
                  <div key={c.id} className="p-2.5 rounded bg-slate-900/80 border border-slate-800 flex justify-between items-center">
                    <div>
                      <span className="font-bold text-slate-200">{c.name}</span>
                      <span className="text-slate-500 text-[10px] ml-2">{c.origin_id} → {c.destination_id}</span>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className="text-slate-400">{c.current_temp_c}°C</span>
                      <StatusBadge
                        status={c.condition === 'BREACHED_DAMAGED' ? 'critical' : 'nominal'}
                        label={c.lifecycle_stage}
                        size="xs"
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </PageContainer>
  );
};

export default ExpeditionPage;
