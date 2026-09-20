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
 * Scenario Endpoints
 */
export const getScenarios = async () => {
  try {
    const response = await apiClient.get('/scenarios');
    notifyConnectivity(true);
    cacheResource(0, 'scenarios_list', response.data);
    return response.data;
  } catch (err) {
    notifyConnectivity(false, err.message);
    const cached = await getCachedResource(0, 'scenarios_list');
    if (cached && cached.data) return cached.data;
    throw err;
  }
};

export const getScenarioSummary = async (scenarioId = 1) => {
  return fetchWithCacheFallback(`/scenarios/${scenarioId}/summary`, {}, 'summary', scenarioId);
};

/**
 * Dashboard Command Center Summary
 */
export const getDashboardSummary = async (scenarioId = 1) => {
  return fetchWithCacheFallback('/dashboard/summary', { scenario_id: scenarioId }, 'dashboard', scenarioId);
};

/**
 * Assets / Fleet Telemetry
 */
export const getAssets = async (scenarioId = 1) => {
  return fetchWithCacheFallback('/assets', { scenario_id: scenarioId }, 'assets', scenarioId);
};

/**
 * Personnel & Muster Roll-Call
 */
export const getPersonnel = async (scenarioId = 1) => {
  return fetchWithCacheFallback('/personnel', { scenario_id: scenarioId }, 'personnel', scenarioId);
};

/**
 * Cold-Chain Cargo Telemetry & Lifecycle
 */
export const getCargo = async (scenarioId = 1) => {
  return fetchWithCacheFallback('/cargo', { scenario_id: scenarioId }, 'cargo', scenarioId);
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

/**
 * Leaflet GIS Map Topology
 */
export const getMapTopology = async (scenarioId = 1) => {
  return fetchWithCacheFallback('/map/topology', { scenario_id: scenarioId }, 'map_topology', scenarioId);
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

