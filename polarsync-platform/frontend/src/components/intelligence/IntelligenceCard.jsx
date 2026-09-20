import React from 'react';

const IntelligenceCard = ({ title, icon: Icon, badge, children, style = {} }) => {
  return (
    <div
      style={{
        background: 'rgba(15, 23, 42, 0.75)',
        backdropFilter: 'blur(10px)',
        border: '1px solid rgba(255, 255, 255, 0.08)',
        borderRadius: '8px',
        padding: '1.25rem',
        display: 'flex',
        flexDirection: 'column',
        gap: '0.85rem',
        boxShadow: '0 4px 16px rgba(0, 0, 0, 0.25)',
        ...style
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid rgba(255, 255, 255, 0.06)', paddingBottom: '0.6rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          {Icon && <Icon size={18} color="#38bdf8" />}
          <h3 style={{ margin: 0, fontSize: '0.92rem', fontWeight: 600, color: '#f8fafc', letterSpacing: '0.4px' }}>
            {title}
          </h3>
        </div>
        {badge}
      </div>
      <div>{children}</div>
    </div>
  );
};

export default IntelligenceCard;
