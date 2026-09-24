import React, { useState, useEffect } from 'react';
import { Shield, Clock, Filter, User, Activity, CheckCircle, RefreshCw } from 'lucide-react';
import { getAuditLogs } from '../../services/api';
import StatusBadge from './StatusBadge';

export const AuditLogViewer = ({ limit = 30 }) => {
  const [logs, setLogs] = useState([]);
  const [filterType, setFilterType] = useState('ALL');
  const [loading, setLoading] = useState(true);

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const entityParam = filterType === 'ALL' ? null : filterType;
      const data = await getAuditLogs(limit, entityParam);
      setLogs(Array.isArray(data) ? data : []);
    } catch (err) {
      console.warn('Failed to fetch audit logs:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, [filterType]);

  return (
    <div className="polar-glass p-5 rounded-xl border border-slate-800 font-mono text-xs">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-800 mb-4">
        <div className="flex items-center gap-2">
          <Shield className="w-4 h-4 text-sky-400" />
          <h3 className="text-sm font-bold text-slate-100 uppercase tracking-wider">
            Operational Audit Trail & Intervention Log
          </h3>
        </div>

        <div className="flex items-center gap-2">
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="p-1.5 rounded bg-slate-900 border border-slate-700 text-slate-200 text-[11px]"
          >
            <option value="ALL">All Event Types</option>
            <option value="ROUTE">Routes & Corridors</option>
            <option value="CARGO">Cargo Movements</option>
            <option value="SAR">SAR & Emergencies</option>
            <option value="PERSONNEL">Personnel Muster</option>
            <option value="ALERT">Alert Actions</option>
            <option value="AUTH">Authentication</option>
          </select>
          <button
            onClick={fetchLogs}
            className="p-1.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors"
            title="Refresh logs"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {logs.length === 0 ? (
        <div className="text-center py-6 text-slate-500">
          No audit logs recorded for this category.
        </div>
      ) : (
        <div className="space-y-2.5 max-h-96 overflow-y-auto pr-1">
          {logs.map((log) => (
            <div
              key={log.id}
              className="p-3 rounded-lg bg-slate-900/80 border border-slate-800 hover:border-slate-700 transition-colors flex flex-col sm:flex-row sm:items-center justify-between gap-2"
            >
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="font-bold text-sky-400">{log.action}</span>
                  <span className="text-slate-500">•</span>
                  <span className="text-slate-300">{log.entity_type}: <span className="text-slate-100 font-bold">{log.entity_id}</span></span>
                </div>
                <div className="text-[11px] text-slate-400 flex items-center gap-3">
                  <span className="flex items-center gap-1 text-slate-400">
                    <User className="w-3 h-3 text-slate-500" /> {log.operator} ({log.role})
                  </span>
                  {log.details && Object.keys(log.details).length > 0 && (
                    <span className="text-slate-500">
                      | {JSON.stringify(log.details).slice(0, 70)}...
                    </span>
                  )}
                </div>
              </div>

              <div className="text-[10px] text-slate-500 flex items-center gap-1 sm:text-right flex-shrink-0">
                <Clock className="w-3 h-3" />
                {new Date(log.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default AuditLogViewer;
