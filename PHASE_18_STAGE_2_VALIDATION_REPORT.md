# PHASE 18 — REAL-WORLD VALIDATION AND STAGE 2 DEMONSTRATION REPORT
## Explainable Quality Grading System (EQGS) — Fresh-Market Produce & Livestock Health

**Document ID:** EQGS-REP-PHASE18-01  
**Milestone:** Stage 2 (70%) Real-World Validation & Live Demonstration Readiness  
**Date:** September 2026  
**Status:** Verification Passed (176/176 Backend Tests, Frontend 0 Build Errors)  

---

## 1. Executive Summary

Phase 18 establishes the complete end-to-end real-world validation framework, double-blind annotation infrastructure, controlled before-and-after trial runner, stakeholder usability study mechanism, failure analysis, and live demonstration assets for the **Explainable Quality Grading System (EQGS)**.

The system primary domain is **fresh-market tomato quality grading (Grade A / Grade B / Grade C)**, while preserving the livestock health triage module as a completely isolated secondary architecture.

### Current System Status & Zero-Fabrication Declaration

In strict compliance with academic and scientific integrity standards, **no synthetic images are counted as real data, no expert grades are simulated, and no stakeholder responses are fabricated**:

| Dimension | Measured Status | System Indicator | Details |
| :--- | :--- | :--- | :--- |
| **Genuine Photographs Collected** | **0 / 30** | `PENDING_REAL_DATA` | Infrastructure active; ready for physical field harvest intake. |
| **Double-Blind Annotations** | **0 Completed** | `PENDING_EXPERT_ANNOTATION` | Grader 1 & 2 blind isolation and Senior Reviewer queues active. |
| **Controlled Real-Data Experiments** | **0 Evaluated** | `PENDING_REAL_EXPERIMENT` | Trial runner operational; baseline division-by-zero defense active. |
| **Stakeholder Field Usability** | **0 Evaluated** | `PENDING_EXTERNAL_EVIDENCE` | Ethical consent, 5-task checklist, 5 Likert items implemented. |
| **Synthetic Development Dataset** | **300 Images** | `SYNTHETIC_PRODUCE` | Isolated in `dataset/produce/synthetic/` (100 A, 100 B, 100 C). |
| **Edge & Failure Cases** | **4 Cases** | `DOCUMENTED_FAILURES` | Blur/lighting, occlusion, borderline defects, wood grain/shadow. |

---

## 2. Phase 18 Completed Deliverables

### Task 1: Genuine Produce Ingestion & 30-Image Target Framework
- **Category Balancing Guidelines**: Established 3 collection target categories:
  - Apparent High-Quality ($N_{\text{target}} = 10$)
  - Apparent Minor Defects ($N_{\text{target}} = 10$)
  - Apparent Substantial Defects ($N_{\text{target}} = 10$)
- **Important Distinction**: These categories are collection sampling guidelines to enforce visual diversity during harvesting—they are **never** treated as ground truth labels.
- **Batch Upload Interface**: Implemented drag-and-drop batch upload supporting up to 30 simultaneous photos on the frontend with file size, dimensions, and duplicate warnings.
- **12-Step Ingestion & Optical Quality Gate**:
  - Image variance Laplacian sharpness ($\tau \ge 100.0$)
  - Luminance check ($30.0 \le \mu_L \le 235.0$, $\sigma_L \ge 20.0$)
  - Aspect ratio bounding ($0.33 \le \text{AR} \le 3.00$)
  - SHA-256 and 64-bit dHash perceptual hashing with Hamming distance deduplication
  - Metadata CSV tracking in `dataset/produce/real/metadata.csv`
- **CLI Ingestion Script**: Enhanced `scripts/ingest_real_produce_dataset.py` with `--category` flags and detailed status summary.

### Task 2: Double-Blind Human Annotation Workflow
- **Triple-Role Isolation**:
  - **Grader 1**: Grades independently; AI provisional grade is withheld.
  - **Grader 2**: Blind to Grader 1's grade and AI provisional grade.
  - **Senior Reviewer**: Audits escalated disagreements and provides mandatory textual rationale.
- **Automated Dispute Resolution**:
  - Consistent grades automatically ratify consensus (`CONSENSUS_REACHED` / `CONSENSUS_AUTO`).
  - Divergent grades escalate to `DISAGREEMENT` / `OPEN_DISAGREEMENT`.
