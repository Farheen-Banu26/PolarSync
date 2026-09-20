/**
 * PolarSync Offline IndexedDB Storage Layer (Stage 3.4)
 * Database: polarsync-offline
 * Stores: operational_cache, sync_queue, metadata
 */
import { openDB } from 'idb';

const DB_NAME = 'polarsync-offline';
const DB_VERSION = 1;

/**
 * Open or upgrade the IndexedDB database
 */
export const initDB = async () => {
  return openDB(DB_NAME, DB_VERSION, {
    upgrade(db) {
      // 1. Operational API Cache Store
      if (!db.objectStoreNames.contains('operational_cache')) {
        const cacheStore = db.createObjectStore('operational_cache', { keyPath: 'key' });
        cacheStore.createIndex('scenario_idx', 'scenario_id');
        cacheStore.createIndex('resource_idx', 'resource');
      }

      // 2. Offline Sync Queue Store
      if (!db.objectStoreNames.contains('sync_queue')) {
        const queueStore = db.createObjectStore('sync_queue', { keyPath: 'id' });
        queueStore.createIndex('status_idx', 'status');
        queueStore.createIndex('timestamp_idx', 'timestamp');
      }

      // 3. Metadata Store
      if (!db.objectStoreNames.contains('metadata')) {
        db.createObjectStore('metadata', { keyPath: 'key' });
      }
    },
  });
};

/**
 * Cache operational data from API
 */
export const cacheResource = async (scenarioId, resource, data) => {
  try {
    const db = await initDB();
    const key = `scenario:${scenarioId}:${resource}`;
    const entry = {
      key,
      scenario_id: Number(scenarioId),
      resource,
      data,
      cached_at: new Date().toISOString(),
      source: 'api'
    };
    await db.put('operational_cache', entry);
    
    // Update metadata last cache timestamp
    await db.put('metadata', {
      key: `last_cached:${resource}`,
      timestamp: entry.cached_at,
      scenario_id: Number(scenarioId)
    });
    return entry;
  } catch (err) {
    console.warn(`IndexedDB cacheResource error for ${resource}:`, err);
    return null;
  }
};

/**
 * Retrieve cached operational data
 */
export const getCachedResource = async (scenarioId, resource) => {
  try {
    const db = await initDB();
    const key = `scenario:${scenarioId}:${resource}`;
    const entry = await db.get('operational_cache', key);
    return entry || null;
  } catch (err) {
    console.warn(`IndexedDB getCachedResource error for ${resource}:`, err);
    return null;
  }
};

/**
 * Get all cached operational records metadata
 */
export const getAllCachedMetadata = async () => {
  try {
    const db = await initDB();
    const all = await db.getAll('operational_cache');
    return all.map(entry => ({
      key: entry.key,
      scenario_id: entry.scenario_id,
      resource: entry.resource,
      cached_at: entry.cached_at,
      dataSize: JSON.stringify(entry.data).length
    }));
  } catch (err) {
    console.warn('IndexedDB getAllCachedMetadata error:', err);
    return [];
  }
};

/**
 * Enqueue a local operational action for synchronization
 */
export const enqueueOperation = async (resource, operation, payload) => {
  try {
    const db = await initDB();
    const id = `op-${Date.now()}-${Math.random().toString(36).substring(2, 7)}`;
    const queuedOp = {
      id,
      timestamp: new Date().toISOString(),
      resource,
      operation,
      payload,
      status: 'PENDING',
      retry_count: 0,
      error_message: null
    };
    await db.put('sync_queue', queuedOp);
    return queuedOp;
  } catch (err) {
    console.warn('IndexedDB enqueueOperation error:', err);
    return null;
  }
};

/**
 * Get all pending synchronization operations
 */
export const getPendingOperations = async () => {
  try {
    const db = await initDB();
    const all = await db.getAll('sync_queue');
    return all.filter(op => op.status === 'PENDING' || op.status === 'FAILED');
  } catch (err) {
    console.warn('IndexedDB getPendingOperations error:', err);
    return [];
  }
};

/**
 * Get all queue operations (all statuses)
 */
export const getAllQueueOperations = async () => {
  try {
    const db = await initDB();
    const all = await db.getAll('sync_queue');
    return all.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
  } catch (err) {
    console.warn('IndexedDB getAllQueueOperations error:', err);
    return [];
  }
};

/**
 * Update an operation's status in sync_queue
 */
export const updateOperationStatus = async (id, status, errorMessage = null) => {
  try {
    const db = await initDB();
    const op = await db.get('sync_queue', id);
    if (op) {
      op.status = status;
      if (status === 'FAILED') {
        op.retry_count = (op.retry_count || 0) + 1;
        op.error_message = errorMessage;
      } else if (status === 'SYNCED') {
        op.synced_at = new Date().toISOString();
        op.error_message = null;
      }
      await db.put('sync_queue', op);
    }
    return op;
  } catch (err) {
    console.warn('IndexedDB updateOperationStatus error:', err);
    return null;
  }
};

/**
 * Clear synced operations
 */
export const clearSyncedOperations = async () => {
  try {
    const db = await initDB();
    const all = await db.getAll('sync_queue');
    const synced = all.filter(op => op.status === 'SYNCED');
    const tx = db.transaction('sync_queue', 'readwrite');
    for (const op of synced) {
      await tx.store.delete(op.id);
    }
    await tx.done;
    return synced.length;
  } catch (err) {
    console.warn('IndexedDB clearSyncedOperations error:', err);
    return 0;
  }
};
