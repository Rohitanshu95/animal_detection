import React, { useState, useMemo } from 'react';
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
   const [searchTerms, setSearchTerms] = useState({
     species: '',
     location: '',
     tags: ''
   });

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

   // Calculate active filter count
   const activeFilterCount = useMemo(() => {
     return Object.values(filters).reduce((count, filterArray) => {
       return count + (Array.isArray(filterArray) ? filterArray.length : (filterArray ? 1 : 0));
     }, 0);
   }, [filters]);

   const clearAllFilters = () => {
     setFilters({});
     setSearchTerms({ species: '', location: '', tags: '' });
   };

   // Filter options based on search
   const filteredOptions = (category, options) => {
     const searchTerm = searchTerms[category]?.toLowerCase() || '';
     return Object.entries(options).filter(([key]) =>
       key.toLowerCase().includes(searchTerm)
     );
   };

  return (
    <div className="w-full h-full border-r border-slate-200 p-6 flex flex-col overflow-y-auto bg-white">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-4">
          <h3 className="font-bold text-slate-900 flex items-center gap-2">
            <Filter className="w-4 h-4 text-emerald-600" />
            Filter Archive
          </h3>
          {activeFilterCount > 0 && (
            <span className="text-xs bg-emerald-100 text-emerald-700 px-2 py-1 rounded-full font-medium">
              {activeFilterCount} active
            </span>
          )}
        </div>
        <div className="flex items-center gap-2">
          {activeFilterCount > 0 && (
            <button
              onClick={clearAllFilters}
              className="text-xs text-slate-500 hover:text-slate-700 underline"
            >
              Clear All
            </button>
          )}
          {onClose && (
            <button onClick={onClose} className="lg:hidden p-1 text-slate-400">
              <X className="w-5 h-5" />
            </button>
          )}
        </div>
      </div>

      {/* Status Filter */}
      <FilterSection title="Status">
        {stats?.status && Object.entries(stats.status).map(([status, count], index) => (
          <label key={index} className="flex items-center justify-between cursor-pointer group select-none">
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


      {/* Year Filter */}
      <FilterSection title="Year">
        <select
          onChange={(e) => setFilters(prev => ({ ...prev, year: e.target.value }))}
          value={filters.year || ''}
          className="w-full bg-slate-50 border border-slate-300 rounded-lg p-2 text-sm text-slate-700 outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500"
        >
          <option value="">All Time</option>
          {stats?.years && Object.entries(stats.years).map(([year, count], index) => (
            <option key={index} value={year}>{year} ({count})</option>
          ))}
        </select>
      </FilterSection>



      {/* Species Filter */}
      <FilterSection title="Species">
        <div className="mb-3">
          <div className="relative">
            <Search className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              placeholder="Search species..."
              value={searchTerms.species}
              onChange={(e) => setSearchTerms(prev => ({ ...prev, species: e.target.value }))}
              className="w-full pl-9 pr-3 py-2 bg-slate-50 border border-slate-300 rounded-lg text-sm text-slate-700 outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500"
            />
          </div>
        </div>
        <div className="max-h-48 overflow-y-auto">
          {stats?.species && filteredOptions('species', stats.species).map(([species, count], index) => (
            <label key={index} className="flex items-center justify-between cursor-pointer group select-none py-1">
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
        </div>
      </FilterSection>
      
      {/* Location Filter */}
      <FilterSection title="Region / Division">
        <div className="mb-3">
          <div className="relative">
            <Search className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              placeholder="Search locations..."
              value={searchTerms.location}
              onChange={(e) => setSearchTerms(prev => ({ ...prev, location: e.target.value }))}
              className="w-full pl-9 pr-3 py-2 bg-slate-50 border border-slate-300 rounded-lg text-sm text-slate-700 outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500"
            />
          </div>
        </div>
        <div className="max-h-48 overflow-y-auto">
          {stats?.location && filteredOptions('location', stats.location).map(([location, count], index) => (
            <label key={index} className="flex items-center justify-between cursor-pointer group select-none py-1">
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
        </div>
      </FilterSection>

      {/* Tags Filter */}
      <FilterSection title="Animal Tags">
        <div className="mb-3">
          <div className="relative">
            <Search className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              placeholder="Search tags..."
              value={searchTerms.tags}
              onChange={(e) => setSearchTerms(prev => ({ ...prev, tags: e.target.value }))}
              className="w-full pl-9 pr-3 py-2 bg-slate-50 border border-slate-300 rounded-lg text-sm text-slate-700 outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500"
            />
          </div>
        </div>
        <div className="max-h-48 overflow-y-auto">
          {stats?.tags && filteredOptions('tags', stats.tags).map(([tag, count], index) => (
            <label key={`${tag}-${index}`} className="flex items-center justify-between cursor-pointer group select-none py-1">
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
        </div>
      </FilterSection>
    </div>
  );
};

export default IncidentFilters;
