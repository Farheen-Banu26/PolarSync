import React, { useState, useEffect, useMemo } from 'react';
import PageContainer from '../components/common/PageContainer';
import ScenarioSelector from '../components/common/ScenarioSelector';
import StatusBadge from '../components/common/StatusBadge';
import LoadingState from '../components/common/LoadingState';
import ErrorState from '../components/common/ErrorState';
import CacheIndicator from '../components/common/CacheIndicator';
import { useScenario } from '../context/ScenarioContext';
import { getAlerts } from '../services/api';
import { Bell, AlertTriangle, AlertCircle, Info, ShieldCheck, Filter } from 'lucide-react';

export const AlertsPage = () => {
  const { scenarioId, setScenarioId } = useScenario();
  const [data, setData] = useState(null);
  const [filter, setFilter] = useState('ALL');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchAlerts = async (scId) => {
    setLoading(true);
    setError(null);
    try {
      const res = await getAlerts(scId);
      setData(Array.isArray(res) ? { alerts: res } : res);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed to load alerts');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAlerts(scenarioId);
  }, [scenarioId]);

  // Filter and sort: Critical first, then Warning, then Info
  const filteredAlerts = useMemo(() => {
    if (!data?.alerts) return [];
    let list = [...data.alerts];

    if (filter !== 'ALL') {
      list = list.filter(a => a.severity === filter);
    }

    // Sort order: CRITICAL (0), WARNING (1), INFO (2)
    const severityRank = { CRITICAL: 0, WARNING: 1, INFO: 2 };
    list.sort((a, b) => {
      const rankDiff = (severityRank[a.severity] ?? 3) - (severityRank[b.severity] ?? 3);
      if (rankDiff !== 0) return rankDiff;
      return a.timestamp_tick - b.timestamp_tick;
    });

    return list;
  }, [data, filter]);

  return (
    <PageContainer
      title="Mission Alert & Safety Engine"
      subtitle="Autonomous Rule Engine, Telemetry Outlier Triggers & Multi-Tier Severity Notifications"
      badge="ALERT ENGINE"
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
        <LoadingState message="Extracting mission alert logs from simulation..." />
      ) : error ? (
        <ErrorState message={error} onRetry={() => fetchAlerts(scenarioId)} />
      ) : (
        <div className="space-y-6">
          {/* Summary Strip */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 font-mono text-xs">
            <div className="polar-glass p-4 rounded-xl border border-slate-800 flex items-center justify-between">
              <span className="text-slate-400">TOTAL LOGGED ALERTS</span>
              <span className="text-xl font-bold text-slate-100">{data?.total_alerts || 0}</span>
            </div>
            <div className="polar-glass p-4 rounded-xl border border-rose-500/30 bg-rose-950/10 flex items-center justify-between">
              <span className="text-rose-300 font-semibold">CRITICAL SEVERITY</span>
              <span className="text-xl font-bold text-rose-400">{data?.critical_alerts || 0}</span>
            </div>
            <div className="polar-glass p-4 rounded-xl border border-amber-500/30 bg-amber-950/10 flex items-center justify-between">
              <span className="text-amber-300 font-semibold">WARNING SEVERITY</span>
              <span className="text-xl font-bold text-amber-400">{data?.warning_alerts || 0}</span>
            </div>
          </div>

          {/* Filter Bar */}
          <div className="flex flex-wrap items-center justify-between gap-3 p-3 rounded-xl bg-slate-900/90 border border-slate-800 font-mono text-xs">
            <div className="flex items-center gap-2 text-slate-400 font-semibold">
              <Filter className="w-4 h-4 text-sky-400" />
              <span>SEVERITY FILTER:</span>
            </div>

            <div className="flex items-center gap-1.5">
              {[
                { id: 'ALL', label: `All (${data?.total_alerts || 0})` },
                { id: 'CRITICAL', label: `Critical (${data?.critical_alerts || 0})` },
                { id: 'WARNING', label: `Warning (${data?.warning_alerts || 0})` },
                { id: 'INFO', label: 'Info' },
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

          {/* Alerts Table */}
          <div className="polar-glass rounded-xl border border-slate-800 overflow-hidden">
            <div className="p-4 border-b border-slate-800 flex justify-between items-center">
              <h3 className="text-sm font-bold font-mono text-sky-400 uppercase tracking-wider flex items-center gap-2">
                <Bell className="w-4 h-4" /> Operational Alert Stream ({filteredAlerts.length} Events)
              </h3>
              <span className="text-xs font-mono text-slate-500">
                Scenario {scenarioId} Event Logs (Prioritized)
              </span>
            </div>

            {filteredAlerts.length === 0 ? (
              <div className="p-8 text-center font-mono text-xs text-slate-400">
                <ShieldCheck className="w-8 h-8 text-emerald-400 mx-auto mb-2" />
                No active operational alerts for this filter criteria.
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs font-mono">
                  <thead className="bg-slate-900/80 text-slate-400 uppercase border-b border-slate-800">
                    <tr>
                      <th className="p-3">Alert ID</th>
                      <th className="p-3">Tick / Time</th>
                      <th className="p-3">Severity</th>
                      <th className="p-3">Category</th>
                      <th className="p-3">Source Entity</th>
                      <th className="p-3">Message & Operational Diagnostic</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60">
                    {filteredAlerts.map((a) => {
                      const isCritical = a.severity === 'CRITICAL';
                      const isWarning = a.severity === 'WARNING';

                      return (
                        <tr key={a.id} className={`transition ${
                          isCritical ? 'bg-rose-950/15' : isWarning ? 'bg-amber-950/10' : 'hover:bg-slate-800/40'
                        }`}>
                          <td className="p-3 font-bold text-sky-400">{a.id}</td>
                          <td className="p-3 text-slate-400">T+{a.timestamp_tick}m</td>
                          <td className="p-3">
                            <StatusBadge
                              status={isCritical ? 'critical' : isWarning ? 'warning' : 'info'}
                              label={a.severity}
                              size="xs"
                            />
                          </td>
                          <td className="p-3 text-slate-300 font-semibold">{a.category}</td>
                          <td className="p-3 text-slate-400">{a.source_entity_id || 'SYSTEM'}</td>
                          <td className="p-3 font-medium text-slate-200">
                            <div>{a.message}</div>
                            {a.details && a.details !== a.message && (
                              <div className="text-[11px] text-slate-400 mt-0.5">{String(a.details)}</div>
                            )}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      )}
    </PageContainer>
  );
};

export default AlertsPage;
