import React from 'react';
import { Search, Filter, X } from 'lucide-react';

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

const IncidentFilters = ({ onClose }) => {
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

      <FilterSection title="Status">
        <Checkbox label="Reported" count="12" />
        <Checkbox label="Investigated" count="5" />
        <Checkbox label="Closed" count="89" />
        <Checkbox label="Prosecuted" count="3" />
      </FilterSection>

      <FilterSection title="Year">
        <select className="w-full bg-slate-50 border border-slate-300 rounded-lg p-2 text-sm text-slate-700 outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500">
          <option>All Time</option>
          <option>2024</option>
          <option>2023</option>
          <option>2022</option>
        </select>
      </FilterSection>

      <FilterSection title="Species">
        <Checkbox label="Elephant" count="45" />
        <Checkbox label="Pangolin" count="32" />
        <Checkbox label="Tiger" count="12" />
        <Checkbox label="Rhino" count="8" />
      </FilterSection>

      <FilterSection title="Region / Division">
        <Checkbox label="Baripada" count="24" />
        <Checkbox label="Athagarh" count="15" />
        <Checkbox label="Similipal" count="42" />
      </FilterSection>
    </div>
  );
};

export default IncidentFilters;
