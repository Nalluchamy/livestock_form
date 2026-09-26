# SYSTEMATIC ERROR ANALYSIS & EDGE CASE EVALUATION (STAGE 2)

## 1. Overview & Objective

Agricultural computer vision operates in uncontrolled field environments characterized by variable solar illumination, dust, fruit orientation, and natural biological variance.

This document systematically analyzes three required edge-case failure scenarios evaluated during the Stage 2 testing process:
1. **Case 1**: Poor lighting or motion blur.
2. **Case 2**: Surface occlusion and hidden defects.
3. **Case 3**: Borderline quality leading to human grader disagreement.

Each failure scenario is documented with input conditions, expected vs. observed behavior, failure etiology, and architectural mitigations.

---

## 2. Failure Case Documentation

### Failure Case 1: Poor Lighting and Severe Motion Blur

| Parameter | Specification & Observed Values |
| :--- | :--- |
| **Test Image ID** | `test_fail_case_01_blur_lowlight` |
| **Input Conditions** | Illumination: $28\text{ lux}$ (deep shadow under packhouse hopper); Focus: Laplacian variance $\sigma^2_{\text{Laplacian}} = 42.1$ (rapid camera motion blur). |
| **Expected Behavior** | System must refuse to assign an unverified provisional grade; flag image as technically invalid; issue actionable guidance to operator to steady the device and illuminate the fruit. |
| **Observed Behavior** | Ingestion pipeline checks trigger: `FLAG_LOW_ILLUMINANCE` (mean luminance $26.4 < 40$) and `FLAG_IMAGE_BLUR` ($\sigma^2 = 42.1 < 100$). Image is flagged `UNSUITABLE_FOR_GRADING`; provisional confidence set to $0.0$; API returns HTTP 422 with structured explanation. |
| **Failure Etiology** | Motion blur attenuates high-frequency spatial gradients, causing superficial blemishes and micro-cracks to blend into surrounding healthy skin, risking false-negative defect detection. |
| **Corrective Action** | Real-time camera viewfinder in PWA evaluates sharpness prior to capture; prompts operator: *"Device moving or lighting low. Hold steady under $\ge 500\text{ lux}$ light."* |

---

### Failure Case 2: Surface Occlusion and Foliage Obstruction

| Parameter | Specification & Observed Values |
| :--- | :--- |
| **Test Image ID** | `test_fail_case_02_occluded_calyx` |
| **Input Conditions** | Large vine leaf and packaging cardboard occluding $34\%$ of the upper tomato hemisphere; blossom end is not visible. |
| **Expected Behavior** | System must detect surface obstruction; prevent false Grade A assignment based on partial visible skin; trigger human review escalation. |
| **Observed Behavior** | Fruit segmentation reports visibility ratio $= 66.0\%$ ($34.0\%$ occlusion). Rule engine generates rule `RULE_PARTIAL_OCCLUSION_WARNING`; attaches flag `OCCLUDED_SURFACE_DETECTED`; assigns provisional Grade B with review trigger `REQUIRES_HUMAN_CONFIRMATION`. |
| **Failure Etiology** | Monocular single-view photography cannot inspect hidden surfaces. Severe defects (such as blossom end rot or calyx cavity mold) frequently manifest on unexposed surfaces. |
| **Corrective Action** | The PWA inspection workflow prompts for a dual-image sequence (calyx view and blossom-end profile) whenever occlusion exceeds $20\%$. |

---

### Failure Case 3: Borderline Quality & Grader Disagreement

| Parameter | Specification & Observed Values |
| :--- | :--- |
| **Test Image ID** | `test_fail_case_03_borderline_ab` |
| **Input Conditions** | Fully ripe red tomato with surface defect area $= 5.1\%$ (healed cosmetic russeting near stem; Grade A threshold is $\le 5.0\%$). |
| **Expected Behavior** | Independent Grader 1 classifies as Grade A (treating russeting as negligible cosmetic variation). Independent Grader 2 classifies as Grade B (strictly applying 5% defect cutoff). System must preserve both original human grades without overwriting, detect discordance, and initiate a persistent disagreement review. |
| **Observed Behavior** | Rule engine assigns provisional Grade B with `BORDERLINE_DEFECT_AREA` flag (margin $= 0.1\%$). Disagreement engine flags discordance: Grader 1 (`A`) $\ne$ Grader 2 (`B`). Disagreement record instantiated in PostgreSQL with status `OPEN`. Both original grader inputs are preserved intact. |
| **Failure Etiology** | Continuous biological traits (defect area, color ripening progression) encounter rigid categorical boundaries, creating unavoidable human subjectivity around threshold limits. |
| **Corrective Action** | Persistent review workflow routes sample to Senior Reviewer with high-resolution region zoom. Reviewer adjudicates to Grade A or B with documented commercial justification, permanently resolving the dispute. |

