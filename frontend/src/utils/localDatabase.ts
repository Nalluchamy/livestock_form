/**
 * IndexedDB Storage Engine for Offline Livestock Health Grading.
 * Zero external dependencies.
 */
const DB_NAME = 'ELHGS_Offline_DB';
const DB_VERSION = 1;

export interface QueuedGradingItem {
  id: string; // Local UUID or timestamp
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
        if (!db.objectStoreNames.contains('offline_queue')) {
          const store = db.createObjectStore('offline_queue', { keyPath: 'id' });
          store.createIndex('status', 'status', { unique: false });
          store.createIndex('timestamp', 'timestamp', { unique: false });
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
