# ⚠️ System Limitations & Documented Edge Case Audit

> **Scope Statement:** ELHGS is an AI-assisted livestock health and condition grading system that provides explainable recommendations using non-identifiable images and measurable health attributes. It supports human graders and never replaces expert judgment.

| Field | Description |
|:---|:---|
| **Document Version** | 1.1.0 (Phase 11 Audit Edition) |
| **Edge Cases Documented** | 4 real system execution scenarios with inputs, outputs, confidence, & action |
| **Real Evaluation Status** | Retrospective evaluation on held-out splits; prospective human study pending |
| **Audit Status** | Verified against running API, PostgreSQL models, and PWA services |

---

## 1. Overview & Operational Boundaries

While ELHGS delivers a robust Rule Engine baseline and white-box Decision Tree advisory model, real-world deployment presents edge cases involving image quality degradations, borderline expert disagreements, partial field observation data, and offline synchronization collisions. 

This document details 4 empirical edge cases run directly through the application, providing exact input parameters, system outputs, confidence scores, review actions, and technical rationales.

---

## 2. Documented Edge Cases (With System Outputs)

### Edge Case 1: Poor Image Quality / Bad Lighting / Missing Photo

- **Scenario:** A field inspector attempts to grade an animal in low-light pen conditions where the camera capture fails or produces an unreadable dark image.
- **Input Parameters:** Physical attributes provided (`body_condition: 3.0`, `coat_quality: "Smooth"`, `eye_condition: "Clear"`, `wound_presence: "None"`, `mobility: "Normal"`, `appetite: "Good"`), but `has_image` flag set to `False`.
- **System Output:**
  ```json
  {
    "grade": "A",
    "confidence": 80.0,
    "reasons": [
      "Body condition is optimal",
      "Coat quality is smooth",
      "Eye condition is clear",
      "Wound presence is none",
      "Mobility is normal",
      "Appetite is good",
      "Final Grade: A (Average of sub-grades)"
    ],
    "missing_attributes": [],
    "review_required": false
  }
  ```
- **Confidence Score:** **80.0%** (-20% penalty automatically applied due to missing/invalid image evidence).
- **Action Taken:** **Graded with reduced confidence badge.**
- **Technical Rationale:** The Rule Engine successfully computes Grade A based on physical observation metrics, but penalizes overall confidence by 20% to account for unverified image evidence.

---

### Edge Case 2: Borderline / Ambiguous Expert Disagreement (Real Validation Sample `VAL-014`)

- **Scenario:** A borderline animal with slightly elevated BCS (3.6) and mild mobility limp evaluates close to the B/C boundary. Grader 1 assigned **Grade B**, while Grader 2 assigned **Grade C**. The field grader submits **Grade C**.
- **Input Parameters:** `body_condition: 3.6`, `coat_quality: "Slightly rough"`, `eye_condition: "Clear"`, `wound_presence: "None"`, `mobility: "Slight limp"`, `appetite: "Fair"`, `human_grade: "C"`.
- **System Output:**
  ```json
  {
    "grade": "B",
    "confidence": 100.0,
    "reasons": [
      "Body condition is slightly under/overweight",
      "Coat quality is slightly rough",
      "Eye condition is clear",
      "Wound presence is none",
      "Mobility is slight limp",
      "Appetite is fair",
      "Final Grade: B (Average of sub-grades)"
    ],
    "disagreement": {
      "human_grade": "C",
      "system_grade": "B",
      "reason": "Human graded C, but system calculated B based on rules.",
      "review_required": true
    }
  }
  ```
- **Confidence Score:** **100.0%** (All attributes present).
- **Action Taken:** **Flagged for Senior Review (`review_required = True`). Human grade C preserved.**
- **Technical Rationale:** The system calculates Grade B based on sub-grade averaging (numeric 2.0). When the human grader submits Grade C, `detect_disagreement` catches the mismatch and creates a `Disagreement` entity for senior review while **never overwriting human authority**.

---

### Edge Case 3: Partial Attributes / Field Connectivity Gap

- **Scenario:** A field worker in a remote pasture loses battery or time and submits an evaluation with 2 of 6 physical attributes omitted (`wound_presence` and `appetite` left blank).
- **Input Parameters:** `body_condition: 3.0`, `coat_quality: "Smooth"`, `eye_condition: "Clear"`, `mobility: "Normal"` (`wound_presence` and `appetite` missing).
- **System Output:**
  ```json
  {
    "grade": "A",
    "confidence": 70.0,
    "reasons": [
      "Body condition is optimal",
      "Coat quality is smooth",
      "Eye condition is clear",
      "Mobility is normal",
      "Final Grade: A (Average of sub-grades)"
    ],
    "missing_attributes": ["wound_presence", "appetite"],
    "review_required": false
  }
  ```
