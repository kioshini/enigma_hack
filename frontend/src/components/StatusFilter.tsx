import React from 'react';
import { StatusFilter, Stats } from '../types';

interface StatusFilterProps {
  current: StatusFilter;
  onChange: (status: StatusFilter) => void;
  stats: Stats | null;
}

const STATUSES: { value: StatusFilter; label: string; color: string; statsKey: keyof Stats | null }[] = [
  { value: 'ALL', label: 'All', color: '#6b7280', statsKey: 'total' },
  { value: 'NEW', label: 'New', color: '#3b82f6', statsKey: 'new' },
  { value: 'PROCESSED', label: 'Processed', color: '#22c55e', statsKey: 'processed' },
  { value: 'NEEDS_OPERATOR', label: 'Needs Operator', color: '#eab308', statsKey: 'needs_operator' },
  { value: 'ESCALATED', label: 'Escalated', color: '#ef4444', statsKey: 'escalated' },
  { value: 'CLOSED', label: 'Closed', color: '#9ca3af', statsKey: 'closed' },
];

export const StatusFilterBar: React.FC<StatusFilterProps> = ({ current, onChange, stats }) => {
  return (
    <div className="filter-bar">
      {STATUSES.map((s) => {
        const count = stats && s.statsKey ? stats[s.statsKey] : null;
        return (
          <button
            key={s.value}
            className={`filter-btn ${current === s.value ? 'active' : ''}`}
            style={{
              borderColor: s.color,
              backgroundColor: current === s.value ? s.color : 'transparent',
              color: current === s.value ? '#fff' : s.color,
            }}
            onClick={() => onChange(s.value)}
          >
            {s.label}
            {count !== null && <span className="badge">{count}</span>}
          </button>
        );
      })}
    </div>
  );
};
