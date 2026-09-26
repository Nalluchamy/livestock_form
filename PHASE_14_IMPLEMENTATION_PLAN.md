# PHASE 14 IMPLEMENTATION PLAN
## Real-World Pilot, Model Validation & Production Verification

### Explainable Livestock Health Grading System (ELHGS)

> **MANDATORY CLINICAL DISCLAIMER:**
> **ELHGS condition grading is an observational decision-support score, not a veterinary medical diagnosis. Urgent cases require immediate clinical examination by a licensed veterinarian.**

---

## 1. Executive Summary & Audit Baseline

Phase 13 delivered 119 verified passing backend tests, a clean React 19 frontend production build, Alembic migration `0004_auth_and_audit`, Bcrypt password hashing, JWT access tokens, single-use rotating refresh tokens, private authenticated image serving with path traversal / Zip-Slip protections, and structured audit logging.

This Phase 14 plan builds directly on the Phase 13 foundation to prepare ELHGS for a small, supervised real-world cattle assessment pilot. Our repository and security audit identified specific vulnerabilities and deployment readiness requirements that this plan addresses incrementally.

---

## 2. Repository & Security Audit Findings (Task 1)

| Area | Severity | Finding | Resolution |
| :--- | :--- | :--- | :--- |
| **Authentication** | **P0 - Critical** | Refresh-token rotation revokes used tokens, but presenting an already-revoked token returns generic 401 without invalidating the compromised token family. | Implement token reuse detection: if a revoked refresh token is presented, immediately revoke all active refresh tokens for that user account (`revoke_all_user_tokens`) and emit a critical security audit event (`AUTH_TOKEN_REUSE_DETECTED`). |
| **Environment Guards** | **P0 - Critical** | In `backend/core/auth_deps.py`, `DEMO_MODE=True` falls back to `repo.ensure_admin_user()` regardless of whether `ENVIRONMENT` is set to `staging` or `production`. | Enforce that demo mode fallback is only valid when `ENVIRONMENT.lower() in ("development", "test")`. Any unauthenticated request in staging or production will strictly return 401 Unauthorized. |
| **Frontend Security** | **P1 - High** | `frontend/src/pages/Login.tsx` pre-fills admin credentials and unconditionally renders "Supervised Pilot Role Presets" in all builds. | Restrict presets and pre-filled credentials to development mode (`import.meta.env.DEV`). In production builds, default to empty credentials and hide demo buttons. |
| **Endpoint Authorization** | **P1 - High** | `/api/v1/sync` and `/api/v1/grade` lack `get_current_user` dependencies; `GET /api/v1/annotations` does not restrict non-expert roles (`FARMER`). | Add `get_current_user` and `require_role` across all endpoints to ensure server-enforced RBAC even if frontend controls are bypassed. |
| **Disaster Recovery** | **P1 - High** | Backup and restore scripts exist (`scripts/backup_db.py`, `scripts/restore_db.py`), but end-to-end restoration parity and RTO have not been proven in an automated test. | Create `backend/tests/test_disaster_recovery.py` to run backup, alter database, restore, verify full table parity, and measure Recovery Time Objective (RTO). |
| **Deployment Smoke** | **P2 - Medium** | Nginx and Docker configurations lack automated smoke tests verifying security headers and rate limits. | Create `backend/tests/test_deployment_smoke.py` validating `/health`, security headers, 15MB upload limits, and production flags. |
| **Model Evaluation** | **P2 - Medium** | Model evaluation pipeline must compute complete metrics (macro precision, recall, F1, Cohen's kappa, confusion matrix) when real consensus data is present. | Ensure `train_real.py` and `real_dataset_runner.py` compute full metric suites when $N \ge 10$ and strictly return `PENDING_REAL_DATA` when $N < 10$ without fabricating data. |

---

## 3. Incremental Implementation Order

### Stage 1: Production Authentication Hardening (Task 2)
1. Update `backend/repositories/user_repository.py`:
   - Add `get_refresh_token_any_status(token_hash)` to look up tokens regardless of revocation status.
   - Verify `revoke_all_user_tokens(user_id)` invalidates all active sessions.
2. Update `backend/api/v1/auth.py`:
   - In `/refresh`, detect if the submitted token was already revoked.
   - If revoked: invoke family invalidation, log critical audit event, and return 401 with explicit security alert.
3. Update `backend/core/auth_deps.py`:
   - Check `settings.ENVIRONMENT.lower() in ("development", "test")` before permitting `DEMO_MODE` fallback.
4. Update `frontend/src/pages/Login.tsx`:
   - Gate preset credentials behind `import.meta.env.DEV`.
5. Add unit tests in `backend/tests/test_auth_api.py` for token reuse family revocation and staging demo mode enforcement.

### Stage 2: Endpoint Authorization & RBAC Enforcement (Task 2)
1. Update `backend/api/v1/sync.py`: Add `current_user: User = Depends(get_current_user)`.
2. Update `backend/api/v1/grading.py`: Add `current_user: User = Depends(get_current_user)` to `POST /grade` and `GET /grading-events`.
3. Update `backend/api/v1/annotations.py`: Enforce `require_role("EXPERT_GRADER", "SENIOR_REVIEWER", "ADMIN")` on `GET /annotations` and `GET /annotations/{sample_id}`.
4. Update `backend/api/v1/reviews.py`: Enforce authentication across review retrieval endpoints.
5. Add comprehensive role isolation tests across all 4 roles (`FARMER`, `EXPERT_GRADER`, `SENIOR_REVIEWER`, `ADMIN`).

### Stage 3: Database Disaster Recovery Verification (Task 3)
1. Implement `backend/tests/test_disaster_recovery.py`:
   - Generate automated backup using `backup_db.py`.
   - Verify SHA-256 checksum and manifest entry.
   - Insert records / modify database to simulate data corruption or loss.
   - Execute restore with `restore_db.py --yes`.
   - Verify complete data parity across `users`, `refresh_tokens`, `audit_logs`, `expert_annotations`, `disagreement_reviews`.
   - Measure and record actual RTO.

### Stage 4: Secure Deployment & Operational Monitoring (Task 4)
1. Implement `backend/tests/test_deployment_smoke.py`:
   - Test `/api/v1/health` and `/api/v1/health/detailed` probes.
   - Test security headers (`X-Content-Type-Options: nosniff`, `Cache-Control: private`).
   - Test upload limits (15MB max) and rate limiting.
   - Verify staging/production configuration validation.

### Stage 5: Genuine Cattle Dataset Tracking & Ethical Ingestion (Task 5)
1. Verify `GET /api/v1/dataset/collection-progress` returns accurate counts without fabrication.
2. Confirm provenance records are kept strictly in `dataset/real/documentation/provenance_records.json`.
3. Preserve `PENDING_REAL_WORLD_COLLECTION` status when samples $< 10$.

### Stage 6: Independent Expert Annotation & Double-Blind Verification (Task 6)
1. Verify double-blind isolation and self-grading prevention in `AnnotationRepository` and API.
2. Verify senior reviewer adjudication workflow.
3. Verify agreement metrics calculation (exact %, adjacent %, Cohen's kappa) when annotations are submitted.

### Stage 7: Real Model Training & Evaluation Pipeline (Task 7)
1. Verify `backend/ml/train_real.py` and `backend/evaluation/real_dataset_runner.py`.
2. Ensure macro precision, macro recall, macro F1, Cohen's kappa, and confusion matrices are computed for real consensus cohorts.
3. Ensure `PENDING_REAL_DATA` is strictly preserved when samples $< 10$.

### Stage 8: Clinical Safety & Escalation Rules (Task 8)
1. Verify clinical escalation triggers for Grade D conditions (emaciation $< 1.5$, severe wounds, downer cows, severe eye infections).
2. Ensure mandatory clinical non-veterinary diagnosis disclaimer is present on all responses.
3. Document that formal veterinary clinical review is pending live cohort intake.

### Stage 9: Offline Field Reliability & PWA (Task 9)
1. Verify IndexedDB per-user queue isolation in `localDatabase.ts`.
2. Verify offline queue purging on user logout.
3. Verify conflict-safe synchronization in `syncManager.ts`.

### Stage 10: Supervised Field Pilot Preparation (Task 10)
1. Update field pilot operational materials (`field_pilot_checklist.md`, `field_pilot_instructions.md`, `field_pilot_consent_form.md`).
2. Mark pilot execution as pending live cohort intake (zero fabricated field results).

### Stage 11: Real Metrics Dashboard (Task 11)
1. Verify `MetricsDashboard.tsx` cleanly distinguishes synthetic vs retrospective real vs prospective pilot data.

### Stage 12: End-to-End Testing (Task 12)
1. Run full test suite: verify $\ge 125$ passing tests (100% pass rate, 0 regressions).
2. Run frontend production build: verify 0 errors.

### Stage 13: Documentation & Final Audit Deliverables (Task 13)
1. Generate `PHASE_14_FINAL_AUDIT.md` classifying all requirements as PASS, PARTIAL, or NOT YET COMPLETE.
2. Update `README.md`, `docs/operational_runbook.md`, and `walkthrough.md`.

---

## 4. Verification & Success Criteria

- **Zero Regressions:** All 119 baseline tests pass + new Phase 14 tests pass ($\ge 125$ tests total).
- **Security Verified:** Token reuse family revocation, staging DEMO_MODE isolation, and role authorization verified.
- **Disaster Recovery Verified:** Round-trip backup, restore, data parity, and RTO measured.
- **Build Clean:** Frontend builds with 0 TypeScript errors.
- **Zero Fabrication:** No fake samples, false annotations, or fictitious dispute reduction claims.
