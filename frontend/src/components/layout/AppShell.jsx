import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';

const AppShell = () => {
  const [isCollapsed, setIsCollapsed] = useState(false);

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 relative">
      {/* Subtle Background Accents */}
      <div className="fixed top-0 right-0 w-[500px] h-[500px] rounded-full bg-emerald-500/5 blur-[100px] pointer-events-none" />
      <div className="fixed bottom-0 left-0 w-[500px] h-[500px] rounded-full bg-amber-400/5 blur-[100px] pointer-events-none" />

      <Sidebar isCollapsed={isCollapsed} toggle={() => setIsCollapsed(!isCollapsed)} />
      
      <main className={`min-h-screen relative z-10 transition-all duration-300 ease-in-out ${isCollapsed ? 'ml-20' : 'ml-64'}`}>
        <div className="p-8 max-w-7xl mx-auto animate-in fade-in duration-500 slide-in-from-bottom-4">
          <Outlet />
        </div>
      </main>
    </div>
  );
};

export default AppShell;
