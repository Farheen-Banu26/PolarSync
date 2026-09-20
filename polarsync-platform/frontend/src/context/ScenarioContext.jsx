import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { getScenarios, getDashboardSummary, getMapTopology, checkHealth } from '../services/api';

const ScenarioContext = createContext();

export const ScenarioProvider = ({ children }) => {
  const [scenarioId, setScenarioId] = useState(1);
  const [scenarios, setScenarios] = useState([]);
  const [dashboardData, setDashboardData] = useState(null);
  const [mapData, setMapData] = useState(null);
  const [healthStatus, setHealthStatus] = useState({ online: true, sim: 'connected' });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Load scenarios on mount
  useEffect(() => {
    const initScenarios = async () => {
      try {
        const res = await getScenarios();
        setScenarios(res.scenarios || []);
      } catch (err) {
        console.error('Failed to load scenarios list:', err);
      }
    };
    initScenarios();
  }, []);

  // Fetch dashboard and map data whenever scenarioId changes
  const fetchScenarioData = useCallback(async (scId) => {
    setLoading(true);
    setError(null);
    try {
      const [dashRes, mapRes, healthRes] = await Promise.all([
        getDashboardSummary(scId),
        getMapTopology(scId),
        checkHealth()
      ]);
      setDashboardData(dashRes);
      setMapData(mapRes);
      setHealthStatus({
        online: healthRes.online,
        sim: healthRes.data?.simulation_engine || 'connected'
      });
    } catch (err) {
      console.error(`Failed to load scenario ${scId} data:`, err);
      setError(err.response?.data?.detail || err.message || 'Error connecting to PolarSync API');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchScenarioData(scenarioId);
  }, [scenarioId, fetchScenarioData]);

  const value = {
    scenarioId,
    setScenarioId,
    scenarios,
    dashboardData,
    mapData,
    healthStatus,
    loading,
    error,
    refreshData: () => fetchScenarioData(scenarioId),
  };

  return (
    <ScenarioContext.Provider value={value}>
      {children}
    </ScenarioContext.Provider>
  );
};

export const useScenario = () => {
  const context = useContext(ScenarioContext);
  if (!context) {
    throw new Error('useScenario must be used within a ScenarioProvider');
  }
  return context;
};

export default ScenarioContext;
