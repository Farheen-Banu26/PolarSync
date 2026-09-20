import React, { useState, useEffect } from 'react';
import PageContainer from '../components/common/PageContainer';
import ScenarioSelector from '../components/common/ScenarioSelector';
import StatusBadge from '../components/common/StatusBadge';
import LoadingState from '../components/common/LoadingState';
import ErrorState from '../components/common/ErrorState';
import CacheIndicator from '../components/common/CacheIndicator';
import RiskIndicator from '../components/intelligence/RiskIndicator';
import ExplanationPanel from '../components/intelligence/ExplanationPanel';
import { useScenario } from '../context/ScenarioContext';
import { getEmergencies, getEmergencyIntelligence } from '../services/api';
import { ShieldAlert, Award, Compass, CheckCircle2, AlertOctagon, Clock, LifeBuoy, Zap, BrainCircuit, Check, X } from 'lucide-react';

export const EmergencyPage = () => {
  const { scenarioId, setScenarioId } = useScenario();
  const [data, setData] = useState(null);
  const [intelligence, setIntelligence] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchEmergencyData = async (scId) => {
    setLoading(true);
    setError(null);
    try {
      const [res, intel] = await Promise.all([
        getEmergencies(scId),
        getEmergencyIntelligence(scId)
      ]);
      setData(res);
      setIntelligence(intel);
    } catch (err) {
      console.warn('Failed to load emergency decision intelligence:', err);
      setError(err.response?.data?.detail || err.message || 'Failed to load emergency data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEmergencyData(scenarioId);
  }, [scenarioId]);

  const emergency = data?.emergency;
  const sar = data?.sar_decision;
  const lifecycleStages = ['DETECTED', 'MUSTER', 'DISPATCHED', 'ON_SCENE', 'RESOLVED'];

  return (
    <PageContainer
      title="Emergency Response & SAR Decision Engine"
      subtitle="Autonomous Multi-Criteria Search & Rescue Asset Allocation & Explainable Triage"
      badge="SAR DECISION CORE"
    >
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <ScenarioSelector
          selectedScenario={scenarioId}
          onSelectScenario={setScenarioId}
          disabled={loading}
        />
        <CacheIndicator isCached={data?._isCached} cachedAt={data?._cachedAt} />
      </div>

      {loading ? (
        <LoadingState message="Evaluating multi-criteria SAR asset allocation models..." />
      ) : error ? (
        <ErrorState message={error} onRetry={() => fetchEmergencyData(scenarioId)} />
      ) : !data?.has_active_emergency ? (
        <div className="space-y-6">
          <div className="polar-glass p-8 rounded-xl border border-slate-800 text-center font-mono">
            <CheckCircle2 className="w-12 h-12 text-emerald-400 mx-auto mb-3" />
            <h3 className="text-lg font-bold text-slate-200">No Active Emergency Incidents</h3>
            <p className="text-xs text-slate-400 mt-1 max-w-md mx-auto">
              Scenario {scenarioId} is operating nominally without search & rescue interventions required. Select Scenario 3 to demonstrate SAR incident management.
            </p>
          </div>

          {/* Explainability Block for Nominal Emergency Standby */}
          {intelligence?.explainability && (
            <ExplanationPanel
              explainability={intelligence.explainability}
              title={`Emergency Standby Status — Scenario ${scenarioId}`}
            />
          )}
        </div>
      ) : (
        <div className="space-y-6">
          {/* Active Incident Overview Banner */}
          <div className="polar-glass p-5 rounded-xl border border-rose-500/40 bg-rose-950/20">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-rose-500/30 mb-4">
              <div className="flex items-center gap-2">
                <AlertOctagon className="w-5 h-5 text-rose-400 animate-pulse" />
                <h3 className="text-base font-bold font-mono text-rose-200">
                  INCIDENT {emergency.id}: {emergency.incident_type}
                </h3>
              </div>
              <div className="flex items-center gap-2 font-mono">
                <RiskIndicator level={emergency.severity} size="md" />
                <StatusBadge status={emergency.status === 'RESOLVED' ? 'nominal' : 'critical'} label={emergency.status} size="sm" />
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 text-xs font-mono">
              <div className="p-3 rounded-lg bg-slate-900/80 border border-slate-800">
                <span className="text-slate-500">NEAREST LANDMARK:</span>
                <div className="font-bold text-slate-200 mt-1">{emergency.nearest_landmark}</div>
              </div>
              <div className="p-3 rounded-lg bg-slate-900/80 border border-slate-800">
                <span className="text-slate-500">COORDINATES:</span>
                <div className="font-bold text-sky-400 mt-1">
                  {emergency.latitude.toFixed(4)}°, {emergency.longitude.toFixed(4)}°
                </div>
              </div>
              <div className="p-3 rounded-lg bg-slate-900/80 border border-slate-800">
                <span className="text-slate-500">AFFECTED PERSONNEL:</span>
                <div className="font-bold text-rose-400 mt-1">
                  {emergency.affected_count} ({emergency.affected_personnel_ids?.join(', ')})
                </div>
              </div>
              <div className="p-3 rounded-lg bg-slate-900/80 border border-slate-800">
                <span className="text-slate-500">REQUIRED CAPABILITIES:</span>
                <div className="font-bold text-amber-300 mt-1">
                  {emergency.required_capabilities?.join(', ') || 'N/A'}
                </div>
              </div>
            </div>

            {/* Visual Incident Lifecycle Timeline */}
            <div className="mt-5 pt-4 border-t border-rose-500/20">
              <div className="text-xs font-mono text-slate-400 mb-3 font-semibold">INCIDENT LIFECYCLE PROGRESSION:</div>
              <div className="flex flex-wrap items-center gap-2.5">
                {lifecycleStages.map((st, idx) => {
                  const currentIdx = lifecycleStages.indexOf(emergency.status);
                  const isDone = currentIdx >= idx;
                  const isCurrent = currentIdx === idx;

                  return (
                    <React.Fragment key={idx}>
                      <div className={`flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-mono border ${
                        isCurrent
                          ? 'bg-rose-500/20 text-rose-300 border-rose-500/50 font-bold animate-pulse'
                          : isDone
                          ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40'
                          : 'bg-slate-900 text-slate-500 border-slate-800'
                      }`}>
                        <span className="font-bold">{isDone ? '✓' : '○'}</span>
                        <span>{st}</span>
                      </div>
                      {idx < lifecycleStages.length - 1 && (
                        <span className="text-slate-600 font-mono font-bold">→</span>
                      )}
                    </React.Fragment>
                  );
                })}
              </div>
            </div>
          </div>

          {/* Explainability Block */}
          {intelligence?.explainability && (
            <ExplanationPanel
              explainability={intelligence.explainability}
              title="Emergency Decision Support & Triage Rationale"
            />
          )}

          {/* SAR Multi-Criteria Decision Matrix */}
          {(sar || intelligence?.candidate_assets?.length > 0) && (
            <div className="polar-glass rounded-xl border border-slate-800 overflow-hidden">
              <div className="p-4 border-b border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                <h3 className="text-sm font-bold font-mono text-sky-400 uppercase tracking-wider flex items-center gap-2">
                  <Award className="w-4 h-4 text-amber-400" />
                  Autonomous SAR Multi-Criteria Asset Selection Matrix
                </h3>
                <div className="text-xs font-mono bg-sky-950 px-3 py-1 rounded border border-sky-800 text-sky-200">
                  OPTIMAL ASSET: <strong>{intelligence?.selected_asset_name || sar?.selected_vehicle_name} ({intelligence?.selected_asset_id || sar?.selected_vehicle_id})</strong>
                </div>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs font-mono">
                  <thead className="bg-slate-900/80 text-slate-400 uppercase border-b border-slate-800">
                    <tr>
                      <th className="p-3">Asset Candidate</th>
                      <th className="p-3">Type</th>
                      <th className="p-3">Distance to Target</th>
                      <th className="p-3">Estimated ETA</th>
                      <th className="p-3">Fuel Post-Mission</th>
                      <th className="p-3">Eligibility</th>
                      <th className="p-3">Decision Score</th>
                      <th className="p-3">Selection Explanation</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60">
                    {(intelligence?.candidate_assets || sar?.evaluations || []).map((ev) => {
                      const isWinner = ev.vehicle_id === (intelligence?.selected_asset_id || sar?.selected_vehicle_id);

                      return (
                        <tr key={ev.vehicle_id} className={`transition ${
                          isWinner ? 'bg-sky-500/10 border-l-4 border-sky-400' : 'hover:bg-slate-800/40'
                        }`}>
                          <td className="p-3 font-bold text-slate-200">
                            <div>{ev.vehicle_name}</div>
                            <div className="text-[10px] text-slate-500">{ev.vehicle_id}</div>
                          </td>
                          <td className="p-3 text-slate-300">{ev.vehicle_type}</td>
                          <td className="p-3 text-sky-400 font-bold">{ev.distance_km} km</td>
                          <td className="p-3 text-slate-200">{ev.estimated_transit_time_min} min</td>
                          <td className="p-3 text-slate-300">{ev.fuel_after_mission_pct}%</td>
                          <td className="p-3">
                            <StatusBadge
                              status={ev.is_eligible ? 'nominal' : 'critical'}
                              label={ev.is_eligible ? 'ELIGIBLE' : 'DISQUALIFIED'}
                              size="xs"
                            />
                          </td>
                          <td className="p-3 font-bold text-sm text-sky-300">
                            {ev.score > 0 ? ev.score : 'N/A'}
                          </td>
                          <td className="p-3 text-slate-400 max-w-xs">
                            {isWinner ? (
                              <span className="text-emerald-400 font-bold flex items-center gap-1">
                                <Zap className="w-3.5 h-3.5 flex-shrink-0" />
                                SELECTED: Optimal speed & capability match
                              </span>
                            ) : ev.disqualification_reasons?.length > 0 ? (
                              <span className="text-rose-400">{ev.disqualification_reasons.join('; ')}</span>
                            ) : (
                              <span>Higher transit latency / sub-optimal score</span>
                            )}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}
    </PageContainer>
  );
};

export default EmergencyPage;