- **API & UI Support**: Integrated double-blind inspection and submission tab in `/produce` with viewer-id isolation and grade masking.

### Task 3: Controlled Before-and-After Trial Runner
- **Cohort Architecture**:
  - Cohort A: Baseline unassisted grading.
  - Cohort B: AI-assisted grading with 10-attribute diagnostic explanations.
- **Statistical Metric Suite**:
  - Inter-rater agreement rate
  - Cohen's Kappa ($\kappa$)
  - Dispute rate & Relative Dispute Reduction (RDR):
    $$\text{RDR} = \frac{\text{Dispute}_{\text{baseline}} - \text{Dispute}_{\text{assisted}}}{\text{Dispute}_{\text{baseline}}}$$
  - Median duration per specimen (seconds)
  - Senior reviewer escalation counts
- **Division-by-Zero Defense**: If baseline dispute rate is $0.0\%$, the runner returns `None` (`UNDEFINED (Baseline Dispute Rate = 0.0%)`), preventing runtime math errors.

### Task 4: Real-World Failure Analysis Framework
Integrated formal edge-case evaluations from `docs/ERROR_ANALYSIS.md` into backend API and UI:
1. **Case 1: Poor Lighting & Severe Motion Blur** (Optical quality flaw, rejected by quality gate before grading).
2. **Case 2: Surface Occlusion & Foliage Obstruction** (Monocular limitation, capped at Grade B, dual-angle prompt).
3. **Case 3: Borderline Defect Percentage (4.8% vs 5.2%)** (Subtle defect near Grade A/B boundary, flagged for double-blind verification).
4. **Case 4: Background Wood Grain & Packing Box Shadow** (Artifact interference, HSV chroma isolation separates fruit from wood).

### Task 5: Stakeholder Usability Validation Protocol
- **Ethical Safeguards & Consent**: Implemented voluntary consent mechanism in compliance with `docs/STAKEHOLDER_VALIDATION.md` (no pacing surveillance, no worker ranking, zero facial biometrics).
- **Structured 5-Task Protocol**:
  1. Image capture and optical check.
  2. Attribute extraction and explanation review.
  3. Double-blind grading submission.
  4. Senior adjudication review.
  5. Offline PWA capture and sync.
- **Standardized Survey**: 5-point Likert ratings ($Q_1$ Usability, $Q_2$ Explanation Clarity, $Q_3$ Attribute Accuracy, $Q_4$ Disagreement Fairness, $Q_5$ Packhouse Viability) plus qualitative feedback fields.
- **Persistence & Integrity**: Stored in `dataset/produce/real/reports/stakeholder_feedback.json`, initialized with `PENDING_EXTERNAL_EVIDENCE`.

### Task 6: Stage 2 Metrics Dashboard
- Live dashboard `/metrics` updated with:
  - Real Produce Collection Target Card ($N=0/30$, category breakdown).
  - Controlled Experiment Table with $N_{\text{baseline}}$ and $N_{\text{assisted}}$ sample counters.
  - Stakeholder Usability Study Card with task completion rates and Likert radar bars.
  - Documented Genuine-Image Failure Cases Card with severity badges and mitigations.

### Task 7: 8-Step Demonstration Suite & Presentation Script
- **Interactive Stepper**: Integrated 8-step guided demonstration in `/produce` covering system architecture, optical quality gate, explainable rules, real dataset integrity, double-blind annotation, controlled trials, failure analysis, and stakeholder readiness.
- **Demonstration Script**: Authored complete 18-minute presentation script in `docs/STAGE_2_DEMONSTRATION_SCRIPT.md` including timing budget, speaker notes, visual cues, and anticipated reviewer Q&A.

### Task 8: Verification & Quality Assurance
- **Backend Tests**: **176 passed, 0 failed** in 34.05s (`pytest backend/tests`).
- **Frontend Production Build**: **0 errors**, built cleanly with Vite + TypeScript in 4.23s.

---

## 3. Summary of Files Created and Modified

### Backend Modules Created/Modified
- `backend/evaluation/real_produce_pipeline.py`:
  - Added `collection_category` to `METADATA_FIELDNAMES` and `ingest_real_produce_image`.
  - Added `get_real_produce_dataset_status` with category distribution and annotation status breakdown.
  - Added `get_real_produce_samples` with double-blind grade masking for Graders 1 and 2.
  - Added `get_stakeholder_validation_status` and `submit_stakeholder_feedback`.
  - Added `get_genuine_failure_cases` for the 4 documented edge cases.
