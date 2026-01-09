import React from 'react';
import { MapPin, Calendar, MoreHorizontal, Eye } from 'lucide-react';
import { motion } from 'framer-motion';

const IncidentCard = ({ incident, onClick }) => {
  return (
    <motion.div
      whileHover={{ y: -4 }}
      onClick={() => onClick(incident)}
      className="bg-white rounded-xl p-5 cursor-pointer border border-slate-200 shadow-sm hover:shadow-lg hover:border-emerald-200 transition-all group"
    >
      <div className="flex justify-between items-start mb-4">
        <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-amber-50 text-amber-700 border border-amber-100">
          {incident.status}
        </span>
        <button className="p-1 rounded-full hover:bg-slate-100 text-slate-400 hover:text-slate-600 transition-colors">
          <MoreHorizontal className="w-4 h-4" />
        </button>
      </div>

      <h3 className="font-bold text-lg text-slate-900 mb-2 truncate group-hover:text-emerald-700 transition-colors">
        {incident.animals}
      </h3>

      <div className="space-y-2 mb-4">
        <div className="flex items-center gap-2 text-sm text-slate-500">
          <MapPin className="w-4 h-4 text-emerald-600" />
          <span className="truncate">{incident.location}</span>
        </div>
        <div className="flex items-center gap-2 text-sm text-slate-500">
          <Calendar className="w-4 h-4 text-emerald-600" />
          <span>{incident.date}</span>
        </div>
      </div>

      <p className="text-sm text-slate-600 line-clamp-2 mb-4 h-10 leading-relaxed">
        {incident.description}
      </p>

      <div className="flex items-center justify-between pt-4 border-t border-slate-100">
        <div className="flex items-center gap-2">
          <span className="text-xs font-mono text-slate-400">
            ID: {incident._id.slice(-6)}
          </span>
        </div>
        <button className="flex items-center gap-1 text-xs font-bold text-emerald-600 opacity-0 group-hover:opacity-100 transition-opacity">
          View Details <Eye className="w-3 h-3" />
        </button>
      </div>
    </motion.div>
  );
};

export default IncidentCard;
