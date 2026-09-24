import React, { useState, useEffect } from 'react';
import PageContainer from '../components/common/PageContainer';
import KPICard from '../components/common/KPICard';
import ScenarioSelector from '../components/common/ScenarioSelector';
import StatusBadge from '../components/common/StatusBadge';
import LoadingState from '../components/common/LoadingState';
import ErrorState from '../components/common/ErrorState';
import CacheIndicator from '../components/common/CacheIndicator';
import PolarMap from '../components/gis/PolarMap';
import RiskIndicator from '../components/intelligence/RiskIndicator';
import ExplanationPanel from '../components/intelligence/ExplanationPanel';
import RecommendationCard from '../components/intelligence/RecommendationCard';
import IntelligenceCard from '../components/intelligence/IntelligenceCard';
import AuditLogViewer from '../components/common/AuditLogViewer';
import { useScenario } from '../context/ScenarioContext';
import { getIntelligenceSummary } from '../services/api';
import {
  Shield,
  Truck,
  Users,
  Radio,
  Package,
  ThermometerSnowflake,
  AlertTriangle,
  RefreshCw,
  Clock,
  Compass,
  CheckCircle2,
  AlertCircle,
  Activity,
  ArrowRight,
  TrendingDown,
  LifeBuoy,
  BrainCircuit,
  Eye,
  Sliders,
  Sparkles
} from 'lucide-react';

