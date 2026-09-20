import React, { useState, useEffect } from 'react';
import PageContainer from '../components/common/PageContainer';
import ScenarioSelector from '../components/common/ScenarioSelector';
import StatusBadge from '../components/common/StatusBadge';
import LoadingState from '../components/common/LoadingState';
import ErrorState from '../components/common/ErrorState';
import CacheIndicator from '../components/common/CacheIndicator';
import { useScenario } from '../context/ScenarioContext';
import { useConnectivity } from '../context/ConnectivityContext';
import { getPersonnel } from '../services/api';
import { Users, Heart, MapPin, AlertCircle, CheckCircle2, UserCheck, ShieldAlert, Check } from 'lucide-react';

export const PersonnelPage = () => {
  const { scenarioId, setScenarioId } = useScenario();
  const { performLocalOperation } = useConnectivity();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [localStatuses, setLocalStatuses] = useState({});

  const fetchPersonnel = async (scId) => {
    setLoading(true);
    setError(null);
    try {
      const res = await getPersonnel(scId);
      setData(res);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed to load personnel data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPersonnel(scenarioId);
  }, [scenarioId]);

  const handleToggleCheckin = async (person) => {
    const currentStatus = localStatuses[person.id] || person.status;
    const newStatus = currentStatus === 'CHECKED_IN' || currentStatus === 'OK' ? 'UNCONFIRMED_DUE' : 'CHECKED_IN';
    
    setLocalStatuses(prev => ({ ...prev, [person.id]: newStatus }));
    
    // Enqueue offline operation
    await performLocalOperation('personnel', 'UPDATE_CHECKIN', {
      personnel_id: person.id,
      status: newStatus
    });
  };

  const muster = data?.muster_summary;

  return (
    <PageContainer
      title="Personnel Movement & Muster Tracking"
      subtitle="Expedition Roster, Location Telemetry, Vital Signs & Autonomous Muster Roll-Call"
      badge="PERSONNEL OPERATIONS"
    >
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <ScenarioSelector
          selectedScenario={scenarioId}
          onSelectScenario={setScenarioId}
          disabled={loading}
        />
        <CacheIndicator isCached={data?._isCached} cachedAt={data?._cachedAt} />
      </div>

      {loading && !data ? (
        <LoadingState message="Extracting personnel muster roll-call from simulation..." />
      ) : error && !data ? (
        <ErrorState message={error} onRetry={() => fetchPersonnel(scenarioId)} />
      ) : (
        <div className="space-y-6">
          {/* Muster Summary Banner */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 font-mono text-xs">
            <div className="polar-glass p-4 rounded-xl border border-slate-800 flex items-center justify-between">
              <div>
                <span className="text-slate-400">TOTAL EXPEDITION ROSTER</span>
                <div className="text-xl font-bold text-slate-100 mt-1">{data?.personnel?.length || 25} Members</div>
              </div>
              <Users className="w-6 h-6 text-sky-400" />
            </div>

            <div className="polar-glass p-4 rounded-xl border border-emerald-500/30 bg-emerald-950/10 flex items-center justify-between">
              <div>
                <span className="text-emerald-400 font-semibold">BASE / CHECKED-IN</span>
                <div className="text-xl font-bold text-emerald-300 mt-1">
                  {muster ? muster.checked_in_count : data?.personnel?.length || 25} Accounted
                </div>
              </div>
              <UserCheck className="w-6 h-6 text-emerald-400" />
            </div>

            <div className="polar-glass p-4 rounded-xl border border-sky-500/30 bg-sky-950/10 flex items-center justify-between">
              <div>
                <span className="text-sky-400 font-semibold">FIELD OPERATIONS</span>
                <div className="text-xl font-bold text-sky-300 mt-1">
                  {muster ? muster.field_count : 0} in Field
                </div>
              </div>
              <MapPin className="w-6 h-6 text-sky-400" />
            </div>

            <div className={`polar-glass p-4 rounded-xl border flex items-center justify-between ${
              muster && muster.unconfirmed_count > 0
                ? 'border-rose-500/40 bg-rose-950/20 text-rose-300'
                : 'border-slate-800'
            }`}>
              <div>
                <span className={muster && muster.unconfirmed_count > 0 ? 'text-rose-400 font-bold' : 'text-slate-400'}>
                  UNCONFIRMED / MISSING
                </span>
                <div className={`text-xl font-bold mt-1 ${muster && muster.unconfirmed_count > 0 ? 'text-rose-400 animate-pulse' : 'text-slate-100'}`}>
                  {muster ? muster.unconfirmed_count : 0} Personnel
                </div>
              </div>
              <ShieldAlert className={`w-6 h-6 ${muster && muster.unconfirmed_count > 0 ? 'text-rose-400' : 'text-slate-600'}`} />
            </div>
          </div>

          {/* Unconfirmed Alert Details if Scenario 3 or active missing */}
          {muster && muster.unconfirmed_count > 0 && (
            <div className="p-4 rounded-xl border border-rose-500/40 bg-rose-950/30 text-rose-200 font-mono text-xs">
              <div className="flex items-center gap-2 font-bold text-sm mb-1 text-rose-300">
                <AlertCircle className="w-4 h-4 text-rose-400" />
                <span>ACTIVE MUSTER ROLL-CALL FLAG: {muster.unconfirmed_count} UNCONFIRMED</span>
              </div>
              <p className="text-slate-300 text-[11px]">
                Autonomous muster triage detected missing heartbeat signals. Flagged Personnel IDs:{' '}
                <strong className="text-rose-300 font-mono">{muster.unconfirmed_ids?.join(', ')}</strong>.
                Dispatched SAR asset has resolved the distress and restored vitals telemetry.
              </p>
            </div>
          )}

          {/* Personnel Table */}
          <div className="polar-glass rounded-xl border border-slate-800 overflow-hidden">
            <div className="p-4 border-b border-slate-800 flex justify-between items-center">
              <h3 className="text-sm font-bold font-mono text-sky-400 uppercase tracking-wider flex items-center gap-2">
                <Users className="w-4 h-4" /> Expedition Roster ({data?.personnel?.length || 0} Members)
              </h3>
              <span className="text-xs font-mono text-slate-500">
                Scenario {scenarioId} Live Roll-Call
              </span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs font-mono">
                <thead className="bg-slate-900/80 text-slate-400 uppercase border-b border-slate-800">
                  <tr>
                    <th className="p-3">Personnel ID</th>
                    <th className="p-3">Name</th>
                    <th className="p-3">Role</th>
                    <th className="p-3">Location</th>
                    <th className="p-3">Current Coordinates</th>
                    <th className="p-3">Movement</th>
                    <th className="p-3">Heartbeat</th>
                    <th className="p-3">Vehicle</th>
                    <th className="p-3">Muster State</th>
                    <th className="p-3">Field Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {data?.personnel?.map((p) => {
                    const effectiveStatus = localStatuses[p.id] || p.status;
                    const isEmergency = effectiveStatus === 'AFFECTED_EMERGENCY' || effectiveStatus === 'UNCONFIRMED_DUE';

                    return (
                      <tr key={p.id} className={`transition ${
                        isEmergency ? 'bg-rose-950/20' : 'hover:bg-slate-800/40'
                      }`}>
                        <td className="p-3 font-bold text-sky-400">{p.id}</td>
                        <td className="p-3 font-semibold text-slate-200">{p.name}</td>
                        <td className="p-3 text-slate-300">{p.role}</td>
                        <td className="p-3 text-slate-300">{p.assigned_location_id}</td>
                        <td className="p-3 text-slate-400">
                          {p.latitude ? `${p.latitude.toFixed(4)}°, ${p.longitude.toFixed(4)}°` : 'Station Grid'}
                        </td>
                        <td className="p-3 text-slate-300">{p.movement_status}</td>
                        <td className="p-3">
                          <div className="flex items-center gap-1.5">
                            <Heart className={`w-3.5 h-3.5 ${p.heartbeat_active ? 'text-rose-500 animate-pulse' : 'text-slate-600'}`} />
                            <span className={p.heartbeat_active ? 'text-emerald-400 font-bold' : 'text-slate-500 font-bold'}>
                              {p.heartbeat_active ? 'ACTIVE' : 'LOST'}
                            </span>
                          </div>
                        </td>
                        <td className="p-3 text-slate-400">{p.assigned_vehicle_id || 'STATION / NONE'}</td>
                        <td className="p-3">
                          <StatusBadge
                            status={
                              effectiveStatus === 'OK' || effectiveStatus === 'ACTIVE' || effectiveStatus === 'CHECKED_IN'
                                ? 'nominal'
                                : isEmergency
                                ? 'critical'
                                : 'neutral'
                            }
                            label={effectiveStatus}
                            size="xs"
                          />
                        </td>
                        <td className="p-3">
                          <button
                            onClick={() => handleToggleCheckin(p)}
                            className="px-2 py-1 rounded bg-slate-800 hover:bg-slate-700 text-sky-300 border border-slate-700 text-[10px] transition cursor-pointer"
                            title="Toggle local check-in"
                          >
                            Check-In
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

export default PersonnelPage;
