import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, FileText, Upload, Bot, Settings, Leaf } from 'lucide-react';
import { cn } from "../../lib/utils";

const Sidebar = () => {
  const navItems = [
    { icon: LayoutDashboard, label: 'Dashboard', path: '/dashboard' },
    { icon: FileText, label: 'Incidents', path: '/incidents' },
    { icon: Upload, label: 'Bulk Upload', path: '/bulk-upload' },
    { icon: Bot, label: 'AI Assistant', path: '/assistant' },
  ];

  return (
    <aside className="w-64 h-screen fixed left-0 top-0 z-40 border-r border-slate-200 bg-white flex flex-col shadow-sm">
      <div className="p-6 flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-emerald-50 bg-gradient-to-br from-emerald-500 to-emerald-600 flex items-center justify-center shadow-lg shadow-emerald-500/20">
          <Leaf className="text-white w-6 h-6" />
        </div>
        <div>
          <h1 className="font-bold text-lg tracking-tight text-slate-900">EcoGuard</h1>
          <p className="text-xs text-slate-500">Wildlife Archive</p>
        </div>
      </div>

      <nav className="flex-1 px-4 py-6 space-y-2">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              cn(
                "flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 group relative overflow-hidden",
                isActive 
                  ? "bg-emerald-50 text-emerald-700 font-semibold border border-emerald-100" 
                  : "text-slate-500 hover:text-slate-900 hover:bg-slate-50"
              )
            }
          >
            {({ isActive }) => (
              <>
                <item.icon className={cn("w-5 h-5 relative z-10", isActive ? "text-emerald-600" : "text-slate-400")} />
                <span className="relative z-10">{item.label}</span>
                {isActive && <div className="absolute left-0 top-0 bottom-0 w-1 bg-emerald-500 rounded-r-full" />}
              </>
            )}
          </NavLink>
        ))}
      </nav>

      <div className="p-4 border-t border-slate-100 mx-4">
        <button className="flex items-center gap-3 px-4 py-3 text-slate-500 hover:text-slate-900 transition-colors w-full rounded-lg hover:bg-slate-50">
          <Settings className="w-5 h-5" />
          <span className="font-medium">Settings</span>
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;
