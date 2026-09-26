# Data Retention and Consent Revocation Policy

## 1. Overview and Purpose
The Explainable Livestock Health Grading System (ELHGS) is designed to operate under strict agricultural privacy, biological ethics, and cybersecurity compliance principles. This document defines the policies, retention lifecycles, and standard operating procedures (SOPs) for data storage, consent revocation (right-to-erasure), and archival management across livestock images, expert annotations, and telemetry records.

---

## 2. Data Classification Matrix

| Data Category | Artifacts | Location | Retention Period | De-Identification Standard |
|---|---|---|---|---|
| **Raw Images (Intake)** | Unsanitized original submissions | `dataset/real/raw/images/` | Maximum 14 days (or purged immediately post-sanitization) | Non-reversible deletion once normalized |
| **Sanitized Images** | Metadata-stripped, 512x512 RGB images | `dataset/real/processed/images/` | Indefinite (or until consent revocation) | EXIF, GPS, camera serials stripped; faces & human features obscured |
| **Provenance & Consent** | Contributor IDs, consent flags, timestamps, image SHA-256 | `dataset/real/documentation/provenance_records.json` | 5 years post-pilot | Contributor pseudonymization; separated from training matrices |
| **Expert Annotations** | Blind grades (1 & 2), consensus, clinical rationales | PostgreSQL `expert_annotations` table | Indefinite | Reviewer usernames pseudonymous in research publications |
| **Audit Logs** | Login, access attempts, grade submissions, admin ops | PostgreSQL `audit_logs` table | 3 years minimum (tamper-evident) | Passwords, tokens, auth headers automatically `[REDACTED]` |
| **Offline Cache** | Cached records, sync queue | Farmer device IndexedDB | Purged on logout or maximum 7 days | Encrypted at rest (OS keystore / sandbox) |

---

## 3. Right-to-Erasure & Consent Revocation SOP

If a participating farmer, rancher, or research partner revokes consent for their submitted livestock data:

### Step 1: Formal Request Intake
1. Identify the contributor's pseudonymized ID (e.g., `EXP-FARM-04`) or specific sample IDs.
2. Confirm identity through administrative authentication (`ADMIN` role required).

### Step 2: Image Purging
1. Remove raw and processed images corresponding to the sample ID:
   ```bash
   rm dataset/real/raw/images/{sample_id}.*
   rm dataset/real/processed/images/{sample_id}.jpg
   ```
2. Verify file removal via canonical path check.

### Step 3: Database & Provenance Anonymization
1. Update `expert_annotations`:
   - Either delete record if unreferenced in frozen model benchmarks:
     ```sql
     DELETE FROM expert_annotations WHERE sample_id = 'target_sample_id';
     ```
   - Or set `image_path = 'REVOKED_DELETED'` and clear notes if retained for aggregate statistical validity without identifiable media.
2. Update `provenance_records.json` marking `consent_obtained: false` and `status: "PURGED_ON_REVOCATION"`.

### Step 4: Model Retraining Protocol
- If the revoked sample was part of a training split, trigger a dataset split re-generation:
  ```bash
  python backend/evaluation/dataset_split.py
  ```
- Re-train baseline models to guarantee no lingering feature weights derived from the revoked image.

### Step 5: Audit Documentation
Log the deletion action in `audit_logs` with action `CONSENT_REVOCATION_PURGE` and resource `target_sample_id`. Zero raw image data or contributor PII is preserved in the audit log.
