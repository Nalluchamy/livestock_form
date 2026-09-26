/**
 * IndexedDB Storage Engine for Offline Livestock Health Grading.
 * Per-user queue isolation for secure offline operation on shared devices.
 * Zero external dependencies.
 */
const DB_NAME = 'ELHGS_Offline_DB';
const DB_VERSION = 2;

export interface QueuedGradingItem {
  id: string; // Local UUID or timestamp
  userId?: string; // Isolated per-user ID to prevent queue bleed
  timestamp: number;
  attributes: Record<string, any>;
  human_grade?: string;
  imageBlob?: Blob | null;
  imageHash?: string;
  status: 'pending' | 'syncing' | 'conflict' | 'failed';
  retryCount: number;
  error?: string;
}

export class LocalDatabase {
  private db: IDBDatabase | null = null;

  async init(): Promise<IDBDatabase> {
    if (this.db) return this.db;

    return new Promise((resolve, reject) => {
      const request = indexedDB.open(DB_NAME, DB_VERSION);

      request.onupgradeneeded = (event) => {
        const db = (event.target as IDBOpenDBRequest).result;
        let store: IDBObjectStore;
        if (!db.objectStoreNames.contains('offline_queue')) {
          store = db.createObjectStore('offline_queue', { keyPath: 'id' });
        } else {
          store = (event.currentTarget as any).transaction.objectStore('offline_queue');
        }

        if (!store.indexNames.contains('status')) {
          store.createIndex('status', 'status', { unique: false });
        }
        if (!store.indexNames.contains('timestamp')) {
          store.createIndex('timestamp', 'timestamp', { unique: false });
        }
        if (!store.indexNames.contains('userId')) {
          store.createIndex('userId', 'userId', { unique: false });
        }
      };

      request.onsuccess = (event) => {
        this.db = (event.target as IDBOpenDBRequest).result;
        resolve(this.db);
      };

      request.onerror = (event) => {
        reject((event.target as IDBOpenDBRequest).error);
      };
    });
  }

  async saveItem(item: QueuedGradingItem): Promise<void> {
    const db = await this.init();
    return new Promise((resolve, reject) => {
      const tx = db.transaction('offline_queue', 'readwrite');
      const store = tx.objectStore('offline_queue');
      const req = store.put(item);

      req.onsuccess = () => resolve();
      req.onerror = () => reject(req.error);
    });
  }

  async getAllPending(): Promise<QueuedGradingItem[]> {
    const db = await this.init();
    return new Promise((resolve, reject) => {
      const tx = db.transaction('offline_queue', 'readonly');
      const store = tx.objectStore('offline_queue');
      const req = store.getAll();

      req.onsuccess = () => resolve(req.result || []);
      req.onerror = () => reject(req.error);
    });
  }

  async getItemsForUser(userId: string): Promise<QueuedGradingItem[]> {
    const all = await this.getAllPending();
    return all.filter((item) => !item.userId || item.userId === userId);
  }

  async removeItem(id: string): Promise<void> {
    const db = await this.init();
    return new Promise((resolve, reject) => {
      const tx = db.transaction('offline_queue', 'readwrite');
      const store = tx.objectStore('offline_queue');
      const req = store.delete(id);

      req.onsuccess = () => resolve();
      req.onerror = () => reject(req.error);
    });
  }

  async clearUserQueue(userId: string): Promise<void> {
    const userItems = await this.getItemsForUser(userId);
    for (const item of userItems) {
      await this.removeItem(item.id);
    }
  }

  async clearAll(): Promise<void> {
    const db = await this.init();
    return new Promise((resolve, reject) => {
      const tx = db.transaction('offline_queue', 'readwrite');
      const store = tx.objectStore('offline_queue');
      const req = store.clear();

      req.onsuccess = () => resolve();
      req.onerror = () => reject(req.error);
    });
  }
}

export const localDB = new LocalDatabase();