- `backend/api/v1/produce_grading.py`:
  - `POST /api/v1/produce/real/batch-upload`: 12-step batch upload with per-file status.
  - `GET /api/v1/produce/real/samples`: Blind-isolated sample listings.
  - `GET /api/v1/produce/stakeholder/status`: Stakeholder study status.
  - `POST /api/v1/produce/stakeholder/submit`: Anonymous stakeholder survey submission.
  - `GET /api/v1/produce/real/failure-cases`: Failure case documentation.
- `backend/evaluation/produce_experiment_runner.py`:
  - Added median duration, senior escalations count, and reference evaluations count.
  - Added division-by-zero defense in `calculate_relative_dispute_reduction`.
- `backend/repositories/annotation_repository.py`:
  - Added optional `species` filter to `list_annotations`.
- `scripts/ingest_real_produce_dataset.py`:
  - Added `--category` flag and comprehensive `--status` report.

### Frontend Components Created/Modified
- `frontend/src/services/produceService.ts`:
  - Added `listRealProduceSamples`, `batchUploadRealProduce`, `getStakeholderStatus`, `submitStakeholderFeedback`, `getProduceFailureCases`.
  - Added sample size counters ($N_{\text{baseline}}$, $N_{\text{assisted}}$) to `ProduceExperimentSummary`.
- `frontend/src/pages/ProduceGrading.tsx`:
  - Redesigned into 5 tabbed views: *Grading & Diagnostics*, *Batch Ingestion*, *Double-Blind Annotation*, *Stakeholder Study Form*, and *Guided Demonstration*.
- `frontend/src/pages/MetricsDashboard.tsx`:
  - Added Stage 2 Collection Category targets card (10/10/10).
  - Added sample size counters to Controlled Experiment card.
  - Added Stage 2 Stakeholder Usability Study card.
  - Added Documented Genuine-Image Edge & Failure Cases card.

### Documentation & Test Suites
- `docs/STAGE_2_DEMONSTRATION_SCRIPT.md`: Comprehensive 18-minute demonstration script with speaker notes and defense Q&A.
- `backend/tests/test_real_produce_validation.py`: Added 5 Phase 18 unit tests (total 15 tests in file, all passing).

---

## 4. Verification Test Results

### Backend Test Suite (Pytest)
```
============================= test session starts =============================
platform win32 -- Python 3.11.16, pytest-9.1.1, pluggy-1.6.0
rootdir: D:\livestock_farm
plugins: anyio-4.15.1
collected 176 items

backend\tests\test_agreement_metrics.py .....                            [  2%]
backend\tests\test_annotation_schema.py .....                            [  5%]
backend\tests\test_audit_logging.py ....                                 [  7%]
backend\tests\test_auth_api.py ............                              [ 14%]
backend\tests\test_clinical_safety_escalation.py .....                   [ 17%]
backend\tests\test_confidence.py ....                                    [ 19%]
backend\tests\test_database_reliability.py .....                         [ 22%]
backend\tests\test_dataset_splitting.py ....                             [ 25%]
backend\tests\test_dataset_upload_api.py .....                           [ 27%]
backend\tests\test_dataset_versioning_manifest.py ...                    [ 29%]
backend\tests\test_deployment_smoke.py .....                             [ 32%]
backend\tests\test_disagreements_api.py .                                [ 32%]
backend\tests\test_disaster_recovery.py ...                              [ 34%]
backend\tests\test_experiment_framework.py ...                           [ 36%]
backend\tests\test_experiment_persistence.py ..                          [ 37%]
backend\tests\test_expert_annotation_workflow.py ....                    [ 39%]
backend\tests\test_explanation.py ..                                     [ 40%]
backend\tests\test_grading_api.py .....                                  [ 43%]
backend\tests\test_grading_service.py .....                              [ 46%]
backend\tests\test_health_api.py .                                       [ 47%]
backend\tests\test_image_sanitization.py .........                       [ 52%]
backend\tests\test_metrics_api.py .                                      [ 52%]
backend\tests\test_ml_prediction.py ..                                   [ 53%]
backend\tests\test_model_loading.py .                                    [ 54%]
backend\tests\test_phase11_api.py ....                                   [ 56%]
backend\tests\test_produce_experiments_and_api.py ......                 [ 60%]
backend\tests\test_produce_ingestion_and_cv.py .....                     [ 63%]
backend\tests\test_produce_rubric_and_rules.py ........                  [ 67%]
backend\tests\test_rbac_permissions.py ..............                    [ 75%]
backend\tests\test_real_assessment_e2e.py ...                            [ 77%]
backend\tests\test_real_dataset_runner.py ...                            [ 78%]
backend\tests\test_real_produce_validation.py ...............            [ 87%]
backend\tests\test_review_persistence.py ....                            [ 89%]
backend\tests\test_rule_engine.py ...                                    [ 91%]
backend\tests\test_secure_image_storage.py .....                         [ 94%]
backend\tests\test_sync_api.py .                                         [ 94%]
backend\tests\test_synthetic_produce_dataset.py .........                [100%]

===================== 176 passed, 152 warnings in 34.05s ======================
```

