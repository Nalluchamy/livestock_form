# Phase 12 Implementation Plan: Real Livestock Dataset, Expert Annotation & Field Pilot

## 1. Executive Summary & Objective

The primary objective of **Phase 12** is to transform the Explainable Livestock Health Grading System (ELHGS) real-data infrastructure established in Phase 11 into a complete, usable, evidence-based livestock assessment workflow:
$$\text{Real Livestock Image} \rightarrow \text{Privacy Preprocessing} \rightarrow \text{Expert Annotation} \rightarrow \text{Validated Dataset} \rightarrow \text{Leakage-Safe Splitting} \rightarrow \text{Model Training \& Evaluation} \rightarrow \text{Explainable Assessment} \rightarrow \text{Human Review} \rightarrow \text{Persistent Metrics}$$

Phase 12 prioritizes **Cattle** (beef and dairy health and condition scoring) as the initial documented species and rubric, establishing a rigorous separation between directly visible physical traits and clinical attributes requiring human physical examination.

---

## 2. Existing Functionality vs. Missing Capabilities (Gap Analysis)

| Capability Area | Existing State (Phase 11) | Missing Capabilities (Phase 12 Objective) |
| :--- | :--- | :--- |
| **Species Scope** | Generic livestock rubric (A–D). | Documented Cattle Rubric v2 distinguishing visible traits (BCS, coat, eye clarity, external lesions) from clinical/management observations (appetite, progressive mobility). Prohibition of inferring appetite solely from photos. |
| **Dataset Ingestion** | Pillow image sanitizer functions in `backend/evaluation/ingestion.py`. | HTTP endpoints (`POST /api/v1/dataset/upload` & batch import), persistent storage in `dataset/real/processed/images/`, separate provenance records (`provenance_records.json`), and dynamic manifest tracking. |
| **Expert Annotation** | Pydantic schema and statistical agreement functions. | Persistent database table (`expert_annotations`), backend API (`/api/v1/annotations`), and React interface (`ExpertAnnotation.tsx`) with double-blind grader isolation, quality rejection, and consensus adjudication. |
| **Dataset Versioning** | Static manifest stub. | Versioned dataset manifests (e.g. `v1.0.0-real-pilot`), automated quality checks, group-aware splitting export, and dataset quality reporting. |
| **Model Training** | Synthetic dataset training script (`train.py`) and retrospective runner stub (`real_dataset_runner.py`). | Structured-attribute training pipeline on genuine consensus data (`train_real.py`), artifact serialization, and explicit pending states when real samples are below threshold. |
| **Clinical Safety** | Static explanation text and general confidence score. | Urgent clinical escalation triggers (Grade D, severe wounds, inability to stand), mandatory veterinary disclaimer on all API/UI outputs, and formal escalation documentation. |
| **Field Pilot** | Stakeholder protocol draft with pending status. | Supervised field pilot checklist, participant instructions, informed consent templates, and structured collection templates in `data/field_pilot/`. |

---

## 3. Scope Definition: Initial Livestock Species (Cattle)

- **Target Population:** Beef and dairy cattle across pastoral, feedlot, and auction environments.
- **Physical Observation Taxonomy:**
  1. *Directly Photo-Observable Attributes:*
     - **Body Condition Score (BCS):** 1.0–5.0 scale (rib visibility, spine prominence, tailhead fat deposits, transverse process sharpness).
     - **Coat / Hide Quality:** `Smooth`, `Slightly rough`, `Rough`, `Severe lesions` (mange, parasite patches).
     - **Eye Condition:** `Clear`, `Slight discharge`, `Cloudy`, `Severe infection` (pinkeye / infectious bovine keratoconjunctivitis).
     - **External Wound Presence:** `None`, `Minor`, `Moderate`, `Severe` (lacerations, abscesses, swelling).
  2. *Human Examination / Clinical History Required Attributes (NEVER inferred from photos):*
     - **Appetite:** `Good`, `Fair`, `Poor`, `None` (must be confirmed by feed intake observation or rancher log; **never inferred solely from a photograph**).
     - **Mobility / Locomotion:** `Normal`, `Slight limp`, `Lame`, `Unable to stand` (requires observing animal walking across hard/soft footing).
     - **Weight:** Live scale measurement in kg if available.

---

## 4. Proposed Technical Architecture & Detailed Implementation

### Component A: Cattle Scope & Rubric Documentation
- **File:** `docs/cattle_grading_rubric_v2.md`
- Defines the 5-point BCS rubric mapped to A/B/C/D tiers.
- Details the strict rule prohibiting algorithmic inference of appetite or internal systemic health from 2D photos.
- Specifies image capture standards: Lateral standing view, natural daylight/adequate pen lighting, minimum $512\times512$, no human or identifying ranch markers.

### Component B: Real Dataset Ingestion & Upload APIs
- **Files:** `backend/api/v1/dataset.py`, `backend/evaluation/ingestion.py`
- Endpoints:
  - `POST /api/v1/dataset/upload`: Upload single livestock image; runs format validation, SHA-256 and perceptual dHash duplicate check, EXIF/GPS scrubbing, 512x512 normalization, and PII heuristic flagging. Saves sanitized file to `dataset/real/processed/images/{uuid}.jpg`.
  - `POST /api/v1/dataset/batch-import`: Ingests zip/tar of multiple images or local folder with batch manifest.
- Provenance separation: Store consent metadata and permitted data sources in `dataset/real/documentation/provenance_records.json` separate from training features.

