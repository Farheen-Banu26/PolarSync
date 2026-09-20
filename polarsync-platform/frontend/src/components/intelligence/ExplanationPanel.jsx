import React from 'react';
import { ShieldAlert, Info, Eye, CheckCircle2 } from 'lucide-react';

const ExplanationPanel = ({ explainability, title = "Operational Explainability & Decision Support" }) => {
  if (!explainability) return null;

  const {
    what_happened,
    why_it_matters,
    what_to_watch,
    recommended_operator_action
  } = explainability;

  return (
    <div
      style={{
        background: 'rgba(15, 23, 42, 0.75)',
        backdropFilter: 'blur(8px)',
        border: '1px solid rgba(56, 189, 248, 0.25)',
        borderRadius: '8px',
        padding: '1.25rem',
        marginTop: '1rem',
        marginBottom: '1rem'
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '1rem', borderBottom: '1px solid rgba(255,255,255,0.08)', paddingBottom: '0.6rem' }}>
        <Info size={18} color="#38bdf8" />
        <h4 style={{ margin: 0, fontSize: '0.95rem', fontWeight: 600, color: '#f8fafc', letterSpacing: '0.5px' }}>
          {title}
        </h4>
        <span style={{ marginLeft: 'auto', fontSize: '0.7rem', color: '#94a3b8', background: 'rgba(56, 189, 248, 0.1)', padding: '2px 8px', borderRadius: '4px', border: '1px solid rgba(56,189,248,0.2)' }}>
          Traceable Intelligence
        </span>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1rem' }}>
        {/* 1. What Happened */}
        <div style={{ background: 'rgba(30, 41, 59, 0.6)', padding: '0.85rem', borderRadius: '6px', borderLeft: '3px solid #38bdf8' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '4px', color: '#38bdf8', fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase' }}>
            <Info size={14} /> WHAT HAPPENED
          </div>
          <div style={{ fontSize: '0.82rem', color: '#e2e8f0', lineHeight: 1.45 }}>
            {what_happened}
          </div>
        </div>

        {/* 2. Why It Matters */}
        <div style={{ background: 'rgba(30, 41, 59, 0.6)', padding: '0.85rem', borderRadius: '6px', borderLeft: '3px solid #f59e0b' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '4px', color: '#f59e0b', fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase' }}>
            <ShieldAlert size={14} /> WHY IT MATTERS
          </div>
          <div style={{ fontSize: '0.82rem', color: '#e2e8f0', lineHeight: 1.45 }}>
            {why_it_matters}
          </div>
        </div>

        {/* 3. What to Watch */}
        <div style={{ background: 'rgba(30, 41, 59, 0.6)', padding: '0.85rem', borderRadius: '6px', borderLeft: '3px solid #a855f7' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '4px', color: '#a855f7', fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase' }}>
            <Eye size={14} /> WHAT TO WATCH
          </div>
          <div style={{ fontSize: '0.82rem', color: '#e2e8f0', lineHeight: 1.45 }}>
            {what_to_watch}
          </div>
        </div>

        {/* 4. Operator Action */}
        <div style={{ background: 'rgba(30, 41, 59, 0.6)', padding: '0.85rem', borderRadius: '6px', borderLeft: '3px solid #10b981' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '4px', color: '#10b981', fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase' }}>
            <CheckCircle2 size={14} /> RECOMMENDED OPERATOR ACTION
          </div>
          <div style={{ fontSize: '0.82rem', color: '#e2e8f0', lineHeight: 1.45, fontWeight: 500 }}>
            {recommended_operator_action}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ExplanationPanel;
