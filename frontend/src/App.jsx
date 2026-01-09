import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import AppShell from './components/layout/AppShell';
import Dashboard from './pages/Dashboard';
import Incidents from './pages/Incidents';
import BulkUpload from './pages/BulkUpload';
import Assistant from './pages/Assistant';

const App = () => {
  return (
    <Routes>
      <Route element={<AppShell />}>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/incidents" element={<Incidents />} />
        <Route path="/bulk-upload" element={<BulkUpload />} />
        <Route path="/assistant" element={<Assistant />} />
      </Route>
    </Routes>
  );
};

export default App;
