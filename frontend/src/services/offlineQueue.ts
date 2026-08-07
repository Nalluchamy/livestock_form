import { localDB, QueuedGradingItem } from '../utils/localDatabase';

export async function enqueueOfflineGrading(
  attributes: Record<string, any>,
  humanGrade?: string,
  imageBlob?: Blob | null,
  imageHash?: string
): Promise<QueuedGradingItem> {
  const item: QueuedGradingItem = {
    id: `offline_${Date.now()}_${Math.random().toString(36).substr(2, 5)}`,
    timestamp: Date.now(),
    attributes,
    human_grade: humanGrade,
    imageBlob: imageBlob || null,
    imageHash: imageHash || undefined,
    status: 'pending',
    retryCount: 0,
  };

  await localDB.saveItem(item);
  return item;
}

export async function getPendingQueue(): Promise<QueuedGradingItem[]> {
  return await localDB.getAllPending();
}

export async function removeQueueItem(id: string): Promise<void> {
  await localDB.removeItem(id);
}
