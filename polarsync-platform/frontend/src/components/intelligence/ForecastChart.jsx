import React from 'react';
import { TrendingDown, AlertTriangle, ShieldCheck } from 'lucide-react';
import RiskIndicator from './RiskIndicator';

const ForecastChart = ({ forecast }) => {
  if (!forecast) return null;

  const {
    resource,
    current_value,
    unit,
    current_rate,
    forecast_horizon_hours,
    forecast_value,
    autonomy_hours_remaining,
    risk,
    confidence_note,
    explanation,
    historical_points = [],
    projected_points = []
  } = forecast;

  const allPoints = [...historical_points, ...projected_points];
  if (allPoints.length === 0) return null;

  const width = 500;
  const height = 180;
  const padding = { top: 25, right: 30, bottom: 35, left: 55 };

  const values = allPoints.map((p) => p.value);
  const maxVal = Math.max(...values, 100);
  const minVal = 0;

  const getX = (index) => {
    const total = allPoints.length - 1 || 1;
    return padding.left + (index / total) * (width - padding.left - padding.right);
  };

  const getY = (val) => {
    const range = maxVal - minVal || 1;
    return height - padding.bottom - ((val - minVal) / range) * (height - padding.top - padding.bottom);
  };

  // Build SVG path strings
  const histPath = historical_points
    .map((p, idx) => `${idx === 0 ? 'M' : 'L'} ${getX(idx)} ${getY(p.value)}`)
    .join(' ');

  const splitIdx = Math.max(0, historical_points.length - 1);
  const projPath = [
    historical_points[splitIdx],
    ...projected_points
  ]
    .map((p, idx) => {
      const globalIdx = splitIdx + idx;
      return `${idx === 0 ? 'M' : 'L'} ${getX(globalIdx)} ${getY(p.value)}`;
    })
    .join(' ');

  const isCritical = risk === 'CRITICAL';

  return (
    <div
      style={{
        background: 'rgba(15, 23, 42, 0.7)',
        border: `1px solid ${isCritical ? 'rgba(239, 68, 68, 0.3)' : 'rgba(56, 189, 248, 0.2)'}`,
        borderRadius: '8px',
        padding: '1.25rem',
        marginBottom: '1rem'
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <TrendingDown size={18} color={isCritical ? '#ef4444' : '#38bdf8'} />
            <h4 style={{ margin: 0, fontSize: '0.95rem', fontWeight: 600, color: '#f8fafc' }}>
              {resource} Depletion Projection
            </h4>
            <RiskIndicator level={risk} size="sm" />
          </div>
          <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginTop: '2px' }}>
            Current Rate: <span style={{ color: '#f1f5f9', fontWeight: 600 }}>{current_rate} {unit}/day</span>
            {autonomy_hours_remaining && (
              <span style={{ marginLeft: '12px' }}>
                Autonomy Horizon: <span style={{ color: isCritical ? '#ef4444' : '#38bdf8', fontWeight: 600 }}>{autonomy_hours_remaining} hrs ({(autonomy_hours_remaining / 24).toFixed(1)}d)</span>
              </span>
            )}
          </div>
        </div>

        <div style={{ textAlign: 'right' }}>
          <div style={{ fontSize: '1.1rem', fontWeight: 700, fontFamily: 'monospace', color: isCritical ? '#ef4444' : '#38bdf8' }}>
            {current_value} <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>{unit}</span>
          </div>
          <div style={{ fontSize: '0.7rem', color: '#64748b' }}>Current Stock</div>
        </div>
      </div>

      {/* SVG Chart */}
      <div style={{ width: '100%', overflowX: 'auto' }}>
        <svg viewBox={`0 0 ${width} ${height}`} style={{ width: '100%', height: 'auto', minWidth: '420px' }}>
          {/* Background Grid Lines */}
          {[0, 0.25, 0.5, 0.75, 1].map((pct) => {
            const val = minVal + pct * (maxVal - minVal);
            const y = getY(val);
            return (
              <g key={pct}>
                <line
                  x1={padding.left}
                  y1={y}
                  x2={width - padding.right}
                  y2={y}
                  stroke="rgba(255, 255, 255, 0.07)"
                  strokeDasharray="3 3"
                />
                <text
                  x={padding.left - 8}
                  y={y + 3}
                  fill="#64748b"
                  fontSize="9"
                  textAnchor="end"
                  fontFamily="monospace"
                >
                  {val.toFixed(0)}
                </text>
              </g>
            );
          })}

          {/* Projection Divider */}
          {historical_points.length > 0 && projected_points.length > 0 && (
            <line
              x1={getX(splitIdx)}
              y1={padding.top}
              x2={getX(splitIdx)}
              y2={height - padding.bottom}
              stroke="rgba(245, 158, 11, 0.5)"
              strokeWidth="1.5"
              strokeDasharray="4 2"
            />
          )}

          {/* Historical Line */}
          {histPath && (
            <path
              d={histPath}
              fill="none"
              stroke="#38bdf8"
              strokeWidth="2.5"
            />
          )}

          {/* Projected Line (Dashed) */}
          {projPath && (
            <path
              d={projPath}
              fill="none"
              stroke={isCritical ? '#ef4444' : '#f59e0b'}
              strokeWidth="2.5"
              strokeDasharray="5 4"
            />
          )}

          {/* Points */}
          {allPoints.map((p, idx) => {
            const cx = getX(idx);
            const cy = getY(p.value);
            return (
              <g key={idx}>
                <circle
                  cx={cx}
                  cy={cy}
                  r={p.is_projected ? 3.5 : 4}
                  fill={p.is_projected ? (isCritical ? '#ef4444' : '#f59e0b') : '#38bdf8'}
                  stroke="#0f172a"
                  strokeWidth="1.5"
                />
                <text
                  x={cx}
                  y={height - padding.bottom + 14}
                  fill="#94a3b8"
                  fontSize="8.5"
                  textAnchor="middle"
                  fontFamily="monospace"
                >
                  {p.time_label}
                </text>
              </g>
            );
          })}
        </svg>
      </div>

      {/* Chart Legend */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: '0.5rem', borderTop: '1px solid rgba(255,255,255,0.06)', paddingTop: '0.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px', fontSize: '0.72rem' }}>
          <span style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#38bdf8' }}>
            <span style={{ width: '12px', height: '2px', backgroundColor: '#38bdf8' }} /> Historical Telemetry
          </span>
          <span style={{ display: 'flex', alignItems: 'center', gap: '6px', color: isCritical ? '#ef4444' : '#f59e0b' }}>
            <span style={{ width: '12px', height: '2px', borderTop: `2px dashed ${isCritical ? '#ef4444' : '#f59e0b'}` }} /> Projected Horizon
          </span>
        </div>
        <span style={{ fontSize: '0.68rem', color: '#64748b', fontStyle: 'italic' }}>
          {confidence_note}
        </span>
      </div>

      <div style={{ marginTop: '0.5rem', fontSize: '0.78rem', color: '#cbd5e1', lineHeight: 1.4 }}>
        {explanation}
      </div>
    </div>
  );
};

export default ForecastChart;