### Frontend Production Build (Vite + TypeScript)
```
> elhgs-frontend@0.1.0 build
> tsc && vite build

vite v5.4.21 building for production...
transforming...
✓ 1725 modules transformed.
rendering chunks...
computing gzip size...
dist/index.html                   0.90 kB │ gzip:   0.50 kB
dist/assets/index-Bytu8AH9.css   39.53 kB │ gzip:   7.11 kB
dist/assets/index-D8O1bUQL.js   564.64 kB │ gzip: 160.51 kB
✓ built in 4.23s
```

---

## 5. Physical World Action Checklist for the User

Because the software and experimental pipeline are now 100% complete and fully verified, the following physical real-world tasks must be personally administered by human investigators:

### Step 1: Collect 30 Genuine Tomato Photographs
- [ ] Visit a local tomato farm, market stall, or collection packhouse.
- [ ] Capture 30 sharp photographs using a smartphone camera (holding steady under adequate lighting):
  - **10 Specimens**: Apparent High-Quality (smooth, uniform red/pink, negligible defect).
  - **10 Specimens**: Apparent Minor Defects (light surface scratches, minor russeting, small cat-facing $< 15\%$).
  - **10 Specimens**: Apparent Substantial Defects (sunscald, blossom-end rot, deep growth cracks $\ge 15\%$).
- [ ] Ingest the photos using the Web UI at `/produce` (*Batch Ingestion* tab) or using CLI:
  ```bash
  .venv\Scripts\python scripts/ingest_real_produce_dataset.py --input-dir /path/to/photos --category apparent_high_quality
  ```

### Step 2: Administer Double-Blind Expert Annotation
- [ ] Enlist two independent agricultural evaluators or graders (**Grader 1** and **Grader 2**).
- [ ] Have Grader 1 evaluate the 30 specimens on `/produce` (*Double-Blind Annotation* tab).
- [ ] Have Grader 2 evaluate the same 30 specimens independently without seeing Grader 1's entries.
- [ ] Have a packhouse supervisor or senior researcher log in as **Senior Reviewer** to adjudicate any disputed specimens.

### Step 3: Run the Controlled Validation Experiment
- [ ] Once consensus annotations reach $\ge 10$ samples, navigate to `/metrics` and trigger the real-data validation experiment.
- [ ] Confirm calculation of Cohen's Kappa, inter-rater agreement rate, and relative dispute reduction.

### Step 4: Administer Field Usability & Stakeholder Study
- [ ] Present the informed consent form to 3–5 farm managers or packhouse workers.
- [ ] Guide participants through the 5 structured tasks (optical capture, explanation review, blind grading, adjudication, offline sync).
- [ ] Have participants submit their anonymous 5-item Likert scores and qualitative feedback via the *Stakeholder Study Form* tab at `/produce`.
- [ ] Verify the metrics dashboard updates from `PENDING_EXTERNAL_EVIDENCE` to `RECORDED_SESSIONS`.

### Step 5: Deliver Stage 2 Presentation
- [ ] Open the presentation script in [`docs/STAGE_2_DEMONSTRATION_SCRIPT.md`](file:///d:/livestock_farm/docs/STAGE_2_DEMONSTRATION_SCRIPT.md).
- [ ] Deliver the 18-minute walkthrough using the interactive stepper at `/produce` (*Guided Demonstration* tab).
