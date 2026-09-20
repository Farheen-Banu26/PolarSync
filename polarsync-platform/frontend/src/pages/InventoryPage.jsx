import React, { useState, useEffect } from 'react';
import PageContainer from '../components/common/PageContainer';
import ScenarioSelector from '../components/common/ScenarioSelector';
import StatusBadge from '../components/common/StatusBadge';
import LoadingState from '../components/common/LoadingState';
import ErrorState from '../components/common/ErrorState';
import CacheIndicator from '../components/common/CacheIndicator';
import RiskIndicator from '../components/intelligence/RiskIndicator';
import ExplanationPanel from '../components/intelligence/ExplanationPanel';
import RecommendationCard from '../components/intelligence/RecommendationCard';
import ForecastChart from '../components/intelligence/ForecastChart';
import { useScenario } from '../context/ScenarioContext';
import { getInventory, getAutonomyIntelligence, getResupplyRisk, getResourceForecast, getIntelligenceSummary } from '../services/api';
import { Boxes, Fuel, AlertTriangle, ShieldCheck, BarChart3, AlertOctagon, TrendingDown, Clock, CheckCircle, ArrowRight } from 'lucide-react';

export const InventoryPage = () => {
  const { scenarioId, setScenarioId } = useScenario();
  const [inventoryList, setInventoryList] = useState([]);
  const [autonomyItems, setAutonomyItems] = useState([]);
  const [resupplyRisks, setResupplyRisks] = useState([]);
  const [forecasts, setForecasts] = useState([]);
  const [summaryData, setSummaryData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchInventoryData = async (scId) => {
    setLoading(true);
    setError(null);
    try {
      const [invData, autoData, riskData, fcData, sumData] = await Promise.all([
        getInventory(scId),
        getAutonomyIntelligence(scId),
        getResupplyRisk(scId),
        getResourceForecast(scId),
        getIntelligenceSummary(scId)
      ]);
      setInventoryList(invData?.inventory || (Array.isArray(invData) ? invData : []));
      setAutonomyItems(Array.isArray(autoData) ? autoData : (autoData?.autonomy || []));
      setResupplyRisks(Array.isArray(riskData) ? riskData : (riskData?.resupply_risk || []));
      setForecasts(Array.isArray(fcData) ? fcData : (fcData?.forecasts || []));
      setSummaryData(sumData || null);
    } catch (err) {
      console.warn('Failed to load inventory intelligence:', err);
      setError(err.response?.data?.detail || err.message || 'Failed to load inventory data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInventoryData(scenarioId);
  }, [scenarioId]);

  return (
    <PageContainer
      title="Autonomous Inventory & Winter Autonomy"
      subtitle="Dynamic Burn-Rate Analytics, Explainable Resupply Risk & Depletion Forecasting"
      badge="LOGISTICS CORE"
    >
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <ScenarioSelector
          selectedScenario={scenarioId}
          onSelectScenario={setScenarioId}
          disabled={loading}
        />
        <CacheIndicator isCached={inventoryList?._isCached} cachedAt={inventoryList?._cachedAt} />
      </div>

      {loading ? (
        <LoadingState message="Extracting Days of Autonomy calculations & depletion forecasts..." />
      ) : error ? (
        <ErrorState message={error} onRetry={() => fetchInventoryData(scenarioId)} />
      ) : (
        <div className="space-y-6">
          {/* Scenario 2 Crisis Alert Banner */}
          {scenarioId === 2 && (
            <div className="p-4 rounded-xl border border-rose-500/40 bg-rose-950/30 text-rose-200 font-mono text-xs flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
              <div className="flex items-center gap-2.5">
                <AlertOctagon className="w-5 h-5 text-rose-400 animate-pulse flex-shrink-0" />
                <div>
                  <div className="font-bold text-sm text-rose-300">CRITICAL RESUPPLY RISK — FUEL AUTONOMY BREACH</div>
                  <div className="text-[11px] text-slate-300 mt-0.5">
                    Generator consumption surge and storage leak reduced Maitri-II fuel autonomy below the 7.0-day safety threshold.
                  </div>
                </div>
              </div>
              <RiskIndicator level="CRITICAL" size="md" />
            </div>
          )}

          {/* Autonomy Intelligence Grid */}
          <div className="polar-glass p-5 rounded-xl border border-slate-800">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-bold font-mono text-sky-400 uppercase tracking-wider flex items-center gap-2">
                <BarChart3 className="w-4 h-4" /> Winter Autonomy Intelligence Matrix
              </h3>
              <span className="text-xs font-mono text-slate-400">
                Safety Buffer vs Consumption Horizon
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {autonomyItems.map((item, idx) => {
                const maxDays = Math.max(item.days_of_autonomy, item.resupply_window_days + item.safety_buffer_days, 15);
                const autonomyPct = Math.min(100, (item.days_of_autonomy / maxDays) * 100);
                const thresholdPct = Math.min(100, (item.resupply_window_days / maxDays) * 100);
                const isCritical = item.risk === 'CRITICAL';
                const isWarning = item.risk === 'WATCH' || item.risk === 'AT_RISK';

                return (
                  <div
                    key={idx}
                    className={`p-4 rounded-xl border font-mono text-xs ${
                      isCritical
                        ? 'bg-rose-950/20 border-rose-500/40'
                        : isWarning
                        ? 'bg-amber-950/20 border-amber-500/30'
                        : 'bg-slate-900/80 border-slate-800'
                    }`}
                  >
                    <div className="flex justify-between items-start mb-2">
                      <div>
                        <div className="font-bold text-slate-100 text-sm flex items-center gap-2">
                          {item.category === 'FUEL' ? <Fuel className="w-4 h-4 text-sky-400" /> : <Boxes className="w-4 h-4 text-slate-400" />}
                          {item.category}
                        </div>
                        <div className="text-slate-400 text-[11px]">{item.location_name}</div>
                      </div>
                      <RiskIndicator level={item.risk} size="xs" />
                    </div>

                    <div className="my-3">
                      <div className="flex justify-between text-slate-400 mb-1">
                        <span>Days of Autonomy:</span>
                        <span className={`font-bold ${isCritical ? 'text-rose-400' : isWarning ? 'text-amber-400' : 'text-emerald-400'}`}>
                          {item.days_of_autonomy.toFixed(2)} Days
                        </span>
                      </div>
                      <div className="w-full bg-slate-950 rounded-full h-2.5 overflow-hidden relative border border-slate-800">
                        <div
                          className={`h-full rounded-full transition-all duration-500 ${
                            isCritical ? 'bg-rose-500' : isWarning ? 'bg-amber-500' : 'bg-emerald-500'
                          }`}
                          style={{ width: `${autonomyPct}%` }}
                        />
                        {/* Resupply window marker */}
                        <div
                          className="absolute top-0 bottom-0 w-0.5 bg-sky-400"
                          style={{ left: `${thresholdPct}%` }}
                          title={`Resupply Window: ${item.resupply_window_days}d`}
                        />
                      </div>
                      <div className="flex justify-between text-[10px] text-slate-500 mt-1">
                        <span>0d</span>
                        <span className="text-sky-400">Target: {item.resupply_window_days}d</span>
                        <span>{maxDays.toFixed(0)}d</span>
                      </div>
                    </div>

                    <div className="space-y-1 text-[11px] border-t border-slate-800/80 pt-2 text-slate-300">
                      <div className="flex justify-between">
                        <span className="text-slate-500">Current Stock:</span>
                        <span className="font-semibold text-slate-200">{item.current_stock.toLocaleString()} {item.unit}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-500">Burn Rate:</span>
                        <span className="font-semibold text-slate-200">{item.daily_consumption_rate.toFixed(1)} {item.unit}/day</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-500">Safety Buffer:</span>
                        <span className="text-slate-300">{item.safety_buffer_days.toFixed(1)} Days</span>
                      </div>
                    </div>

                    <div className="mt-2.5 text-[10px] text-slate-400 leading-tight bg-slate-950/60 p-2 rounded border border-slate-800/60">
                      {item.explanation}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Explainability Panel */}
          {summaryData?.explainability && (
            <ExplanationPanel
              explainability={summaryData.explainability}
              title={`Consumables Autonomy & Logistics Intelligence — Scenario ${scenarioId}`}
            />
          )}

          {/* Resource Depletion Forecasts */}
          {forecasts.length > 0 && (
            <div className="polar-glass p-5 rounded-xl border border-slate-800">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-bold font-mono text-sky-400 uppercase tracking-wider flex items-center gap-2">
                  <TrendingDown className="w-4 h-4" /> Explainable Resource Depletion Forecasts
                </h3>
                <span className="text-xs font-mono text-slate-400">
                  Deterministic Consumption Projection Models
                </span>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                {forecasts.map((fc, idx) => (
                  <ForecastChart key={idx} forecast={fc} />
                ))}
              </div>
            </div>
          )}

          {/* Actionable Resupply Risk Matrix */}
          <div className="polar-glass p-5 rounded-xl border border-slate-800">
            <h3 className="text-sm font-bold font-mono text-sky-400 uppercase tracking-wider mb-4 flex items-center gap-2">
              <ShieldCheck className="w-4 h-4" /> Resupply Priority & Decision Guidance
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {resupplyRisks.map((risk, idx) => (
                <RecommendationCard
                  key={idx}
                  title={risk.category}
                  category={`${risk.category} (${risk.location_name})`}
                  riskLevel={risk.risk_level}
                  metric={`${risk.days_of_autonomy}d Autonomy`}
                  explanation={risk.explanation}
                  action={risk.recommended_action}
                />
              ))}
            </div>
          </div>
        </div>
      )}
    </PageContainer>
  );
};

export default InventoryPage;
