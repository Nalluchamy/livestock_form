# Database Backup, Disaster Recovery & Integrity Runbook

## 1. Objectives & Scope
This runbook defines disaster recovery (DR) objectives, automated backup procedures, point-in-time recovery protocols, and verification steps for the Explainable Livestock Health Grading System (ELHGS).

- **Recovery Point Objective (RPO):** Maximum 1 hour data loss for active grading sessions; maximum 24 hours for archival logs.
- **Recovery Time Objective (RTO):** Full database restore and service resumption within 15 minutes.

---

## 2. Backup Strategy & Automation

ELHGS database operations support both development SQLite storage and production PostgreSQL clustered deployments.

### 2.1 Scheduled Backup Script
Automated daily snapshots are managed via `scripts/backup_db.py`.
```bash
# Execute manual snapshot
python scripts/backup_db.py [optional_destination_directory]
```

### 2.2 Cron Automation (Linux Production Server)
```cron
# Daily backup at 02:00 UTC
0 2 * * * /app/.venv/bin/python /app/scripts/backup_db.py /var/backups/elhgs >> /var/log/elhgs_backup.log 2>&1
```

### 2.3 Verification & Cryptographic Checksums
Each backup:
1. Calculates a SHA-256 cryptographic hash.
2. Updates `backups/db/backup_manifest.json` with timestamp, file size, and status `VERIFIED`.
3. Verifies file non-emptiness.

---

## 3. Disaster Recovery & Restoration SOP

In the event of database corruption, data loss, or server migration:

### 3.1 Pre-Flight Integrity Verification
Before restoring, `scripts/restore_db.py` inspects the target backup against `backup_manifest.json`:
- Recalculates SHA-256.
- Halts execution immediately if checksum mismatch occurs (tamper defense).
- Creates a safety rollback snapshot of the active target database (`.prerestore_<timestamp>.bak`).

### 3.2 Restoration Execution
```bash
# Interactive restore (prompts for confirmation)
python scripts/restore_db.py backups/db/elhgs_backup_20260925_064933.sqlite

# Unattended automated restore (e.g., CI/CD or DR pipeline)
python scripts/restore_db.py backups/db/elhgs_backup_20260925_064933.sqlite --yes
```

### 3.3 Post-Restoration Verification Checklist
1. Execute health check:
   ```bash
   curl -s http://localhost:8000/api/v1/health | jq .data.database
   ```
2. Verify table migration revision:
   ```bash
   alembic current
   ```
   Must display `0004_auth_and_audit (head)`.
3. Verify test suite integrity:
   ```bash
   pytest backend/tests/ -k "test_health_check or test_api_create_and_list_reviews"
   ```
