import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ConnectivityProvider } from './context/ConnectivityContext';
import { ScenarioProvider } from './context/ScenarioContext';
import AppLayout from './components/layout/AppLayout';
import DashboardPage from './pages/DashboardPage';
import ExpeditionPage from './pages/ExpeditionPage';
import CargoPage from './pages/CargoPage';
import InventoryPage from './pages/InventoryPage';
import PersonnelPage from './pages/PersonnelPage';
import AssetsPage from './pages/AssetsPage';
import EmergencyPage from './pages/EmergencyPage';
import ConnectivityPage from './pages/ConnectivityPage';
import AlertsPage from './pages/AlertsPage';

export function App() {
  return (
    <BrowserRouter>
      <ConnectivityProvider>
        <ScenarioProvider>
          <Routes>
            <Route path="/" element={<AppLayout />}>
              <Route index element={<Navigate to="/dashboard" replace />} />
              <Route path="dashboard" element={<DashboardPage />} />
              <Route path="expedition" element={<ExpeditionPage />} />
              <Route path="cargo" element={<CargoPage />} />
              <Route path="inventory" element={<InventoryPage />} />
              <Route path="personnel" element={<PersonnelPage />} />
              <Route path="assets" element={<AssetsPage />} />
              <Route path="emergency" element={<EmergencyPage />} />
              <Route path="connectivity" element={<ConnectivityPage />} />
              <Route path="alerts" element={<AlertsPage />} />
              <Route path="*" element={<Navigate to="/dashboard" replace />} />
            </Route>
          </Routes>
        </ScenarioProvider>
      </ConnectivityProvider>
    </BrowserRouter>
  );
}

export default App;
