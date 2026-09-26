# ELHGS Production Operational Runbook

## 1. System Architecture & Components
The Explainable Livestock Health Grading System (ELHGS) is an enterprise veterinary AI platform comprising:
- **FastAPI Backend (v0.1.0)**: Asynchronous REST API with JWT authentication, role-based access control (RBAC), and sanitization pipelines.
- **PostgreSQL / SQLite Database**: Relational datastore managed via Alembic migrations (revisions 0001 through 0004).
- **React Frontend (v19)**: Vite + TypeScript + Tailwind CSS PWA with offline queue isolation and cryptographic token storage.
- **Evaluation & ML Engine**: Retrospective real evaluation, decision trees, logistic regression, and inter-expert Cohen's Kappa scoring.
- **Nginx Reverse Proxy**: TLS termination, security headers (CSP, HSTS), rate limiting, and 15MB request limits.

---

## 2. Deployment & Startup Checklist

### 2.1 Environment Configuration
Configure production environment variables in `.env`:
```ini
ENVIRONMENT=production
DEMO_MODE=false
SECRET_KEY=generate_with_openssl_rand_hex_64
DATABASE_URL=postgresql+psycopg2://postgres:strong_db_password@postgres:5432/livestock_grading
SECURE_COOKIES=true
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
LOCKOUT_MAX_ATTEMPTS=5
LOCKOUT_DURATION_MINUTES=15
MAX_UPLOAD_SIZE_BYTES=15728640
```

### 2.2 Database Initialization & Migration
```bash
# Verify database connection
python -c "from backend.database.connection import engine; engine.connect()"

# Run Alembic migrations to latest head (0004_auth_and_audit)
alembic upgrade head
```

### 2.3 Initial Admin Bootstrap
Upon first boot, the system ensures an administrative user exists using credentials specified in settings (`admin` / `AdminSecurePass2026!`). Immediately change this password post-deployment via:
```bash
POST /api/v1/auth/reset-password
```

---

## 3. Incident Response Protocols

### Incident 1: Repeated Failed Logins / Account Lockout Alert
- **Symptom**: User receives HTTP 403 `User account is temporarily locked due to multiple failed login attempts.`
- **Triage**: Query `audit_logs` for `action = 'AUTH_LOGIN_FAILURE'` and `action = 'AUTH_ACCOUNT_LOCKED'` filtered by target username.
- **Remediation**:
  If legitimate user forgot password, administrator can reset failed attempts:
  ```bash
  PATCH /api/v1/admin/users/{user_id}/status
  {"unlock": true}
  ```
  If brute force attack detected from external IP, block IP at Nginx / firewall level.

### Incident 2: Model Performance Degradation / Data Leakage
- **Symptom**: Accuracy dropped or synthetic test metrics do not match held-out test split.
- **Triage**: Inspect dataset collection progress:
  ```bash
  GET /api/v1/dataset/collection-progress
  ```
- **Remediation**:
  Ensure samples $\ge 10$ before deploying real-data models. Never train and test on the same ranch/cohort splits. Maintain strict `PENDING_REAL_DATA` indicators when sample volume is insufficient.

### Incident 3: Data Breach / PII Ingestion Flag
- **Symptom**: An uploaded livestock image contains human faces, license plates, or ranch signage.
- **Triage**: Automated screener marks sample as `flagged_for_manual_review = True`.
- **Remediation**:
  Grader or reviewer submits:
  ```bash
  POST /api/v1/annotations/{sample_id}/flag-quality
  {"reason": "Identifiable ranch worker face detected in background."}
  ```
  Sample status immediately transitions to `REJECTED`, preventing inclusion in training or public exports.

### Incident 4: Compromised Token Family / Refresh Token Reuse Alert
- **Symptom**: Audit log alert `AUTH_TOKEN_REUSE_DETECTED` with status `FAILURE`.
- **Triage**: An already-revoked refresh token was presented for rotation, indicating token replay, exfiltration, or client state corruption.
- **Remediation**:
  1. The server automatically executed full token family revocation (`revoke_all_user_tokens`), immediately invalidating all active sessions for that user account.
  2. Confirm with user via out-of-band communication if their device or credentials were compromised.
  3. Require password reset via `/api/v1/auth/reset-password` before issuing new session credentials.

---

## 4. Disaster Recovery & Restoration Procedures

### 4.1 Automated Backup Execution
Automated daily backups run via cron/scheduler generating SHA-256 checksums and manifest records:
```bash
python scripts/backup_db.py
```
Backups are archived in `backups/db/` and recorded in `backup_manifest.json`.

### 4.2 Database Restoration
In case of data corruption, node failover, or disaster recovery drills:
```bash
python scripts/restore_db.py backups/db/elhgs_backup_<timestamp>.sqlite --yes
```
The utility:
1. Validates the SHA-256 hash against `backup_manifest.json` (aborts if checksum mismatches).
2. Generates a safety rollback snapshot (`.prerestore_<timestamp>.bak`).
3. Restores the database with complete record parity.

### 4.3 Measured Recovery Time Objective (RTO)
- **Measured RTO**: $< 0.5$ seconds for SQLite development/pilot databases; $< 5.0$ seconds for PostgreSQL staging databases.
- **Parity Verified**: Users, RefreshTokens, AuditLogs, ExpertAnnotations, DimSamples, FactGradingEvents, DisagreementReviews, and ExperimentResults.
