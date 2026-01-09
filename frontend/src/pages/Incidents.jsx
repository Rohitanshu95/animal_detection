
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import IncidentFilters from '../components/incidents/IncidentFilters';
import IncidentCard from '../components/incidents/IncidentCard';
import IncidentFormModal from '../components/incidents/IncidentFormModal';
import { Plus, Search, Loader, X, MapPin, Calendar, Bot } from 'lucide-react';

// Mock data
const MOCK_INCIDENTS = Array.from({ length: 9 }).map((_, i) => ({
  _id: `inc_${i}`,
  date: '2025-01-08',
  location: ['Baripada Division', 'Athagarh', 'Similipal Reserve'][i % 3],
  animals: ['Asian Elephant', 'Pangolin Scales', 'Leopard Skin'][i % 3],
  description: 'Seizure of wildlife products found during routine patrol near the northern boundary.',
  status: ['Reported', 'Investigated', 'Closed'][i % 3]
}));

const Incidents = () => {
  const [incidents, setIncidents] = useState([]);
  const [selectedIncident, setSelectedIncident] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState({});

  const fetchIncidents = async () => {
    setIsLoading(true);
    try {
      const params = new URLSearchParams();
      if (searchQuery) params.append('search', searchQuery);
      // Add other filters as needed by your backend API
      
      const response = await axios.get(`http://localhost:8000/incidents?${params.toString()}`);
      setIncidents(response.data);
    } catch (error) {
      console.error("Failed to fetch incidents:", error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    const timer = setTimeout(() => {
      fetchIncidents();
    }, 500); // Debounce search
    return () => clearTimeout(timer);
  }, [searchQuery, filters]);

  const handleIncidentCreated = () => {
    fetchIncidents();
    setIsModalOpen(false);
  };

  return (
    <div className="flex h-screen -m-8 overflow-hidden">
      {/* Filters Sidebar */}
      <div className="hidden lg:block w-72 h-full border-r border-slate-200 bg-white shrink-0 z-10">
        <IncidentFilters filters={filters} setFilters={setFilters} />
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-y-auto bg-slate-50/50">
        <div className="sticky top-0 z-20 bg-white/80 backdrop-blur-sm border-b border-slate-200 px-8 py-4 flex justify-between items-center gap-4">
          <div className="relative flex-1 max-w-2xl">
            <Search className="w-5 h-5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input 
              type="text" 
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search by description, animal, or location..." 
              className="w-full bg-slate-100 border-transparent focus:bg-white border focus:border-emerald-500 rounded-full py-2.5 pl-10 pr-4 text-sm text-slate-800 focus:outline-none transition-all"
            />
          </div>
          
          <button 
            onClick={() => setIsModalOpen(true)}
            className="flex items-center gap-2 bg-emerald-600 hover:bg-emerald-700 text-white px-5 py-2.5 rounded-full font-bold shadow-md hover:shadow-lg transition-all"
          >
            <Plus className="w-5 h-5" />
            New Entry
          </button>
        </div>

        <div className="p-8">
          {isLoading ? (
            <div className="flex justify-center py-20">
              <Loader className="w-8 h-8 animate-spin text-emerald-600" />
            </div>
          ) : incidents.length === 0 ? (
            <div className="text-center py-20 text-slate-500">
              No incidents found matching your criteria.
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6 mb-8">
              {incidents.map((incident) => (
                <IncidentCard 
                  key={incident._id} 
                  incident={incident} 
                  onClick={setSelectedIncident}
                />
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Detail Drawer */}
      {selectedIncident && (
        <div 
          className="fixed inset-y-0 right-0 w-full max-w-2xl bg-white border-l border-slate-200 z-50 shadow-2xl animate-in slide-in-from-right duration-300 flex flex-col"
        >
          {/* Drawer Header */}
          <div className="px-8 py-6 border-b border-slate-100 flex items-start justify-between bg-slate-50/50">
            <div>
              <div className="flex items-center gap-3 mb-2">
                <span className="px-3 py-1 rounded-full text-xs font-bold bg-amber-50 text-amber-700 border border-amber-100 uppercase tracking-wide">
                  {selectedIncident.status || 'Reported'}
                </span>
                <span className="text-xs font-mono text-slate-400">ID: {selectedIncident._id}</span>
              </div>
              <h2 className="text-3xl font-bold text-slate-900 leading-tight">{selectedIncident.title || 'Untitled Incident'}</h2>
            </div>
            <button 
              onClick={() => setSelectedIncident(null)} 
              className="p-2 rounded-full hover:bg-slate-200 text-slate-400 hover:text-slate-700 transition-colors"
            >
              <X className="w-6 h-6" />
            </button>
          </div>

          {/* Drawer Content */}
          <div className="flex-1 overflow-y-auto p-8 space-y-8">
            {/* Key Metadata Card */}
            <div className="grid grid-cols-2 gap-4">
              <div className="p-4 rounded-xl bg-slate-50 border border-slate-100">
                <div className="flex items-center gap-2 text-slate-500 mb-1">
                  <MapPin className="w-4 h-4 text-emerald-600" />
                  <span className="text-xs font-bold uppercase tracking-wider">Location</span>
                </div>
                <p className="font-semibold text-slate-900">{selectedIncident.location}</p>
              </div>
              <div className="p-4 rounded-xl bg-slate-50 border border-slate-100">
                <div className="flex items-center gap-2 text-slate-500 mb-1">
                  <Calendar className="w-4 h-4 text-emerald-600" />
                  <span className="text-xs font-bold uppercase tracking-wider">Date</span>
                </div>
                <p className="font-semibold text-slate-900">{new Date(selectedIncident.created_at).toLocaleDateString()}</p>
              </div>
            </div>

            {/* Description Section */}
            <div>
              <h3 className="text-sm font-bold text-slate-900 uppercase tracking-widest mb-4 border-b border-slate-100 pb-2">
                Incident Description
              </h3>
              <div className="prose prose-slate max-w-none text-slate-600 leading-relaxed">
                <p>{selectedIncident.description}</p>
              </div>
            </div>

            {/* AI Analysis Section */}
            <div className="bg-emerald-50/50 rounded-xl p-6 border border-emerald-100">
              <h4 className="flex items-center gap-2 font-bold text-emerald-800 mb-3">
                <Bot className="w-5 h-5" />
                AI Intelligence Analysis
              </h4>
              <ul className="space-y-2 text-sm text-emerald-700">
                 {selectedIncident.extracted_animals && selectedIncident.extracted_animals.length > 0 ? (
                    <li className="flex items-start gap-2">
                      <span className="mt-1.5 w-1.5 h-1.5 rounded-full bg-emerald-500 flex-shrink-0" />
                      <span>Identified Species: <strong>{selectedIncident.extracted_animals.join(', ')}</strong></span>
                    </li>
                 ) : (
                    <li className="flex items-start gap-2">
                      <span className="mt-1.5 w-1.5 h-1.5 rounded-full bg-emerald-500 flex-shrink-0" />
                      <span>No specific animals extracted.</span>
                    </li>
                 )}
                 {selectedIncident.ai_summary && (
                    <li className="flex items-start gap-2">
                      <span className="mt-1.5 w-1.5 h-1.5 rounded-full bg-emerald-500 flex-shrink-0" />
                      <span>{selectedIncident.ai_summary}</span>
                    </li>
                 )}
              </ul>
            </div>
          </div>

          {/* Drawer Footer */}
          <div className="p-6 border-t border-slate-100 bg-slate-50 flex justify-end gap-3">
            <button className="px-5 py-2.5 rounded-lg border border-slate-200 text-slate-600 font-semibold hover:bg-white hover:border-slate-300 transition-all">
              Edit Record
            </button>
            <button className="px-5 py-2.5 rounded-lg bg-emerald-600 text-white font-bold hover:bg-emerald-700 shadow-lg shadow-emerald-500/20 transition-all">
              Generate Report
            </button>
          </div>
        </div>
      )}

      <IncidentFormModal 
        isOpen={isModalOpen} 
        onClose={() => setIsModalOpen(false)} 
        onSuccess={handleIncidentCreated}
      />
    </div>
  );
};

export default Incidents;

