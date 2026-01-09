import React, { useState } from 'react';
import { Upload, FileSpreadsheet, CheckCircle, AlertTriangle, ArrowRight, X } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';


const BulkUpload = () => {
  const [step, setStep] = useState('upload'); // upload, review, success
  const [uploading, setUploading] = useState(false);
  const [file, setFile] = useState(null);
  const [parsedIncidents, setParsedIncidents] = useState([]);
  const [error, setError] = useState(null);

  const handleFileDrop = async (e) => {
    e.preventDefault();
    const droppedFile = e.dataTransfer?.files[0] || e.target.files[0];
    if (droppedFile) {
      setFile(droppedFile);
      setUploading(true);
      setError(null);

      const formData = new FormData();
      formData.append('file', droppedFile);

      try {
        // Use the excel/parse endpoint to preview data
        const response = await axios.post('http://localhost:8000/excel/parse', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });
        
        if (response.data.success) {
          setParsedIncidents(response.data.incidents);
          setStep('review');
        } else {
          setError('Failed to parse file. Please check format.');
        }
      } catch (err) {
        console.error(err);
        setError('Error uploading file. ' + (err.response?.data?.detail || err.message));
      } finally {
        setUploading(false);
      }
    }
  };

  const handleCommit = async () => {
    setUploading(true);
    try {
      // Send the reviewed JSON data to the batch endpoint
      await axios.post('http://localhost:8000/incidents/batch', parsedIncidents);
      setStep('success');
    } catch (err) {
      console.error(err);
      setError('Import failed. ' + (err.response?.data?.detail || err.message));
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">Bulk Import</h1>
        <p className="text-slate-400">Upload Excel/CSV manifests to batch import incidents.</p>
      </div>

      {/* Wizard Steps */}
      <div className="flex items-center gap-4 mb-12">
        {['upload', 'review', 'success'].map((s, i) => (
          <React.Fragment key={s}>
            <div className={`flex items-center gap-2 ${step === s ? 'text-emerald-400' : 'text-slate-600'}`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center border ${step === s ? 'border-emerald-500 bg-emerald-500/20' : 'border-slate-700'}`}>
                {i + 1}
              </div>
              <span className="capitalize font-medium">{s}</span>
            </div>
            {i < 2 && <div className="h-px bg-slate-800 flex-1 min-w-[50px]" />}
          </React.Fragment>
        ))}
      </div>

      <AnimatePresence mode="wait">
        {step === 'upload' && (
          <motion.div 
            initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }}
            className="glass-card p-12 rounded-2xl border-2 border-dashed border-slate-700 flex flex-col items-center justify-center text-center hover:border-emerald-500/50 transition-colors"
            onDragOver={(e) => e.preventDefault()}
            onDrop={handleFileDrop}
          >
            <div className="w-20 h-20 bg-slate-800 rounded-full flex items-center justify-center mb-6">
              <Upload className="w-10 h-10 text-emerald-500" />
            </div>
            <h3 className="text-xl font-semibold text-white mb-2">Drag & Drop your file here</h3>
            <p className="text-slate-400 mb-8">Supports .xlsx and .csv files (Max 50MB)</p>
            <label className="bg-emerald-600 hover:bg-emerald-500 text-white px-6 py-3 rounded-lg font-medium cursor-pointer transition-colors">
              Browse Files
              <input type="file" className="hidden" accept=".xlsx,.csv" onChange={handleFileDrop} />
            </label>
            {uploading && <p className="mt-4 text-emerald-400 animate-pulse">Parsing file...</p>}
            {error && <p className="mt-4 text-red-500">{error}</p>}
          </motion.div>
        )}

        {step === 'review' && (
          <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }}>
            {/* Header / Stats */}
            <div className="glass-card rounded-xl overflow-hidden mb-6">
              <div className="p-4 bg-slate-800/50 border-b border-white/5 flex justify-between items-center">
                <div className="flex items-center gap-4">
                  <div className="p-3 bg-emerald-900/30 rounded-lg border border-emerald-500/20 text-emerald-400">
                    <FileSpreadsheet className="w-6 h-6" />
                  </div>
                  <div>
                    <h4 className="font-bold text-white text-lg">{file?.name}</h4>
                    <div className="flex items-center gap-3 text-sm text-slate-400">
                       <span>{parsedIncidents.length} Records Found</span>
                       <span className="w-1 h-1 bg-slate-600 rounded-full"/>
                       <span>{parsedIncidents.filter(i => i.ai_enriched).length} AI Enriched</span>
                       <span className="w-1 h-1 bg-slate-600 rounded-full"/>
                       <span className="text-amber-400">{parsedIncidents.filter(i => !i.date || !i.location).length} Attention Needed</span>
                    </div>
                  </div>
                </div>
                <button onClick={() => setStep('upload')} className="p-2 hover:bg-white/5 rounded-full text-slate-400 hover:text-white transition-colors">
                  <X className="w-5 h-5" />
                </button>
              </div>

              {/* Review List */}
              <div className="max-h-[600px] overflow-y-auto p-4 space-y-4 bg-slate-900/50">
                {parsedIncidents.map((incident, index) => (
                  <div key={index} className="bg-slate-800/40 border border-slate-700/50 rounded-xl p-4 hover:border-emerald-500/30 transition-all group">
                    {/* Top Row: Meta + Status */}
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex items-center gap-3">
                         <span className="bg-slate-800 text-slate-400 text-xs font-mono px-2 py-1 rounded border border-slate-700">#{index + 1}</span>
                         {incident.quarter_number && (
                           <span className="text-xs font-medium text-emerald-600 bg-emerald-900/20 px-2 py-1 rounded border border-emerald-900/30">
                             Q{incident.quarter_number} / {incident.quarter_date_range}
                           </span>
                         )}
                      </div>
                      <div className="flex items-center gap-2">
                         {/* Status Selector */}
                         <select 
                            value={incident.status || 'Reported'}
                            onChange={(e) => {
                               const newIncidents = [...parsedIncidents];
                               newIncidents[index].status = e.target.value;
                               setParsedIncidents(newIncidents);
                            }}
                            className="bg-slate-900 border border-slate-700 text-slate-300 text-xs rounded-md px-2 py-1 focus:ring-1 focus:ring-emerald-500 focus:border-emerald-500"
                         >
                            <option value="Reported">Reported</option>
                            <option value="Investigated">Investigated</option>
                            <option value="Case Closed">Case Closed</option>
                         </select>
                         <button 
                            onClick={() => {
                                const newIncidents = parsedIncidents.filter((_, i) => i !== index);
                                setParsedIncidents(newIncidents);
                            }}
                            className="text-slate-500 hover:text-red-400 p-1"
                            title="Remove Incident"
                         >
                            <X className="w-4 h-4" />
                         </button>
                      </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      {/* Left: Original / Source Context */}
                      <div className="space-y-3">
                         <div className="flex items-center gap-2 text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">
                           <FileSpreadsheet className="w-3 h-3" /> Source Data
                         </div>
                         
                         <div>
                            <label className="text-xs text-slate-500 block mb-1">Raw Description</label>
                            <p className="text-sm text-slate-300 bg-slate-900/50 p-3 rounded-lg border border-slate-800 leading-relaxed italic">
                              "{incident.description}"
                            </p>
                         </div>
                         
                         <div className="grid grid-cols-2 gap-3">
                            <div>
                               <label className="text-xs text-slate-500 block mb-1">Page No</label>
                               <input 
                                  type="text" 
                                  value={incident.page_no || ''} 
                                  readOnly
                                  className="w-full bg-slate-900/30 border border-slate-800 text-slate-400 text-sm rounded px-3 py-1.5 cursor-not-allowed"
                               />
                            </div>
                            <div>
                               <label className="text-xs text-slate-500 block mb-1">Original Date</label>
                               <div className="bg-slate-900/30 border border-slate-800 text-slate-400 text-sm rounded px-3 py-1.5 truncate">
                                  {incident.raw_date}
                               </div>
                            </div>
                         </div>
                      </div>

                      {/* Right: AI Extracted / Editable */}
                      <div className="space-y-3 border-l border-white/5 pl-6">
                         <div className="flex items-center gap-2 text-xs font-semibold text-emerald-500 uppercase tracking-wider mb-2">
                           <CheckCircle className="w-3 h-3" /> Extracted & Normalized
                         </div>

                         <div className="grid grid-cols-2 gap-3">
                            <div>
                               <label className="text-xs text-slate-500 block mb-1">Date (YYYY-MM-DD)</label>
                               <input 
                                  type="date"
                                  value={incident.date || ''}
                                  onChange={(e) => {
                                     const newIncidents = [...parsedIncidents];
                                     newIncidents[index].date = e.target.value;
                                     setParsedIncidents(newIncidents);
                                  }}
                                  className={`w-full bg-slate-900 border ${!incident.date ? 'border-amber-500/50 bg-amber-900/10' : 'border-slate-700'} text-white text-sm rounded px-3 py-1.5 focus:ring-1 focus:ring-emerald-500 transition-colors`}
                               />
                            </div>
                            <div>
                               <label className="text-xs text-slate-500 block mb-1">Location / Division</label>
                               <input 
                                  type="text"
                                  value={incident.location || ''}
                                  onChange={(e) => {
                                     const newIncidents = [...parsedIncidents];
                                     newIncidents[index].location = e.target.value;
                                     setParsedIncidents(newIncidents);
                                  }}
                                  className="w-full bg-slate-900 border border-slate-700 text-white text-sm rounded px-3 py-1.5 focus:ring-1 focus:ring-emerald-500"
                               />
                            </div>
                         </div>

                         <div>
                            <label className="text-xs text-slate-500 block mb-1">Entities Detected (Animals & Products)</label>
                            <input 
                               type="text"
                               value={incident.animals || ''}
                               onChange={(e) => {
                                  const newIncidents = [...parsedIncidents];
                                  newIncidents[index].animals = e.target.value;
                                  setParsedIncidents(newIncidents);
                               }}
                               placeholder="e.g. Elephant Tusks, Pangolin"
                               className="w-full bg-slate-900 border border-slate-700 text-emerald-300 font-medium text-sm rounded px-3 py-1.5 focus:ring-1 focus:ring-emerald-500"
                            />
                         </div>

                         <div className="grid grid-cols-2 gap-3">
                            <div>
                               <label className="text-xs text-slate-500 block mb-1">Quantity</label>
                               <input 
                                  type="text"
                                  value={incident.quantity || ''}
                                  onChange={(e) => {
                                     const newIncidents = [...parsedIncidents];
                                     newIncidents[index].quantity = e.target.value;
                                     setParsedIncidents(newIncidents);
                                  }}
                                  placeholder="e.g. 5 kg"
                                  className="w-full bg-slate-900 border border-slate-700 text-white text-sm rounded px-3 py-1.5 focus:ring-1 focus:ring-emerald-500"
                               />
                            </div>
                            <div>
                               <label className="text-xs text-slate-500 block mb-1">Source / Agency</label>
                               <input 
                                  type="text"
                                  value={incident.source || ''}
                                  onChange={(e) => {
                                     const newIncidents = [...parsedIncidents];
                                     newIncidents[index].source = e.target.value;
                                     setParsedIncidents(newIncidents);
                                  }}
                                  placeholder="e.g. Forest Dept"
                                  className="w-full bg-slate-900 border border-slate-700 text-white text-sm rounded px-3 py-1.5 focus:ring-1 focus:ring-emerald-500"
                               />
                            </div>
                         </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
            
            {error && <div className="mb-4 text-rose-400 bg-rose-950/20 border border-rose-900/50 p-3 rounded-lg text-center text-sm">{error}</div>}

            <div className="flex justify-end gap-3 mt-6">
              <button 
                onClick={() => setStep('upload')} 
                className="px-6 py-2.5 rounded-lg border border-slate-700 text-slate-300 font-medium hover:bg-slate-800 transition-all"
              >
                Cancel
              </button>
              <button 
                onClick={handleCommit} 
                className="px-8 py-2.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-bold shadow-lg shadow-emerald-500/20 flex items-center gap-2 transition-all hover:scale-[1.02] active:scale-[0.98]"
              >
                {uploading ? (
                   <>
                     <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                     Importing...
                   </>
                ) : (
                   <>
                     Approve & Import {parsedIncidents.length} Records
                     <ArrowRight className="w-5 h-5" />
                   </>
                )}
              </button>
            </div>
          </motion.div>
        )}

        {step === 'success' && (
          <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} className="text-center py-20">
            <div className="w-24 h-24 bg-emerald-500/20 rounded-full flex items-center justify-center mx-auto mb-6 border border-emerald-500/50">
              <CheckCircle className="w-12 h-12 text-emerald-500" />
            </div>
            <h2 className="text-3xl font-bold text-white mb-2">Import Successful!</h2>
            <p className="text-slate-400 mb-8">{parsedIncidents.length} incidents have been added to the database.</p>
            <button onClick={() => setStep('upload')} className="text-emerald-400 hover:text-emerald-300 font-medium">Upload another file</button>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default BulkUpload;
