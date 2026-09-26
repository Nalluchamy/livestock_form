# REAL PRODUCE DATASET PROTOCOL & CURATION GUIDELINES (STAGE 2)

## 1. Objective & Target Scope

This protocol establishes the standardized procedure for assembling, curating, preprocessing, and splitting a real-image produce dataset for the Stage 2 prototype.

- **Primary Commodity**: Fresh Market Tomatoes (*Solanum lycopersicum*).
- **Target Sample Volume**: 60–100 genuine high-resolution images representing realistic harvest diversity across grades A, B, and C.
- **Ethical Foundation**: Transparent provenance, verified permissible licensing (CC0, CC-BY 4.0, or project-captured agricultural media with written facility permission), zero worker surveillance, and zero biometric privacy capture.

---

## 2. Directory Hierarchy

All produce dataset assets are structured strictly as follows:

```
dataset/produce/
├── raw/                     # Original unmodified image uploads (quarantine & ingestion)
├── processed/               # Sanitized, normalized, privacy-scrubbed images (UUID-named)
├── annotations/             # Double-blind expert annotations and adjudicated labels (JSONL)
├── splits/                  # Leakage-safe train, validation, and test split manifests
├── reports/                 # Automated image quality reports and hash logs
└── documentation/           # Provenance manifests, licensing agreements, and capture logs
```

---

## 3. Image Capture & Ingestion Specifications

### 3.1. Physical Capture Conditions
- **Device Requirements**: Standard mobile smartphone camera ($\ge 8\text{ MP}$) or tablet camera.
- **Background**: Neutral matte surface (e.g., solid gray card, clean harvest crate, non-reflective white backdrop) to maximize segmentation accuracy.
- **Illumination**: Diffuse daylight or shadow-free agricultural grading table lighting ($\ge 500\text{ lux}$). Avoid direct harsh sunlight causing specular glares or extreme shadows.
- **Framing & Orientation**: Fruit centered, filling approximately $60\% - 85\%$ of the frame. Capture top (calyx/stem) and lateral profile views.
- **Exclusion of Workers**: No human hands, fingers holding fruit, faces, or personal clothing may appear within the frame.

### 3.2. Automated Sanitization & Validation Pipeline
Every uploaded raw image traverses an automated ingest pipeline (`backend/evaluation/produce_ingestion.py`):

1. **EXIF/GPS Scrubbing**: All Exchangeable Image File (EXIF) metadata, GPS coordinates, device serial numbers, and capture software signatures are stripped before disk write.
2. **Cryptographic Deduplication**:
   - Exact duplicate prevention via SHA-256 hash lookup against existing raw manifests.
   - Near-duplicate prevention via perceptual difference hash (dHash 64-bit); image pairs with Hamming distance $\le 4$ are flagged as duplicate captures of the same fruit.
3. **Automated Quality Gate**:
   - Focus verification using Laplacian variance ($\sigma^2_{\text{Laplacian}} \ge 100$).
   - Illumination check: mean luminance in range $[40, 245]$.
   - Occlusion check: fruit surface visibility $\ge 70\%$.
4. **Persistent Renaming**: Images are renamed using cryptographic UUIDv4 (`tom_<uuid>.jpg`) to sever any connection to original local file paths or collector identities.

---

## 4. Leakage-Safe Dataset Splitting

To prevent optimistic bias during machine learning evaluation, dataset splitting strictly respects **Lot and Subject Boundaries**:
- If multiple photographs of the same tomato specimen (e.g., stem-end view and lateral view) exist, all views of that physical specimen are assigned exclusively to **one** partition (Train, Validation, or Test).
- Standard partition ratio: $70\%$ Training, $15\%$ Validation, $15\%$ Test.
- Stratification: Partitions must maintain approximately balanced representation across Grades A, B, and C.

---

## 5. Provenance Manifest Schema

Each curated image is logged in `dataset/produce/documentation/provenance_manifest.json` with the following attributes:
```json
{
  "sample_id": "tom_9c2a1e8f-7b4d-4e92-a1f0-08123456789a",
  "original_filename_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "commodity": "tomato",
  "source_type": "project_captured",
  "license": "CC-BY-4.0",
  "collection_date": "2026-09-25",
  "lighting_lux_estimate": 620,
  "surface_defect_pct": 3.8,
  "provisional_grade": "A",
  "verified_reference_grade": "PENDING_EXPERT_REVIEW",
  "sha256": "4b227777d4dd1fc61c6f884f48641d02b4d121d3fd328cb08b5531fcacdabf8a"
}
```

---

## 6. Strict Non-Fabrication Policy

> [!WARNING] Transparency Mandate
> If genuine tomato images have not yet been placed into `dataset/produce/raw/` by the research team or field station, the ingestion engine and dashboard must report status:
> `PENDING_REAL_IMAGES`
>
> The system shall never inject synthetic random noise, copy fake web stock photos without documentation, or generate fictitious sample counts to give a false impression of completed field data collection.