export const DashboardPage = () => {
  const {
    scenarioId,
    setScenarioId,
    dashboardData,
    mapData,
    healthStatus,
    loading: scenarioLoading,
    error: scenarioError,
    refreshData: refreshScenarioData
  } = useScenario();

  const [intelligence, setIntelligence] = useState(null);
  const [intelLoading, setIntelLoading] = useState(false);
  const [intelError, setIntelError] = useState(null);

  const fetchIntelligence = async (sId) => {
    try {
      setIntelLoading(true);
      const data = await getIntelligenceSummary(sId);
      setIntelligence(data);
      setIntelError(null);
    } catch (err) {
      console.warn('Failed to load operational intelligence summary:', err);
      setIntelError(err.message);
    } finally {
      setIntelLoading(false);
    }
  };

  useEffect(() => {
    fetchIntelligence(scenarioId);
  }, [scenarioId]);

  const handleRefresh = () => {
    refreshScenarioData();
    fetchIntelligence(scenarioId);
  };

  // Core operational stages for SIH demonstration
  const operationalPillars = [
    { name: 'PLAN', desc: 'Traverse Routing & Buffers' },
    { name: 'TRACK', desc: 'Kinematics & GPS Positions' },
    { name: 'MONITOR', desc: 'Cold-Chain & Telemetry' },
    { name: 'PREDICT', desc: 'Days of Autonomy' },
    { name: 'ALERT', desc: 'Rule Engine Triggers' },
    { name: 'RESPOND', desc: 'Autonomous SAR Dispatch' },
  ];

  const loading = scenarioLoading || intelLoading;
  const error = scenarioError;

  return (
    <PageContainer
      title="PolarSync Command Center"
      subtitle="Integrated Polar Expedition Logistics and Asset Management System"
      badge="SIMULATION MODE"
    >
      {/* Header Bar with Status Indicators and Scenario Selector */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 mb-6 pb-4 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <h2 className="text-xl font-bold font-mono text-slate-100">
              {dashboardData?.scenario_name || `Scenario ${scenarioId}`}
            </h2>
          </div>
          <p className="text-xs text-slate-400 max-w-2xl">
            {dashboardData?.description || 'Loading operational scenario telemetry...'}
          </p>
        </div>

        <div className="flex items-center gap-3">
          <CacheIndicator isCached={dashboardData?._isCached} cachedAt={dashboardData?._cachedAt} />
          <div className="flex items-center gap-2 font-mono text-xs">
            <span className="text-slate-400">BACKEND:</span>
            <StatusBadge
              status={healthStatus.online ? 'online' : 'offline'}
              label={healthStatus.online ? 'ONLINE' : 'OFFLINE'}
              size="xs"
            />
          </div>
          <div className="flex items-center gap-2 font-mono text-xs">
            <span className="text-slate-400">READINESS:</span>
            <RiskIndicator level={intelligence?.overall_readiness || dashboardData?.readiness?.status || 'NOMINAL'} size="sm" />
          </div>
          <button
            onClick={handleRefresh}
            disabled={loading}
            className="p-2 rounded-lg bg-slate-800/80 hover:bg-slate-700 text-sky-400 border border-slate-700 transition cursor-pointer"
            title="Refresh Scenario Data"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Unified Scenario Selector */}
      <div className="mb-6">
        <ScenarioSelector
          selectedScenario={scenarioId}
          onSelectScenario={setScenarioId}
          disabled={loading}
        />
      </div>

      {loading && !dashboardData ? (
        <LoadingState message="Executing scenario simulation & extracting telemetry..." />
      ) : error && !dashboardData ? (
        <ErrorState
          title="Command Center Disconnected"
          message={error}
          onRetry={handleRefresh}
        />
      ) : (
        <>
          {/* 6 High-Level Operational KPI Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4 mb-6">
            <KPICard
              label="Expedition Readiness"
              value={intelligence?.overall_readiness || dashboardData?.readiness?.status || 'N/A'}
              subtext={`Highest Risk: ${intelligence?.highest_risk || 'NOMINAL'}`}
              icon={Shield}
              badgeText={intelligence?.overall_readiness || 'OPTIMAL'}
            />

            <KPICard
              label="Personnel Muster"
              value={`${dashboardData?.personnel?.accounted ?? 0} / ${dashboardData?.personnel?.total ?? 0}`}
              subtext={
                dashboardData?.personnel?.unconfirmed > 0
                  ? `⚠ ${dashboardData.personnel.unconfirmed} Unconfirmed Missing`
                  : '25 / 25 ALL ACCOUNTED'
              }
              icon={Users}
              badgeText={dashboardData?.personnel?.unconfirmed > 0 ? 'CRITICAL' : 'NOMINAL'}
            />

            <KPICard
              label="Active Fleet"
              value={`${dashboardData?.assets?.active ?? 0} / ${dashboardData?.assets?.total ?? 0}`}
              subtext="Deployable Assets"
              icon={Truck}
              badgeText="FLEET"
            />

            <KPICard
              label="Cargo Status"
              value={`${dashboardData?.cargo?.delivered ?? 0} / ${dashboardData?.cargo?.total ?? 0}`}
              subtext={`${dashboardData?.cargo?.in_transit ?? 0} In-Transit`}
              icon={Package}
              badgeText="PAYLOAD"
            />

            <KPICard
              label="Cold-Chain Health"
              value={`${dashboardData?.cargo?.cold_chain_health_pct ?? 100}%`}
              subtext={
                dashboardData?.cargo?.cold_chain_health_pct < 100
                  ? 'Thermal Drift / Breach Active'
                  : 'All Payloads Nominal'
              }
              icon={ThermometerSnowflake}
              badgeText={dashboardData?.cargo?.cold_chain_health_pct < 100 ? 'BREACH' : 'NOMINAL'}
            />

            <KPICard
              label="Mission Alerts"
              value={`${dashboardData?.alerts?.total ?? 0}`}
              subtext={`${dashboardData?.alerts?.critical ?? 0} Critical | ${dashboardData?.alerts?.warning ?? 0} Warning`}
              icon={AlertTriangle}
              badgeText={dashboardData?.alerts?.critical > 0 ? 'CRITICAL' : 'NOMINAL'}
            />
          </div>

          {/* STAGE 3.5: OPERATIONAL INTELLIGENCE & EXPLAINABILITY */}
          {intelligence && (
            <div className="mb-6 space-y-4">
              {/* Top Intelligence Banner */}
              <div className="p-4 rounded-xl polar-glass border border-sky-500/30 bg-gradient-to-r from-slate-900/90 via-slate-900/70 to-slate-900/90">
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 pb-3 border-b border-slate-800">
                  <div className="flex items-center gap-2">
                    <BrainCircuit className="w-5 h-5 text-sky-400 animate-pulse" />
                    <div>
                      <h3 className="text-sm font-bold font-mono text-slate-100 uppercase tracking-wider">
                        Operational Intelligence Synthesis
                      </h3>
                      <p className="text-[11px] text-slate-400">
                        Multi-Factor Decision Support & Automated Anomaly Detection
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3 font-mono text-xs">
                    <span className="text-slate-400">OVERALL READINESS:</span>
                    <RiskIndicator level={intelligence.overall_readiness} size="md" />
                    <span className="text-slate-400 ml-2">SECTOR RISK:</span>
                    <RiskIndicator level={intelligence.highest_risk} size="md" />
                  </div>
                </div>

                {/* 6-Factor Readiness Breakdown */}
                <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2.5 mt-3">
                  {intelligence.readiness?.factors?.map((f, idx) => (
                    <div
                      key={idx}
                      className="p-2.5 rounded-lg bg-slate-950/70 border border-slate-800 flex flex-col justify-between"
                    >
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-xs font-mono font-bold text-slate-200">{f.name}</span>
                        <RiskIndicator level={f.state} size="sm" showLabel={false} />
                      </div>
                      <div className="text-[11px] font-mono font-semibold text-sky-300 truncate">
                        {f.metric}
                      </div>
                      <div className="text-[10px] text-slate-400 mt-1 line-clamp-2 leading-tight">
                        {f.reason}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* 4-Pillar Explainability Panel */}
              <ExplanationPanel
                explainability={intelligence.explainability}
                title={`Operational Context & Decision Rationale — Scenario ${scenarioId}`}
              />

              {/* Actionable Operator Guidance / Highest Attention items */}
              {intelligence.resupply_risk && (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                  {intelligence.resupply_risk
                    .filter((r) => r.risk_level === 'CRITICAL' || r.risk_level === 'AT_RISK' || r.risk_level === 'WATCH')
                    .slice(0, 3)
                    .map((item, idx) => (
                      <RecommendationCard
                        key={idx}
                        title={item.category}
                        category={item.category}
                        riskLevel={item.risk_level}
                        metric={`${item.days_of_autonomy}d Autonomy`}
                        explanation={item.explanation}
                        action={item.recommended_action}
                      />
                    ))}
                </div>
              )}
            </div>
          )}

          {/* Main Grid: GIS Map (Left) + Mission Status (Right) */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
            {/* LEFT: Leaflet GIS Command Center Map */}
            <div className="lg:col-span-2 flex flex-col">
              <PolarMap
                locations={mapData?.locations || []}
                dangerZones={mapData?.danger_zones || []}
                routes={mapData?.routes || []}
                assets={mapData?.assets || []}
                personnel={mapData?.personnel || []}
                emergency={mapData?.emergency || null}
                height="640px"
              />
            </div>

            {/* RIGHT: Real-time Mission Status & Subsystem Summary */}
            <div className="flex flex-col gap-4">
              <div className="polar-glass p-5 rounded-xl border border-slate-800 flex-1 flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between pb-3 border-b border-slate-800 mb-4">
                    <h3 className="text-sm font-bold font-mono text-sky-400 uppercase tracking-wider flex items-center gap-2">
                      <Activity className="w-4 h-4" /> Subsystem Telemetry
                    </h3>
                    <StatusBadge
                      status={dashboardData?.readiness?.status === 'EXCELLENT' ? 'nominal' : 'warning'}
                      label={dashboardData?.readiness?.status || 'ONLINE'}
                      size="xs"
                    />
                  </div>

                  <div className="space-y-3 text-xs font-mono">
                    <div className="flex items-center justify-between p-2.5 rounded-lg bg-slate-900/80 border border-slate-800">
                      <span className="text-slate-400 flex items-center gap-2">
                        <Radio className="w-3.5 h-3.5 text-sky-400" /> Satellite Link:
                      </span>
                      <span className="font-bold text-slate-200">
                        {dashboardData?.connectivity?.status || 'ONLINE'}
                      </span>
                    </div>

                    <div className="flex items-center justify-between p-2.5 rounded-lg bg-slate-900/80 border border-slate-800">
                      <span className="text-slate-400 flex items-center gap-2">
                        <Users className="w-3.5 h-3.5 text-emerald-400" /> Muster State:
                      </span>
                      <span className="font-bold">
                        {dashboardData?.personnel?.unconfirmed > 0 ? (
                          <span className="text-rose-400 font-bold">23/25 (2 UNCONFIRMED)</span>
                        ) : (
                          <span className="text-emerald-400">25/25 ALL ACCOUNTED</span>
                        )}
                      </span>
                    </div>

                    <div className="flex items-center justify-between p-2.5 rounded-lg bg-slate-900/80 border border-slate-800">
                      <span className="text-slate-400 flex items-center gap-2">
                        <Truck className="w-3.5 h-3.5 text-sky-400" /> Fleet Readiness:
                      </span>
                      <span className="font-bold text-slate-200">
                        {dashboardData?.assets?.active} / {dashboardData?.assets?.total} Active
                      </span>
                    </div>

                    <div className="flex items-center justify-between p-2.5 rounded-lg bg-slate-900/80 border border-slate-800">
                      <span className="text-slate-400 flex items-center gap-2">
                        <Package className="w-3.5 h-3.5 text-cyan-400" /> Cargo Delivered:
                      </span>
                      <span className="font-bold text-slate-200">
                        {dashboardData?.cargo?.delivered} / {dashboardData?.cargo?.total} Units
                      </span>
                    </div>

                    <div className="flex items-center justify-between p-2.5 rounded-lg bg-slate-900/80 border border-slate-800">
                      <span className="text-slate-400 flex items-center gap-2">
                        <ThermometerSnowflake className="w-3.5 h-3.5 text-cyan-400" /> Thermal Health:
                      </span>
                      <span className="font-bold text-slate-200">
                        {dashboardData?.cargo?.cold_chain_health_pct}% Nominal
                      </span>
                    </div>

                    <div className="flex items-center justify-between p-2.5 rounded-lg bg-slate-900/80 border border-slate-800">
                      <span className="text-slate-400 flex items-center gap-2">
                        <AlertCircle className="w-3.5 h-3.5 text-amber-400" /> Alert Engine:
                      </span>
                      <span className="font-bold text-slate-200">
                        {dashboardData?.alerts?.critical} Critical • {dashboardData?.alerts?.warning} Warning
                      </span>
                    </div>
                  </div>
                </div>

                {/* Scenario specific status callout */}
                {scenarioId === 2 && (
                  <div className="mt-3 p-3 rounded-lg bg-rose-950/40 border border-rose-500/30 text-xs font-mono">
                    <div className="text-rose-300 font-bold mb-1 flex items-center gap-1.5">
                      <TrendingDown className="w-3.5 h-3.5 text-rose-400" />
                      CRITICAL FUEL AUTONOMY
                    </div>
                    <p className="text-slate-400 text-[11px]">
                      Fuel leak and consumption surge reduced Days of Autonomy to under 5 days against an 8-day resupply window.
                    </p>
                  </div>
                )}

                {scenarioId === 3 && (
                  <div className="mt-3 p-3 rounded-lg bg-rose-950/40 border border-rose-500/30 text-xs font-mono">
                    <div className="text-rose-300 font-bold mb-1 flex items-center gap-1.5">
                      <LifeBuoy className="w-3.5 h-3.5 text-rose-400" />
                      SAR DISPATCH & RESOLUTION
                    </div>
                    <p className="text-slate-400 text-[11px]">
                      Crevasse fall incident at C-3 triggered optimal SAR asset selection, on-scene triage, and muster resolution.
                    </p>
                  </div>
                )}

                {scenarioId === 4 && (
                  <div className="mt-3 p-3 rounded-lg bg-amber-950/40 border border-amber-500/30 text-xs font-mono">
                    <div className="text-amber-300 font-bold mb-1 flex items-center gap-1.5">
                      <ThermometerSnowflake className="w-3.5 h-3.5 text-amber-400" />
                      COLD-CHAIN THERMAL BREACH
                    </div>
                    <p className="text-slate-400 text-[11px]">
                      Refrigeration malfunction resulted in ambient freezing breach below -30.0°C safety envelope.
                    </p>
                  </div>
                )}

                {scenarioId === 5 && (
                  <div className="mt-3 p-3 rounded-lg bg-sky-950/40 border border-sky-500/30 text-xs font-mono">
                    <div className="text-sky-300 font-bold mb-1 flex items-center gap-1.5">
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                      STORE & FORWARD REPLAY
                    </div>
                    <p className="text-slate-400 text-[11px]">
                      30/30 offline telemetry frames buffered during satellite outage successfully replayed and synchronized.
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* BOTTOM: Operational Event Flow Pipeline */}
          <div className="polar-glass p-5 rounded-xl border border-slate-800">
            {/* Top Sequence: PLAN -> TRACK -> MONITOR -> PREDICT -> ALERT -> RESPOND */}
            <div className="mb-4 pb-4 border-b border-slate-800">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-xs font-bold font-mono text-sky-400 uppercase tracking-wider flex items-center gap-2">
                  <Clock className="w-3.5 h-3.5" /> Operational Control Sequence
                </h3>
                <span className="text-[11px] font-mono text-slate-500">
                  Integrated Autonomous Workflow
                </span>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2">
                {operationalPillars.map((p, idx) => (
                  <div
                    key={idx}
                    className="p-2.5 rounded-lg bg-slate-900/90 border border-slate-800 flex flex-col justify-between"
                  >
                    <div className="flex items-center justify-between text-xs font-mono">
                      <span className="text-sky-400 font-bold">{p.name}</span>
                      <span className="text-[10px] text-slate-500 font-mono">0{idx + 1}</span>
                    </div>
                    <span className="text-[10px] text-slate-400 font-mono mt-1">{p.desc}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Bottom Scenario Specific Events */}
            <div>
              <div className="text-xs font-mono text-slate-400 mb-2 font-semibold">
                SCENARIO {scenarioId} EVENT TIMELINE:
              </div>
              <div className="flex flex-wrap items-center gap-2.5">
                {dashboardData?.event_flow?.map((step, idx) => (
                  <React.Fragment key={idx}>
                    <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-900/90 border border-slate-700/80 text-xs font-mono shadow-sm">
                      <span className="w-4 h-4 rounded-full bg-sky-500/20 text-sky-400 border border-sky-500/40 flex items-center justify-center font-bold text-[9px]">
                        {idx + 1}
                      </span>
                      <span className="font-semibold text-slate-200">{step}</span>
                    </div>
                    {idx < (dashboardData?.event_flow?.length || 0) - 1 && (
                      <span className="text-slate-600 font-mono font-bold">→</span>
                    )}
                  </React.Fragment>
                ))}
              </div>
            </div>

            {/* Bottom Audit Log Timeline */}
            <div className="mt-6">
              <AuditLogViewer limit={15} />
            </div>
          </div>
        </>
      )}
    </PageContainer>
  );
};

export default DashboardPage;
