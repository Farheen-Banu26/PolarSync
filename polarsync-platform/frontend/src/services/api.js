import axios from 'axios';
import { cacheResource, getCachedResource } from './db';

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8001/api/v1';

const apiClient = axios.create({
  baseURL: BASE_URL,
  timeout: 6000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Automatically attach auth token if present
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('polarsync_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}, (error) => Promise.reject(error));

// Connectivity event callbacks
let onConnectivityChangeCallback = null;

export const setConnectivityListener = (callback) => {
  onConnectivityChangeCallback = callback;
};

const notifyConnectivity = (isOnline, reason = null) => {
  if (onConnectivityChangeCallback) {
    onConnectivityChangeCallback(isOnline, reason);
  }
};

/**
 * Universal Cache-First / Network-Fallback helper
 */
const fetchWithCacheFallback = async (endpoint, params, resource, scenarioId) => {
  try {
    const response = await apiClient.get(endpoint, { params });
    notifyConnectivity(true);
    
    // Save to IndexedDB cache
    if (scenarioId && resource) {
      cacheResource(scenarioId, resource, response.data);
    }
    
    if (Array.isArray(response.data)) {
      const arr = [...response.data];
      arr._isCached = false;
      arr._cachedAt = new Date().toISOString();
      return arr;
    }

    return {
      ...response.data,
      _isCached: false,
      _cachedAt: new Date().toISOString()
    };
  } catch (err) {
    console.warn(`API call failed for ${endpoint}: ${err.message}. Attempting IndexedDB fallback...`);
    notifyConnectivity(false, err.message);

    // Fallback to IndexedDB cache
    if (scenarioId && resource) {
      const cached = await getCachedResource(scenarioId, resource);
      if (cached && cached.data) {
        if (Array.isArray(cached.data)) {
          const arr = [...cached.data];
          arr._isCached = true;
          arr._cachedAt = cached.cached_at;
          return arr;
        }
        return {
          ...cached.data,
          _isCached: true,
          _cachedAt: cached.cached_at
        };
      }
    }
    
    // No cache available, throw original error
    throw err;
  }
};

/**
 * Health check API call
 */
export const checkHealth = async () => {
  try {
    const response = await apiClient.get('/health');
    notifyConnectivity(true);
    return {
      online: true,
      data: response.data,
      error: null,
    };
  } catch (err) {
    notifyConnectivity(false, err.message);
    return {
      online: false,
      data: null,
      error: err.message || 'Backend connection failed',
    };
  }
};

/**
 * Scenarios API
 */
export const listScenarios = async () => {
  try {
    const response = await apiClient.get('/scenarios');
    notifyConnectivity(true);
    return response.data;
  } catch (err) {
    notifyConnectivity(false, err.message);
    return [
      { id: 1, name: 'Scenario 1: Normal Operations', file: 'scenario_1_normal.json' },
      { id: 2, name: 'Scenario 2: Fuel Crisis', file: 'scenario_2_fuel_crisis.json' },
      { id: 3, name: 'Scenario 3: Emergency SAR', file: 'scenario_3_emergency_sar.json' },
      { id: 4, name: 'Scenario 4: Cold Chain Breach', file: 'scenario_4_cold_chain_breach.json' },
      { id: 5, name: 'Scenario 5: Satellite Loss & Sync', file: 'scenario_5_connectivity_loss.json' },
    ];
  }
};

export const getScenarios = listScenarios;

export const getScenarioSummary = async (scenarioId = 1) => {
  return fetchWithCacheFallback(`/scenarios/${scenarioId}/summary`, {}, 'scenario_summary', scenarioId);
};

/**
 * High-Level Dashboard Summary
 */
export const getDashboardSummary = async (scenarioId = 1) => {
  return fetchWithCacheFallback('/dashboard/summary', { scenario_id: scenarioId }, 'dashboard_summary', scenarioId);
};

/**
 * Fleet Assets & Vehicles
 */
export const getAssets = async (scenarioId = 1) => {
  return fetchWithCacheFallback('/assets', { scenario_id: scenarioId }, 'assets', scenarioId);
};

/**
 * Expedition Personnel Roster & Muster
 */
export const getPersonnel = async (scenarioId = 1) => {
  return fetchWithCacheFallback('/personnel', { scenario_id: scenarioId }, 'personnel', scenarioId);
};

export const checkInPersonnel = async (personnelId, status = 'CHECKED_IN', operator = 'Field Operator') => {
  const response = await apiClient.post(`/personnel/${personnelId}/check-in`, { status, operator });
  return response.data;
};

/**
 * Cold-Chain Cargo Manifests
 */
export const getCargo = async (scenarioId = 1) => {
  return fetchWithCacheFallback('/cargo', { scenario_id: scenarioId }, 'cargo', scenarioId);
};

export const updateCargoStage = async (cargoId, newStage, operator = 'Logistics Officer') => {
  const response = await apiClient.post(`/cargo/${cargoId}/update-stage`, { new_stage: newStage, operator });
  return response.data;
};

/**
 * Inventory Stock & Days of Autonomy
 */
export const getInventory = async (scenarioId = 1) => {
  return fetchWithCacheFallback('/inventory', { scenario_id: scenarioId }, 'inventory', scenarioId);
};

/**
 * Emergencies & SAR Decision Engine
 */
export const getEmergencies = async (scenarioId = 3) => {
  return fetchWithCacheFallback('/emergencies', { scenario_id: scenarioId }, 'emergencies', scenarioId);
};

export const dispatchSarTeam = async (incidentId, selectedVehicleId, operator = 'Expedition Commander', reason = 'Optimal SAR asset score') => {
  const response = await apiClient.post(`/emergencies/${incidentId}/dispatch-sar`, {
    selected_vehicle_id: selectedVehicleId,
    operator,
    reason
  });
  return response.data;
};

export const resolveEmergency = async (incidentId, operator = 'Medical/Safety Officer', outcomeNotes = 'Casualty rescued safely') => {
  const response = await apiClient.post(`/emergencies/${incidentId}/resolve`, {
    operator,
    outcome_notes: outcomeNotes
  });
  return response.data;
};

export const resetEmergency = async (incidentId) => {
  const response = await apiClient.post(`/emergencies/${incidentId}/reset`);
  return response.data;
};

/**
 * Satellite Connectivity & Offline Replay Buffer
 */
export const getConnectivity = async (scenarioId = 5) => {
  return fetchWithCacheFallback('/connectivity', { scenario_id: scenarioId }, 'connectivity', scenarioId);
};

/**
 * Operational Alerts Log
 */
export const getAlerts = async (scenarioId = 1) => {
  return fetchWithCacheFallback('/alerts', { scenario_id: scenarioId }, 'alerts', scenarioId);
};

export const acknowledgeAlert = async (alertId, status = 'ACKNOWLEDGED', operator = 'Duty Officer') => {
  const response = await apiClient.post(`/alerts/${alertId}/acknowledge`, { status, operator });
  return response.data;
};

/**
 * Leaflet GIS Map Topology
 */
export const getMapTopology = async (scenarioId = 1) => {
  return fetchWithCacheFallback('/map/topology', { scenario_id: scenarioId }, 'map_topology', scenarioId);
};

/**
 * Route Planning & Validation API
 */
export const planRoute = async (payload, scenarioId = 1) => {
  const response = await apiClient.post(`/expeditions/plan-route?scenario_id=${scenarioId}`, payload);
  return response.data;
};

export const saveRoute = async (payload) => {
  const response = await apiClient.post('/expeditions/save-route', payload);
  return response.data;
};

export const getPlannedRoutes = async () => {
  const response = await apiClient.get('/expeditions/planned-routes');
  return response.data;
};

/**
 * Audit Logs API
 */
export const getAuditLogs = async (limit = 50, entityType = null) => {
  const params = { limit };
  if (entityType) params.entity_type = entityType;
  const response = await apiClient.get('/audit-logs', { params });
  return response.data;
};

/**
 * POST /sync — Synchronize batch of local offline operations
 */
export const syncOperations = async (operations) => {
  try {
    const response = await apiClient.post('/sync', { operations });
    notifyConnectivity(true);
    return response.data;
  } catch (err) {
    notifyConnectivity(false, err.message);
    throw err;
  }
};

/**
 * Operational Intelligence API (Stage 3.5)
 */
export const getIntelligenceSummary = async (scenarioId = 1) => {
  return fetchWithCacheFallback('/intelligence/summary', { scenario_id: scenarioId }, 'intelligence_summary', scenarioId);
};

export const getAutonomyIntelligence = async (scenarioId = 1) => {
  return fetchWithCacheFallback('/intelligence/autonomy', { scenario_id: scenarioId }, 'intelligence_autonomy', scenarioId);
};

export const getResupplyRisk = async (scenarioId = 1) => {
  return fetchWithCacheFallback('/intelligence/resupply-risk', { scenario_id: scenarioId }, 'intelligence_resupply_risk', scenarioId);
};

export const getReadinessIntelligence = async (scenarioId = 1) => {
  return fetchWithCacheFallback('/intelligence/readiness', { scenario_id: scenarioId }, 'intelligence_readiness', scenarioId);
};

export const getEmergencyIntelligence = async (scenarioId = 1) => {
  return fetchWithCacheFallback('/intelligence/emergency', { scenario_id: scenarioId }, 'intelligence_emergency', scenarioId);
};

export const getResourceForecast = async (scenarioId = 1) => {
  return fetchWithCacheFallback('/intelligence/forecast', { scenario_id: scenarioId }, 'intelligence_forecast', scenarioId);
};

export default apiClient;
