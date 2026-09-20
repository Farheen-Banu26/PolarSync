import React, { useState, useEffect } from 'react';
import PageContainer from '../components/common/PageContainer';
import ScenarioSelector from '../components/common/ScenarioSelector';
import StatusBadge from '../components/common/StatusBadge';
import LoadingState from '../components/common/LoadingState';
import ErrorState from '../components/common/ErrorState';
import CacheIndicator from '../components/common/CacheIndicator';
import { useScenario } from '../context/ScenarioContext';
import { useConnectivity } from '../context/ConnectivityContext';
import { getCargo } from '../services/api';
import { Package, ThermometerSnowflake, AlertOctagon, BarChart2, ShieldAlert, CheckCircle2 } from 'lucide-react';

export const CargoPage = () => {
  const { scenarioId, setScenarioId } = useScenario();
  const { performLocalOperation } = useConnectivity();
  const [cargoList, setCargoList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [localStages, setLocalStages] = useState({});

  const fetchCargo = async (scId) => {
    setLoading(true);
    setError(null);
    try {
      const data = await getCargo(scId);
      setCargoList(Array.isArray(data) ? data : (data.cargo || []));
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed to load cargo data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCargo(scenarioId);
  }, [scenarioId]);

  const handleInspectCargo = async (cargo) => {
    const newStage = 'INSPECTED';
    setLocalStages(prev => ({ ...prev, [cargo.id]: newStage }));

    await performLocalOperation('cargo', 'UPDATE_STAGE', {
      cargo_id: cargo.id,
      lifecycle_stage: newStage
    });
  };

  return (
    <PageContainer
      title="Cold-Chain & Cargo Logistics"
      subtitle="Thermal Telemetry, Environmental Monitoring & Lifecycle Progression"
      badge="CARGO PIPELINE"
    >
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <ScenarioSelector
          selectedScenario={scenarioId}
          onSelectScenario={setScenarioId}
          disabled={loading}
        />
        <CacheIndicator isCached={cargoList?._isCached} cachedAt={cargoList?._cachedAt} />
      </div>

      {loading && cargoList.length === 0 ? (
        <LoadingState message="Extracting cold-chain sensor telemetry..." />
      ) : error && cargoList.length === 0 ? (
        <ErrorState message={error} onRetry={() => fetchCargo(scenarioId)} />
      ) : (
        <div className="space-y-6">
          {/* Scenario 4 Breach Alert Banner */}
          {scenarioId === 4 && (
            <div className="p-4 rounded-xl border border-rose-500/40 bg-rose-950/30 text-rose-200 font-mono text-xs flex items-center justify-between gap-4">
              <div className="flex items-center gap-2.5">
                <AlertOctagon className="w-5 h-5 text-rose-400 animate-pulse" />
                <div>
                  <div className="font-bold text-sm text-rose-300">COLD-CHAIN THERMAL BREACH DETECTED</div>
                  <div className="text-[11px] text-slate-300 mt-0.5">
                    Medical sample container active cooling failed, resulting in rapid ambient drift to freezing temperatures below safety threshold (-30.0°C).
                  </div>
                </div>
              </div>
              <StatusBadge status="critical" label="BREACHED_DAMAGED" size="sm" />
            </div>
          )}

          {/* Thermal Envelope & Range Visualization */}
          <div className="polar-glass p-5 rounded-xl border border-slate-800">
            <h3 className="text-sm font-bold font-mono text-sky-400 uppercase tracking-wider mb-4 flex items-center gap-2">
              <BarChart2 className="w-4 h-4" /> Thermal Envelope vs Temperature Sensors
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {cargoList.map((c) => {
                const isBreached = c.condition === 'BREACHED_DAMAGED';
                const isWarning = c.condition === 'WARNING_DRIFT';

                const scaleMin = -45;
                const scaleMax = 0;
                const totalRange = scaleMax - scaleMin;

                const allowedMinPct = Math.max(0, Math.min(100, ((c.min_temp_c - scaleMin) / totalRange) * 100));
                const allowedMaxPct = Math.max(0, Math.min(100, ((c.max_temp_c - scaleMin) / totalRange) * 100));
                const currentTempPct = Math.max(0, Math.min(100, ((c.current_temp_c - scaleMin) / totalRange) * 100));

                return (
                  <div key={c.id} className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 font-mono text-xs">
                    <div className="flex justify-between items-start mb-2">
                      <div>
                        <div className="font-bold text-slate-100 text-sm">{c.name}</div>
                        <div className="text-slate-400 text-[11px]">{c.category} • {c.weight_kg}kg</div>
                      </div>
                      <StatusBadge
                        status={isBreached ? 'critical' : isWarning ? 'warning' : 'nominal'}
                        label={c.condition}
                        size="xs"
                      />
                    </div>

                    <div className="my-3">
                      <div className="flex justify-between text-[11px] mb-1.5">
                        <span className="text-slate-400">Current Temp:</span>
                        <span className={`font-bold text-sm flex items-center gap-1 ${
                          isBreached ? 'text-rose-400' : isWarning ? 'text-amber-400' : 'text-cyan-400'
                        }`}>
                          <ThermometerSnowflake className="w-3.5 h-3.5" />
                          {c.current_temp_c}°C
                        </span>
                      </div>

                      {/* Visual Temperature Envelope Graphic */}
                      <div className="relative w-full h-4 bg-slate-950 rounded-full border border-slate-800 overflow-hidden">
                        <div
                          className="absolute h-full bg-emerald-500/20 border-x border-emerald-500/50"
                          style={{
                            left: `${allowedMinPct}%`,
                            width: `${allowedMaxPct - allowedMinPct}%`
                          }}
                          title={`Safe Range: [${c.min_temp_c}°C, ${c.max_temp_c}°C]`}
                        />
                        <div
                          className={`absolute top-0 bottom-0 w-2 -ml-1 rounded-full shadow-lg ${
                            isBreached ? 'bg-rose-500 ring-2 ring-rose-300' : isWarning ? 'bg-amber-400' : 'bg-cyan-400'
                          }`}
                          style={{ left: `${currentTempPct}%` }}
                        />
                      </div>

                      <div className="flex justify-between text-[10px] text-slate-500 mt-1">
                        <span>-45°C</span>
                        <span className="text-emerald-400">Safe: [{c.min_temp_c}°C to {c.max_temp_c}°C]</span>
                        <span>0°C</span>
                      </div>
                    </div>

                    <div className="pt-2 border-t border-slate-800 flex justify-between text-[11px] text-slate-400">
                      <span>Stage: <strong className="text-sky-300">{localStages[c.id] || c.lifecycle_stage}</strong></span>
                      <span>Carrier: <strong className="text-slate-200">{c.assigned_vehicle_id || 'STATION'}</strong></span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Detailed Cargo Table */}
          <div className="polar-glass rounded-xl border border-slate-800 overflow-hidden">
            <div className="p-4 border-b border-slate-800 flex justify-between items-center">
              <h3 className="text-sm font-bold font-mono text-sky-400 uppercase tracking-wider flex items-center gap-2">
                <Package className="w-4 h-4" /> Manifest & Thermal Sensors ({cargoList.length} Items)
              </h3>
              <span className="text-xs font-mono text-slate-500">
                Scenario {scenarioId} Manifest State
              </span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs font-mono">
                <thead className="bg-slate-900/80 text-slate-400 uppercase border-b border-slate-800">
                  <tr>
                    <th className="p-3">Cargo ID / Name</th>
                    <th className="p-3">Type</th>
                    <th className="p-3">Weight</th>
                    <th className="p-3">Origin → Destination</th>
                    <th className="p-3">Carrier</th>
                    <th className="p-3">Lifecycle Stage</th>
                    <th className="p-3">Current Temp</th>
                    <th className="p-3">Allowed Range</th>
                    <th className="p-3">Thermal Status</th>
                    <th className="p-3">Field Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {cargoList.map((c) => {
                    const isBreached = c.condition === 'BREACHED_DAMAGED';
                    const isWarning = c.condition === 'WARNING_DRIFT';
                    const currentStage = localStages[c.id] || c.lifecycle_stage;

                    return (
                      <tr key={c.id} className="hover:bg-slate-800/40 transition">
                        <td className="p-3 font-bold text-slate-200">
                          <div>{c.name}</div>
                          <div className="text-[10px] text-slate-500">{c.id}</div>
                        </td>
                        <td className="p-3 text-slate-300">{c.category}</td>
                        <td className="p-3 text-slate-400">{c.weight_kg} kg</td>
                        <td className="p-3 text-slate-300 font-semibold">
                          {c.origin_id} → {c.destination_id}
                        </td>
                        <td className="p-3 text-slate-400">{c.assigned_vehicle_id || 'STATION / NONE'}</td>
                        <td className="p-3">
                          <span className="px-2 py-0.5 rounded bg-sky-950 text-sky-300 border border-sky-800 font-bold">
                            {currentStage}
                          </span>
                        </td>
                        <td className="p-3">
                          <div className="flex items-center gap-1.5 font-bold">
                            <ThermometerSnowflake className={`w-3.5 h-3.5 ${isBreached ? 'text-rose-400' : isWarning ? 'text-amber-400' : 'text-cyan-400'}`} />
                            <span className={isBreached ? 'text-rose-400' : isWarning ? 'text-amber-400' : 'text-slate-200'}>
                              {c.current_temp_c}°C
                            </span>
                          </div>
                        </td>
                        <td className="p-3 text-slate-400">
                          [{c.min_temp_c}°C, {c.max_temp_c}°C]
                        </td>
                        <td className="p-3">
                          <StatusBadge
                            status={isBreached ? 'critical' : isWarning ? 'warning' : 'nominal'}
                            label={c.condition}
                            size="xs"
                          />
                        </td>
                        <td className="p-3">
                          <button
                            onClick={() => handleInspectCargo(c)}
                            className="px-2 py-1 rounded bg-slate-800 hover:bg-slate-700 text-sky-300 border border-slate-700 text-[10px] transition cursor-pointer"
                            title="Inspect cargo manifest"
                          >
                            Inspect
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

export default CargoPage;
