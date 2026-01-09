import React, { useState } from 'react';
import axios from 'axios';
import { X, Save, Loader } from 'lucide-react';

const IncidentFormModal = ({ isOpen, onClose, onSuccess }) => {
  const [formData, setFormData] = useState({
    description: '',
    location: '',
    date: new Date().toISOString().split('T')[0],
    source: '',
    status: 'Reported'
  });
  const [isSaving, setIsSaving] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async () => {
    if (!formData.description || !formData.location) return;

    setIsSaving(true);
    try {
      await axios.post('http://localhost:8000/incidents', formData);
      onSuccess?.();
      // Reset form
      setFormData({
        description: '',
        location: '',
        date: new Date().toISOString().split('T')[0],
        source: '',
        status: 'Reported'
      });
    } catch (error) {
      console.error("Failed to save incident:", error);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm animate-in fade-in">
      <div className="bg-white w-full max-w-2xl rounded-2xl overflow-hidden shadow-2xl animate-in zoom-in-95 border border-slate-100">
        <div className="p-6 border-b border-slate-100 flex justify-between items-center bg-slate-50/50">
          <h2 className="text-xl font-bold text-slate-900">Report New Incident</h2>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-700 transition-colors">
            <X className="w-6 h-6" />
          </button>
        </div>
        
        <div className="p-6 space-y-6 max-h-[70vh] overflow-y-auto">
          <div className="grid grid-cols-2 gap-6">
            <div className="space-y-2">
              <label className="text-sm font-bold text-slate-700">Date Observed</label>
              <input 
                type="date" 
                value={formData.date}
                onChange={e => setFormData({...formData, date: e.target.value})}
                className="w-full glass-input rounded-lg px-4 py-2 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-emerald-500/20" 
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-bold text-slate-700">Location</label>
              <input 
                type="text" 
                value={formData.location}
                onChange={e => setFormData({...formData, location: e.target.value})}
                placeholder="e.g. Baripada Division" 
                className="w-full glass-input rounded-lg px-4 py-2 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-emerald-500/20" 
              />
            </div>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-bold text-slate-700">Description</label>
            <textarea 
              value={formData.description}
              onChange={e => setFormData({...formData, description: e.target.value})}
              placeholder="Describe the incident details (Species will be auto-extracted)..." 
              className="w-full glass-input rounded-lg px-4 py-2 min-h-[120px] border border-slate-200 focus:outline-none focus:ring-2 focus:ring-emerald-500/20" 
            />
          </div>

          <div className="grid grid-cols-2 gap-6">
             <div className="space-y-2">
              <label className="text-sm font-bold text-slate-700">Source</label>
              <input 
                type="text" 
                value={formData.source}
                onChange={e => setFormData({...formData, source: e.target.value})}
                placeholder="Reporting Agency" 
                className="w-full glass-input rounded-lg px-4 py-2 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-emerald-500/20" 
              />
            </div>
             <div className="space-y-2">
              <label className="text-sm font-bold text-slate-700">Status</label>
              <select 
                value={formData.status}
                onChange={e => setFormData({...formData, status: e.target.value})}
                className="w-full glass-input rounded-lg px-4 py-2 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-emerald-500/20"
              >
                <option>Reported</option>
                <option>Investigated</option>
                <option>Closed</option>
              </select>
            </div>
          </div>
        </div>

        <div className="p-6 border-t border-slate-100 bg-slate-50/50 flex justify-end gap-3">
          <button onClick={onClose} className="px-6 py-2 rounded-lg text-slate-600 hover:bg-slate-100 transition-colors font-medium">Cancel</button>
          <button 
            onClick={handleSubmit}
            disabled={isSaving}
            className="px-6 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white font-bold flex items-center gap-2 shadow-lg shadow-emerald-500/20 transition-all disabled:opacity-50"
          >
            {isSaving ? <Loader className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
            {isSaving ? 'Saving...' : 'Save Report'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default IncidentFormModal;
