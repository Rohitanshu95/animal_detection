import React, { useState } from 'react';
import { Search, Filter, X, Calendar } from 'lucide-react';

const FilterSection = ({ title, children }) => (
  <div className="mb-6">
    <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">{title}</h4>
    <div className="space-y-2">
      {children}
    </div>
  </div>
);

const Checkbox = ({ label, count }) => (
  <label className="flex items-center justify-between cursor-pointer group select-none">
    <div className="flex items-center gap-2">
      <input type="checkbox" className="w-4 h-4 rounded border-slate-300 text-emerald-600 focus:ring-emerald-500" />
      <span className="text-sm text-slate-600 group-hover:text-slate-900 transition-colors">{label}</span>
    </div>
    {count && <span className="text-xs text-slate-400 bg-slate-100 px-2 py-0.5 rounded-full">{count}</span>}
  </label>
);

const IncidentFilters = ({ filters, setFilters, stats, onClose }) => {
  const handleFilterChange = (category, value) => {
    setFilters(prev => {
      const current = prev[category] || [];
      const updated = current.includes(value)
        ? current.filter(item => item !== value)
        : [...current, value];
      
      return { ...prev, [category]: updated };
    });
  };

  const isSelected = (category, value) => (filters[category] || []).includes(value);

  return (
    <div className="w-full h-full border-r border-slate-200 p-6 flex flex-col overflow-y-auto bg-white">
      <div className="flex items-center justify-between mb-6">
        <h3 className="font-bold text-slate-900 flex items-center gap-2">
          <Filter className="w-4 h-4 text-emerald-600" />
          Filter Archive
        </h3>
        {onClose && (
          <button onClick={onClose} className="lg:hidden p-1 text-slate-400">
            <X className="w-5 h-5" />
          </button>
        )}
      </div>

      {/* Status Filter */}
      <FilterSection title="Status">
        {stats?.status && Object.entries(stats.status).map(([status, count]) => (
          <label key={status} className="flex items-center justify-between cursor-pointer group select-none">
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={isSelected('status', status)}
                onChange={() => handleFilterChange('status', status)}
                className="w-4 h-4 rounded border-slate-300 text-emerald-600 focus:ring-emerald-500"
              />
              <span className="text-sm text-slate-600 group-hover:text-slate-900 transition-colors">{status}</span>
            </div>
            <span className="text-xs text-slate-400 bg-slate-100 px-2 py-0.5 rounded-full">{count}</span>
          </label>
        ))}
      </FilterSection>

      {/* Division Filter */}
      <FilterSection title="Division">
        <select
          onChange={(e) => setFilters(prev => ({ ...prev, division: e.target.value }))}
          value={filters.division || ''}
          className="w-full bg-slate-50 border border-slate-300 rounded-lg p-2 text-sm text-slate-700 outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500"
        >
          <option value="">All Divisions</option>
          {stats?.location && Object.entries(stats.location).map(([location, count]) => (
            <option key={location} value={location}>{location} ({count})</option>
          ))}
        </select>
      </FilterSection>

      {/* Year Filter */}
      <FilterSection title="Year">
        <select
          onChange={(e) => setFilters(prev => ({ ...prev, year: e.target.value }))}
          value={filters.year || ''}
          className="w-full bg-slate-50 border border-slate-300 rounded-lg p-2 text-sm text-slate-700 outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500"
        >
          <option value="">All Time</option>
          {stats?.years && Object.entries(stats.years).map(([year, count]) => (
            <option key={year} value={year}>{year} ({count})</option>
          ))}
        </select>
      </FilterSection>



      {/* Species Filter */}
      <FilterSection title="Species">
        {stats?.species && Object.entries(stats.species).map(([species, count]) => (
          <label key={species} className="flex items-center justify-between cursor-pointer group select-none">
            <div className="flex items-center gap-2">
              <input 
                 type="checkbox"
                 checked={isSelected('species', species)}
                 onChange={() => handleFilterChange('species', species)}
                 className="w-4 h-4 rounded border-slate-300 text-emerald-600 focus:ring-emerald-500" 
              />
              <span className="text-sm text-slate-600 group-hover:text-slate-900 transition-colors truncate max-w-[120px]" title={species}>{species}</span>
            </div>
            <span className="text-xs text-slate-400 bg-slate-100 px-2 py-0.5 rounded-full">{count}</span>
          </label>
        ))}
      </FilterSection>
      
      {/* Location Filter */}
      <FilterSection title="Region / Division">
          {stats?.location && Object.entries(stats.location).map(([location, count]) => (
            <label key={location} className="flex items-center justify-between cursor-pointer group select-none">
              <div className="flex items-center gap-2">
                <input
                   type="checkbox"
                   checked={isSelected('location', location)}
                   onChange={() => handleFilterChange('location', location)}
                   className="w-4 h-4 rounded border-slate-300 text-emerald-600 focus:ring-emerald-500"
                />
                <span className="text-sm text-slate-600 group-hover:text-slate-900 transition-colors truncate max-w-[120px]" title={location}>{location}</span>
              </div>
              <span className="text-xs text-slate-400 bg-slate-100 px-2 py-0.5 rounded-full">{count}</span>
            </label>
          ))}
      </FilterSection>

      {/* Tags Filter */}
      <FilterSection title="Animal Tags">
        {stats?.tags && Object.entries(stats.tags).map(([tag, count]) => (
          <label key={tag} className="flex items-center justify-between cursor-pointer group select-none">
            <div className="flex items-center gap-2">
              <input
                 type="checkbox"
                 checked={isSelected('tags', tag)}
                 onChange={() => handleFilterChange('tags', tag)}
                 className="w-4 h-4 rounded border-slate-300 text-emerald-600 focus:ring-emerald-500"
              />
              <span className="text-sm text-slate-600 group-hover:text-slate-900 transition-colors truncate max-w-[120px]" title={tag}>{tag}</span>
            </div>
            <span className="text-xs text-slate-400 bg-slate-100 px-2 py-0.5 rounded-full">{count}</span>
          </label>
        ))}
      </FilterSection>
    </div>
  );
};

export default IncidentFilters;
