# Cattle Health and Condition Grading Rubric (v2.0)

> **MANDATORY CLINICAL DISCLAIMER:**
> **ELHGS condition grading is an observational decision-support score, not a veterinary medical diagnosis. Urgent cases require immediate clinical examination by a licensed veterinarian.**

---

## 1. Scope & Purpose

This rubric standardizes health and condition grading specifically for **beef and dairy cattle** within the Explainable Livestock Health Grading System (ELHGS). It establishes objective criteria for physical health evaluation while enforcing strict ethical and scientific boundaries regarding what can and cannot be determined from photographs.

---

## 2. Taxonomy of Attributes: Visible vs. Physical Examination

To eliminate speculative or fabricated machine learning predictions, ELHGS enforces a strict separation between **directly photo-visible physical traits** and **clinical/management observations requiring physical examination or temporal records**.

### 2.1 Directly Photo-Visible Attributes (Extractable from Standardized Imagery)

| Attribute | Assessment Method | Valid Levels / Scale | Clinical Description |
| :--- | :--- | :--- | :--- |
| **Body Condition Score (BCS)** | Visual anatomical scoring (ribs, spine, hooks, pins, tailhead fat) | `1.0` to `5.0` (0.1 increments) | Standard 5-point beef/dairy scale. 1.0 = emaciated, 3.0 = optimal moderate, 5.0 = grossly obese. |
| **Coat / Hide Quality** | Visual texture and integrity | `Smooth`, `Slightly rough`, `Rough`, `Severe lesions` | Evaluates sheen, hair loss, presence of mange, ringworm patches, lice damage, or deep crusting. |
| **Eye Condition** | Close/lateral facial view | `Clear`, `Slight discharge`, `Cloudy`, `Severe infection` | Assesses conjunctival clarity, lacrimation, corneal opacity, or signs of infectious bovine keratoconjunctivitis (pinkeye). |
| **External Wound Presence** | Surface visual inspection | `None`, `Minor`, `Moderate`, `Severe` | Identifies abrasions, lacerations, open punctures, purulent abscesses, or deep tissue necrosis. |

---

### 2.2 Physical Examination / Management Record Attributes (STRICT NON-INFERENCE RULE)

> [!CAUTION]
> **STRICT PROTOCOL RULE: NEVER INFER APPETITE OR TEMPORAL MOBILITY SOLELY FROM A 2D PHOTOGRAPH.**
> A single photograph provides zero temporal, behavioural, or kinetic data. Under no circumstances should an algorithm or human grader fabricate or guess appetite or locomotion from a static image.

| Attribute | Mandatory Source | Valid Levels / Scale | Scientific Rationale |
| :--- | :--- | :--- | :--- |
| **Appetite** | Feed bunk intake log, rumination collar, or direct rancher observation over 12–24h | `Good`, `Fair`, `Poor`, `None` | An animal cannot be judged as eating or anorexic from a still photo; requires longitudinal observation. |
| **Mobility / Locomotion** | Dynamic motion assessment on flat hard/soft footing | `Normal`, `Slight limp`, `Lame`, `Unable to stand` | Locomotion scoring requires evaluating stride length, weight transfer, and spinal arch while moving. |
| **Live Weight** | Calibrated platform scale measurement | Numeric ($kg$) | Accurate body mass cannot be reliably determined by single-view 2D pixels without scale calibration. |

---

## 3. Five-Point Cattle Body Condition Score (BCS) Mapping

The 5-point scale maps deterministically to system grades as follows:

| Condition Tier | 5-Point BCS Range | Grade | Anatomical & Clinical Indicators |
| :--- | :--- | :--- | :--- |
| **Optimal / Prime** | $2.5 \le \text{BCS} \le 3.5$ | **Grade A** (Healthy) | Ribs barely visible or smoothly covered; transverse processes rounded; tailhead pockets lightly filled with fat. Optimal for breeding or market. |
| **Moderate Deviation** | $2.0 \le \text{BCS} < 2.5$ OR $3.6 \le \text{BCS} \le 4.0$ | **Grade B** (Observation) | Slightly thin (individual ribs palpable/visible) or moderately fleshy (patchy fat deposits over pins/hooks). Needs dietary adjustment. |
| **Marked Deviation** | $1.5 \le \text{BCS} < 2.0$ OR $4.1 \le \text{BCS} \le 4.5$ | **Grade C** (Treatment) | Marked thinness (sharp spine and transverse processes, visible shelf) or heavy fat cover (deep tailhead folds, flat back). Needs intervention. |
| **Critical / Extreme** | $\text{BCS} < 1.5$ OR $\text{BCS} > 4.5$ | **Grade D** (Critical) | **Severe emaciation** (bone structure prominent, zero subcutaneous fat, muscle wasting) or **morbid obesity**. Triggers urgent veterinary escalation. |

---

## 4. Multi-Attribute Consolidation & Hierarchical Rule Engine

1. **Critical Failure Rule:**
   If *any* attribute evaluates to Grade D (e.g. `BCS < 1.5`, `Wound: Severe`, `Eye: Severe infection`, or `Mobility: Unable to stand`), the overall grade is immediately **Grade D**, and an urgent veterinary escalation alert is triggered.
2. **Warning Threshold Rule:**
   If *two or more* attributes evaluate to Grade C (e.g., `BCS 1.8` and `Coat: Rough`), the overall grade is capped at **Grade C**.
3. **Consolidation Average Rule:**
   If no critical rule is met, numerical equivalents ($A=1, B=2, C=3, D=4$) are rounded to the nearest grade.

---

## 5. Photographic Capture & Image Quality Standards

To be accepted into the validated dataset or processed by the grading engine, images must satisfy these criteria:

1. **Framing & Angle:**
   - Lateral full-body profile of the standing animal (head to tailhead, top of spine to hooves visible).
   - Perpendicular angle ($90^\circ \pm 15^\circ$ to animal's flank).
2. **Lighting & Environmental Conditions:**
   - Diffuse natural daylight or high-lumen, non-flicker covered pen lighting.
   - Avoid deep backlight shadows, specular sun glare, or obstruction by dense corral rails.
3. **Resolution & Format:**
   - Minimum native capture: $512 \times 512$ pixels.
   - Formats accepted: JPEG, PNG, WebP.
4. **Privacy & Anonymization Standards:**
   - Zero human faces, identifying apparel, or operator landmarks.
   - Ear tags with farm-specific registration numbers or GPS metadata are strictly stripped/scrubbed upon ingestion.

---

## 6. Urgent Clinical Escalation Triggers

The system automatically generates a **CLINICAL ESCALATION ALERT** requiring urgent veterinary review when any of the following are detected:
- Overall assigned or predicted grade is **Grade D**.
- **Wounds:** Recorded as `Severe` (punctures, deep lacerations, necrotic tissue, maggots).
- **Mobility:** Recorded as `Unable to stand` (downer cow, severe trauma, spinal injury).
- **Body Condition:** $\text{BCS} < 1.5$ (severe cachexia) or $\text{BCS} > 4.5$ (extreme ketosis/hepatic lipidosis risk).
- **Eye Condition:** Recorded as `Severe infection` (corneal perforation, panophthalmitis).
