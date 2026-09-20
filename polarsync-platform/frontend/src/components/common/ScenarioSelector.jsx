import React from 'react';
import { Layers, ChevronDown } from 'lucide-react';

const SCENARIOS = [
  { id: 1, name: 'Scenario 1: Normal Operations', badge: 'NOMINAL', color: 'text-emerald-400' },
  { id: 2, name: 'Scenario 2: Fuel Crisis', badge: 'CRITICAL RESUPPLY', color: 'text-amber-400' },
  { id: 3, name: 'Scenario 3: Emergency & SAR', badge: 'SAR INCIDENT', color: 'text-rose-400' },
  { id: 4, name: 'Scenario 4: Cold-Chain Breach', badge: 'THERMAL BREACH', color: 'text-rose-400' },
  { id: 5, name: 'Scenario 5: Satellite Loss & Sync', badge: 'STORE & FORWARD', color: 'text-sky-400' },
];

export const ScenarioSelector = ({ selectedScenario, onSelectScenario, disabled = false }) => {
  return (
    <div className="flex flex-wrap items-center gap-2 p-1.5 rounded-xl bg-slate-900/90 border border-slate-800 shadow-inner">
      <div className="flex items-center gap-2 px-3 py-1.5 text-xs font-mono font-semibold text-slate-400">
        <Layers className="w-3.5 h-3.5 text-sky-400" />
        <span>SCENARIO:</span>
      </div>

      <div className="flex flex-wrap items-center gap-1.5">
        {SCENARIOS.map((sc) => {
          const isSelected = selectedScenario === sc.id;
          return (
            <button
              key={sc.id}
              onClick={() => onSelectScenario(sc.id)}
              disabled={disabled}
              className={`px-3 py-1.5 rounded-lg text-xs font-mono transition-all duration-200 flex items-center gap-2 ${
                isSelected
                  ? 'bg-sky-500/20 text-sky-200 border border-sky-500/50 shadow-sm font-semibold'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60 border border-transparent'
              } ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
            >
              <span className={`w-2 h-2 rounded-full ${isSelected ? 'bg-sky-400 shadow-glow' : 'bg-slate-600'}`} />
              <span>S{sc.id}: {sc.name.split(':')[1]?.trim() || sc.name}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
};

export default ScenarioSelector;
