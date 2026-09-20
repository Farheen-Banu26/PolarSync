import React from 'react';
import { AlertTriangle, CheckCircle, Clock, ArrowRight } from 'lucide-react';
import RiskIndicator from './RiskIndicator';

const RecommendationCard = ({ title, category, riskLevel, action, explanation, metric }) => {
  const isCritical = riskLevel === 'CRITICAL';

  return (
    <div
      style={{
        background: isCritical ? 'rgba(239, 68, 68, 0.08)' : 'rgba(30, 41, 59, 0.7)',
        border: `1px solid ${isCritical ? 'rgba(239, 68, 68, 0.3)' : 'rgba(255, 255, 255, 0.08)'}`,
        borderRadius: '8px',
        padding: '1rem',
        display: 'flex',
        flexDirection: 'column',
        gap: '0.6rem'
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          {isCritical ? <AlertTriangle size={16} color="#ef4444" /> : <Clock size={16} color="#38bdf8" />}
          <span style={{ fontWeight: 600, fontSize: '0.85rem', color: '#f8fafc' }}>
            {category || title}
          </span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          {metric && (
            <span style={{ fontSize: '0.75rem', fontFamily: 'monospace', color: '#94a3b8' }}>
              {metric}
            </span>
          )}
          <RiskIndicator level={riskLevel} size="sm" />
        </div>
      </div>

      <div style={{ fontSize: '0.8rem', color: '#cbd5e1', lineHeight: 1.4 }}>
        {explanation}
      </div>

      {action && (
        <div
          style={{
            marginTop: '0.25rem',
            padding: '0.5rem 0.75rem',
            borderRadius: '4px',
            backgroundColor: isCritical ? 'rgba(239, 68, 68, 0.15)' : 'rgba(56, 189, 248, 0.1)',
            borderLeft: `3px solid ${isCritical ? '#ef4444' : '#38bdf8'}`,
            fontSize: '0.78rem',
            color: isCritical ? '#fca5a5' : '#7dd3fc',
            fontWeight: 500,
            display: 'flex',
            alignItems: 'center',
            gap: '6px'
          }}
        >
          <ArrowRight size={14} style={{ flexShrink: 0 }} />
          <span>{action}</span>
        </div>
      )}
    </div>
  );
};

export default RecommendationCard;