### Component C: Persistent Expert Annotation Architecture
- **Model:** `backend/models/expert_annotation.py` (table `expert_annotations`)
  - Columns: `id` (UUID), `sample_id` (String unique), `image_path` (String), `body_condition`, `coat_quality`, `eye_condition`, `wound_presence`, `mobility`, `appetite`, `weight_if_available`, `expert_grade_1`, `expert_grader_1_id`, `expert_grade_2`, `expert_grader_2_id`, `final_consensus_grade`, `consensus_reviewer_id`, `consensus_rationale`, `annotation_status`, `quality_flagged`, `quality_issue_reason`, `created_at`, `updated_at`.
- **Repository:** `backend/repositories/annotation_repository.py`
  - Double-blind grading logic: Grader 2 cannot see Grader 1's assessment before submitting.
  - Quality flagging workflow: Graders can flag image as insufficient quality.
  - Consensus adjudication workflow: Senior reviewer resolves inter-expert disagreements.
- **REST APIs:** `backend/api/v1/annotations.py`
  - `GET /api/v1/annotations`: List annotation tasks with filters (`status`, `grader_id`).
  - `GET /api/v1/annotations/{sample_id}`: Sample details.
  - `POST /api/v1/annotations/{sample_id}/grade`: Submit blind grade.
  - `POST /api/v1/annotations/{sample_id}/consensus`: Adjudicate consensus grade.
  - `POST /api/v1/annotations/{sample_id}/flag-quality`: Flag quality issues.
- **Frontend Page:** `frontend/src/pages/ExpertAnnotation.tsx`
  - Dual-panel UI: Left panel displays sanitized image with zoom; Right panel provides structured attribute entry, independent grade selection, quality flag button, and consensus view for senior reviewers.
  - Added to sidebar navigation and router (`/annotations`).

### Component D: Dataset Validation & Versioning
- **Module:** `backend/evaluation/dataset_versioning.py`
- Generates versioned dataset manifests (`dataset/real/documentation/dataset_manifest.json`) tracking total samples, complete double-blind annotations, disagreements, quality rejections, and class/species distributions.
- Produces group-aware splits (`dataset/real/splits/train.csv`, `val.csv`, `test.csv`) with zero duplicate cross-split leakage.
- Generates `docs/dataset_quality_report.md`.

### Component E: Real Model Training & Evaluation
- **Script/Module:** `backend/ml/train_real.py`
- Trains structured-attribute Decision Tree and Logistic Regression models on genuine expert consensus data.
- Feature set: `body_condition`, `coat_quality_enc`, `eye_condition_enc`, `wound_presence_enc`, `mobility_enc`, `appetite_enc` (observations available at inference time).
- Serializes models: `backend/models/decision_tree_real.joblib`, `backend/models/logistic_regression_real.joblib`.
- Evaluates on held-out test split only; records results in PostgreSQL `experiment_results`.
- If genuine consensus samples $< 10$, logs explicit `PENDING_REAL_DATA` status without fabricating metrics.

### Component F: Clinical Safety, Escalation, & Disclaimer
- **File:** `docs/clinical_safety_and_escalation.md`, `backend/services/grading_service.py`
- Urgent Escalation Triggers:
  - Critical Grade D overall.
  - Severe wounds (`Severe` wound presence).
  - Immobility / recumbency (`Unable to stand`).
  - Emaciation ($BCS < 1.5$) or morbid obesity ($BCS > 4.5$).
- Mandatory Veterinary Disclaimer appended to all responses:
  > *"Condition grade is an observational decision-support score, not a veterinary medical diagnosis. Urgent cases require immediate clinical examination."*

### Component G: Supervised Field Pilot Framework
- **Documents:**
  - `docs/field_pilot_checklist.md`: Pre-pilot, execution, and post-pilot operational steps.
  - `docs/field_pilot_instructions.md`: Grader step-by-step guidance.
  - `docs/field_pilot_consent_form.md`: Formal owner/operator consent template.
- **Storage:** `data/field_pilot/` with structured survey templates (`pilot_feedback_template.json` & `.csv`).

### Component H: Database Migrations
- **Alembic Migration:** `backend/alembic/versions/0003_expert_annotations.py`
  - Creates `expert_annotations` table with appropriate indexes on `sample_id`, `annotation_status`, and `quality_flagged`.

---

## 5. Verification Strategy & Test Plan

1. **Backend Tests:**
   - Maintain all 65 existing tests.
   - Add new tests:
     - `test_dataset_upload_api.py`: Uploading images, format validation, duplicate detection, PII flagging.
     - `test_expert_annotation_workflow.py`: Double-blind submission, blind isolation, consensus adjudication, quality flagging.
     - `test_dataset_versioning_manifest.py`: Quality validation, manifest compilation, group splitting.
     - `test_clinical_safety_escalation.py`: Urgent escalation alerts, veterinary disclaimer inclusion.
     - `test_real_assessment_e2e.py`: End-to-end grading with urgent escalation and persistent logging.
   - Execute: `.venv\Scripts\python -m pytest backend/tests/ -v`
2. **Frontend Tests:**
   - Execute TypeScript check and Vite build: `npm.cmd run build` in `frontend/`.
3. **Database Migration Verification:**
   - Execute: `alembic upgrade head`
4. **Final Deliverable:**
   - Generate `PHASE_12_FINAL_AUDIT.md`.
