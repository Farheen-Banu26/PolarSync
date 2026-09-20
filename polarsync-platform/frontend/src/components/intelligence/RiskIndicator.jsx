import React from 'react';

const RiskIndicator = ({ level = 'SAFE', size = 'md', showLabel = true }) => {
  const normLevel = String(level).toUpperCase();

  const config = {
    SAFE: {
      bg: 'rgba(16, 185, 129, 0.15)',
      text: '#10b981',
      border: 'rgba(16, 185, 129, 0.3)',
      dot: '#10b981',
      label: 'SAFE'
    },
    NOMINAL: {
      bg: 'rgba(16, 185, 129, 0.15)',
      text: '#10b981',
      border: 'rgba(16, 185, 129, 0.3)',
      dot: '#10b981',
      label: 'NOMINAL'
    },
    WATCH: {
      bg: 'rgba(245, 158, 11, 0.15)',
      text: '#f59e0b',
      border: 'rgba(245, 158, 11, 0.3)',
      dot: '#f59e0b',
      label: 'WATCH'
    },
    AT_RISK: {
      bg: 'rgba(249, 115, 22, 0.15)',
      text: '#f97316',
      border: 'rgba(249, 115, 22, 0.3)',
      dot: '#f97316',
      label: 'AT RISK'
    },
    CONDITIONAL: {
      bg: 'rgba(245, 158, 11, 0.15)',
      text: '#f59e0b',
      border: 'rgba(245, 158, 11, 0.3)',
      dot: '#f59e0b',
      label: 'CONDITIONAL'
    },
    DEGRADED: {
      bg: 'rgba(249, 115, 22, 0.15)',
      text: '#f97316',
      border: 'rgba(249, 115, 22, 0.3)',
      dot: '#f97316',
      label: 'DEGRADED'
    },
    CRITICAL: {
      bg: 'rgba(239, 68, 68, 0.15)',
      text: '#ef4444',
      border: 'rgba(239, 68, 68, 0.3)',
      dot: '#ef4444',
      label: 'CRITICAL'
    },
    WARNING: {
      bg: 'rgba(245, 158, 11, 0.15)',
      text: '#f59e0b',
      border: 'rgba(245, 158, 11, 0.3)',
      dot: '#f59e0b',
      label: 'WARNING'
    }
  };

  const current = config[normLevel] || config.SAFE;

  const fontSizes = {
    sm: '0.7rem',
    md: '0.75rem',
    lg: '0.85rem'
  };

  const paddings = {
    sm: '2px 6px',
    md: '3px 8px',
    lg: '5px 12px'
  };

  return (
    <span
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '5px',
        padding: paddings[size] || paddings.md,
        borderRadius: '4px',
        backgroundColor: current.bg,
        border: `1px solid ${current.border}`,
        color: current.text,
        fontSize: fontSizes[size] || fontSizes.md,
        fontWeight: 600,
        letterSpacing: '0.5px',
        fontFamily: 'monospace'
      }}
    >
      <span
        style={{
          width: '6px',
          height: '6px',
          borderRadius: '50%',
          backgroundColor: current.dot,
          boxShadow: `0 0 6px ${current.dot}`
        }}
      />
      {showLabel && (current.label || normLevel)}
    </span>
  );
};

export default RiskIndicator;