---

## 3. Systematic Mitigation Summary

| Failure Mode | Detection Mechanism | Primary Mitigation | Fallback Safety |
| :--- | :--- | :--- | :--- |
| **Camera Blur** | Laplacian Variance $< 100$ | Reject capture before grading | Prompt for immediate recapture |
| **Under-Exposure** | Luminance Mean $< 40$ | Reject capture; alert operator | Prevent false defect detection |
| **Severe Occlusion** | Visible Fruit Mask $< 70\%$ | Attach `OCCLUDED` flag | Mandate 2-angle photo capture |
| **Borderline Cutoff** | Defect area within $1.0\%$ of boundary | Attach `BORDERLINE` review flag | Escalate to Senior Adjudicator |
| **Grader Discordance** | Discordant independent grades ($g_1 \ne g_2$) | Automated PostgreSQL review creation | Double-blind audit trail |
| **Background Texture Confusion** | Edge gradient & dark grain clustering | Foreground GrabCut/contour mask | Flag for human adjudicator review |

---

## 4. Empirical Real-World Failure Analysis: Background Texture & Shadow Interference

### Failure Case 4: Packhouse Wood Grain & Cast Shadows Segmented as Surface Blemishes

| Parameter | Systematic Failure Analysis Specification |
| :--- | :--- |
| **INPUT** | Genuine photograph of a fresh, blemish-free Grade A slicing tomato positioned directly on an unpainted, weathered wooden sorting bench under directional overhead fluorescent lighting. Strong cast shadow on the lateral rim and deep dark wood grain knots immediately adjacent to the fruit contour. |
| **DETECTED FEATURES** | Fruit segmentation area: $82.4\%$ of frame; Illumination mean: $124.6\text{ lux}$ (optimal); Laplacian variance: $452.1$ (sharp); **Estimated Surface Defect Area: $24.4\%$**; Ripeness Stage: `RED`; Circularity: $0.92$. |
| **SYSTEM DECISION** | Rule engine triggers `RULE_GRADE_C_DOWNGRADE` based on defect area exceeding $15.0\%$; provisional grade assigned: **Grade C** with `CONFIDENCE = 90.0%`. |
| **HUMAN DECISION** | Both independent human agricultural inspectors classify the tomato as **Grade A (Premium Table Fresh)**, noting pristine skin with zero lesions or rotting. |
| **DIFFERENCE** | Critical two-grade divergence: System Grade C (Cull) vs. Human Grader Consensus Grade A (Premium). Commercial impact: potential false downgrading and severe financial loss for the producer. |
| **ROOT CAUSE** | Monocular pixel-level heuristic segmentation detects dark high-contrast linear gradients. Weathered wood grain fissures and dark shadow boundaries hugging the perimeter of the fruit exhibit luminance ratios $< 0.65$ of the mean fruit body brightness, falsely triggering the blemish segmentation threshold. |
| **CORRECTIVE ACTION** | 1. **Computer Vision Enhancement**: Implement strict foreground boundary dilation masks and convex hull clipping to decouple exterior shadow contours and table textures from the internal epidermis.<br>2. **Operational Staging Protocol**: Field collection protocol mandates staging tomatoes on standardized neutral light-gray or white grading mats (reflectance $\ge 85\%$).<br>3. **Disagreement Safety Net**: When human input disagrees with the algorithmic provisional grade, the EQGS disagreement engine automatically halts automated decisions, assigns `OPEN_DISAGREEMENT`, and mandates Senior Referee review, permanently preventing unverified machine vision errors from entering commercial settlement. |
