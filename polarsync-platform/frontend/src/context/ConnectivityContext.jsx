import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import {
  enqueueOperation,
  getPendingOperations,
  getAllQueueOperations,
  updateOperationStatus,
  clearSyncedOperations,
  getAllCachedMetadata
} from '../services/db';
import { syncOperations, setConnectivityListener, checkHealth } from '../services/api';

const ConnectivityContext = createContext();

export const ConnectivityProvider = ({ children }) => {
  const [networkStatus, setNetworkStatus] = useState('ONLINE'); // ONLINE | OFFLINE | SYNCING | SYNCED | SYNC_ERROR
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [queue, setQueue] = useState([]);
  const [cachedMeta, setCachedMeta] = useState([]);
  const [lastSyncResult, setLastSyncResult] = useState(null);
  const [lastSyncTimestamp, setLastSyncTimestamp] = useState(null);

  // Refresh queue and cache metadata
  const refreshStorageStats = useCallback(async () => {
    try {
      const [queueItems, metaItems] = await Promise.all([
        getAllQueueOperations(),
        getAllCachedMetadata()
      ]);
      setQueue(queueItems);
      setCachedMeta(metaItems);
    } catch (err) {
      console.warn('Error refreshing storage stats:', err);
    }
  }, []);

  // Update connectivity status from API interceptor or browser events
  const handleConnectivityChange = useCallback((online, reason = null) => {
    setIsOnline(online);
    setNetworkStatus((prev) => {
      if (!online) return 'OFFLINE';
      if (prev === 'OFFLINE' || prev === 'SYNC_ERROR') return 'ONLINE';
      return prev;
    });
    refreshStorageStats();
  }, [refreshStorageStats]);

  useEffect(() => {
    setConnectivityListener(handleConnectivityChange);

    const onBrowserOnline = () => {
      checkHealth().then((res) => {
        handleConnectivityChange(res.online);
      });
    };
    const onBrowserOffline = () => handleConnectivityChange(false, 'Browser offline');

    window.addEventListener('online', onBrowserOnline);
    window.addEventListener('offline', onBrowserOffline);

    // Initial check
    refreshStorageStats();

    return () => {
      window.removeEventListener('online', onBrowserOnline);
      window.removeEventListener('offline', onBrowserOffline);
    };
  }, [handleConnectivityChange, refreshStorageStats]);

  // Synchronize pending queue operations with backend
  const syncNow = useCallback(async () => {
    const pending = await getPendingOperations();
    if (pending.length === 0) {
      setNetworkStatus('SYNCED');
      setTimeout(() => setNetworkStatus('ONLINE'), 3000);
      return { accepted: [], rejected: [], total: 0 };
    }

    setNetworkStatus('SYNCING');

    // Mark items as SYNCING in IndexedDB
    for (const op of pending) {
      await updateOperationStatus(op.id, 'SYNCING');
    }
    await refreshStorageStats();

    try {
      const payload = pending.map((op) => ({
        id: op.id,
        resource: op.resource,
        operation: op.operation,
        payload: op.payload,
        timestamp: op.timestamp,
        retry_count: op.retry_count || 0
      }));

      const result = await syncOperations(payload);

      // Process accepted items
      for (const item of result.accepted || []) {
        await updateOperationStatus(item.id, 'SYNCED');
      }

      // Process rejected items
      for (const item of result.rejected || []) {
        await updateOperationStatus(item.id, 'FAILED', item.message);
      }

      setLastSyncResult(result);
      setLastSyncTimestamp(result.server_timestamp || new Date().toISOString());
      setNetworkStatus(result.rejected?.length > 0 ? 'SYNC_ERROR' : 'SYNCED');

      await refreshStorageStats();

      // Return to ONLINE after brief notice if everything succeeded
      if (!result.rejected || result.rejected.length === 0) {
        setTimeout(() => {
          setNetworkStatus('ONLINE');
        }, 4000);
      }

      return result;
    } catch (err) {
      console.error('Synchronization failed:', err);
      for (const op of pending) {
        await updateOperationStatus(op.id, 'FAILED', err.message || 'Network unreachable');
      }
      setNetworkStatus('SYNC_ERROR');
      await refreshStorageStats();
      throw err;
    }
  }, [refreshStorageStats]);

  // Perform and queue local field operations
  const performLocalOperation = useCallback(async (resource, operation, payload, autoSync = true) => {
    const queued = await enqueueOperation(resource, operation, payload);
    await refreshStorageStats();

    if (autoSync && isOnline) {
      try {
        await syncNow();
      } catch (err) {
        console.warn('Auto-sync failed, queued for later:', err);
      }
    }

    return queued;
  }, [isOnline, syncNow, refreshStorageStats]);

  const pendingCount = queue.filter((op) => op.status === 'PENDING' || op.status === 'FAILED').length;

  const value = {
    networkStatus,
    isOnline,
    queue,
    pendingCount,
    cachedMeta,
    cacheCount: cachedMeta.length,
    lastSyncResult,
    lastSyncTimestamp,
    syncNow,
    performLocalOperation,
    clearSyncedOperations: async () => {
      await clearSyncedOperations();
      await refreshStorageStats();
    },
    refreshStorageStats,
    setSimulatedOffline: (offline) => {
      handleConnectivityChange(!offline, offline ? 'Manual Offline Simulation' : null);
    }
  };

  return (
    <ConnectivityContext.Provider value={value}>
      {children}
    </ConnectivityContext.Provider>
  );
};

export const useConnectivity = () => {
  const context = useContext(ConnectivityContext);
  if (!context) {
    throw new Error('useConnectivity must be used within a ConnectivityProvider');
  }
  return context;
};

export default ConnectivityContext;
