# REAL PRODUCE DATASET AUDIT & INGESTION REPORT (PHASE 17)

## 1. Dataset Objective

The genuine tomato validation dataset is established to provide an empirical, real-world benchmark for the **Explainable Quality Grading System (EQGS)** Stage 2 produce grading module. Its primary objectives are:
- Validating the deterministic produce grading rubric against genuine agricultural harvest conditions.
- Measuring inter-rater reliability (Cohen's Kappa $\kappa$) between independent agricultural inspectors.
- Evaluating the error-prevention efficacy of EQGS optical quality gates on uncurated smartphone captures.
- Serving as the exclusive evaluation partition for production accuracy claims, strictly quarantined from synthetic development data.

---

## 2. Collection Procedure

The real produce ingestion protocol follows a structured 5-step operational workflow:
1. **Field Capture**: Produce inspectors, packhouse staff, or farm collection managers photograph individual tomatoes using standard smartphone cameras (12–48 MP) under operational ambient light.
2. **Standardized Staging**: Fruit is positioned on clean packhouse grading mats, electronic scales, or harvest crates with calyx or lateral profile facing the lens.
3. **Ingestion Verification**: Images are ingested via `POST /api/v1/produce/real/upload` or the CLI tool `scripts/ingest_real_produce_dataset.py`.
4. **Sanitization & Provenance**: The system scrubs all EXIF/GPS tags, calculates SHA-256 and perceptual difference hashes (dHash), evaluates human presence/PII flags, normalizes the resolution to a clean square format, and assigns an anonymized identifier (`real_tom_<uuid>`).
5. **Raw Evidence Preservation**: The uncompressed original image is preserved immutable in `dataset/produce/real/raw/`, while the sanitized working image is saved in `dataset/produce/real/processed/`.

---

## 3. Real Images Actually Collected & Target Metrics

In strict accordance with the project's **non-fabrication and scientific integrity principles**, all counts represent physical files verified on disk and recorded in `dataset/produce/real/metadata.csv`:

| Parameter | Specification | Current Verified Status |
| :--- | :--- | :--- |
| **Real Images Collected** | Physical genuine photos on disk | **0** |
| **Target Required (Minimum)** | Mandatory threshold for Stage 2 validation | **30** |
| **Remaining Images Required** | Outstanding quota to begin statistical trials | **30** |
| **Recommended Target** | Recommended sample size for distribution coverage | **50** |
| **Repository Status** | Current state of real dataset | **`PENDING_REAL_DATA`** |

> [!IMPORTANT]
> **Strict Non-Fabrication Commitment**: Under no circumstances does the system claim 30 genuine photographs exist prior to physical ingestion. Synthetic images from `dataset/produce/synthetic/` are permanently quarantined and are never converted or substituted into real data partitions.

---

## 4. Image-Source Description

Target acquisition environments encompass three primary agricultural collection stages:
1. **Farm Packhouses**: Primary sorting and washing tables in rural collection centers (natural daylight from open bays, diffuse fluorescent lamps).
2. **Wholesale Produce Mandis / Markets**: Direct wholesale collection stalls with fruit held in standard plastic crates or wooden sorting bins under ambient daylight.
3. **Greenhouse Harvest Stations**: Direct off-vine harvest benches evaluating early ripeness stages (Breaker, Turning, Light Red).

---

## 5. Privacy & Data Protection Procedure

To safeguard participants, photographers, and farm locations:
1. **EXIF & GPS Stripping**: All Exchangeable Image File Format (EXIF) metadata, including GPS coordinates, camera serial numbers, device models, and timestamps, are permanently stripped upon upload.
2. **Heuristic PII & Human Presence Screening**: Images are scanned for human presence via skin-tone density heuristics and vertical aspect ratio thresholds. If human faces, hands, or identifiable human features cover $> 45\%$ of the upper frame quadrant, the upload is rejected with HTTP 422: *"Crop to fruit only; human presence detected."*
3. **Anonymized Identifiers**: Images are decoupled from farm names and user identities, receiving random hexadecimal identifiers (`real_tom_<12hex>`).

---

## 6. Double-Blind Annotation Procedure

Ground truth quality grades are **never assigned automatically** by computer vision models. The reference grade is established through an independent double-blind expert workflow:

```
GENUINE PRODUCE IMAGE
        │
        ▼
   Anonymized ID
        │
   ┌────┴────────────────────────┐
   ▼                             ▼
Grader 1 (Blind)            Grader 2 (Blind)
(Does NOT see Grader 2)     (Does NOT see Grader 1)
   │                             │
   └──────────────┬──────────────┘
                  ▼
         Disagreement Check
        ┌─────────┴─────────┐
        ▼                   ▼
     Identical           Conflicting
 (Grader 1 == Grader 2)   (Grader 1 != Grader 2)
        │                   │
        ▼                   ▼
CONSENSUS_REACHED    OPEN_DISAGREEMENT
 (Reference Grade)          │
                            ▼
                    Senior Adjudicator
                  (Authoritative Decision)
                            │
                            ▼
                    CONSENSUS_REACHED
```

---

## 7. Grader Workflow & State Machine

1. **State `PENDING`**: Image is ingested and registered; awaiting assignment to Grader 1.
2. **State `PARTIALLY_ANNOTATED`**: Grader 1 has submitted independent assessment (grade, confidence, observations); Grader 2 has not yet submitted. Grader 1's grade is masked from Grader 2.
3. **State `CONSENSUS_REACHED`**: Both Grader 1 and Grader 2 have submitted matching grades (e.g., both Grade A). The grade is automatically promoted to authoritative ground truth `grade`.
4. **State `DISAGREEMENT`**: Grader 1 and Grader 2 submitted discordant grades (e.g., Grader 1 = A, Grader 2 = B). The record is flagged with `review_status = 'OPEN_DISAGREEMENT'` and routed to the Senior Reviewer.
5. **Adjudication**: The Senior Reviewer inspects both independent grades, full-resolution crops, and biological attributes, submitting a binding consensus grade and clinical rationale.

---

## 8. Current Grade Distribution

As of Phase 17 initiation:
- **Total Genuine Images**: 0
- **Grade A (Premium)**: 0 (0.0%)
- **Grade B (Commercial)**: 0 (0.0%)
- **Grade C (Cull/Reject)**: 0 (0.0%)
- **Status**: Held as `PENDING_REAL_DATA`.

---

## 9. Data-Quality & Optical Checks

Every genuine photograph must pass the automated optical quality gate before entering the dataset:
- **Format Verification**: Valid JPEG, PNG, or WebP bytes (max 15 MB).
- **Dimension Check**: Minimum resolution $\ge 150 \times 150\text{ px}$; maximum $\le 8000 \times 8000\text{ px}$.
- **Illumination Gate**: Mean luminance $Y \in [40.0, 240.0]\text{ lux proxy}$. Captures below 40 lux trigger `FLAG_LOW_ILLUMINANCE`.
- **Sharpness Gate**: Focus Laplacian variance $\sigma^2_{\text{Laplacian}} \ge 100.0$. Captures below 100 trigger `FLAG_IMAGE_BLUR` and are classified as `REJECTED_IMAGE`.
- **Occlusion Threshold**: Fruit surface obstruction must not exceed $20.0\%$ for Grade A clearance.

---

## 10. Duplicate & Near-Duplicate Detection

To prevent dataset contamination and data leakage:
1. **Exact Cryptographic Matches**: SHA-256 hash computed on binary contents. Exact matches are rejected immediately with HTTP 409 Conflict.
2. **Perceptual Near-Duplicates**: 64-bit difference hash (dHash) computed across adjacent pixel gradients. Samples with Hamming distance $d_H \le 4$ are rejected at ingestion as near-duplicates of existing photos.

---

## 11. Dataset Limitations

1. **Monocular Single-View Occlusion**: A single smartphone photograph cannot observe the unexposed underside or stem cavity of the fruit. Severe lesions on hidden hemispheres require dual-angle photography.
2. **Ambient Lighting Variance**: Natural solar shifts in open-air packhouses introduce color temperature shifts ($3000\text{K} - 6500\text{K}$) that affect RGB chromaticity.
3. **Background Detritus**: Heuristic edge segmentation can be affected by dark wood grain, shadows, or debris on non-standard grading tables.

---

## 12. Remaining Collection Requirements

To fulfill the Stage 2 milestone validation protocol:
- **Mandatory Minimum**: 30 genuine, double-blind annotated tomato photographs.
- **Diversity Target**: At least 10 Grade A, 10 Grade B, 5 Grade C, and 5 documented edge cases (poor lighting, partial occlusion, borderline defects).
- **Current Deficit**: 30 images remaining (`PENDING_REAL_DATA`).
