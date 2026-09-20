import React, { useState, useEffect } from 'react';
import PageContainer from '../components/common/PageContainer';
import ScenarioSelector from '../components/common/ScenarioSelector';
import StatusBadge from '../components/common/StatusBadge';
import LoadingState from '../components/common/LoadingState';
import ErrorState from '../components/common/ErrorState';
import { useScenario } from '../context/ScenarioContext';
import { useConnectivity } from '../context/ConnectivityContext';
import { getConnectivity } from '../services/api';
import {
  Radio,
  Database,
  CheckCircle2,
  HardDriveDownload,
  Server,
  RefreshCw,
  AlertCircle,
  Clock,
  Layers,
  Trash2,
  Send,
  Wifi,
  WifiOff
} from 'lucide-react';

export const ConnectivityPage = () => {
  const { scenarioId, setScenarioId } = useScenario();
  const {
    networkStatus,
    isOnline,
    queue,
    pendingCount,
    cachedMeta,
    cacheCount,
    lastSyncResult,
    lastSyncTimestamp,
    syncNow,
    clearSyncedOperations,
    setSimulatedOffline,
    refreshStorageStats
  } = useConnectivity();

  const [simData, setSimData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [syncingManual, setSyncingManual] = useState(false);
  const [syncMessage, setSyncMessage] = useState(null);

  const fetchSimConnectivity = async (scId) => {
    setLoading(true);
    setError(null);
    try {
      const res = await getConnectivity(scId);
      setSimData(res);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed to load connectivity status');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSimConnectivity(scenarioId);
    refreshStorageStats();
  }, [scenarioId, refreshStorageStats]);

  const handleSyncClick = async () => {
    setSyncingManual(true);
    setSyncMessage(null);
    try {
      const res = await syncNow();
      setSyncMessage({
        type: res.rejected?.length > 0 ? 'warning' : 'success',
        text: `Sync finished: ${res.accepted?.length || 0} accepted, ${res.rejected?.length || 0} rejected.`
      });
    } catch (err) {
      setSyncMessage({
        type: 'error',
        text: `Sync failed: ${err.message || 'Server offline'}`
      });
    } finally {
      setSyncingManual(false);
    }
  };

  return (
    <PageContainer
      title="Satellite Uplink & Offline Synchronization"
      subtitle="Iridium Satellite Blackout Resilience, Local IndexedDB Storage & Opportunistic Reconciliation"
      badge="FIELD CONNECTIVITY"
    >
      <div className="mb-6">
        <ScenarioSelector
          selectedScenario={scenarioId}
          onSelectScenario={setScenarioId}
          disabled={loading}
        />
      </div>

      {loading && !simData ? (
        <LoadingState message="Extracting satellite queue synchronization metrics..." />
      ) : error && !simData ? (
        <ErrorState message={error} onRetry={() => fetchSimConnectivity(scenarioId)} />
      ) : (
        <div className="space-y-6">
          {/* Top Status Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 font-mono text-xs">
            {/* Network State */}
            <div className="polar-glass p-5 rounded-xl border border-slate-800 flex flex-col justify-between">
              <div>
                <span className="text-slate-400 uppercase">System Network Mode</span>
                <div className="flex items-center gap-2 mt-2">
                  {networkStatus === 'OFFLINE' ? (
                    <WifiOff className="w-5 h-5 text-amber-400" />
                  ) : (
                    <Wifi className="w-5 h-5 text-emerald-400" />
                  )}
                  <span className="text-xl font-bold text-slate-100">{networkStatus}</span>
                </div>
              </div>
              <div className="mt-3 pt-2 border-t border-slate-800 flex items-center justify-between text-[11px]">
                <span className="text-slate-500">Physical Link:</span>
                <span className={isOnline ? 'text-emerald-400' : 'text-amber-400'}>
                  {isOnline ? 'ESTABLISHED' : 'DISCONNECTED'}
                </span>
              </div>
            </div>

            {/* Offline IndexedDB Cache */}
            <div className="polar-glass p-5 rounded-xl border border-slate-800 flex flex-col justify-between">
              <div>
                <span className="text-slate-400 uppercase">Local IndexedDB Cache</span>
                <div className="flex items-center gap-2 mt-2">
                  <Database className="w-5 h-5 text-sky-400" />
                  <span className="text-xl font-bold text-slate-100">{cacheCount} Datasets</span>
                </div>
              </div>
              <div className="mt-3 pt-2 border-t border-slate-800 flex items-center justify-between text-[11px]">
                <span className="text-slate-500">Database:</span>
                <span className="text-sky-300 font-bold">polarsync-offline</span>
              </div>
            </div>

            {/* Local Sync Queue Pending */}
            <div className="polar-glass p-5 rounded-xl border border-slate-800 flex flex-col justify-between">
              <div>
                <span className="text-slate-400 uppercase">Local Queue Pending</span>
                <div className="flex items-center gap-2 mt-2">
                  <HardDriveDownload className={`w-5 h-5 ${pendingCount > 0 ? 'text-amber-400' : 'text-slate-400'}`} />
                  <span className={`text-xl font-bold ${pendingCount > 0 ? 'text-amber-300' : 'text-slate-100'}`}>
                    {pendingCount} Changes
                  </span>
                </div>
              </div>
              <div className="mt-3 pt-2 border-t border-slate-800 flex items-center justify-between text-[11px]">
                <span className="text-slate-500">Total Enqueued:</span>
                <span className="text-slate-300">{queue.length} ops</span>
              </div>
            </div>

            {/* Simulator Blackout Frame Stream */}
            <div className="polar-glass p-5 rounded-xl border border-slate-800 flex flex-col justify-between">
              <div>
                <span className="text-slate-400 uppercase">Telemetry Replay Engine</span>
                <div className="flex items-center gap-2 mt-2">
                  <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                  <span className="text-xl font-bold text-slate-100">
                    {simData?.synchronized_event_count || 0} / {simData?.buffered_event_count || 0} Frames
                  </span>
                </div>
              </div>
              <div className="mt-3 pt-2 border-t border-slate-800 flex items-center justify-between text-[11px]">
                <span className="text-slate-500">Sim Link Status:</span>
                <span className="text-slate-300 font-bold">{simData?.network_status}</span>
              </div>
            </div>
          </div>

          {/* Sync Queue Manager Panel */}
          <div className="polar-glass rounded-xl border border-slate-800 overflow-hidden">
            <div className="p-4 border-b border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div>
                <h3 className="text-sm font-bold font-mono text-sky-400 uppercase tracking-wider flex items-center gap-2">
                  <Server className="w-4 h-4" /> Offline Change Queue & Reconciliation
                </h3>
                <p className="text-xs font-mono text-slate-400 mt-0.5">
                  Local field updates queued in IndexedDB for upload to FastAPI when network is restored.
                </p>
              </div>

              <div className="flex items-center gap-2 font-mono text-xs">
                <button
                  onClick={handleSyncClick}
                  disabled={syncingManual || networkStatus === 'SYNCING'}
                  className="px-3.5 py-1.5 rounded-lg bg-sky-500/20 hover:bg-sky-500/30 text-sky-200 border border-sky-500/40 font-semibold transition cursor-pointer flex items-center gap-1.5"
                >
                  <RefreshCw className={`w-3.5 h-3.5 ${syncingManual ? 'animate-spin' : ''}`} />
                  <span>Sync Now ({pendingCount})</span>
                </button>

                {queue.some(q => q.status === 'SYNCED') && (
                  <button
                    onClick={clearSyncedOperations}
                    className="px-3 py-1.5 rounded-lg bg-slate-800/80 hover:bg-slate-700 text-slate-400 hover:text-slate-200 border border-slate-700 transition cursor-pointer flex items-center gap-1"
                    title="Clear Synced Operations from Log"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                    <span>Clear Synced</span>
                  </button>
                )}
              </div>
            </div>

            {/* Sync status feedback notification */}
            {syncMessage && (
              <div className={`px-4 py-2 text-xs font-mono border-b ${
                syncMessage.type === 'error'
                  ? 'bg-rose-950/40 border-rose-500/40 text-rose-300'
                  : syncMessage.type === 'warning'
                  ? 'bg-amber-950/40 border-amber-500/40 text-amber-300'
                  : 'bg-emerald-950/40 border-emerald-500/40 text-emerald-300'
              }`}>
                {syncMessage.text}
              </div>
            )}

            {queue.length === 0 ? (
              <div className="p-8 text-center font-mono text-xs text-slate-400">
                <CheckCircle2 className="w-8 h-8 text-emerald-400 mx-auto mb-2" />
                No local actions in queue. All field operations are synchronized with the server.
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs font-mono">
                  <thead className="bg-slate-900/80 text-slate-400 uppercase border-b border-slate-800">
                    <tr>
                      <th className="p-3">Operation ID</th>
                      <th className="p-3">Timestamp</th>
                      <th className="p-3">Resource</th>
                      <th className="p-3">Action</th>
                      <th className="p-3">Payload Details</th>
                      <th className="p-3">Retries</th>
                      <th className="p-3">Queue Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60">
                    {queue.map((op) => {
                      const isPending = op.status === 'PENDING';
                      const isFailed = op.status === 'FAILED';
                      const isSynced = op.status === 'SYNCED';

                      return (
                        <tr key={op.id} className="hover:bg-slate-800/40 transition">
                          <td className="p-3 font-bold text-sky-400">{op.id}</td>
                          <td className="p-3 text-slate-400">
                            {new Date(op.timestamp).toLocaleTimeString()}
                          </td>
                          <td className="p-3 font-semibold text-slate-300 uppercase">{op.resource}</td>
                          <td className="p-3 text-amber-300">{op.operation}</td>
                          <td className="p-3 text-slate-300 max-w-xs truncate">
                            <code>{JSON.stringify(op.payload)}</code>
                            {op.error_message && (
                              <div className="text-[10px] text-rose-400 mt-0.5 font-sans">
                                ⚠ {op.error_message}
                              </div>
                            )}
                          </td>
                          <td className="p-3 text-slate-400">{op.retry_count || 0}</td>
                          <td className="p-3">
                            <StatusBadge
                              status={isSynced ? 'nominal' : isFailed ? 'critical' : 'warning'}
                              label={op.status}
                              size="xs"
                            />
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          {/* 6-Phase Connectivity Timeline */}
          <div className="polar-glass p-6 rounded-xl border border-slate-800">
            <h3 className="text-sm font-bold font-mono text-sky-400 uppercase tracking-wider mb-4 flex items-center gap-2">
              <Clock className="w-4 h-4" /> Operational Offline-to-Online Lifecycle
            </h3>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-6 gap-3 text-xs font-mono">
              <div className="p-3.5 rounded-lg bg-slate-900/90 border border-slate-800 flex flex-col justify-between">
                <div className="text-slate-500 font-bold">STAGE 1</div>
                <div className="font-semibold text-emerald-400 mt-2">CONNECTED</div>
                <div className="text-[11px] text-slate-400 mt-1">Live streaming & cache updates</div>
              </div>

              <div className="p-3.5 rounded-lg bg-slate-900/90 border border-slate-800 flex flex-col justify-between">
                <div className="text-slate-500 font-bold">STAGE 2</div>
                <div className="font-semibold text-rose-400 mt-2">NETWORK LOST</div>
                <div className="text-[11px] text-slate-400 mt-1">Blackout detected by client</div>
              </div>

              <div className="p-3.5 rounded-lg bg-slate-900/90 border border-slate-800 flex flex-col justify-between">
                <div className="text-slate-500 font-bold">STAGE 3</div>
                <div className="font-semibold text-amber-400 mt-2">LOCAL CACHE ACTIVE</div>
                <div className="text-[11px] text-slate-400 mt-1">IndexedDB serves operational data</div>
              </div>

              <div className="p-3.5 rounded-lg bg-slate-900/90 border border-slate-800 flex flex-col justify-between">
                <div className="text-slate-500 font-bold">STAGE 4</div>
                <div className="font-semibold text-sky-400 mt-2">CHANGES QUEUED</div>
                <div className="text-[11px] text-slate-400 mt-1">Local actions entered into queue</div>
              </div>

              <div className="p-3.5 rounded-lg bg-slate-900/90 border border-slate-800 flex flex-col justify-between">
                <div className="text-slate-500 font-bold">STAGE 5</div>
                <div className="font-semibold text-sky-400 mt-2">NETWORK RESTORED</div>
                <div className="text-[11px] text-slate-400 mt-1">Uplink handshake re-established</div>
              </div>

              <div className="p-3.5 rounded-lg bg-slate-900/90 border border-slate-800 flex flex-col justify-between">
                <div className="text-slate-500 font-bold">STAGE 6</div>
                <div className="font-semibold text-emerald-400 mt-2">SYNC COMPLETE</div>
                <div className="text-[11px] text-slate-400 mt-1">FIFO batch reconciled on server</div>
              </div>
            </div>
          </div>
        </div>
      )}
    </PageContainer>
  );
};

export default ConnectivityPage;
