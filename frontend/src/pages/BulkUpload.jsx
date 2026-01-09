import React, { useState } from 'react';
import { Upload, FileSpreadsheet, CheckCircle, AlertTriangle, ArrowRight, X } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const BulkUpload = () => {
  const [step, setStep] = useState('upload'); // upload, review, success
  const [uploading, setUploading] = useState(false);
  const [file, setFile] = useState(null);

  const handleFileDrop = (e) => {
    e.preventDefault();
    const droppedFile = e.dataTransfer?.files[0] || e.target.files[0];
    if (droppedFile) {
      setFile(droppedFile);
      // Simulate parsing delay
      setUploading(true);
      setTimeout(() => {
        setUploading(false);
        setStep('review');
      }, 1500);
    }
  };

  const handleCommit = () => {
    setUploading(true);
    setTimeout(() => {
      setUploading(false);
      setStep('success');
    }, 1500);
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
          </motion.div>
        )}

        {step === 'review' && (
          <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }}>
            <div className="glass-card rounded-xl overflow-hidden mb-6">
              <div className="p-4 bg-slate-800/50 border-b border-white/5 flex justify-between items-center">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-green-900/50 rounded text-green-400"><FileSpreadsheet className="w-5 h-5" /></div>
                  <div>
                    <h4 className="font-semibold text-white">{file?.name}</h4>
                    <p className="text-xs text-slate-400">14 Incidents detected • 2 Alerts</p>
                  </div>
                </div>
                <button onClick={() => setStep('upload')} className="text-slate-400 hover:text-white"><X className="w-5 h-5" /></button>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm text-slate-400">
                  <thead className="bg-slate-900/50 text-slate-200 uppercase text-xs font-semibold">
                    <tr>
                      <th className="p-4">Date</th>
                      <th className="p-4">Location</th>
                      <th className="p-4">Items</th>
                      <th className="p-4">Context</th>
                      <th className="p-4">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-white/5">
                    {[1, 2, 3].map((i) => (
                      <tr key={i} className="hover:bg-white/5">
                        <td className="p-4 text-white">2024-03-1{i}</td>
                        <td className="p-4">Kruger Park</td>
                        <td className="p-4 text-emerald-400">Ivory Tusks (12kg)</td>
                        <td className="p-4 truncate max-w-[200px]">Found concealed in cargo truck...</td>
                        <td className="p-4"><span className="px-2 py-1 bg-amber-500/10 text-amber-500 rounded text-xs border border-amber-500/20">Review</span></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
            
            <div className="flex justify-end gap-3">
              <button onClick={() => setStep('upload')} className="px-6 py-2 rounded-lg text-slate-300 hover:bg-slate-800">Cancel</button>
              <button onClick={handleCommit} className="px-6 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-medium flex items-center gap-2">
                {uploading ? 'Importing...' : 'Import 14 Incidents'} <ArrowRight className="w-4 h-4" />
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
            <p className="text-slate-400 mb-8">14 incidents have been added to the database.</p>
            <button onClick={() => setStep('upload')} className="text-emerald-400 hover:text-emerald-300 font-medium">Upload another file</button>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default BulkUpload;
