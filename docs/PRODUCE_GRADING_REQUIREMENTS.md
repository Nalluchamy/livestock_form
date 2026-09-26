# PRODUCE QUALITY GRADING REQUIREMENTS SPECIFICATION (STAGE 2)

## 1. System Overview & Problem Scope

The Explainable Produce Quality Grading System provides farm packhouses, receiving docks, and field stations with an objective, explainable, and accountable method to grade agricultural produce (demonstrated on fresh market tomatoes) and systematically reduce grader-to-grader disputes.

The system addresses the primary root causes of commercial friction in farm produce grading:
1. **Subjective Boundary Disagreements**: Ambiguity between Grade A (premium table fruit) and Grade B (processing/cosmetic seconds) leading to dock rejections or payment disputes.
2. **Opaque Quality Assessments**: Graders assigning categorical grades without recorded visual justification or measurable criteria.
3. **Operational Fatigue & Inconsistency**: Quality drift over grading shifts due to changing lighting or grader fatigue.
4. **Lack of Dispute Adjudication**: Absence of an auditable double-blind review workflow to resolve grader discrepancies.

---

## 2. User Roles & Personas

| Role Code | Role Name | Primary Responsibility & Permissions |
| :--- | :--- | :--- |
| `FARMER` | Farm Field Handler / Packhouse Operator | Uploads produce lot images, views provisional grades, logs visual observations, uses offline field queue. |
| `EXPERT_GRADER` | Produce Quality Inspector | Conducts blind independent evaluations; enters measured attributes; cannot see peer grades before submission. |
| `SENIOR_REVIEWER` | Senior Agricultural Adjudicator | Reviews and resolves inter-grader disagreements; views audit trails; establishes definitive reference grade. |
| `ADMIN` | Farm System Administrator | Configures rubric thresholds; manages user accounts; monitors system health and experiment audit logs. |

---

## 3. Functional Requirements (FR)

### FR-1: Real Produce Image Ingestion & Privacy Sanitization
- **FR-1.1**: The system shall accept single image uploads (JPEG/PNG/WEBP, up to 10MB) and bulk ZIP archives of produce images.
- **FR-1.2**: All incoming images must be stripped of EXIF metadata, including GPS coordinates, camera serial numbers, and device identifiers.
- **FR-1.3**: Cryptographic integrity must be enforced: SHA-256 for exact duplicate detection and perceptual dHash (difference hash, hamming distance $\le 4$) for near-duplicate identification.
- **FR-1.4**: Images exhibiting identifiable human faces or intrusive worker clothing must be automatically flagged for privacy quarantine.

### FR-2: Computer Vision Feature Extraction & Quality Checks
- **FR-2.1**: Automated quality pre-checks must validate:
  - **Focus/Blur**: Laplacian variance threshold ($\ge 100$ required; $<100$ rejected as blurred).
  - **Illumination**: Mean pixel luminance in range $[40, 245]$; values outside flagged as under/over-exposed.
  - **Occlusion**: Minimum fruit surface visibility $\ge 70\%$; occluded $>30\%$ triggers `OCCLUDED_SURFACE` flag.
- **FR-2.2**: The pipeline shall automatically compute:
  - **Ripeness Stage / Color Ratio**: Normalized red-to-green and red-to-yellow chromaticity ratios from RGB/HSV color spaces.
  - **Surface Defect Area %**: Percentage of total segmented fruit surface exhibiting blemishes, dark spots, rot, or cracks.
  - **Shape Symmetry & Uniformity**: Contour aspect ratio ($\text{width}/\text{height}$) and circularity index ($4\pi \times \text{area} / \text{perimeter}^2$).

### FR-3: Explainable Rule-Based Grading Engine
- **FR-3.1**: The grading engine shall evaluate tomatoes into three provisional tiers:
  - **Grade A (Premium / Choice)**: Meets strict color uniformity, defect area $< 5\%$, zero severe bruising, intact skin.
  - **Grade B (Commercial / Processing)**: Acceptable maturity, defect area $5\% - 15\%$, minor skin cracking or slight bruising permitted.
  - **Grade C (Cull / Reject)**: Unmarketable fresh, defect area $> 15\%$, active rot, severe crush/sunscald damage.
- **FR-3.2**: Every grading decision must generate:
  - Deterministic provisional grade (`A`, `B`, or `C`).
  - Itemized triggered rules explaining why criteria were met or failed.
  - Primary contributing factors in plain, non-technical language.
  - Measured confidence score based on rule margin of clearance.
  - Escalation flags triggering human expert review for borderline cases.
- **FR-3.3**: Advisory machine learning inference (Decision Tree / Logistic Regression) may run in parallel to provide statistical comparison, but the deterministic rule engine remains authoritative.

### FR-4: Double-Blind Expert Annotation & Disagreement Adjudication
- **FR-4.1**: Independent graders shall evaluate produce lots without visibility of concurrent grader scores or AI provisional grades.
- **FR-4.2**: If two independent graders disagree on a lot (e.g., Grader 1 assigns Grade A, Grader 2 assigns Grade B), a disagreement event must be automatically instantiated in PostgreSQL.
- **FR-4.3**: Disagreements follow a persistent lifecycle:
  - `OPEN`: Automated detection upon submission of discordant independent grades.
  - `UNDER_REVIEW`: Claimed by a Senior Reviewer with assigned reviewer ID.
  - `RESOLVED`: Final reference grade confirmed with documented rationale and timestamp.

### FR-5: Before-and-After Controlled Experiment Framework
- **FR-5.1**: The system shall support a counterbalanced experiment comparing human-only grading against AI-assisted grading.
- **FR-5.2**: The framework must track and persist in PostgreSQL:
  - Inter-grader agreement (exact match %, Cohen's kappa $\kappa$).
  - Grader dispute rate (% of lots triggering disagreement).
  - Relative dispute-rate reduction: $\frac{\text{DisputeRate}_{\text{human}} - \text{DisputeRate}_{\text{assisted}}}{\text{DisputeRate}_{\text{human}}} \times 100\%$.
  - Average assessment time per sample (seconds).
- **FR-5.3**: Real measured results must be strictly demarcated from synthetic or pending benchmarks (`PENDING_EXPERIMENT`).

### FR-6: Field-Friendly Offline PWA Architecture
- **FR-6.1**: Graders must be able to record observations, capture photos, and queue assessments in IndexedDB without cellular connectivity.
- **FR-6.2**: Queue items must synchronize automatically upon connection restoration with conflict detection.
- **FR-6.3**: User session boundary enforcement must ensure local storage partitions prevent data exposure across shared field tablets.

---

## 4. Non-Functional Requirements (NFR)

- **NFR-1 (Integrity & Non-Fabrication)**: System interfaces and reports must never display fabricated sample counts, fake expert annotations, or artificial performance percentages. Where genuine field data is pending, interfaces must state `PENDING_REAL_IMAGES` or `PENDING_EXPERIMENT`.
- **NFR-2 (Inference Latency)**: End-to-end rule evaluation and image feature extraction must execute in $< 500$ ms per produce image.
- **NFR-3 (Regulatory & Ethical Compliance)**: Zero worker facial recognition, zero productivity pacing quotas, and no punitive grader surveillance.
