import { localDB, QueuedGradingItem } from '../utils/localDatabase';
import { submitGrade } from './gradingService';

export interface SyncResult {
  syncedCount: number;
  failedCount: number;
  conflicts: QueuedGradingItem[];
}

export async function processOfflineSyncQueue(): Promise<SyncResult> {
  const items = await localDB.getAllPending();
  let syncedCount = 0;
  let failedCount = 0;
  const conflicts: QueuedGradingItem[] = [];

  for (const item of items) {
    if (item.status === 'syncing') continue;

    try {
      // Mark syncing
      item.status = 'syncing';
      await localDB.saveItem(item);

      // Two-Stage Sync: Stage 1 - Submit Attribute JSON first
      await submitGrade({
        attributes: item.attributes,
        human_grade: item.human_grade as any,
      });

      // Stage 2 - Photo upload (simulated or image_id link)
      // On success, remove from IndexedDB queue
      await localDB.removeItem(item.id);
      syncedCount++;
    } catch (err: any) {
      item.retryCount += 1;
      item.status = item.retryCount > 3 ? 'failed' : 'pending';
      item.error = err?.message || 'Sync failed';
      await localDB.saveItem(item);
      failedCount++;
    }
  }

  return { syncedCount, failedCount, conflicts };
}
