# 📋 ELHGS Real-World Dataset Collection & Privacy Protocol

> **Scope Statement:** ELHGS is an AI-assisted livestock health and condition grading system that provides explainable recommendations using non-identifiable images and measurable health attributes. It supports human graders and never replaces expert judgment.

| Metadata Field | Value |
| :--- | :--- |
| **Document Version** | 1.1.0 (Phase 11 Production Data Upgrade) |
| **Target Domain** | Livestock Health and Condition Grading (Cattle, Swine, Sheep) |
| **Applicable Standards** | ISO/IEC 23894 (AI Risk Management), OIE Terrestrial Animal Health Standards |
| **Status** | Active Protocol — Governing Genuine Field Data Ingestion |

---

## 1. Ethical Principles & Informed Consent

1. **Farmer & Owner Consent:** All imagery and physical measurements collected from participating farms require written, informed consent from the animal owner or authorized farm manager.
2. **Voluntary Participation & Withdrawal:** Farm operators may withdraw their participation at any point prior to model training cutoff, triggering purging of raw assets.
3. **Non-Punitive Guarantee:** Data collected is strictly restricted to health grading research and advisory decision support. Under no circumstances may data be used for agricultural quota enforcement, tax inspection, or employee surveillance.

---

## 2. Privacy by Design & De-Identification Safeguards

To prevent indirect worker identification or facility location exposure:

### 2.1 Photographic Framing Standards
- **Subject Isolation:** Images must frame the livestock subject only. The camera angle should capture the lateral flank, head/eye profile, and limbs necessary for condition assessment.
- **Human Exclusion:** Absolutely no human faces, hands, clothing logos, or identification badges may be visible in the image frame.
- **Facility De-Identification:** Graders must avoid capturing background signage, facility names, vehicle license plates, or unique architectural markers.

### 2.2 Metadata & EXIF Stripping
- **Two-Tier Scrubbing:**
  1. *Client-Side Canvas Sanitization:* The PWA strips EXIF headers (GPS coordinates, device serials, timestamp offsets) during client-side canvas re-encoding before transmission.
  2. *Server-Side Ingestion Sanitization:* The backend ingestion pipeline (`backend/evaluation/ingestion.py`) parses binary image streams, discards all TIFF/EXIF tag dictionaries, and normalizes the image array.
- **UUID File Obfuscation:** Processed images are stored with randomized UUID identifiers (e.g., `8d2f5a6b-9c3e-4b1a-8f2d-7e4a1c5b9d3f.jpg`), preventing temporal or sequence-based correlation.

---

## 3. Data Provenance & Traceability

1. **Batch Manifests:** Real dataset intake is recorded in `dataset/real/documentation/manifest.json`, documenting ingestion timestamp, broad agricultural zone (e.g., `Zone-Northwest-Cattle`), and sample count.
2. **Segregation from Synthetic Data:**
   - Real data is strictly isolated under `dataset/real/`.
   - Synthetic data used for development and test harnesses resides in `dataset/synthetic/`.
   - Machine learning benchmark reports must explicitly demarcate whether performance metrics originate from `synthetic` development sets or `retrospective_real` evaluations.

---

## 4. Expert Annotation Protocol

### 4.1 Grader Qualifications
- Annotations must be provided by licensed veterinarians or officially certified livestock graders with documented field experience in Body Condition Scoring (BCS).

### 4.2 Independent Double-Blind Annotation Schema
Each sample is independently assessed by two expert evaluators without access to each other's grades or AI model recommendations:

```csv
sample_id,image_path,body_condition,coat_quality,eye_condition,wound_presence,mobility,appetite,weight_if_available,expert_grade_1,expert_grade_2,final_consensus_grade,annotation_status
```

### 4.3 Handling Disagreements & Consensus
- Disagreements between `expert_grade_1` and `expert_grade_2` are **preserved** in the dataset rather than discarded or artificially averaged.
- Status values:
  - `PENDING`: Waiting for second expert evaluation.
  - `INCOMPLETE`: Missing critical physical attribute measurements.
  - `DISAGREEMENT`: Grader 1 and Grader 2 assigned differing grades (e.g., A vs B); flagged for Senior Review.
  - `CONSENSUS_REACHED`: Graders agreed identically, or Senior Reviewer adjudicated final grade.
  - `REJECTED`: Sample failed image quality or framing guidelines.
- **AI Model Prohibition:** Expert ground-truth labels must **never** be generated or imputed by an AI model.

---

## 5. Dataset Splitting & Leakage Prevention

1. **Group-Aware Splitting:** Multiple images or longitudinal observations of the same animal must reside strictly within a single split (Train, Validation, or Test).
2. **Duplicate & Near-Duplicate Rejection:** SHA-256 and perceptual hashing are executed prior to splitting to prevent identical imagery across splits.
3. **Partition Targets:** 70% Train, 15% Validation, 15% Test when sample size $N \ge 100$. For small pilot cohorts, k-fold cross-validation with group constraints is enforced.

---

## 6. Known Limitations & Reporting

1. **Pilot Dataset Size:** When genuine real-world sample sizes are limited, model performance metrics must be reported with explicit confidence intervals and marked as `[Pilot Evaluation]`.
2. **Pending Real-Data Status:** If genuine real data has not yet completed full double-blind annotation, the system must report `PENDING_REAL_DATA` rather than presenting synthetic results as field-validated.
