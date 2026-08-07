# 📡 Offline-First & PWA Synchronization Architecture

The Explainable Livestock Health Grading System (ELHGS) is designed to operate seamlessly in remote farming locations with zero or intermittent internet connectivity.

---

## 1. PWA & Caching Architecture
- **Web App Manifest (`manifest.json`):** Enables standalone installation on mobile and tablet devices.
- **Service Worker (`sw.js`):**
  - **Static Assets:** Cache-First strategy for application shell (HTML, CSS, JS icons).
  - **API Endpoints:** Network-First strategy with graceful offline fallback JSON payload.

---

## 2. Local IndexedDB Storage Schema

When internet connection is lost, all evaluation data is stored in the device's native `window.indexedDB` (`ELHGS_Offline_DB`):

```typescript
interface QueuedGradingItem {
  id: string; // Unique timestamp-based ID
  timestamp: number;
  attributes: Record<string, any>;
  human_grade?: string;
  imageBlob?: Blob | null;
  imageHash?: string;
  status: 'pending' | 'syncing' | 'conflict' | 'failed';
  retryCount: number;
  error?: string;
}
```

---

## 3. Two-Stage Low-Bandwidth Synchronization

To support weak agricultural cellular connections (2G/3G), synchronization executes in two distinct stages:

```
[ Local Device (Offline) ]
           │
           │  1. Online Connection Detected
           ▼
┌──────────────────────────────────────────┐
│ STAGE 1: Attribute Sync                  │
│ Post lightweight JSON payload (~1 KB)     │
│ Endpoint: POST /api/v1/grade (or /sync)  │
└──────────────────────────────────────────┘
           │
           │  Stage 1 Succeeds (Grade recorded)
           ▼
┌──────────────────────────────────────────┐
│ STAGE 2: Image Upload                    │
│ Post compressed JPEG (<500 KB)           │
└──────────────────────────────────────────┘
```

---

## 4. Client-Side Image Optimization

Before storing or transmitting photos:
1. **Dimension Resizing:** Scaled to maximum 1024x1024 keeping aspect ratio.
2. **Quality Compression:** Canvas output set to JPEG 70% quality (<500 KB payload).
3. **EXIF Metadata Stripping:** Redrawn onto a clean HTML5 canvas to automatically remove location/worker privacy metadata.
4. **Payload Hashing:** Cryptographic SHA-256 hash computed for audit integrity.

---

## 5. Offline Conflict Resolution Strategy

If an animal sample was graded remotely while a device was offline:
1. The sync engine detects a timestamp or entity collision.
2. A `ConflictDialog` modal prompts the user:
   - **Keep Server Version (Default):** Preserves remote authority.
   - **Overwrite with Local Field Version:** Pushes the offline field observation.
3. Neither strategy overwrites human expert authority.
