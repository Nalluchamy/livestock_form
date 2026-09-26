# REAL TOMATO DATASET COLLECTION CHECKLIST & FIELD GUIDE
## Phase 20 Pilot Collection (10 Images) & Stage 2 Expansion (30 Images)

**Document ID:** EQGS-DOC-FIELD-COLLECTION-01  
**Project:** Explainable Quality Grading System (EQGS)  
**Target Milestone:** Initial Pilot (10 Genuine Photographs) -> Full Stage 2 Target (30 Genuine Photographs)  
**Applies To:** Smartphone Field Photography, Farm Managers, Quality Evaluators  

---

## 1. Collection Objectives & Targets

To validate the Explainable Quality Grading System with authentic empirical data, follow this structured collection guide using any standard smartphone camera.

### Initial Pilot Collection Matrix (10 Photographs Target)

| Category Code | Sampling Category | Target Count | Visual Characteristics (Collection Sampling Guidance Only) |
| :--- | :--- | :--- | :--- |
| `apparent_high_quality` | **Apparently High-Quality** | **3 Photos** | Smooth, firm, uniform red/pink skin; round/symmetrical shape; no visible cracks, rot, or severe blemishes ($< 5\%$ estimated surface blemish). |
| `apparent_minor_defects` | **Minor Visible Defects** | **4 Photos** | Small surface scratches, slight shoulder russeting/yellowing, minor blossom-end scarring, slight asymmetry ($5\% \le \text{blemish} < 15\%$). |
| `apparent_substantial_defects` | **Substantial Visible Defects** | **3 Photos** | Obvious blossom-end rot, deep growth cracks, soft bruised areas, mold spots, or major shape deformation ($\ge 15\%$ surface blemish). |

> [!IMPORTANT]
> **Collection Categories $\neq$ Final Grades**:  
> These categories are field sampling guidance buckets designed to guarantee defect diversity in the raw dataset. They are **never** treated as ground-truth labels. The true reference grade (Grade A, B, or C) is established strictly by independent, double-blind human expert consensus.

---

## 2. Photography Environment & Setup Rules

### 2.1 Specimen Placement
- **One Tomato Per Photograph**: Capture exactly one solitary tomato centered in the camera frame.
- **Surface**: Place the specimen on a plain, neutral background:
  - **Recommended**: A clean sheet of white printer paper, a neutral grey tray, or a solid plain tabletop.
  - **Avoid**: Dark rustic wood grain, newspaper/text, cluttered tools, or packing boxes with printed logos (this avoids false blemish detection from background texture).

### 2.2 Illumination & Exposure
- **Diffuse, Adequate Lighting**: Photograph under bright ambient daylight or diffuse indoor overhead lighting ($\ge 500\text{ lux}$).
- **Avoid Harsh Shadows & Glare**: Do not use direct phone flash against glossy tomato skin (causes white blowout patches). Avoid casting your own hand or body shadow directly over the tomato.
- **Exposure Quality Check**: The system's optical quality gate requires mean luminance between $30.0$ and $235.0$ lux equivalent.

### 2.3 Framing & Camera Technique
- **Camera Orientation**: Hold the smartphone steady directly perpendicular (top-down or $45^\circ$ forward angle) to the tomato.
- **Frame Coverage**: The tomato should occupy approximately **$60\%\text{--}80\%$ of the image frame**.
- **Focus & Sharpness**: Tap the smartphone screen on the tomato's center to lock focus before snapping. Hold still for 1 second.
  - *Quality Gate Requirement*: The system automatically measures Laplacian variance. A sharpness score $< 100.0$ will reject the photograph as blurred.

---

## 3. Privacy, Anonymity & Data Protection Protocol

To protect worker confidentiality and comply with research ethics:

- [x] **No Human Faces or Bodies**: Ensure hands, fingers, faces, feet, or reflective clothing do not appear anywhere in the frame.
- [x] **No Personal or Farm Identifiers**: Do not include grower tags, address labels, license plates, invoice receipts, or branded logos in the background.
- [x] **No Background Geolocation Cues**: Frame tightly on the tomato and neutral surface so farm facilities, vehicles, or specific packhouse landmarks are not visible.
- [x] **Automated Metadata Scrubbing**: When uploaded, the EQGS backend automatically scrubs all EXIF headers, GPS coordinates, device serial numbers, and timestamp tags before storing the processed photograph.

---

## 4. Step-by-Step Collection & Ingestion Procedure

### Step 1: Physical Sourcing
Select 10 fresh-market tomatoes (3 smooth/clean, 4 with minor blemishes, 3 with noticeable defects/scars).

### Step 2: Photographing
Photograph each specimen individually following Section 2. Save them to a folder on your phone or computer as `.jpg` or `.png`.

### Step 3: Upload via EQGS Web Interface
1. Launch the EQGS application in your browser and log in.
2. Navigate to the **Produce Quality Grading** page (`/produce`).
3. Click on the **📥 Batch Ingestion** tab.
4. Select the matching collection category from the dropdown:
   - For the 3 clean tomatoes: Select `Apparently High-Quality`.
   - For the 4 minor defect tomatoes: Select `Minor Visible Defects`.
   - For the 3 substantial defect tomatoes: Select `Substantial Visible Defects`.
5. Drag and drop the corresponding photo files into the upload box.
6. Click **Ingest Batch**.
7. Review the per-image status indicators:
   - Green `ACCEPTED`: Photo passed all 12 optical and privacy checks.
   - Red `REJECTED`: Check the failure reason (e.g., `IMAGE_BLUR` or `LIGHTING_TOO_DARK`) and recapture if needed.

### Alternative Step 3: Upload via CLI Script
Alternatively, place photos in a directory on your machine and run:
```bash
# Ingest 3 apparently high-quality tomatoes
.venv\Scripts\python scripts/ingest_real_produce_dataset.py --input-dir "C:/path/to/clean_tomatoes" --category apparent_high_quality

# Ingest 4 minor defect tomatoes
.venv\Scripts\python scripts/ingest_real_produce_dataset.py --input-dir "C:/path/to/minor_defects" --category apparent_minor_defects

# Ingest 3 substantial defect tomatoes
.venv\Scripts\python scripts/ingest_real_produce_dataset.py --input-dir "C:/path/to/substantial_defects" --category apparent_substantial_defects
```

---

## 5. Post-Ingestion Next Steps

Once the initial 10 genuine photographs are ingested:
1. **Check Dashboard Progress**: Visit `/metrics` to observe the **Initial Milestone (Phase 20 Pilot)** indicator reach $10 / 10$ ($100\%$).
2. **Conduct Double-Blind Grading Session**:
   - Have **Grader 1** grade all 10 images on `/produce` (*Double-Blind Annotation* tab).
   - Have **Grader 2** grade the same 10 images independently.
   - Any divergent grades will escalate to the **Senior Reviewer** queue for authoritative resolution with written rationale.
3. **Execute Real-Data Experiment**: Once 10 consensus reference grades are ratified, trigger the controlled experiment at `/metrics` to generate empirical Cohen's Kappa ($\kappa$) and dispute reduction statistics.