- **Confidence Score:** **70.0%** (-15% penalty per missing attribute $\times 2 = -30\%$).
- **Action Taken:** **Graded with missing attribute warning.**
- **Technical Rationale:** The Rule Engine evaluates available attributes, but explicitly itemizes missing attributes in `missing_attributes` and applies a 30% confidence penalty. If 3 or more attributes were missing, confidence would drop below 50%, triggering automatic Senior Review.

---

### Edge Case 4: Offline Synchronization Collision

- **Scenario:** The same animal is evaluated independently on two offline field devices before reconnecting to cellular networks. Device 1 assigns Grade A (`client_offline_id: "OFF-UUID-9012"`), and Device 2 assigns Grade B (`client_offline_id: "OFF-UUID-9012"`).
- **Input Parameters:** Two incoming payloads to `POST /api/v1/sync` sharing the same `client_offline_id`.
- **System Output:**
  ```json
  {
    "status": "success",
    "message": "Sync completed with 1 new event processed and 1 duplicate skipped.",
    "data": {
      "synced_count": 1,
      "duplicate_count": 1,
      "failed_count": 0
    }
  }
  ```
- **Action Taken:** **Client-side UUID Deduplication Fired.**
- **Technical Rationale:** The two-stage sync manager checks `client_offline_id` against existing database records. The initial event is persisted to `fact_grading_events`, while the duplicate submission is safely trapped and logged to prevent database corruption.

---

## 3. Analytical Finding: ML Model vs. Rule Engine Performance Gap

### Measured Empirical Performance Gap
On the $N=32$ real validation dataset ([`data/validation_set/`](file:///c:/Users/nallu/Desktop/livestock_farm/data/validation_set/)):
- **Rule Engine Baseline vs. Expert Consensus:** **Cohen's Kappa $\mathbf{\kappa = 0.6279}$** (71.88% exact match, 93.75% adjacent match).
- **Decision Tree ML Model vs. Expert Consensus:** **Cohen's Kappa $\mathbf{\kappa = 0.3043}$** (53.12% exact match, 81.25% adjacent match).

### Root Cause Analysis
The Decision Tree ML model was trained on a 600-sample synthetic dataset (`dataset_loader.py`) generated using a simplified single-attribute threshold heuristic (where any single non-ideal attribute triggered a grade cap). In contrast, the real expert validation dataset was evaluated using multi-attribute sub-grade averaging and multi-warning thresholds (`rules.py`). This training distribution mismatch causes the Decision Tree ML model to over-penalize minor individual attribute variations on real expert samples.

### Technical Recommendation
1. **Production Default:** The deterministic, explainable **Rule Engine MUST be treated as the primary production default grading method**.
2. **ML Positioning:** The Decision Tree ML model is positioned strictly as an **experimental/advisory secondary layer** until retrained on a larger real-world expert validation dataset ($N \ge 500$).

---

## 4. Stage 2 Produce Quality Grading Operational Boundaries & External Dependencies

### 4.1. Domain Delineation
The Stage 2 demonstration establishes Fresh Market Tomato Quality Grading as the primary demonstration domain. The livestock health grading engine (Phases 1–14) is completely preserved as a dedicated secondary module.
- Produce attributes (surface blemish %, ripeness color index, aspect ratio circularity, bruise severity) are strictly quarantined from livestock attributes.

### 4.2. External Data Dependencies (Transparency Disclosure)
1. **Real Image Collection Status**: The ingestion and sanitization pipeline (`backend/evaluation/produce_ingestion.py`) is fully functional. In the absence of a large field-collected raw dataset on disk, the system transparently reports `PENDING_REAL_IMAGES` rather than injecting unverified synthetic images.
2. **Double-Blind Expert Annotation**: The double-blind interface and persistent adjudication workflow are operational. Where agricultural produce graders have not yet logged live in-person annotations, reference grading is explicitly marked as `PENDING_EXPERT_REVIEW`.
3. **Controlled Experiment Protocol**: The before-and-after experiment runner (`backend/evaluation/produce_experiment_runner.py`) provides end-to-end mathematical metrics (Cohen's kappa, dispute reduction %, timing) and PostgreSQL persistence. Trials pending physical participant execution are designated `PENDING_EXPERIMENT`.
4. **Stakeholder Validation**: Comprehensive consent forms, task protocols, and survey instruments are created in `docs/STAKEHOLDER_VALIDATION.md` and flagged as `PENDING_EXTERNAL_EVIDENCE`.

### 4.3. Optical & Physical Boundaries
- **Internal Flesh Quality**: Photographic inspection cannot assess internal sugar content (Brix), internal hollow cavities (puffiness), or seed cavity rot without destructive testing or near-infrared spectroscopy (NIR).
- **Surface Lighting Glare**: Severe specular reflection from direct sunlight can mimic pale/unripe patches; standardized diffuse lighting ($\ge 500\text{ lux}$) is mandatory.
